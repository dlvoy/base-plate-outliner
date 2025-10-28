# Usage Guidelines

**Visual Examples**: For rendered images of all features and modes, check out the [Sample Renderings Gallery](./GALLERY.md)

See also [tutorial on creating custom baseplate](./TUTORIAL.md)

## How It Works

1. **Image Loading**: The script loads the PNG image and converts it to grayscale
2. **Thresholding**: Pixels are classified as "inside" (dark, value < threshold) or "outside" (light, value >= threshold)
3. **Rectangle Decomposition**: A greedy algorithm decomposes the shape into rectangular regions, attempting to minimize the number of baseplates needed
4. **Edge Processing** (optional): When `--edge` is used, the shape is split into edge and interior regions using morphological erosion with 8-connectivity (ensuring uniform thickness in all directions including diagonals)
5. **Border/Frame Generation** (optional):
   - **Border Mode** (`--border`): Creates a border around the outside edge of the shape, following its contours with precise millimeter positioning and sizing
   - **Frame Mode** (`--frame --border`): Creates a filled rectangular frame that encloses the entire shape. The frame fills the area between the shape's bounding box and an outer rectangle expanded by the specified padding
   - Both modes use an optimized rectangle decomposition algorithm to minimize the number of cubes while maintaining exact mm dimensions
6. **OpenSCAD Generation**: The script generates an OpenSCAD file with properly positioned `machineblock()` calls for baseplates, and `cube()` calls for interior fill and borders
7. **Debug Mode** (optional): When enabled with `--debug`, each baseplate receives a unique random color. The colors maintain the same saturation and lightness as the default yellow (#EAC645) but vary in hue, making it easy to distinguish individual baseplates in the rendered model

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

You may want use image editor supporting pixel art mode, like free online tool Piskel App: https://www.piskelapp.com/p/create/sprite/

## Output

The script generates:
- An OpenSCAD `.scad` file ready to be opened in OpenSCAD
- Statistics about the baseplates used (sizes and quantities)

The generated OpenSCAD file can be opened in OpenSCAD, rendered and exported to 3MF or STL for 3D printing.

## Examples

```bash
# Use default image.png (generates image.scad)
python3 generate_irregular_baseplate.py

# Specify custom image (generates my_shape.scad)
python3 generate_irregular_baseplate.py my_shape.png

# Custom output file (overrides default naming)
python3 generate_irregular_baseplate.py my_shape.png -o custom_output.scad

# Custom threshold (more sensitive to dark pixels)
python3 generate_irregular_baseplate.py my_shape.png -t 100

# Debug mode with random colors for each baseplate
python3 generate_irregular_baseplate.py my_shape.png --debug

# Edge mode: only 1 brick unit thick edge with baseplates, rest filled with cubes
python3 generate_irregular_baseplate.py my_shape.png --edge

# Edge mode with 3 brick units thickness
python3 generate_irregular_baseplate.py my_shape.png --edge=3

# Border mode: add 5mm border around the shape
python3 generate_irregular_baseplate.py my_shape.png --border

# Border with custom 3.2mm thickness
python3 generate_irregular_baseplate.py my_shape.png --border=3.2

# Border with height adjustment (+2.5mm taller)
python3 generate_irregular_baseplate.py my_shape.png --border --borderHeightAdjust=2.5

# Border with negative adjustment (-1.5mm shorter, final height = 1.7mm)
python3 generate_irregular_baseplate.py my_shape.png --border --borderHeightAdjust=-1.5

# Combine edge and border modes
python3 generate_irregular_baseplate.py my_shape.png --edge=2 --border=4.5 --borderHeightAdjust=1.0

# Frame mode: rectangular border with no padding (frame touches shape edges)
python3 generate_irregular_baseplate.py my_shape.png --frame --border=0

# Frame mode with 5mm padding between shape and frame
python3 generate_irregular_baseplate.py my_shape.png --frame --border=5

# Frame mode with custom padding and height adjustment
python3 generate_irregular_baseplate.py my_shape.png --frame --border=3 --borderHeightAdjust=2.0

# Combine edge and frame modes
python3 generate_irregular_baseplate.py my_shape.png --edge=2 --frame --border=4.5

# Use custom OpenSCAD config file
python3 generate_irregular_baseplate.py my_shape.png --config=my-custom-config.scad

# Generate baseplates for Nanoblocks (half-size bricks)
python3 generate_irregular_baseplate.py my_shape.png --config=configs/config-nano.scad

# Center the model at origin (useful for 3D printing)
python3 generate_irregular_baseplate.py my_shape.png --center

# Combine multiple options: centered model with border and debug colors
python3 generate_irregular_baseplate.py my_shape.png --border=3.2 --center --debug

# Center a frame-based design
python3 generate_irregular_baseplate.py my_shape.png --frame --border=5 --center
```
