> **Note:** This section is incomplete.

OpenSCAD is a [2D](https://en.wikipedia.org/wiki/2D_computer_graphics)/[3D](https://en.wikipedia.org/wiki/3D computer graphics software) and [solid modeling](https://en.wikipedia.org/wiki/Solid modeling) program that is based on a [Functional programming](https://en.wikipedia.org/wiki/Functional programming) [language](https://en.wikipedia.org/wiki/Procedural modeling) used to create [models](https://en.wikipedia.org/wiki/Polygonal modeling) that are  previewed on the screen, and rendered into 3D [mesh](https://en.wikipedia.org/wiki/Polygon mesh) that can be exported in a variety of 2D/3D file formats.
   
A script in the OpenSCAD language is used to create 2D or 3D models. This script is a free format list of action statements.
  object();
  variable = value;
  operator()   action();
  operator() { action();    action(); }
  operator()   operator() { action(); action(); }
  operator() { operator()   action();
               operator() { action(); action(); } }
**Objects**
  Objects are the building blocks for models, created by 2D and 3D primitives. Objects end in a semicolon ';'.
  Examples are: cube(), sphere(), polygon(), circle(), etc.
**Actions**
  Action statements include creating objects using primitives and assigning values to variables. Action statements also end in a semicolon ';'.
  Example: a=1; b = a+7;
**Operators**
  Operators, or transformations, modify the location, color and other properties of objects. Operators use braces '{}' when their scope covers more than one action. More than one operator may be used for the same action or group of actions. Multiple operators are processed Right to Left, that is, the operator closest to the action is processed first. Operators do not end in semicolons ';', but the individual actions they contain do. 
  Examples:   
    cube(5);
    x = 4+y;
    rotate(40) square(5,10);
    translate([10,5]) { circle(5); square(4); }
    rotate(60) color("red") { circle(5); square(4); }
    color("blue") { translate([5,3,0]) sphere(5); rotate([45,0,45]) { cylinder(10); cube([5,6,7]); } }

## Comments
Comments are a way of leaving notes within the script, or code, (either to yourself or to future programmers) describing how the code works, or what it does. Comments are not evaluated by the compiler, and should not be used to describe self-evident code. 
 
OpenSCAD uses C++-style comments:
 // This is a comment
   
 myvar = 10; // The rest of the line is a comment
   
 /*
    Multi-line comments
    can span multiple lines.
 */

## Values and Data Types
A value in OpenSCAD is either a Number (like 42), a Boolean (like true), a String (like "foo"), a Range (like [0: 1: 10]), a Vector (like [1,2,3]), or the Undefined value (undef). Values can be stored in variables, passed as function arguments, and returned as function results.

[OpenSCAD is a dynamically typed language with a fixed set of data types. There are no type names, and no user defined types.]

### Numbers
Numbers are the most important type of value in OpenSCAD, and they are written in the familiar decimal notation used in other languages. Eg, -1, 42, 0.5, 2.99792458e+8. 

> **Requires:** Development snapshot
Hexadecimal constants are allowed in the C style, `0x` followed by hexadecimal digits.  [OpenSCAD does not support octal notation for numbers.]

In addition to decimal numerals, the following names for special numbers are defined:
* `PI`

OpenSCAD has only a single kind of number, which is a 64 bit IEEE floating point number. OpenSCAD does not distinguish integers and floating point numbers as two different types, nor does it support complex numbers. Because OpenSCAD uses the IEEE floating point standard, there are a few deviations from the behavior of numbers in mathematics:
* We use binary floating point. A fractional number is not represented exactly unless the denominator is a power of 2. For example, 0.2 (2/10) does not have an exact internal representation, but 0.25 (1/4) and 0.375 (3/8) are represented exactly.
* The largest representable number is about 1e308. If a numeric result is too large, then the result can be infinity (printed as inf by echo).
* The smallest representable number is about -1e308. If a numeric result is too small, then the result can be -infinity (printed as -inf by echo).
* Values are precise to about 16 decimal digits.
* If a numeric result is invalid, then the result can be Not A Number (printed as nan by echo).
* If a non-zero numeric result is too close to zero to be representable, then the result is -0 if the result is negative, otherwise it is 0. Zero (0) and negative zero (-0) are treated as two distinct numbers by some of the math operations, and are printed differently by 'echo', although they compare as equal.

The constants `inf` and `nan` are not supported as numeric constants by OpenSCAD, even though you can compute numbers that are printed this way by 'echo'. You can define variables with these values by using:
 inf = 1e200 * 1e200;
 nan = 0 / 0;
 echo(inf,nan);

The value `nan` is the only OpenSCAD value that is not equal to any other value, including itself. Although you can test if a variable 'x' has the undefined value using 'x == undef', you can't use 'x == 0/0' to test if x is Not A Number. Instead, you must use 'x != x' to test if x is nan.

### Boolean values
Booleans are variables with two states, typically denoted in OpenSCAD as true and false.  
Boolean variables are typically generated by conditional tests and are employed by conditional statement 'if()'. conditional operator '? :', 
and generated by logical operators `!` (not), `&&` (and), and `||` (or).  Statements such as `if()` actually accept non-boolean variables, but most values are converted to `true` in a boolean context. The values that count as `false` are:
* `false`
* `0` and `-0`
* `""`
* `[]`
* `undef`

Note that `"false"` (the string), `[0]` (a numeric vector), 
`[ [] ]` (a vector containing an empty vector), `[false]` 
(a vector containing the Boolean value false) and `0/0` (not a number) all count as true.

### Strings
A string is a sequence of zero or more unicode characters. String values are used to specify file names when importing a file, and to display text for debugging purposes when using echo(). Strings can also be used with the [**text()** primitive](OpenSCAD_User_Manual/Text ), added in version **2015.03**.

A string literal is written as a sequence of characters enclosed in quotation marks `"`, like this: `""` (an empty string), or `"this is a string"`.

To include a `"` character in a string literal, use `\"`. To include a `\` character in a string literal, use `\\`. The following escape sequences beginning with `\` can be used within string literals:
* \" → "
* \\ → \
* \t → tab
* \n → newline
* \r → carriage return
* \x21 → ! - valid only in the range from \x01 to \x7f, \x00 produces a space
* \u03a9 → Ω - 4 digit unicode code point, see <b>text()</b> for further information on unicode characters
* \U01f600 → 😀 - 6 digit unicode code point
This behavior is new since OpenSCAD-2011.04. You can upgrade old files using the following sed command: `sed 's/\\/\\\\/g' non-escaped.scad > escaped.scad`

**Example:**
   
  echo("The quick brown fox \tjumps \"over\" the lazy dog.\rThe quick brown fox.\nThe \\lazy\\ dog.");
   
  **result**

    ECHO: "The quick brown fox     jumps "over" the lazy dog.
    The quick brown fox.
    The \lazy\ dog."
   
  **old result**
    ECHO: "The quick brown fox \tjumps \"over\" the lazy dog.
    The quick brown fox.\nThe \\lazy\\ dog."

### Ranges
Ranges are used by [ for() loops](OpenSCAD_User_Manual/Conditional_and_Iterator_Functions#For_Loop) and [children()](OpenSCAD_User_Manual/User-Defined_Functions_and_Modules#Children). They have 2 varieties:
   [<*start*>:<*end*>]
   [<*start*>:<*increment*>:<*end*>]

A missing <*increment*> defaults to 1.

Although enclosed in square brackets [] , they are not vectors. They use colons : for separators rather than commas.
 r1 = [0:10];
 r2 = [0.5:2.5:20];
 echo(r1); // ECHO: [0: 1: 10]
 echo(r2); // ECHO: [0.5: 2.5: 20]

**In version 2021.01 and earlier**, a range in the form  [<*start*>:<*end*>] with <*start*> greater than <*end*> generates a warning and is equivalent to [<*end*>: 1: <*start*>].

A range in the form  [<*start*>:1:<*end*>] with <*start*> greater than <*end*> does not generate a warning and is equivalent to []. > **Requires:** Development snapshot This also applies when the increment is omitted.

The <*increment*> in a range may be negative (for versions after 2014).  A start value less than the end value, with a negative increment, does not generate a warning and is equivalent to [].

You should take care with step values that cannot be represented exactly as binary floating point numbers. Integers are okay, as are fractional values whose denominator is a power of two. For example, 0.25 (1/4) and 0.375 (3/8) are safe, but 0.2 (2/10) may cause problems. The problem with these step values is that your range may have more or fewer elements than you expect, due to inexact arithmetic.

### The Undefined Value
The undefined value is a special value written as `undef`. It is the initial value of a variable that hasn't been assigned a value, and it is often returned as a result by functions or operations that are passed illegal arguments. Finally, `undef` can be used as a null value, equivalent to `null` or `NULL` in other programming languages.

All arithmetic expressions containing `undef` values evaluate as `undef`. In logical expressions, `undef` is equivalent to `false`. Relational operator expressions with `undef` evaluate as `false` except for `undef==undef`, which is `true`.

Note that numeric operations may also return 'nan' (not-a-number) to indicate an illegal argument. For example, `0/false` is `undef`, but `0/0` is 'nan'. Relational operators like < and > return `false` if passed illegal arguments. Although `undef` is a language value, 'nan' is not.

## Variables
OpenSCAD variables are created by a statement with a name or [identifier](https://en.wikipedia.org/wiki/Identifier (computer programming)), assignment via an expression and a semicolon. The role of arrays, found in many imperative languages, is handled in OpenSCAD via vectors. Valid identifiers are composed of simple characters and underscores [a-zA-Z0-9_] and do not allow high-ascii or unicode characters.

**Before Development snapshot**, variable names can begin with digits.  In **Development snapshot**, names starting with `0x` and followed by hexadecimal digits represent a hexadecimal constant, and other variable names beginning with digits will trigger a warning.

 var = 25;
 xx = 1.25 * cos(50);
 y = 2*xx+var;
 logic = true;
 MyString = "This is a string";
 a_vector = [1,2,3];
 rr = a_vector[2];      // member of vector
 range1 = [-1.5:0.5:3]; // for() loop range
 xx = [0:5];            // alternate for() loop range

OpenSCAD is a [ Functional](https://en.wikipedia.org/wiki/Functional programming) programming language, as such [variables](https://en.wikipedia.org/wiki/Variable_(computer_science%29)) are bound to expressions and keep a single value during their entire lifetime due to the requirements of [referential transparency](https://en.wikipedia.org/wiki/Referential transparency (computer science)). In [imperative languages](https://en.wikipedia.org/wiki/Imperative programming), such as C, the same behavior is seen as constants, which are typically contrasted with normal variables. 

In other words OpenSCAD variables are more like constants, but with an important difference. If variables are assigned a value multiple times, only the last assigned value is used in all places in the code. See further discussion at [#Variables cannot be changed](#Variables cannot be changed).  This behavior is due to the need to supply variable input on the [command line](OpenSCAD User Manual/Using OpenSCAD in a command line environment), via the use of *-D variable=value* option. OpenSCAD currently places that assignment at the end of the source code, and thus must allow a variable's value to be changed for this purpose.

Values cannot be modified during run time; all variables are effectively constants that do not change once created. Each variable retains its last assigned value, in line with [Functional](https://en.wikipedia.org/wiki/Functional programming) programming languages. Unlike [Imperative](https://en.wikipedia.org/wiki/Imperative programming) languages, such as C, OpenSCAD is not an iterative language, and as such the concept of *x*&nbsp;=&nbsp;*x*&nbsp;+&nbsp;1 is not valid. The only way an expression like this could work is if the *x* on the right comes from a parent scope, such as an argument list, and the assignment operation creates a new *x* in the current scope. Understanding this concept leads to understanding the beauty of OpenSCAD.

**Before version 2015.03**, it was not possible to do assignments at any place except the file top-level and module top-level. Inside an *if/else*&nbsp; or *for*&nbsp; loop, assign() was needed.

**Since version 2015.03**, variables can now be assigned in any scope. Note that assignments are valid only within the scope in which they are defined - it is still not possible to leak values to an outer scope. See [Scope of variables](#Scope of variables) for more details.

 a=0;
 if (a==0) 
   {
  a=1; //  before 2015.03 this line would generate a Compile Error
       //  since 2015.03  no longer an error, but the value a=1 is confined to within the braces {}
   }
### Undefined variable
Referring to a variable that has not had a value assigned triggers a warning, and yields the special value **undef**.

It is possible to detect an undefined variable using `is_undef(var)`.  (Note that the simpler `var == undef` will yield a warning.)

  **Example**
   
  echo("Variable a is ", a);                // Variable a is undef, triggers a warning
  if (is_undef(a)) {                        // does not trigger a warning
    echo("Variable a is tested undefined"); // Variable a is tested undefined
  }

### Scope of variables
When operators such as translate() and color() need to encompass more than one action ( actions end in ;), braces {} are needed to group the actions, creating a new, inner scope.
When there is only one semicolon, braces are usually optional.

Each pair of braces creates a new scope inside the scope where they were used. **Since 2015.03**, new variables can be created within this new scope. New values can be given to variables that were created in an outer scope. 
These variables and their values are also available to further inner scopes created within this scope, but are **not available** to anything outside this scope. Variables still have only the last value assigned within a scope.

                        // scope 1
  a = 6;                // create a
  echo(a,b);            //                6, undef
  translate([5,0,0]){   // scope 1.1
    a= 10;
    b= 16;              // create b
    echo(a,b);          //              100, 16   a=10; was overridden by later a=100;
    color("blue") {     // scope 1.1.1
      echo(a,b);        //              100, 20
      cube();
      b=20;
    }                   // back to 1.1
    echo(a,b);          //              100, 16
    a=100;              // override a in 1.1
  }                     // back to 1   
  echo(a,b);            //                6, undef
  color("red"){         // scope 1.2
    cube();
    echo(a,b);          //                6, undef
  }                     // back to 1
  echo(a,b);            //                6, undef
   
  //In this example, scopes 1 and 1.1 are outer scopes to 1.1.1 but 1.2 is not.
   **Anonymous scopes** are not considered scopes:
  {
    angle = 45;
  }
  rotate(angle) square(10);

For() loops are not an exception to the rule about variables having only one value within a scope. A copy of loop contents is created for each pass. Each pass is given its own scope, allowing any variables to have unique values for that pass. No, you still can't do a=a+1;

### Variables cannot be changed
The simplest description of OpenSCAD variables is that an assignment creates a new variable in the current scope, and that it's not legal to set a variable that has already been set in the current scope.  In a lot of ways, it's best to think of them as named constants, calculated on entry to the scope.

That's not quite accurate.  If you set a variable twice in the same scope, the second assignment triggers a warning (which may abort the program, depending on preferences settings).  It does *not* then replace the value of the variable - rather, it replaces the original assignment, at its position in the list of assignments.  The original assignment is never executed.

 a = 1;   // never executed
 echo(a); // 2
 a = 2;   // executed at the position of the original assignment
 echo(a); // 2

That's still not the complete story.  There are two special cases that do not trigger warnings:
* if the first assignment is in the top level of an `include` file, and the second assignment is in the including file.
* If the first assignment is in the top level of the program source, and the second assignment comes from a `-D` option or from the Customizer.

While this appears to be counter-intuitive, it allows you to do some interesting things: for instance, if you set up your shared library files to have default values defined as variables at their root level, when you include that file in your own code you can 're-define' or override those constants by simply assigning a new value to them - and other variables based on that variable are based on the value from the main program.

 // main.scad
 include <lib.scad>
 a = 2;
 echo(b);

 // lib.scad
 a = 1;
 b = a + 1;

will produce 3.

### Special variables
Special variables provide an alternate means of passing arguments to modules and functions.
All variables starting with a '$' are special variables, similar to special variables in lisp.
As such they are more dynamic than regular variables.
(for more details see [Other Language Features](OpenSCAD_User_Manual/Other_Language_Features#Special_variables))

## Vectors
A vector or list is a sequence of zero or more OpenSCAD values. Vectors are collections of numeric or boolean values, variables, vectors, strings or any combination thereof. They can also be expressions that evaluate to one of these. Vectors handle the role of arrays found in many imperative languages.
The information here also applies to lists and tables that use vectors for their data.
   
A vector has square brackets, [] enclosing zero or more items (elements or members), separated by commas. A vector can contain vectors, which can contain vectors, etc.

**Examples**

    [1,2,3]
    [a,5,b]
    []
    [5.643]
    ["a","b","string"]
    [[1,r],[x,y,z,4,5]]
    [3, 5, [6,7], [[8,9],[10,[11,12],13], c, "string"]
    [4/3, 6*1.5, cos(60)]

use in OpenSCAD:
   cube( [width,depth,height] );           // optional spaces shown for clarity
   translate( [x,y,z] )
   polygon( [ [x<sub>0</sub>,y<sub>0</sub>],  [x<sub>1</sub>,y<sub>1</sub>],  [x<sub>2</sub>,y<sub>2</sub>] ] );

### Creation
Vectors are created by writing the list of elements, separated by commas, and enclosed in square brackets. Variables are replaced by their values.
   cube([10,15,20]);
   a1 = [1,2,3];
   a2 = [4,5];
   a3 = [6,7,8,9];
   b  = [a1,a2,a3];    // [ [1,2,3], [4,5], [6,7,8,9] ]  note increased nesting depth
Vectors can be initialized using a for loop enclosed in square brackets. 

The following example initializes the vector *result* with a length *n* of 10 values to the value of *a*.```openscad
n = 10;
a = 0;

result = [ for (i=[0:n-1]) a ];
echo(result); //ECHO: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
```The following example shows a vector *result* with a *n* length of 10 initialized with values that are alternatively *a* or *b* respectively if the index position *i* is an even or an odd number.```

n = 10;
a = 0;
b = 1;
result = [ for (i=[0:n-1]) (i % 2 == 0) ? a : b ];
echo(result); //ECHO: [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]

```

### Indexing elements within vectors
Elements within vectors are numbered from 0 to n-1 where n is the length returned by [len()](#len).
Address elements within vectors with the following notation:
 e[5]           // element no 5 (sixth) at   1st nesting level
 e[5][2]        // element 2 of element 5    2nd nesting level
 e[5][2][0]     // element 0 of 2 of 5       3rd nesting level
 e[5][2][0][1]  // element 1 of 0 of 2 of 5  4th nesting level

<div id= "example1"> example elements with lengths from len()</div>
 e = [ [1], [], [3,4,5], "string", "x", [[10,11],[12,13,14],[[15,16],[17]]] ];  // length 6
 
 address       length  element
 e[0]          1       [1]
 e[1]          0       []
 e[5]          3       [ [10,11], [12,13,14], [[15,16],[17]] ]
 e[5][1]       3       [ 12, 13, 14 ]
 e[5][2]       2       [ [15,16], [17] ]
 e[5][2][0]    2       [ 15, 16 ]
 e[5][2][0][1] undef   16
     
 e[3]          6       "string"
 e[3 ][2]      1       "r"
   
 s = [2,0,5]; a = 2;
 s[a]          undef   5
 e[s[a]]       3       [ [10,11], [12,13,14], [[15,16],[17]] ]

#### String indexing
The elements (characters) of a string can be accessed:
 "string"[2]    //resolves to "r"
 

#### Dot notation indexing
The first three elements of a vector can be accessed with an alternate dot notation:
 e.x    //equivalent to e[0]
 e.y    //equivalent to e[1]
 e.z    //equivalent to e[2]

### Vector operators
#### concat
> **Requires:** 2015.03
  
`concat()` combines the elements of 2 or more vectors into a single vector. No change in nesting level is made.
  vector1 = [1,2,3]; vector2 = [4]; vector3 = [5,6];
  new_vector = concat(vector1, vector2, vector3); // [1,2,3,4,5,6]
   
  string_vector = concat("abc","def");                 // ["abc", "def"]
  one_string = str(string_vector[0],string_vector[1]); // "abcdef"

#### len
`len()` is a function that returns the length of vectors or strings. 
Indices of elements are from [0] to [length-1].
   **vector**
  : Returns the number of elements at this level.
  : Single values, which are **not** vectors, raise an error.
   **string**
  : Returns the number of characters in a string.
  a = [1,2,3]; echo(len(a));   //  3

[See example elements with lengths](#example1)

### Matrix
A matrix is a vector of vectors.

 Example that defines a 2D rotation matrix
 mr = [
      [cos(angle), -sin(angle)],
      [sin(angle),  cos(angle)]
     ];

## Objects
> **Requires:** Development snapshot

Objects store collections of data, like vectors, but the individual members are accessed by string names rather than by numeric indexes.  They are analogous to JavaScript objects or Python dictionaries.  There is currently a limited implementation of objects:  it is not possible for an OpenSCAD program to create an object, only to receive one as the return value from a function.

### Retrieving a value from an object
    obj.name

Retrieves the named value from the object, for a name that is constant and syntactically suitable for use as an identifier.

    obj["name"]

Retrieves the named value from the object, for a name that is an arbitrary string expression.

Note that members with identifier-like names can be accessed using either mechanism.  The choice depends on the particular use case.

### Iterating over object members
   for (name = obj) { ... }

iterates over the members of the object, in an unspecified order, setting `name` to the name of each member.  It is then typically desirable to access the value using `obj[name]`.

This construct works for [flow-control `for`](OpenSCAD_User_Manual/Conditional_and_Iterator_Functions#For_Loop), [intersection_for()](OpenSCAD_User_Manual/Conditional_and_Iterator_Functions#Intersection_For_Loop), and [list-comprehension `for`](OpenSCAD_User_Manual/List_Comprehensions#for).

## Getting input
There is no mechanism for variable input from keyboard or reading from arbitrary files.  There is no prompting mechanism, no input window, or input fields or any way to manually enter data while the script is running.

Variables can be set via:
* assignments in the script
* [the Customizer](OpenSCAD_User_Manual/Customizer)
* `-D` at the [command line interface](OpenSCAD_User_Manual/Using_OpenSCAD_in_a_command_line_environment)
* accessing data in a few file formats (stl, dxf, png, etc).

With the exception of DXF files, data from files is not accessible to the script, although to a limited extent the script may be able to manipulate the data as a whole.  For example, STL files can be rendered in OpenSCAD, translated, clipped, etc.  But the internal data that constitutes the STL file is inaccessible.

### Getting a point from a drawing
Getting a point is useful for reading an origin point in a 2D view in a technical drawing. The function dxf_cross reads the intersection of two lines on a layer you specify and returns the intersection point. This means that the point must be given with two lines in the DXF file, and not a point entity.

```java

OriginPoint = dxf_cross(file="drawing.dxf", layer="SCAD.Origin", 
                        origin=[0, 0], scale=1);

```

### Getting a dimension value
You can read dimensions from a technical drawing. This can be useful to read a rotation angle, an extrusion height, or spacing between parts. In the drawing, create a dimension that does not show the dimension value, but an identifier. To read the value, you specify this identifier from your program:

```java

TotalWidth = dxf_dim(file="drawing.dxf", name="TotalWidth",
                        layer="SCAD.Origin", origin=[0, 0], scale=1);

```

For a nice example of both functions, see Example009 and the image on the [http://www.openscad.org/ homepage of OpenSCAD].
