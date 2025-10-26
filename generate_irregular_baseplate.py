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


def extract_border_rectangles_mm(mask: np.ndarray, border_thickness_mm: float, unit_size: float = 8.0) -> List[Tuple[float, float, float, float]]:
    """
    Extract border region outside the shape and decompose into mm-based rectangles.

    Args:
        mask: 2D boolean array where True = inside shape (in brick units)
        border_thickness_mm: Thickness of border in millimeters
        unit_size: Size of one brick unit in mm (default 8.0)

    Returns:
        List of rectangles as (x_mm, y_mm, width_mm, height_mm) tuples in millimeters
    """
    rows, cols = mask.shape

    # Find the bounding edges of the shape
    # For each pixel on the edge of the shape, we'll create a border rectangle
    border_rects = []

    # Process each pixel in the mask
    for row in range(rows):
        for col in range(cols):
            if mask[row, col]:
                # Check if this pixel is on the edge (has at least one non-shape neighbor)
                is_edge = False

                # Check all 8 neighbors
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = row + dr, col + dc

                        # If neighbor is outside bounds or not in shape, this is an edge
                        if nr < 0 or nr >= rows or nc < 0 or nc >= cols or not mask[nr, nc]:
                            is_edge = True
                            break
                    if is_edge:
                        break

                # If this is an edge pixel, determine which sides need borders
                if is_edge:
                    # Check each of 8 directions and add border rectangles
                    # We check all 8 neighbors and add borders for missing ones

                    # Helper to check if position is in mask
                    def is_in_shape(r, c):
                        if r < 0 or r >= rows or c < 0 or c >= cols:
                            return False
                        return mask[r, c]

                    # Top (North)
                    if not is_in_shape(row - 1, col):
                        x_mm = col * unit_size
                        y_mm = row * unit_size - border_thickness_mm
                        width_mm = unit_size
                        height_mm = border_thickness_mm
                        border_rects.append((x_mm, y_mm, width_mm, height_mm))

                    # Bottom (South)
                    if not is_in_shape(row + 1, col):
                        x_mm = col * unit_size
                        y_mm = (row + 1) * unit_size
                        width_mm = unit_size
                        height_mm = border_thickness_mm
                        border_rects.append((x_mm, y_mm, width_mm, height_mm))

                    # Left (West)
                    if not is_in_shape(row, col - 1):
                        x_mm = col * unit_size - border_thickness_mm
                        y_mm = row * unit_size
                        width_mm = border_thickness_mm
                        height_mm = unit_size
                        border_rects.append((x_mm, y_mm, width_mm, height_mm))

                    # Right (East)
                    if not is_in_shape(row, col + 1):
                        x_mm = (col + 1) * unit_size
                        y_mm = row * unit_size
                        width_mm = border_thickness_mm
                        height_mm = unit_size
                        border_rects.append((x_mm, y_mm, width_mm, height_mm))

                    # Top-Left (NorthWest) corner
                    if not is_in_shape(row - 1, col - 1):
                        x_mm = col * unit_size - border_thickness_mm
                        y_mm = row * unit_size - border_thickness_mm
                        width_mm = border_thickness_mm
                        height_mm = border_thickness_mm
                        border_rects.append((x_mm, y_mm, width_mm, height_mm))

                    # Top-Right (NorthEast) corner
                    if not is_in_shape(row - 1, col + 1):
                        x_mm = (col + 1) * unit_size
                        y_mm = row * unit_size - border_thickness_mm
                        width_mm = border_thickness_mm
                        height_mm = border_thickness_mm
                        border_rects.append((x_mm, y_mm, width_mm, height_mm))

                    # Bottom-Left (SouthWest) corner
                    if not is_in_shape(row + 1, col - 1):
                        x_mm = col * unit_size - border_thickness_mm
                        y_mm = (row + 1) * unit_size
                        width_mm = border_thickness_mm
                        height_mm = border_thickness_mm
                        border_rects.append((x_mm, y_mm, width_mm, height_mm))

                    # Bottom-Right (SouthEast) corner
                    if not is_in_shape(row + 1, col + 1):
                        x_mm = (col + 1) * unit_size
                        y_mm = (row + 1) * unit_size
                        width_mm = border_thickness_mm
                        height_mm = border_thickness_mm
                        border_rects.append((x_mm, y_mm, width_mm, height_mm))

    # Now merge adjacent rectangles with the same position and size alignment
    # This is a simplified greedy merge
    return merge_mm_rectangles(border_rects)


