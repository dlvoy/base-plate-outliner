#!/usr/bin/env python3
"""
Generate OpenSCAD script for irregular-shaped baseplates from PNG images.

This script reads a PNG image, determines which pixels represent the "inside"
of a shape (dark pixels), and generates an OpenSCAD script that renders
baseplates arranged to match the shape.
"""

import sys
import argparse
import colorsys
import random
from PIL import Image
import numpy as np
from scipy import ndimage
from typing import List, Tuple, Set, Optional


def load_and_threshold_image(image_path: str, threshold: int = 128) -> np.ndarray:
    """
    Load a PNG image and convert it to a binary mask.

    Args:
        image_path: Path to the PNG image
        threshold: Grayscale threshold (0-255). Pixels darker than this are "inside"

    Returns:
        2D numpy array of booleans (True = inside shape, False = outside)
    """
    # Load image and convert to grayscale
    img = Image.open(image_path)

    # Convert to grayscale if needed
    if img.mode != 'L':
        img = img.convert('L')

    # Convert to numpy array
    img_array = np.array(img)

    # Threshold: pixels with value < threshold are "inside" (dark = inside)
    # In grayscale, 0 is black, 255 is white
    binary_mask = img_array < threshold

    return binary_mask


def find_largest_rectangle(mask: np.ndarray, start_row: int, start_col: int) -> Tuple[int, int]:
    """
    Find the largest rectangle starting at (start_row, start_col) within the mask.

    Args:
        mask: 2D boolean array where True = available for placement
        start_row: Starting row position
        start_col: Starting column position

    Returns:
        Tuple of (width, height) of the largest rectangle
    """
    if not mask[start_row, start_col]:
        return (0, 0)

    rows, cols = mask.shape

    # Find maximum width from starting position
    max_width = 0
    for col in range(start_col, cols):
        if mask[start_row, col]:
            max_width += 1
        else:
            break

    if max_width == 0:
        return (0, 0)

    # Find maximum height for each possible width
    best_area = 0
    best_width = 0
    best_height = 0

    for width in range(1, max_width + 1):
        height = 0
        for row in range(start_row, rows):
            # Check if all cells in this row (for the given width) are True
            if all(mask[row, start_col:start_col + width]):
                height += 1
            else:
                break

        area = width * height
        if area > best_area:
            best_area = area
            best_width = width
            best_height = height

    return (best_width, best_height)


