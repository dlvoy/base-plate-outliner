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
import re
import os
from PIL import Image
import numpy as np
from scipy import ndimage
from typing import List, Tuple, Set, Optional, Dict


def parse_openscad_config(config_path: str) -> Dict[str, float]:
    """
    Parse OpenSCAD config file to extract numeric configuration values.

    Args:
        config_path: Path to the OpenSCAD config file

    Returns:
        Dictionary mapping variable names to their values

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If required values cannot be parsed
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    config = {}

    with open(config_path, 'r') as f:
        content = f.read()

    # Parse simple variable assignments like: unitMbu = 1.6;
    # Also handle arrays like: unitGrid = [5, 2];

    # Single value pattern: variable = value;
    single_pattern = r'^\s*(\w+)\s*=\s*([-+]?[0-9]*\.?[0-9]+)\s*;'

    # Array pattern: variable = [val1, val2];
    array_pattern = r'^\s*(\w+)\s*=\s*\[\s*([-+]?[0-9]*\.?[0-9]+)\s*,\s*([-+]?[0-9]*\.?[0-9]+)\s*\]\s*;'

    for line in content.split('\n'):
        # Skip comments
        if line.strip().startswith('//') or line.strip().startswith('/*') or line.strip().startswith('*'):
            continue

        # Try array pattern first
        array_match = re.match(array_pattern, line)
        if array_match:
            var_name = array_match.group(1)
            val1 = float(array_match.group(2))
            val2 = float(array_match.group(3))
            config[var_name] = [val1, val2]
            continue

        # Try single value pattern
        single_match = re.match(single_pattern, line)
        if single_match:
            var_name = single_match.group(1)
            value = float(single_match.group(2))
            config[var_name] = value

    # Validate required values
    required = ['unitMbu', 'unitGrid', 'scale']
    missing = [req for req in required if req not in config]
    if missing:
        raise ValueError(f"Config file missing required values: {', '.join(missing)}")

    return config


def calculate_unit_size(config: Dict[str, float]) -> float:
    """
    Calculate the size of one brick unit in millimeters from config.

    Args:
        config: Dictionary with unitMbu, unitGrid, and scale values

    Returns:
        Size of one brick unit in mm (unitGrid[0] * unitMbu * scale)
    """
    unit_grid = config['unitGrid']
    unit_mbu = config['unitMbu']
    scale_val = config['scale']

    # unitGrid[0] is the X/Y dimension in MBU units
    return unit_grid[0] * unit_mbu * scale_val


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


def extract_border_rectangles_mm(mask: np.ndarray, border_thickness_mm: float, unit_size: float = 8.0, inset_mm: float = 0.0) -> List[Tuple[float, float, float, float]]:
    """
    Extract border region outside the shape and decompose into mm-based rectangles.

    This uses a high-resolution approach:
    1. Create a high-res mask with fine resolution
    2. Mark all border pixels in this high-res space
    3. Apply greedy rectangle decomposition to find optimal rectangles

    Args:
        mask: 2D boolean array where True = inside shape (in brick units)
        border_thickness_mm: Thickness of border in millimeters
        unit_size: Size of one brick unit in mm (default 8.0)
        inset_mm: Inset amount in millimeters to shrink the shape before creating border (default 0.0)
                  Positive value creates clearance for stacked bricks

    Returns:
        List of rectangles as (x_mm, y_mm, width_mm, height_mm) tuples in millimeters
    """
    rows, cols = mask.shape

    # Use a fine resolution (0.1mm) to accurately represent any border thickness
    # This ensures precise mapping regardless of border_thickness_mm value
    resolution_mm = 0.1

    # Calculate padded dimensions to accommodate border
    border_pixels = int(np.ceil(border_thickness_mm / resolution_mm))

    # High-res dimensions - calculate exact sizes
    hr_width = int(np.round(cols * unit_size / resolution_mm)) + 2 * border_pixels
    hr_height = int(np.round(rows * unit_size / resolution_mm)) + 2 * border_pixels

    # Create high-res masks
    hr_shape_mask = np.zeros((hr_height, hr_width), dtype=bool)

    # Map original shape to high-res grid using exact floating-point arithmetic
    for row in range(rows):
        for col in range(cols):
            if mask[row, col]:
                # Calculate high-res coordinates for this brick unit using rounding
                # to ensure consistent mapping
                hr_col_start = int(np.round(col * unit_size / resolution_mm)) + border_pixels
                hr_row_start = int(np.round(row * unit_size / resolution_mm)) + border_pixels
                hr_col_end = int(np.round((col + 1) * unit_size / resolution_mm)) + border_pixels
                hr_row_end = int(np.round((row + 1) * unit_size / resolution_mm)) + border_pixels

                hr_shape_mask[hr_row_start:hr_row_end, hr_col_start:hr_col_end] = True

    # Dilate the shape to create border region
    struct = ndimage.generate_binary_structure(2, 2)
    dilated = hr_shape_mask.copy()
    for _ in range(border_pixels):
        dilated = ndimage.binary_dilation(dilated, structure=struct)

    # For inset version: expand the inner edge cutout
    if inset_mm > 0:
        inset_pixels = int(np.round(inset_mm / resolution_mm))
        struct = ndimage.generate_binary_structure(2, 2)
        # Expand the shape mask to create clearance on inner edge
        inner_edge = hr_shape_mask.copy()
        for _ in range(inset_pixels):
            inner_edge = ndimage.binary_dilation(inner_edge, structure=struct)
        # Border is between outer edge (dilated) and inner edge (expanded shape)
        hr_border_mask = dilated & ~inner_edge
    else:
        # Border is dilated minus original shape
        hr_border_mask = dilated & ~hr_shape_mask

    # Apply greedy rectangle decomposition to the high-res border mask
    hr_rectangles = greedy_rectangle_decomposition(hr_border_mask)

    # Convert high-res rectangles back to mm coordinates
    mm_rectangles = []
    for (hr_col, hr_row, hr_width, hr_height) in hr_rectangles:
        # Convert from high-res grid to mm coordinates
        # Subtract border_pixels offset and multiply by resolution
        x_mm = (hr_col - border_pixels) * resolution_mm
        y_mm = (hr_row - border_pixels) * resolution_mm
        width_mm = hr_width * resolution_mm
        height_mm = hr_height * resolution_mm

        mm_rectangles.append((x_mm, y_mm, width_mm, height_mm))

    return mm_rectangles


def extract_frame_rectangles_mm(mask: np.ndarray, padding_mm: float, unit_size: float = 8.0, inset_mm: float = 0.0) -> List[Tuple[float, float, float, float]]:
    """
    Extract frame region - a filled rectangular border enclosing the entire shape.

    The frame fills the area between:
    - Inner boundary: the rectangular outline of the shape
    - Outer boundary: the inner boundary expanded by padding_mm in all directions

    Args:
        mask: 2D boolean array where True = inside shape (in brick units)
        padding_mm: Padding between shape outline and frame outer edge in millimeters (can be 0)
        unit_size: Size of one brick unit in mm (default 8.0)
        inset_mm: Inset amount in millimeters to shrink the shape before creating frame (default 0.0)
                  Positive value creates clearance for stacked bricks

    Returns:
        List of rectangles as (x_mm, y_mm, width_mm, height_mm) tuples in millimeters
    """
    rows, cols = mask.shape

    # Find the bounding box of the shape in brick units
    shape_rows, shape_cols = np.where(mask)

    if len(shape_rows) == 0:
        # Empty shape, no frame
        return []

    # Bounding box in brick units
    min_row = shape_rows.min()
    max_row = shape_rows.max()
    min_col = shape_cols.min()
    max_col = shape_cols.max()

    # Convert to mm coordinates
    # Inner rectangle (shape bounding box)
    inner_x_mm = min_col * unit_size
    inner_y_mm = min_row * unit_size
    inner_width_mm = (max_col - min_col + 1) * unit_size
    inner_height_mm = (max_row - min_row + 1) * unit_size

    # Outer rectangle (inner + padding)
    outer_x_mm = inner_x_mm - padding_mm
    outer_y_mm = inner_y_mm - padding_mm
    outer_width_mm = inner_width_mm + 2 * padding_mm
    outer_height_mm = inner_height_mm + 2 * padding_mm

    # Create a high-resolution mask to identify frame region
    resolution_mm = 0.1

    # Calculate dimensions for high-res grid
    hr_width = int(np.round(outer_width_mm / resolution_mm))
    hr_height = int(np.round(outer_height_mm / resolution_mm))

    # Create high-res frame mask (everything inside outer rectangle)
    hr_frame_mask = np.ones((hr_height, hr_width), dtype=bool)

    # Create high-res shape mask and subtract it from frame
    hr_shape_mask = np.zeros((hr_height, hr_width), dtype=bool)

    # Map original shape to high-res grid
    for row in range(rows):
        for col in range(cols):
            if mask[row, col]:
                # Calculate position relative to outer rectangle origin
                shape_x_mm = col * unit_size - outer_x_mm
                shape_y_mm = row * unit_size - outer_y_mm

                # Convert to high-res coordinates
                hr_col_start = int(np.round(shape_x_mm / resolution_mm))
                hr_row_start = int(np.round(shape_y_mm / resolution_mm))
                hr_col_end = int(np.round((shape_x_mm + unit_size) / resolution_mm))
                hr_row_end = int(np.round((shape_y_mm + unit_size) / resolution_mm))

                # Clamp to valid range
                hr_col_start = max(0, min(hr_width, hr_col_start))
                hr_col_end = max(0, min(hr_width, hr_col_end))
                hr_row_start = max(0, min(hr_height, hr_row_start))
                hr_row_end = max(0, min(hr_height, hr_row_end))

                hr_shape_mask[hr_row_start:hr_row_end, hr_col_start:hr_col_end] = True

    # For inset version: expand the inner edge cutout
    if inset_mm > 0:
        inset_pixels = int(np.round(inset_mm / resolution_mm))
        struct = ndimage.generate_binary_structure(2, 2)
        # Expand the shape mask to create clearance on inner edge
        inner_edge = hr_shape_mask.copy()
        for _ in range(inset_pixels):
            inner_edge = ndimage.binary_dilation(inner_edge, structure=struct)
        # Frame is between outer rectangle and inner edge (expanded shape)
        hr_frame_mask = hr_frame_mask & ~inner_edge
    else:
        # Frame region is outer rectangle minus shape
        hr_frame_mask = hr_frame_mask & ~hr_shape_mask

    # Apply greedy rectangle decomposition
    hr_rectangles = greedy_rectangle_decomposition(hr_frame_mask)

    # Convert high-res rectangles back to mm coordinates (relative to outer rectangle origin)
    mm_rectangles = []
    for (hr_col, hr_row, hr_width_px, hr_height_px) in hr_rectangles:
        # Convert from high-res grid to mm coordinates, offset by outer rectangle position
        x_mm = outer_x_mm + hr_col * resolution_mm
        y_mm = outer_y_mm + hr_row * resolution_mm
        width_mm = hr_width_px * resolution_mm
        height_mm = hr_height_px * resolution_mm

        mm_rectangles.append((x_mm, y_mm, width_mm, height_mm))

    return mm_rectangles


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


def hex_to_openscad_rgb(hex_color: str) -> str:
    """
    Convert hex color to OpenSCAD RGB format.

    Args:
        hex_color: Hex color string (e.g., "#EAC645")

    Returns:
        OpenSCAD color format string (e.g., "[0.918, 0.776, 0.271]")
    """
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    return f"[{r:.3f}, {g:.3f}, {b:.3f}]"


def generate_openscad_script(rectangles: List[Tuple[int, int, int, int]],
                            output_path: str = "irregular_baseplate.scad",
                            debug: bool = False,
                            image_height: int = 0,
                            interior_rectangles: Optional[List[Tuple[int, int, int, int]]] = None,
                            border_rectangles: Optional[List[Tuple[float, float, float, float]]] = None,
                            border_rectangles_top: Optional[List[Tuple[float, float, float, float]]] = None,
                            border_thickness_mm: float = 0.0,
                            border_height_adjust_mm: float = 0.0,
                            unit_size: float = 8.0,
                            config_path: str = "machineblocks/config/config-default.scad",
                            is_frame_mode: bool = False) -> None:
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
        unit_size: Size of one brick unit in mm (calculated from config)
        config_path: Path to OpenSCAD config file to include
    """

    script_lines = [
        "/**",
        " * Generated Irregular Baseplate",
        " * Auto-generated from PNG image",
        " */",
        "",
        "// Imports",
        "use <machineblocks/lib/block.scad>;",
        f"include <{config_path}>;",
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

        script_lines.append(f"\n// Baseplate {i + 1}: {width}x{height} at position ({x}, {y})")

        # Wrap with color() if in debug mode
        if debug:
            hex_color = generate_random_color()
            openscad_color = hex_to_openscad_rgb(hex_color)
            script_lines.append(f"color({openscad_color}) {{")

        script_lines.append(f"translate([{translate_x}, {translate_y}, 0]) {{")
        script_lines.append("    machineblock(")
        script_lines.append(f"        size = [{width}, {height}, 1],")
        script_lines.append("        baseCutoutType = \"none\",")
        script_lines.append("        studs = true,")
        script_lines.append("        studType = \"solid\",")
        script_lines.append("        studIcon = \"none\",")
        script_lines.append("        pillars = false,")
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
        script_lines.append("        studHeight = studHeight,")
        script_lines.append("        studCutoutAdjustment = studCutoutAdjustment,")
        script_lines.append("        previewRender = previewRender,")
        script_lines.append("        previewQuality = previewQuality,")
        script_lines.append("        baseRoundingResolution = roundingResolution,")
        script_lines.append("        holeRoundingResolution = roundingResolution,")
        script_lines.append("        studRoundingResolution = roundingResolution,")
        script_lines.append("        pillarRoundingResolution = roundingResolution")
        script_lines.append("    );")
        script_lines.append("}")

        # Close color() wrapper if in debug mode
        if debug:
            script_lines.append("}")

    # Generate interior cubes if provided
    if interior_rectangles:
        script_lines.append("\n// Interior fill (cubes)")
        for i, (x, y, width, height) in enumerate(interior_rectangles):
            # Calculate the translation position (same as baseplates)
            translate_x = x * unit_size
            translate_y = (image_height - y - height) * unit_size

            script_lines.append(f"\n// Interior cube {i + 1}: {width}x{height} at position ({x}, {y})")

            # Wrap with color() if in debug mode
            if debug:
                hex_color = generate_random_color()
                openscad_color = hex_to_openscad_rgb(hex_color)
                script_lines.append(f"color({openscad_color}) {{")

            script_lines.append(f"translate([{translate_x}, {translate_y}, 0]) {{")
            script_lines.append("    cube([")
            script_lines.append(f"        {width} * unitGrid[0] * unitMbu * scale,")
            script_lines.append(f"        {height} * unitGrid[0] * unitMbu * scale,")
            script_lines.append("        1 * unitGrid[1] * unitMbu * scale")
            script_lines.append("    ]);")
            script_lines.append("}")

            # Close color() wrapper if in debug mode
            if debug:
                script_lines.append("}")

    # Generate border/frame cubes if provided (these are in mm coordinates already)
    if border_rectangles:
        mode_label = "Frame" if is_frame_mode else "Border"
        thickness_label = f"padding: {border_thickness_mm}mm" if is_frame_mode else f"thickness: {border_thickness_mm}mm"

        script_lines.append(f"\n// {mode_label} (cubes) - positioned and sized in millimeters")
        if border_height_adjust_mm > 0 and border_rectangles_top:
            script_lines.append(f"// {mode_label} {thickness_label}, Two-layer design:")
            script_lines.append(f"//   Base layer: baseplate height (flush with baseplates)")
            script_lines.append(f"//   Top layer: {border_height_adjust_mm}mm tall (inset for clearance)")
        else:
            script_lines.append(f"// {mode_label} {thickness_label}, Height adjustment: {border_height_adjust_mm}mm")

        # Generate base layer
        script_lines.append(f"\n// {mode_label} base layer")
        for i, (x_mm, y_mm, width_mm, height_mm) in enumerate(border_rectangles):
            # Border/frame rectangles are already in mm, but Y needs flipping for OpenSCAD
            # Convert image-space Y (where 0 is top) to OpenSCAD Y (where 0 is bottom)
            translate_x = x_mm
            translate_y = (image_height * unit_size) - y_mm - height_mm

            script_lines.append(f"\n// {mode_label} base cube {i + 1}: {width_mm:.2f}mm x {height_mm:.2f}mm at position ({x_mm:.2f}mm, {y_mm:.2f}mm)")

            # Wrap with color() if in debug mode
            if debug:
                hex_color = generate_random_color()
                openscad_color = hex_to_openscad_rgb(hex_color)
                script_lines.append(f"color({openscad_color}) {{")

            script_lines.append(f"translate([{translate_x:.4f}, {translate_y:.4f}, 0]) {{")
            script_lines.append("    cube([")
            script_lines.append(f"        {width_mm:.4f},  // width in mm")
            script_lines.append(f"        {height_mm:.4f},  // height in mm")
            if border_height_adjust_mm > 0 and border_rectangles_top:
                script_lines.append(f"        (1 * unitGrid[1] * unitMbu * scale)  // baseplate height without studs")
            else:
                script_lines.append(f"        (1 * unitGrid[1] * unitMbu * scale) + {border_height_adjust_mm}  // baseplate height without studs + adjustment")
            script_lines.append("    ]);")
            script_lines.append("}")

            # Close color() wrapper if in debug mode
            if debug:
                script_lines.append("}")

    # Generate top layer for border/frame if provided (with clearance)
    if border_rectangles_top:
        mode_label = "Frame" if is_frame_mode else "Border"

        script_lines.append(f"\n// {mode_label} top layer (inset for clearance)")
        for i, (x_mm, y_mm, width_mm, height_mm) in enumerate(border_rectangles_top):
            translate_x = x_mm
            translate_y = (image_height * unit_size) - y_mm - height_mm

            script_lines.append(f"\n// {mode_label} top cube {i + 1}: {width_mm:.2f}mm x {height_mm:.2f}mm at position ({x_mm:.2f}mm, {y_mm:.2f}mm)")

            # Wrap with color() if in debug mode
            if debug:
                hex_color = generate_random_color()
                openscad_color = hex_to_openscad_rgb(hex_color)
                script_lines.append(f"color({openscad_color}) {{")

            script_lines.append(f"translate([{translate_x:.4f}, {translate_y:.4f}, (1 * unitGrid[1] * unitMbu * scale)]) {{")
            script_lines.append("    cube([")
            script_lines.append(f"        {width_mm:.4f},  // width in mm")
            script_lines.append(f"        {height_mm:.4f},  // height in mm")
            script_lines.append(f"        {border_height_adjust_mm}  // height adjustment")
            script_lines.append("    ]);")
            script_lines.append("}")

            # Close color() wrapper if in debug mode
            if debug:
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

    # Print statistics for border/frame cubes if present
    if border_rectangles:
        mode_label = "frame" if is_frame_mode else "border"
        thickness_label = "padding" if is_frame_mode else "thickness"

        print(f"\nTotal {mode_label} cubes: {len(border_rectangles)}")
        border_area_mm2 = sum(w * h for _, _, w, h in border_rectangles)
        border_sizes = {}
        for _, _, w, h in border_rectangles:
            size_key = f"{w:.2f}x{h:.2f}mm"
            border_sizes[size_key] = border_sizes.get(size_key, 0) + 1

        print(f"{mode_label.capitalize()} {thickness_label}: {border_thickness_mm}mm, Height adjustment: {border_height_adjust_mm}mm")
        print(f"Total area covered by {mode_label}: {border_area_mm2:.2f} mm²")
        print(f"\n{mode_label.capitalize()} cube sizes used (in mm):")
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
        default=None,
        help='Path to output OpenSCAD file (default: derived from input image name, e.g., image.png -> image.scad)'
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
    parser.add_argument(
        '--frame',
        action='store_true',
        help='Frame mode: Creates a filled rectangular border enclosing the entire shape. With this mode, --border specifies padding between shape outline and frame (can be 0). Frame fills the area between shape edges and outer rectangle.'
    )
    parser.add_argument(
        '--config',
        default='machineblocks/config/config-default.scad',
        metavar='CONFIG_PATH',
        help='Path to OpenSCAD config file (default: machineblocks/config/config-default.scad). Values like unitMbu, unitGrid, and scale are read from this file.'
    )

    args = parser.parse_args()

    # Derive output filename from input image if not specified
    if args.output is None:
        # Replace extension with .scad
        base_name = os.path.splitext(args.image)[0]
        args.output = f"{base_name}.scad"

    # Parse OpenSCAD config file
    try:
        config = parse_openscad_config(args.config)
        unit_size = calculate_unit_size(config)
        print(f"Using config: {args.config}")
        print(f"  unitMbu = {config['unitMbu']}, unitGrid = {config['unitGrid']}, scale = {config['scale']}")
        print(f"  Calculated unit size: {unit_size}mm")
    except (FileNotFoundError, ValueError) as e:
        parser.error(f"Config error: {e}")

    # Validate edge thickness if provided
    if args.edge is not None and args.edge < 1:
        parser.error("--edge value must be >= 1")

    # Validate border thickness if provided
    # In frame mode, border=0 is allowed (means no padding between shape and frame)
    # In normal border mode, border must be != 0
    if args.border is not None and args.border == 0 and not args.frame:
        parser.error("--border value must be != 0 (unless using --frame mode where 0 means no padding)")

    # Validate that --frame requires --border to be specified
    if args.frame and args.border is None:
        parser.error("--frame requires --border to be specified (use --border=0 for no padding)")

    # Validate border height will be positive
    if args.border is not None:
        # Calculate base border height from config: unitGrid[1] * unitMbu * scale
        base_border_height = config['unitGrid'][1] * config['unitMbu'] * config['scale']
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

        # Step 2b: Generate border or frame if requested
        border_rectangles_top = None
        if args.border is not None:
            # Get wall thickness adjustment for clearance calculation
            wall_thickness_adj = config.get('baseWallThicknessAdjustment', -0.1)
            # Inset amount is the negative of wall thickness adjustment (to expand cutout)
            inset_mm = -wall_thickness_adj if args.borderHeightAdjust > 0 else 0.0

            if args.frame:
                # Frame mode: filled rectangular border enclosing entire shape
                print(f"\nFrame mode enabled: padding = {args.border}mm")
                border_rectangles = extract_frame_rectangles_mm(binary_mask, args.border, unit_size, inset_mm=0.0)
                print(f"Generated {len(border_rectangles)} frame rectangles (base layer)")

                # Generate top layer with inset if borderHeightAdjust > 0
                if args.borderHeightAdjust > 0:
                    print(f"Generating top layer with {inset_mm}mm inset for clearance")
                    border_rectangles_top = extract_frame_rectangles_mm(binary_mask, args.border, unit_size, inset_mm=inset_mm)
                    print(f"Generated {len(border_rectangles_top)} frame rectangles (top layer)")
            else:
                # Normal border mode: border around shape edges
                print(f"\nBorder mode enabled: border thickness = {args.border}mm")
                border_rectangles = extract_border_rectangles_mm(binary_mask, args.border, unit_size, inset_mm=0.0)
                print(f"Generated {len(border_rectangles)} border rectangles (base layer)")

                # Generate top layer with inset if borderHeightAdjust > 0
                if args.borderHeightAdjust > 0:
                    print(f"Generating top layer with {inset_mm}mm inset for clearance")
                    border_rectangles_top = extract_border_rectangles_mm(binary_mask, args.border, unit_size, inset_mm=inset_mm)
                    print(f"Generated {len(border_rectangles_top)} border rectangles (top layer)")

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
            border_rectangles_top=border_rectangles_top,
            border_thickness_mm=args.border if args.border is not None else 0.0,
            border_height_adjust_mm=args.borderHeightAdjust,
            unit_size=unit_size,
            config_path=args.config,
            is_frame_mode=args.frame
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
