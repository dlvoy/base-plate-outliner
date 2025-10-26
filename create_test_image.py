#!/usr/bin/env python3
"""
Create a simple test image for the irregular baseplate generator.
This creates a simple L-shaped pattern.
"""

from PIL import Image, ImageDraw

# Create a 16x16 pixel image (white background)
img = Image.new('L', (16, 16), color=255)
draw = ImageDraw.Draw(img)

# Draw an L-shape in black
# Vertical part of L: columns 0-3, rows 0-15
draw.rectangle([0, 0, 3, 15], fill=0)

# Horizontal part of L: columns 4-15, rows 12-15
draw.rectangle([4, 12, 15, 15], fill=0)

# Save the image
img.save('test_shape.png')
print("Created test_shape.png - a simple L-shaped pattern (16x16 pixels)")
print("You can now run: python3 generate_irregular_baseplate.py test_shape.png")