def extract_edge_and_interior(mask: np.ndarray, edge_thickness: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Separate a binary mask into edge and interior regions.

    Args:
        mask: 2D boolean array where True = inside shape
        edge_thickness: Thickness of the edge in brick units

    Returns:
        Tuple of (edge_mask, interior_mask)
    """
    # Create structuring element for erosion (8-connectivity for diagonal edges)
    struct = ndimage.generate_binary_structure(2, 2)

    # Erode the mask by edge_thickness pixels
    eroded_mask = mask.copy()
    for _ in range(edge_thickness):
        eroded_mask = ndimage.binary_erosion(eroded_mask, structure=struct)

    # Edge is original minus eroded, interior is eroded
    edge_mask = mask & ~eroded_mask
    interior_mask = eroded_mask

    return edge_mask, interior_mask


def greedy_rectangle_decomposition(mask: np.ndarray) -> List[Tuple[int, int, int, int]]:
    """
    Decompose a binary mask into rectangles using a greedy algorithm.

    Args:
        mask: 2D boolean array where True = inside shape

    Returns:
        List of rectangles as (x, y, width, height) tuples
    """
    # Create a working copy of the mask
    working_mask = mask.copy()
    rectangles = []

    rows, cols = mask.shape

    # Scan through the mask and place rectangles greedily
    for row in range(rows):
        for col in range(cols):
            if working_mask[row, col]:
                # Find the largest rectangle starting here
                width, height = find_largest_rectangle(working_mask, row, col)

                if width > 0 and height > 0:
                    # Record this rectangle
                    rectangles.append((col, row, width, height))

                    # Mark these cells as used
                    working_mask[row:row + height, col:col + width] = False

    return rectangles


def hex_to_hsl(hex_color: str) -> Tuple[float, float, float]:
    """
    Convert hex color to HSL.

    Args:
        hex_color: Hex color string (e.g., "#EAC645")

    Returns:
        Tuple of (hue, saturation, lightness) where hue is 0-360, s and l are 0-1
    """
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return (h * 360, s, l)


def hsl_to_hex(h: float, s: float, l: float) -> str:
    """
    Convert HSL to hex color.

    Args:
        h: Hue (0-360)
        s: Saturation (0-1)
        l: Lightness (0-1)

    Returns:
        Hex color string (e.g., "#EAC645")
    """
    r, g, b = colorsys.hls_to_rgb(h / 360.0, l, s)
    return f"#{int(r * 255):02X}{int(g * 255):02X}{int(b * 255):02X}"


def generate_random_color(base_color: str = "#EAC645") -> str:
    """
    Generate a random color with the same saturation and lightness as base_color,
    but with a random hue.

    Args:
        base_color: Base hex color to derive saturation and lightness from

    Returns:
        Random hex color string
    """
    _, s, l = hex_to_hsl(base_color)
    random_hue = random.uniform(0, 360)
    return hsl_to_hex(random_hue, s, l)


def generate_openscad_script(rectangles: List[Tuple[int, int, int, int]],
                            output_path: str = "irregular_baseplate.scad",
                            debug: bool = False,
                            image_height: int = 0,
                            interior_rectangles: Optional[List[Tuple[int, int, int, int]]] = None) -> None:
    """
    Generate an OpenSCAD script that renders the baseplates.

    Coordinate System Note:
    - Image coordinates: Y=0 at top, Y increases downward
    - OpenSCAD coordinates: Y=0 at bottom, Y increases upward
    - This function flips the Y-axis: translate_y = (image_height - y - height) * unit_size
    - This ensures the rendered model matches the input image orientation

    Args:
        rectangles: List of rectangles as (x, y, width, height) tuples (in image coordinates) for baseplates
        output_path: Path to save the generated .scad file
        debug: If True, use random colors for each baseplate
        image_height: Height of the source image in pixels (for Y-axis flipping)
        interior_rectangles: Optional list of rectangles for interior cubes (if using --edge mode)
    """
    # OpenSCAD uses unitGrid = [5, 2] and unitMbu = 1.6
    # So each brick unit is 5 * 1.6 = 8mm in X/Y
    unit_size = 8.0  # mm per brick unit

    script_lines = [
        "/**",
        " * Generated Irregular Baseplate",
        " * Auto-generated from PNG image",
        " */",
        "",
        "// Imports",
        "use <machineblocks/lib/block.scad>;",
        "include <machineblocks/config/config-default.scad>;",
        "",
    ]

    if interior_rectangles:
        script_lines.append("// Edge baseplates")
    else:
        script_lines.append("// Generate all baseplates")

    for i, (x, y, width, height) in enumerate(rectangles):
        # Calculate the translation position
        # Each unit in the grid corresponds to 8mm
        # NOTE: Y-axis needs to be flipped because image Y=0 is at top, but OpenSCAD Y=0 is at bottom
        translate_x = x * unit_size
        translate_y = (image_height - y - height) * unit_size

        # Generate color (random if debug mode, otherwise default)
        base_color = generate_random_color() if debug else "#EAC645"

        script_lines.append(f"\n// Baseplate {i + 1}: {width}x{height} at position ({x}, {y})")
        script_lines.append(f"translate([{translate_x}, {translate_y}, 0]) {{")
        script_lines.append("    machineblock(")
        script_lines.append(f"        size = [{width}, {height}, 1],")
        script_lines.append("        baseCutoutType = \"none\",")
        script_lines.append("        studs = true,")
        script_lines.append("        studType = \"solid\",")
        script_lines.append("        studIcon = \"none\",")
        script_lines.append("        pillars = false,")
        script_lines.append(f"        baseColor = \"{base_color}\",")
        script_lines.append("        ")
        script_lines.append("        // Config parameters")
        script_lines.append("        unitMbu = unitMbu,")
        script_lines.append("        unitGrid = unitGrid,")
        script_lines.append("        scale = scale,")
        script_lines.append("        baseHeightAdjustment = baseHeightAdjustment,")
        script_lines.append("        baseSideAdjustment = 0,  // Set to 0 to eliminate gaps between baseplates")
        script_lines.append("        baseWallThicknessAdjustment = baseWallThicknessAdjustment,")
        script_lines.append("        baseClampThickness = baseClampThickness,")
        script_lines.append("        tubeXDiameterAdjustment = tubeXDiameterAdjustment,")
        script_lines.append("        tubeYDiameterAdjustment = tubeYDiameterAdjustment,")
        script_lines.append("        tubeZDiameterAdjustment = tubeZDiameterAdjustment,")
        script_lines.append("        holeXDiameterAdjustment = holeXDiameterAdjustment,")
        script_lines.append("        holeYDiameterAdjustment = holeYDiameterAdjustment,")
        script_lines.append("        holeZDiameterAdjustment = holeZDiameterAdjustment,")
        script_lines.append("        pinDiameterAdjustment = pinDiameterAdjustment,")
        script_lines.append("        studDiameterAdjustment = studDiameterAdjustment,")
        script_lines.append("        studCutoutAdjustment = studCutoutAdjustment,")
        script_lines.append("        previewRender = previewRender,")
        script_lines.append("        previewQuality = previewQuality,")
        script_lines.append("        baseRoundingResolution = roundingResolution,")
        script_lines.append("        holeRoundingResolution = roundingResolution,")
        script_lines.append("        studRoundingResolution = roundingResolution,")
        script_lines.append("        pillarRoundingResolution = roundingResolution")
        script_lines.append("    );")
        script_lines.append("}")

    # Generate interior cubes if provided
    if interior_rectangles:
        script_lines.append("\n// Interior fill (cubes)")
        for i, (x, y, width, height) in enumerate(interior_rectangles):
            # Calculate the translation position (same as baseplates)
            translate_x = x * unit_size
            translate_y = (image_height - y - height) * unit_size

            script_lines.append(f"\n// Interior cube {i + 1}: {width}x{height} at position ({x}, {y})")
            script_lines.append(f"translate([{translate_x}, {translate_y}, 0]) {{")
            script_lines.append("    cube([")
            script_lines.append(f"        {width} * unitGrid[0] * unitMbu * scale,")
            script_lines.append(f"        {height} * unitGrid[0] * unitMbu * scale,")
            script_lines.append("        1 * unitGrid[1] * unitMbu * scale")
            script_lines.append("    ]);")
            script_lines.append("}")

    # Write the script to file
    with open(output_path, 'w') as f:
        f.write('\n'.join(script_lines))

    print(f"OpenSCAD script generated: {output_path}")
    print(f"Total baseplates: {len(rectangles)}")

    # Print statistics for baseplates
    total_area = sum(w * h for _, _, w, h in rectangles)
    sizes = {}
    for _, _, w, h in rectangles:
        size_key = f"{w}x{h}"
        sizes[size_key] = sizes.get(size_key, 0) + 1

    print(f"Total brick units covered by baseplates: {total_area}")
    print("\nBaseplate sizes used:")
    for size, count in sorted(sizes.items(), key=lambda x: x[1], reverse=True):
        print(f"  {size}: {count} plates")

    # Print statistics for interior cubes if present
    if interior_rectangles:
        print(f"\nTotal interior cubes: {len(interior_rectangles)}")
        interior_area = sum(w * h for _, _, w, h in interior_rectangles)
        interior_sizes = {}
        for _, _, w, h in interior_rectangles:
            size_key = f"{w}x{h}"
            interior_sizes[size_key] = interior_sizes.get(size_key, 0) + 1

        print(f"Total brick units covered by interior: {interior_area}")
        print("\nInterior cube sizes used:")
        for size, count in sorted(interior_sizes.items(), key=lambda x: x[1], reverse=True):
            print(f"  {size}: {count} cubes")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Generate OpenSCAD script for irregular-shaped baseplates from PNG images.'
    )
    parser.add_argument(
        'image',
        nargs='?',
        default='image.png',
        help='Path to input PNG image (default: image.png)'
    )
    parser.add_argument(
        '-o', '--output',
        default='irregular_baseplate.scad',
        help='Path to output OpenSCAD file (default: irregular_baseplate.scad)'
    )
    parser.add_argument(
        '-t', '--threshold',
        type=int,
        default=128,
        help='Grayscale threshold (0-255). Pixels darker than this are "inside" (default: 128)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode: each baseplate gets a random color (varying hue only)'
    )
    parser.add_argument(
        '--edge',
        nargs='?',
        const=1,
        type=int,
        metavar='THICKNESS',
        help='Only generate baseplates on edge (default thickness: 1 brick unit). Interior filled with cubes. Value must be >= 1.'
    )

    args = parser.parse_args()

    # Validate edge thickness if provided
    if args.edge is not None and args.edge < 1:
        parser.error("--edge value must be >= 1")

    try:
        # Step 1: Load and threshold the image
        print(f"Loading image: {args.image}")
        binary_mask = load_and_threshold_image(args.image, args.threshold)
        print(f"Image size: {binary_mask.shape[1]}x{binary_mask.shape[0]} pixels")
        print(f"Pixels inside shape: {np.sum(binary_mask)}")

        # Step 2: Decompose into rectangles
        print("\nDecomposing shape into rectangles...")

        interior_rectangles = None
        if args.edge is not None:
            # Edge mode: separate edge and interior
            print(f"Edge mode enabled: edge thickness = {args.edge} brick units")
            edge_mask, interior_mask = extract_edge_and_interior(binary_mask, args.edge)

            print(f"Edge pixels: {np.sum(edge_mask)}")
            print(f"Interior pixels: {np.sum(interior_mask)}")

            # Decompose edge into baseplates
            rectangles = greedy_rectangle_decomposition(edge_mask)

            # Decompose interior into cubes
            interior_rectangles = greedy_rectangle_decomposition(interior_mask)
        else:
            # Normal mode: all baseplates
            rectangles = greedy_rectangle_decomposition(binary_mask)

        # Step 3: Generate OpenSCAD script
        print("\nGenerating OpenSCAD script...")
        if args.debug:
            print("Debug mode enabled: Using random colors for each baseplate")
        generate_openscad_script(
            rectangles,
            args.output,
            debug=args.debug,
            image_height=binary_mask.shape[0],
            interior_rectangles=interior_rectangles
        )

        print("\nDone!")

    except FileNotFoundError:
        print(f"Error: Image file '{args.image}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