def merge_mm_rectangles(rectangles: List[Tuple[float, float, float, float]]) -> List[Tuple[float, float, float, float]]:
    """
    Merge adjacent mm-based rectangles to minimize the number of cubes.

    Args:
        rectangles: List of (x, y, width, height) tuples in mm

    Returns:
        Merged list of rectangles
    """
    if not rectangles:
        return []

    # Sort rectangles by y, then x
    sorted_rects = sorted(rectangles, key=lambda r: (r[1], r[0]))

    merged = []
    current = list(sorted_rects[0])

    for rect in sorted_rects[1:]:
        x, y, w, h = rect
        cx, cy, cw, ch = current

        # Try to merge horizontally (same y, height, and adjacent/overlapping x)
        if abs(y - cy) < 0.01 and abs(h - ch) < 0.01:
            if abs(x - (cx + cw)) < 0.01:  # Adjacent on right
                current[2] += w  # Extend width
                continue
            elif abs(x - cx) < 0.01 and abs(w - cw) < 0.01:  # Same position
                continue  # Skip duplicate

        # Try to merge vertically (same x, width, and adjacent/overlapping y)
        if abs(x - cx) < 0.01 and abs(w - cw) < 0.01:
            if abs(y - (cy + ch)) < 0.01:  # Adjacent on bottom
                current[3] += h  # Extend height
                continue

        # Can't merge, save current and start new
        merged.append(tuple(current))
        current = list(rect)

    # Add the last rectangle
    merged.append(tuple(current))

    return merged


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
                            interior_rectangles: Optional[List[Tuple[int, int, int, int]]] = None,
                            border_rectangles: Optional[List[Tuple[float, float, float, float]]] = None,
                            border_thickness_mm: float = 0.0,
                            border_height_adjust_mm: float = 0.0) -> None:
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
        border_rectangles: Optional list of rectangles for border cubes as (x_mm, y_mm, width_mm, height_mm) in millimeters
        border_thickness_mm: Thickness of border in mm
        border_height_adjust_mm: Height adjustment for border in mm
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

    # Generate border cubes if provided (these are in mm coordinates already)
    if border_rectangles:
        script_lines.append("\n// Border (cubes) - positioned and sized in millimeters")
        script_lines.append(f"// Border thickness: {border_thickness_mm}mm, Height adjustment: {border_height_adjust_mm}mm")
        for i, (x_mm, y_mm, width_mm, height_mm) in enumerate(border_rectangles):
            # Border rectangles are already in mm, but Y needs flipping for OpenSCAD
            # Convert image-space Y (where 0 is top) to OpenSCAD Y (where 0 is bottom)
            translate_x = x_mm
            translate_y = (image_height * unit_size) - y_mm - height_mm

            script_lines.append(f"\n// Border cube {i + 1}: {width_mm:.2f}mm x {height_mm:.2f}mm at position ({x_mm:.2f}mm, {y_mm:.2f}mm)")
            script_lines.append(f"translate([{translate_x:.4f}, {translate_y:.4f}, 0]) {{")
            script_lines.append("    cube([")
            script_lines.append(f"        {width_mm:.4f},  // width in mm")
            script_lines.append(f"        {height_mm:.4f},  // height in mm")
            script_lines.append(f"        (1 * unitGrid[1] * unitMbu * scale) + {border_height_adjust_mm}  // baseplate height without studs + adjustment")
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

    # Print statistics for border cubes if present
    if border_rectangles:
        print(f"\nTotal border cubes: {len(border_rectangles)}")
        border_area_mm2 = sum(w * h for _, _, w, h in border_rectangles)
        border_sizes = {}
        for _, _, w, h in border_rectangles:
            size_key = f"{w:.2f}x{h:.2f}mm"
            border_sizes[size_key] = border_sizes.get(size_key, 0) + 1

        print(f"Border thickness: {border_thickness_mm}mm, Height adjustment: {border_height_adjust_mm}mm")
        print(f"Total area covered by border: {border_area_mm2:.2f} mm²")
        print("\nBorder cube sizes used (in mm):")
        for size, count in sorted(border_sizes.items(), key=lambda x: x[1], reverse=True):
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
    parser.add_argument(
        '--border',
        nargs='?',
        const=5.0,
        type=float,
        metavar='THICKNESS_MM',
        help='Add border around shape edge (default thickness: 5mm). Border is drawn outside shape using cubes. Value must be != 0.'
    )
    parser.add_argument(
        '--borderHeightAdjust',
        type=float,
        default=0.0,
        metavar='ADJUST_MM',
        help='Adjustment to border height in mm (default: 0). Added to standard baseplate height without studs. Can be negative to reduce height, but final height must be > 0.'
    )

    args = parser.parse_args()

    # Validate edge thickness if provided
    if args.edge is not None and args.edge < 1:
        parser.error("--edge value must be >= 1")

    # Validate border thickness if provided
    if args.border is not None and args.border == 0:
        parser.error("--border value must be != 0")

    # Validate border height will be positive
    if args.border is not None:
        # Calculate base border height: unitGrid[1] * unitMbu * scale
        # Using default values: 2 * 1.6 * 1.0 = 3.2mm
        base_border_height = 2.0 * 1.6 * 1.0  # Default MachineBlocks values
        final_border_height = base_border_height + args.borderHeightAdjust
        if final_border_height <= 0:
            parser.error(f"Border height would be {final_border_height:.2f}mm (base {base_border_height}mm + adjust {args.borderHeightAdjust}mm). Final height must be > 0.")

    try:
        # Step 1: Load and threshold the image
        print(f"Loading image: {args.image}")
        binary_mask = load_and_threshold_image(args.image, args.threshold)
        print(f"Image size: {binary_mask.shape[1]}x{binary_mask.shape[0]} pixels")
        print(f"Pixels inside shape: {np.sum(binary_mask)}")

        # Step 2: Decompose into rectangles
        print("\nDecomposing shape into rectangles...")

        interior_rectangles = None
        border_rectangles = None

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

        # Step 2b: Generate border if requested
        if args.border is not None:
            print(f"\nBorder mode enabled: border thickness = {args.border}mm")

            # Generate border rectangles directly in mm coordinates
            border_rectangles = extract_border_rectangles_mm(binary_mask, args.border)
            print(f"Generated {len(border_rectangles)} border rectangles")

        # Step 3: Generate OpenSCAD script
        print("\nGenerating OpenSCAD script...")
        if args.debug:
            print("Debug mode enabled: Using random colors for each baseplate")
        generate_openscad_script(
            rectangles,
            args.output,
            debug=args.debug,
            image_height=binary_mask.shape[0],
            interior_rectangles=interior_rectangles,
            border_rectangles=border_rectangles,
            border_thickness_mm=args.border if args.border is not None else 0.0,
            border_height_adjust_mm=args.borderHeightAdjust
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
