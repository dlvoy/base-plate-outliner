# Base Plate Outliner

This tool generates OpenSCAD scripts to render irregular-shaped baseplates based on PNG images.

## Overview

The script analyzes a PNG image to identify a shape (dark pixels = inside, light pixels = outside), then optimally decomposes the shape into rectangular baseplates and generates an OpenSCAD script to render them.

This project uses the **MachineBlocks** library (https://github.com/pks5/machineblocks) for rendering LEGO-compatible bricks in OpenSCAD. MachineBlocks is included as a git submodule.

## Installation

### Prerequisites

You need:
- Python 3 (version 3.6 or higher)
- Git (for cloning the repository and initializing submodules)
- OpenSCAD (for rendering the generated .scad files)

### Step 1: Clone the Repository and Initialize Submodules

**IMPORTANT:** This project uses the MachineBlocks library as a git submodule. You must initialize the submodule after cloning:

```bash
# Clone the repository
git clone <your-repo-url>
cd base-plate-outliner

# Initialize and update submodules
git submodule update --init --recursive
```

If you've already cloned the repository without the `--recursive` flag, you can initialize submodules later:

```bash
git submodule update --init --recursive
```

### Step 2: Set Up Python Environment

### Quick Setup (Recommended)

The easiest way to set up the project is to use the provided setup scripts:

**On Linux/Mac:**
```bash
./setup.sh
```

**On Windows:**
```bash
setup.bat
```

These scripts will automatically:
- Create a virtual environment
- Activate it
- Install all required dependencies

After running the setup script, the virtual environment will be activated and ready to use.

### Manual Setup

If you prefer to set up manually or if the automated script doesn't work:

It's highly recommended to use a Python virtual environment to isolate dependencies:

#### 1. Create a virtual environment

```bash
# Navigate to the project directory
cd /path/to/base-plate-outliner

# Create virtual environment
python3 -m venv .venv
```

#### 2. Activate the virtual environment

**On Linux/Mac:**
```bash
source .venv/bin/activate
```

**On Windows:**
```bash
.venv\Scripts\activate
```

You should see `(.venv)` appear at the beginning of your command prompt, indicating the virtual environment is active.

#### 3. Install Dependencies

With the virtual environment activated, install the required packages:

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install Pillow numpy
```

#### 4. Deactivate when done (optional)

When you're finished working with the script, you can deactivate the virtual environment:

```bash
deactivate
```

**Note:** You'll need to activate the virtual environment (step 2) each time you open a new terminal session to use the script.

## Usage

**Important:** Make sure to activate your virtual environment before running the script:
```bash
source .venv/bin/activate  # On Linux/Mac
# OR: .venv\Scripts\activate  # On Windows
```

### Basic Usage

```bash
python3 generate_irregular_baseplate.py [image.png]
```

If no image is specified, it defaults to `image.png`.

### Options

- `image` - Path to input PNG image (default: `image.png`)
- `-o, --output` - Path to output OpenSCAD file (default: `irregular_baseplate.scad`)
- `-t, --threshold` - Grayscale threshold (0-255). Pixels darker than this value are considered "inside" the shape (default: 128)
- `--debug` - Enable debug mode: each baseplate gets a random color with varying hue (useful for visualizing individual baseplates)

### Examples

```bash
# Use default image.png
python3 generate_irregular_baseplate.py

# Specify custom image
python3 generate_irregular_baseplate.py my_shape.png

# Custom output file
python3 generate_irregular_baseplate.py my_shape.png -o output.scad

# Custom threshold (more sensitive to dark pixels)
python3 generate_irregular_baseplate.py my_shape.png -t 100

# Debug mode with random colors for each baseplate
python3 generate_irregular_baseplate.py my_shape.png --debug
```

## How It Works

1. **Image Loading**: The script loads the PNG image and converts it to grayscale
2. **Thresholding**: Pixels are classified as "inside" (dark, value < threshold) or "outside" (light, value >= threshold)
3. **Rectangle Decomposition**: A greedy algorithm decomposes the shape into rectangular regions, attempting to minimize the number of baseplates needed
4. **OpenSCAD Generation**: The script generates an OpenSCAD file with properly positioned `machineblock()` calls for each rectangle
5. **Debug Mode** (optional): When enabled with `--debug`, each baseplate receives a unique random color. The colors maintain the same saturation and lightness as the default yellow (#EAC645) but vary in hue, making it easy to distinguish individual baseplates in the rendered model

## Creating Test Images

You can create a simple test image using the included helper script (make sure your virtual environment is activated):

```bash
python3 create_test_image.py
```

This creates a 16x16 pixel L-shaped test pattern in `test_shape.png`.

## Image Guidelines

- **Format**: PNG images work best
- **Color**: The script converts to grayscale automatically
- **Threshold**: Dark pixels (grayscale value < 128 by default) are "inside" the shape
- **Size**: Each pixel in the image corresponds to one 1x1 baseplate unit (8mm x 8mm in real dimensions)
- **Keep it Simple**: Use simple black and white images for best results

### Creating Your Own Images

You can create images in any image editor (GIMP, Photoshop, Paint, etc.):

1. Create a new image with the desired dimensions (width x height in pixels = shape in brick units)
2. Fill the background with white (RGB: 255, 255, 255)
3. Draw your shape in black (RGB: 0, 0, 0) or dark gray
4. Save as PNG

## Output

The script generates:
- An OpenSCAD `.scad` file ready to be opened in OpenSCAD
- Statistics about the baseplates used (sizes and quantities)

The generated OpenSCAD file can be opened in OpenSCAD and rendered to STL for 3D printing.

## Algorithm Details

The rectangle decomposition uses a greedy algorithm:
1. Scan the bitmap from top-left to bottom-right
2. At each "inside" pixel, find the largest rectangle that fits
3. Place that rectangle and mark those cells as used
4. Continue scanning

This approach prioritizes larger rectangles, which generally results in fewer total pieces, though it may not always find the absolute optimal solution.

## Example Workflow

```bash
# 0. Activate virtual environment (if not already activated)
source .venv/bin/activate  # On Linux/Mac
# OR: .venv\Scripts\activate  # On Windows

# 1. Create a test image
python3 create_test_image.py

# 2. Generate the OpenSCAD script
python3 generate_irregular_baseplate.py test_shape.png -o my_baseplate.scad

# 3. Open in OpenSCAD
# (Open my_baseplate.scad in OpenSCAD application)

# 4. Render and export to STL for 3D printing

# 5. Deactivate virtual environment when done
deactivate
```

## Technical Details

- **Coordinate System**: The script correctly handles coordinate system conversion:
  - **Image coordinates**: Y=0 is at the top, Y increases downward
  - **OpenSCAD coordinates**: Y=0 is at the bottom, Y increases upward
  - The script automatically flips the Y-axis so the rendered model matches the image orientation
- **Unit Size**: Each brick unit is 8mm (1.6mm × 5 units per the MachineBlocks configuration)
- **Positioning**: Baseplates are positioned using OpenSCAD's `translate()` function
- **Integration**: The generated script uses the MachineBlocks library's `machineblock()` function with standard configuration parameters

## About MachineBlocks

This project uses the [MachineBlocks](https://github.com/pks5/machineblocks) library, which is a comprehensive OpenSCAD library for creating LEGO-compatible bricks and components. MachineBlocks provides:

- Parametric brick generation
- Support for various brick types (standard, Technic, plates, etc.)
- Customizable dimensions and features
- Professional-quality 3D-printable models

The MachineBlocks library is included as a git submodule in the `machineblocks/` directory. The generated OpenSCAD scripts reference:
- `machineblocks/lib/block.scad` - Main library file
- `machineblocks/config/config-default.scad` - Default configuration

For more information about MachineBlocks, visit: https://machineblocks.com/

## Project Structure

```
base-plate-outliner/
├── .venv/                      # Python virtual environment (created by setup)
├── machineblocks/              # Git submodule - MachineBlocks library
│   ├── lib/                    # MachineBlocks library files
│   ├── config/                 # MachineBlocks configuration
│   └── ...
├── generate_irregular_baseplate.py  # Main script
├── create_test_image.py        # Test image generator
├── example_output.scad         # Example generated output
├── setup.sh                    # Linux/Mac setup script
├── setup.bat                   # Windows setup script
├── requirements.txt            # Python dependencies
└── README_irregular_baseplate.md    # This file
```

## Limitations

- The greedy algorithm may not always produce the absolute minimum number of baseplates
- Very complex shapes with many intricate details may result in many small 1x1 plates
- The script doesn't currently optimize for specific baseplate sizes (e.g., preferring standard LEGO sizes)

## Future Improvements

Possible enhancements:
- Implement more sophisticated rectangle packing algorithms (e.g., dynamic programming)
- Add support for preferring standard baseplate sizes (2x2, 4x4, 8x8, 16x16, etc.)
- Add visualization of the decomposition
- Support for colored baseplates based on image colors
- Interactive mode for manual adjustments

## License

This script is provided as-is for use with the MachineBlocks library. The MachineBlocks library itself is:

```
Copyright (c) 2022 - 2025 Jan Philipp Knoeller <pk@pksoftware.de>
Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International
https://creativecommons.org/licenses/by-nc-sa/4.0/
```
