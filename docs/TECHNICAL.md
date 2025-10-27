# Project Technical Details

## Algorithm Details

The rectangle decomposition uses a greedy algorithm:
1. Scan the bitmap from top-left to bottom-right
2. At each "inside" pixel, find the largest rectangle that fits
3. Place that rectangle and mark those cells as used
4. Continue scanning

This approach prioritizes larger rectangles, which generally results in fewer total pieces, though it may not always find the absolute optimal solution.


## Technical Details

- **Coordinate System**: The script correctly handles coordinate system conversion:
  - **Image coordinates**: Y=0 is at the top, Y increases downward
  - **OpenSCAD coordinates**: Y=0 is at the bottom, Y increases upward
  - The script automatically flips the Y-axis so the rendered model matches the image orientation
- **Unit Size**: Calculated from OpenSCAD config values: `unitGrid[0] * unitMbu * scale` (default: 5 * 1.6 * 1.0 = 8mm)
- **Config Integration**: The script parses the OpenSCAD config file to read `unitMbu`, `unitGrid`, and `scale` values, ensuring perfect consistency between Python calculations and OpenSCAD rendering
- **Positioning**: Baseplates are positioned using OpenSCAD's `translate()` function
- **Border Precision**: Border cubes use floating-point mm coordinates for precise positioning (e.g., 3.2mm, 4.5mm)
- **Two-Layer Border/Frame**: When `--borderHeightAdjust > 0`, borders and frames are generated as two separate layers:
  - **Base layer**: Height equals baseplate height, provides main structural support
  - **Top layer**: Height equals `borderHeightAdjust` value, with inner edge inset by 0.1mm (derived from `baseWallThicknessAdjustment`) to provide clearance and prevent brick collision when stacking
  - The outer boundary remains identical between layers while only the inner edge is adjusted for clearance
- **Gap Elimination**: All baseplates are generated with `baseSideAdjustment = 0` to eliminate gaps between adjacent pieces
- **Integration**: The generated script uses the MachineBlocks library's `machineblock()` function with standard configuration parameters
- **Path Handling**: Generated .scad files use relative paths for `use` and `include` directives (e.g., `use <machineblocks/lib/block.scad>`). These paths are relative to the script's main directory. If you generate output files in different directories using `-o`, the relative paths may not resolve correctly in OpenSCAD. Solutions:
  - Generate output files in the same directory as the script
  - Install MachineBlocks globally in OpenSCAD (see OpenSCAD documentation for library paths)
  - Manually edit the `use` and `include` paths in the generated .scad file to use absolute paths or correct relative paths

## Project Structure

```
base-plate-outliner/
├── .venv/                      # Python virtual environment (created by setup)
├── machineblocks/              # Git submodule - MachineBlocks library
│   ├── lib/                    # MachineBlocks library files
│   ├── config/                 # MachineBlocks configuration
│   └── ...
├── configs/                    # Custom configuration files
│   └── config-nano.scad        # Nanoblocks (half-size) configuration
├── generate_irregular_baseplate.py  # Main script
├── test_shape.png              # Test image
├── example_output.scad         # Example generated output
├── setup.sh                    # Linux/Mac setup script
├── setup.bat                   # Windows setup script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Limitations

- The greedy algorithm may not always produce the absolute minimum number of baseplates
- Very complex shapes with many intricate details may result in many small 1x1 plates
- The script doesn't currently optimize for specific baseplate sizes (e.g., preferring standard big-L sizes)

## Future Improvements

Possible enhancements:
- Implement more sophisticated rectangle packing algorithms (e.g., dynamic programming)
- Add support for preferring standard baseplate sizes (2x2, 4x4, 8x8, 16x16, etc.)
- Add visualization of the decomposition
- Support for colored baseplates based on image colors
- Interactive mode for manual adjustments
