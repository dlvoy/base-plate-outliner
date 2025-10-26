__NOTOC__

Using `projection()`, you can create 2d drawings from 3d models, and export them to the dxf format. It works by projecting a 3D model to the (x,y) plane, with z at 0. If `cut=true`, only points with z=0 are considered (effectively cutting the object), with `cut=false`(*the default*), points above and below the plane are considered as well (creating a proper projection).

**Example**: Consider example002.scad, that comes with OpenSCAD. 

![Openscad projection example 2x.png](images/Openscad projection example 2x.png)

Then you can do a 'cut' projection, which gives you the 'slice' of the x-y plane with z=0. 

 projection(cut = true) example002();

![Openscad projection example 3x.png](images/Openscad projection example 3x.png)

You can also do an 'ordinary' projection, which gives a sort of 'shadow' of the object onto the xy plane. 

 projection(cut = false) example002();

![Openscad example projection 8x.png](images/Openscad example projection 8x.png)

**Another Example**

You can also use projection to get a 'side view' of an object. Let's take example002, rotate it, and move it up out of the X-Y plane:

 translate([0,0,25]) rotate([90,0,0]) example002();

![Openscad projection example 4x.png](images/Openscad projection example 4x.png)

Now we can get a side view with projection()

 projection() translate([0,0,25]) rotate([90,0,0]) example002();

![Openscad projection example 5x.png](images/Openscad projection example 5x.png)

Links: 

*[http://www.gilesbathgate.com/2010/06/extracting-2d-mendel-outlines-using-openscad/ More complicated example] from Giles Bathgate's blog
