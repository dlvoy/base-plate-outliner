Users can extend the language by defining their own **functions** and **modules**. This allows grouping portions of script for easy reuse with different values. 
Well chosen names also help document your script.

**Functions** return values. 

**Modules** perform actions, but do not return values.

OpenSCAD calculates the value of variables  at compile-time, not run-time.
The last variable assignment within a scope applies everywhere in that scope. It also applies to any inner scopes, or children, thereof. 
See [Scope of variables](OpenSCAD_User_Manual/General#Scope_of_variables) for more details.
It may be helpful to think of them as override-able constants rather than as variables.

For functions and modules, OpenSCAD makes copies of pertinent portions of the script for each use. 
Each copy has its own scope, which contains fixed values for variables and expressions unique to that instance.

The name of functions and modules is case sensitive, therefore **test()** and **TEST()** refer to different functions/modules.

## Scope
Modules and functions can be defined within a module definition, where they are visible only in the scope of that module.

For example
![Parabola Openscad plot.jpg](images/Parabola Openscad plot.jpg)
```javascript

function parabola(f,x) = ( 1/(4*f) ) * x*x; 
module plotParabola(f,wide,steps=1) {
  function y(x) = parabola(f,x);
  module plot(x,y) {
    translate([x,y])
      circle(1,$fn=12);
  }
  xAxis=[-wide/2:steps:wide/2];
  for (x=xAxis) 
    plot(x, y(x));
}
color("red")  plotParabola(10, 100, 5);
color("blue") plotParabola(4,  60,  2);

```

The function y() and module plot() cannot be called in the global scope.

## Functions
Functions operate on values to calculate and return new values.
**function definition**
 function name ( parameters ) = value ;
**name**
  Your name for this function. A meaningful name is helpful later.   Currently valid names can only be composed of simple characters and underscores [a-zA-Z0-9_] and do not allow high-ascii or unicode characters.
**parameters**
  Zero or more arguments. Parameters can be assigned default values, to use in case they are omitted in the call. Parameter names are local and do not conflict with external variables of the same name.
**value**
  an expression that calculates a value. This value can be a vector.

### Function use
When used, functions are treated as values, and do not themselves end with a semicolon `;`.
```javascript

// example 1
    
function func0() = 5;
function func1(x=3) = 2*x+1;
function func2() = [1,2,3,4];
function func3(y=7) = (y==7) ? 5 : 2 ;
function func4(p0,p1,p2,p3) = [p0,p1,p2,p3];
    
echo(func0());            // 5
a =   func1();            // 7
b =   func1(5);           // 11
echo(func2());            // [1, 2, 3, 4]
echo(func3(2), func3());  // 2, 5
   
z = func4(func0(), func1(), func2(), func3());
//  [5, 7, [1, 2, 3, 4], 5]
   
translate([0, -4*func0(), 0])
  cube([func0(), 2*func0(), func0()]);
// same as translate([0,-20,0]) cube([5,10,5]);

```
```javascript

// example 2  creates for() range to give desired no of steps to cover range
  
function steps(start, no_steps, end) =
  [start : (end-start)/(no_steps-1) : end];
  
echo(steps(10, 3, 5));                // [10 : -2.5 : 5]
for (i = steps(10, 3, 5))  echo(i);   //  10 7.5 5
  
echo(steps(10, 3, 15));               // [10 : 2.5 : 15]
for (i = steps(10, 3, 15)) echo(i);   // 10 12.5 15
  
echo(steps(0, 5, 5));                // [0 : 1.25 : 5]
for (i = steps(0, 5, 5))   echo(i);  // 0 1.25 2.5 3.75 5

```
![OpenScad func ex1 Rhomboid.jpg](images/OpenScad func ex1 Rhomboid.jpg)
```javascript

// example 3     rectangle with top pushed over, keeping same y
  
function rhomboid(x=1, y=1, angle=90)
  = [[0,0],[x,0],
    [x+x*cos(angle)/sin(angle),y],
    [x*cos(angle)/sin(angle),y]];
    
echo (v1); v1 = rhomboid(10,10,35);  // [[0, 0], 
                                     // [10, 0], 
                                     // [24.2815, 10],
                                     // [14.2815, 10]]
polygon(v1);
polygon(rhomboid(10,10,35));         // alternate

```

```javascript

//performing the same action with a module
   
module parallelogram(x=1,y=1,angle=90)
    {polygon([[0,0],[x,0],
              [x+x*cos(angle)/sin(angle),y],
              [x*cos(angle)/sin(angle),y]]);};
  
parallelogram(10,10,35);
</syntaxhighlight >
<p id=letusedinfunction>
You can also use the [**let** statement](OpenSCAD_User_Manual/Mathematical_Functions#let) to create variables in a function:
</p>
<syntaxhighlight lang="javascript">
function get_square_triangle_perimeter(p1, p2) =
  let (hypotenuse = sqrt(p1*p1+p2*p2))
    p1 + p2 + hypotenuse;

```
It can be used to store values in recursive functions. See the [wikipedia page](Wikipedia:let expression) for more information on the general concept.

### Recursive functions
[Recursive](https://en.wikipedia.org/wiki/recursion (computer science)) function calls are supported. Using the Conditional Operator "... **?** ... **:** ... ", it is possible to ensure the recursion is terminated.
```javascript

// recursion example: add all integers up to n
function add_up_to(n) = ( n==0 ? 
                                 0 : 
                                 n + add_up_to(n-1) );

```
There is a built-in recursion limit to prevent an application crash (a few thousands). If the limit is hit, you get an error like: ERROR: Recursion detected calling function ... .

For any [tail-recursive](https://en.wikipedia.org/wiki/Tail call) function that calls itself, OpenSCAD is able to eliminate internally the recursion transforming it in an iterative loop. 

The previous example code is not tail recursion, as the binary '+'  can only execute when both its operand values are available. Its execution will therefore occur after the recursive call  ```

add_up_to(n-1)

```has generated its second operand value. 

However, the following is entitled to tail-recursion elimination:
```javascript

// tail-recursion elimination example: add all integers up to n
function add_up_to(n, sum=0) =
    n==0 ?
        sum :
        add_up_to(n-1, sum+n);
 
echo(sum=add_up_to(100000));
// ECHO: sum = 5.00005e+009

```
Tail-recursion elimination allows much higher recursion limits (up to 1000000).
<div style="clear: both"></div>

### Function Literals
> **Requires:** 2021.01

[Function literals](https://en.wikipedia.org/wiki/Anonymous_function) are expressions that define functions, other names for this are lambdas or closures.
   **function literal**
 function (x) x + x

Function literals can be assigned to variables and passed around like any value. Calling the function uses the normal function call syntax with parenthesis.
 func = function (x) x * x;
 echo(func(5)); // ECHO: 25

It's possible to define functions that return functions. Unbound variables are captured by lexical scope.
 a = 1;
 selector = function (which)
              which == "add"
              ? function (x) x + x + a
   function (x) x * x + a;
              
 echo(selector("add"));     // ECHO: function(x) ((x + x) + a)
 echo(selector("add")(5));  // ECHO: 11
 
 echo(selector("mul"));     // ECHO: function(x) ((x * x) + a)
 echo(selector("mul")(5));  // ECHO: 26

### Overwriting built-in functions
It is possible to overwrite the built-in functions. Note that definitions are handled first, so the evaluation does indeed return `true` for both `echo()` calls as those are evaluated in a later processing step.

{|class="wikitable"
!Source Code
!Console output
|-
|```javascript
echo (sin(1));
function sin(x) = true;
echo (sin(1));
```
|```output
Compiling design (CSG Tree generation)...
ECHO: true
ECHO: true
Compiling design (CSG Products generation)...
```
|}

## Modules
Modules can be used to define objects or, using `children()`, define operators.
Once defined, modules are temporarily added to the language.
**module definition**
 module name ( parameters ) { actions }
**name**
  Your name for this module. Try to pick something meaningful.  Currently, valid names can only be composed of simple characters and underscores [a-zA-Z0-9_] and do not allow high-ASCII or Unicode characters.
**parameters**
  Zero or more arguments. Parameters may be assigned default values, to use in case they are omitted in the call. Parameter names are local and do not conflict with external variables of the same name.
**actions**
  Nearly any statement valid outside a module can be included within a module. This includes the definition of functions and other modules. Such functions and modules can be called only from within the enclosing module. 

Variables can be assigned, but their scope is limited to within each individual use of the module. There is no mechanism in OpenSCAD for modules to return values to the outside.
See [Scope of variables](OpenSCAD_User_Manual/General#Scope_of_variables) for more details.

### Object modules
Object modules use one or more primitives, with associated operators, to define new objects.

In use, object modules are actions ending with a semi-colon ';'.

 name ( parameter values );

![OpenScad Module ex1 Color bar.jpg](images/OpenScad Module ex1 Color bar.jpg)
```javascript

//example 1
   
translate([-30,-20,0])
   ShowColorBars(Expense);
   
ColorBreak=[[0,""],
           [20,"lime"],  // upper limit of color range
           [40,"greenyellow"],
           [60,"yellow"],
           [75,"LightCoral"],
           [200,"red"]];
Expense=[16,20,25,85,52,63,45];
   
module ColorBar(value,period,range){  // 1 color on 1 bar
   RangeHi = ColorBreak[range][0];
   RangeLo = ColorBreak[range-1][0];
   color( ColorBreak[range][1] ) 
   translate([10*period,0,RangeLo])
      if (value > RangeHi)      cube([5,2,RangeHi-RangeLo]);
      else if (value > RangeLo) cube([5,2,value-RangeLo]);
  }  
module ShowColorBars(values){
    for (month = [0:len(values)-1], range = [1:len(ColorBreak)-1])
      ColorBar(values[month],month,range);
}

```
![OpenScad module ex2 House.jpg](images/OpenScad module ex2 House.jpg)
```java

//example 2
module house(roof="flat",paint=[1,0,0]) {
   color(paint)
   if(roof=="flat") { translate([0,-1,0]) cube(); }
   else if(roof=="pitched") {
     rotate([90,0,0]) linear_extrude(height=1)
     polygon(points=[[0,0],[0,1],[0.5,1.5],[1,1],[1,0]]); }
   else if(roof=="domical") {
     translate([0,-1,0]){
       translate([0.5,0.5,1]) sphere(r=0.5,$fn=20); cube(); }
} }

                   house();
translate([2,0,0]) house("pitched");
translate([4,0,0]) house("domical",[0,1,0]);
translate([6,0,0]) house(roof="pitched",paint=[0,0,1]);
translate([0,3,0]) house(paint=[0,0,0],roof="pitched");
translate([2,3,0]) house(roof="domical");
translate([4,3,0]) house(paint=[0,0.5,0.5]);

```
```javascript

//example 3
   
element_data = [[0,"","",0],  // must be in order
    [1,"Hydrogen","H",1.008],   // indexed via atomic number
    [2,"Helium",  "He",4.003]   // redundant atomic number to preserve your sanity later
];
   
Hydrogen = 1;
Helium   = 2;
      
module coaster(atomic_number){
    element     = element_data[atomic_number][1];
    symbol      = element_data[atomic_number][2];
    atomic_mass = element_data[atomic_number][3];
    //rest of script
}

```

### Operator modules
#### Children
Use of children() allows modules to act as operators applied to any or all of the objects within this module instantiation. 
In use, operator modules do not end with a semi-colon.

 name ( parameter values ){scope of operator}
Basicly the children() command is used to apply modifications to objects that are focused by a scope:
  module myModification() { rotate([0,45,0]) children(); } 
  
  myModification()                 // The modification
  {                                // Begin focus
    cylinder(10,4,4);              // First child
    cube([20,2,2], true);          // Second child
  }                                // End focus

Objects are indexed via integers from 0 to $children-1. OpenSCAD sets $children to the total number of objects within the scope.
Objects grouped into a sub scope are treated as one child. 
[See example of separate children](#SeparateChildren) below and [Scope of variables](OpenSCAD_User_Manual/General#Scope_of_variables). Note that `children()`, `echo()` and empty block statements (including `if`s) count as `$children` objects, even if no geometry is present (as of v2017.12.23).

  children();                         all children
  children(index);                    value or variable to select one child
  children([start : step : end]);     select from start to end incremented by step
  children([start : end]);            step defaults to 1 or -1
  children([vector]);                 selection of several children

**Deprecated child() module**

Up to release 2013.06 the now deprecated `child()` module was used instead. This can be translated to the new children() according to the table:

{| class="wikitable"
|-
! up to 2013.06 !! 2014.03 and later
|-
| child() || children(0)
|-
| child(x) || children(x)
|-
| for (a = [0:$children-1]) child(a) || children([0:$children-1])
|}

![OpenSCAD Manual Modules Module move.jpg](images/OpenSCAD Manual Modules Module move.jpg)

*Examples* 
```javascript

//Use all children
    
module move(x=0,y=0,z=0,rx=0,ry=0,rz=0)
{ translate([x,y,z])rotate([rx,ry,rz]) children(); }
   
move(10)           cube(10,true);
move(-10)          cube(10,true);
move(z=7.07, ry=45)cube(10,true);
move(z=-7.07,ry=45)cube(10,true);

```
![OpenSCAD Manual Modules Module lineuo.jpg](images/OpenSCAD Manual Modules Module lineuo.jpg)
```javascript

//Use only the first child, multiple times
  
module lineup(num, space) {
   for (i = [0 : num-1])
     translate([ space*i, 0, 0 ]) children(0);
}

lineup(5, 65){ sphere(30);cube(35);}

```
![OpenSCAD Manual Modules Module SeparateChildren.jpg](images/OpenSCAD Manual Modules Module SeparateChildren.jpg)

<div id="SeparateChildren"></div>
```javascript

  //Separate action for each child
   
  module SeparateChildren(space){
    for ( i= [0:1:$children-1])   // step needed in case $children < 2  
      translate([i*space,0,0]) {children(i);text(str(i));}
  }
   
  SeparateChildren(-20){
    cube(5);              // 0
    sphere(5);            // 1
    translate([0,20,0]){  // 2
      cube(5);
      sphere(5);
    }     
    cylinder(15);         // 3
    cube(8,true);         // 4
  }
  translate([0,40,0])color("lightblue")
    SeparateChildren(20){cube(3,true);}

```

![OpenSCAD Manual Modules Module MultiRange.jpg](images/OpenSCAD Manual Modules Module MultiRange.jpg)
```javascript

//Multiple ranges
module MultiRange(){
   color("lightblue") children([0:1]);
   color("lightgreen")children([2:$children-2]);
   color("lightpink") children($children-1);
}
   
MultiRange()
{
   cube(5);              // 0
   sphere(5);            // 1
   translate([0,20,0]){  // 2
     cube(5);
     sphere(5);
   }     
   cylinder(15);         // 3
   cube(8,true);         // 4
}

```

### Further module examples
  **Objects**
```javascript

module arrow(){
    cylinder(10);
    cube([4,.5,3],true);
    cube([.5,4,3],true);
    translate([0,0,10]) cylinder(4,2,0,true);
}
  
module cannon(){
    difference(){union()
      {sphere(10);cylinder(40,10,8);} cylinder(41,4,4);
} }
  
module base(){
    difference(){
      cube([40,30,20],true);
      translate([0,0,5])  cube([50,20,15],true);
} }

```
  **Operators**
![OpenSCAD Manual Modules Module RotaryCluster v2.jpg](images/OpenSCAD Manual Modules Module RotaryCluster v2.jpg)
```javascript

module aim(elevation,azimuth=0)
    { rotate([0,0,azimuth])
      { rotate([0,90-elevation,0]) children(0);
      children([1:1:$children-1]);   // step needed in case $children < 2
} }
   
aim(30,20)arrow();
aim(35,270)cannon();
aim(15){cannon();base();}

module RotaryCluster(radius=30,number=8)
    for (azimuth =[0:360/number:359])
      rotate([0,0,azimuth])    
        translate([radius,0,0]) { children();
          translate([40,0,30]) text(str(azimuth)); }
   
RotaryCluster(200,7) color("lightgreen") aim(15){cannon();base();}
rotate([0,0,110]) RotaryCluster(100,4.5) aim(35)cannon();
color("LightBlue")aim(55,30){cannon();base();}

```

### Recursive modules
Like functions, modules may contain recursive calls. However, there is no tail-recursion elimination for recursive modules.

The code below generates a crude model of a tree. Each tree branch is itself a modified version of the tree and produced by recursion. Be careful to keep the recursion depth (branching) n below 7 as the number of primitives and the preview time grow exponentially.

![Simple recursive tree.png](images/Simple recursive tree.png)
```javascript

    module simple_tree(size, dna, n) {   
        if (n > 0) {
            // trunk
            cylinder(r1=size/10, r2=size/12, h=size, $fn=24);
            // branches
            translate([0,0,size])
                for(bd = dna) {
                    angx = bd[0];
                    angz = bd[1];
                    scal = bd[2];
                        rotate([angx,0,angz])
                            simple_tree(scal*size, dna, n-1);
                }
        }
        else { // leaves
            color("green")
            scale([1,1,3])
                translate([0,0,size/6]) 
                    rotate([90,0,0]) 
                        cylinder(r=size/6,h=size/10);
        }
    }
    // dna is a list of branching data bd of the tree:
    //      bd[0] - inclination of the branch
    //      bd[1] - Z rotation angle of the branch
    //      bd[2] - relative scale of the branch
    dna = [ [12,  80, 0.85], [55,    0, 0.6], 
            [62, 125, 0.6], [57, -125, 0.6] ];
    simple_tree(50, dna, 5);

```
Another example of recursive module may be found in [Tips and Tricks](OpenSCAD_User_Manual/Tips_and_Tricks#Stack_cylinders_on_top_of_each_other)

### Overwriting built-in modules
It is possible to overwrite the built-in modules.

A simple, but pointless example would be:
```javascript

module sphere(){
    square();
}
sphere();

```
Note that the built-in sphere module can not be called when over written.

A more sensible way to use this language feature is to overwrite the 3D primitives with extruded 2D-primitives.
This allows additional customization of the default parameters and adding additional parameters.
