__FORCETOC__ {{TOC right}}

> **Note:** This section is incomplete.
## Trigonometric functions

The trig functions use the C Language mathematics functions, which are based in turn on Binary Floating Point mathematics, which use approximations of Real Numbers during calculation. OpenSCAD's math functions use the C++ 'double' type, inside Value.h/Value.cc, 

A good resource for the specifics of the C library math functions, such as valid inputs/output ranges, can be found at the Open Group website [http://pubs.opengroup.org/onlinepubs/009695399/basedefs/math.h.html math.h] & [http://pubs.opengroup.org/onlinepubs/009695399/functions/acos.html acos]

### cos
Mathematical **cosine** function of degrees. See [Cosine](https://en.wikipedia.org/wiki/Cosine#Sine.2C_cosine_and_tangent)

**Parameters**

; &lt;degrees&gt; : Decimal.  Angle in degrees. 

{| width="75%"
|**Usage example:**
|-
|
```javascript

 for(i=[0:36])
    translate([i*10,0,0])
       cylinder(r=5,h=cos(i*10)*50+60);

```
|![OpenSCAD_Cos_Function.png](images/OpenSCAD_Cos_Function.png)
|}

### sin
Mathematical **sine** function. See [Sine](https://en.wikipedia.org/wiki/Trigonometric_functions#Sine.2C_cosine_and_tangent)

**Parameters**

; &lt;degrees&gt; : Decimal. Angle in degrees. 

{| width="75%"
|**Usage example 1:**
|-
|
```javascript

 for (i = [0:5]) {
  echo(360*i/6, sin(360*i/6)*80, cos(360*i/6)*80);
   translate([sin(360*i/6)*80, cos(360*i/6)*80, 0 ])
    cylinder(h = 200, r=10);
 }

```
|
|}

{| width="75%"
|**Usage example 2:**
|-
|
```javascript

 for(i=[0:36])
    translate([i*10,0,0])
       cylinder(r=5,h=sin(i*10)*50+60);

```
|![OpenSCAD_Sin_Function.png](images/OpenSCAD_Sin_Function.png)
|}

### tan
Mathematical **tangent** function. See [Tangent](https://en.wikipedia.org/wiki/Trigonometric_functions#Sine.2C_cosine_and_tangent)

**Parameters**

; &lt;degrees&gt; : Decimal.  Angle in degrees. 

 {| width="75%"
|**Usage example:**
|-
|
```javascript

 for (i = [0:5]) {
  echo(360*i/6, tan(360*i/6)*80);
   translate([tan(360*i/6)*80, 0, 0 ])
    cylinder(h = 200, r=10);
 }

```
|
|}

### acos
Mathematical **arccosine**, or **inverse cosine**, expressed in degrees. See: [Inverse trigonometric functions](https://en.wikipedia.org/wiki/Inverse_trigonometric_functions)

### asin
Mathematical **arcsine**, or **inverse sine**, expressed in degrees. See: [Inverse trigonometric functions](https://en.wikipedia.org/wiki/Inverse_trigonometric_functions)

### atan
Mathematical **arctangent**, or **inverse tangent**, function. Returns the principal value of the arc tangent of x, expressed in degrees. `atan` cannot distinguish between y/x and -y/-x and returns angles from -90 to +90. See: [atan2](https://en.wikipedia.org/wiki/Atan2) and also [Inverse trigonometric functions](https://en.wikipedia.org/wiki/Inverse_trigonometric_functions)

### atan2
Mathematical **two-argument atan** function atan2(y,x) that spans the full 360 degrees.  This function returns the full angle between the x axis and the vector(x,y) expressed in degrees, in the range <math>-180 < angle \le 180</math>.

**Usage examples:**
 atan2(5.0,-5.0);     //result: 135 degrees. atan() would give -45
 atan2(y,x);          //angle between (1,0) and (x,y) = angle around z-axis

## Other Mathematical Functions
### abs
Mathematical **absolute value** function. Returns the positive value of a signed decimal number.

**Usage examples:**
 abs(-5.0);  returns 5.0
 abs(0);     returns 0.0
 abs(8.0);   returns 8.0

### ceil
Mathematical **ceiling** function.  

Returns the next highest integer value by rounding up value if necessary.

See: [Ceil Function](https://en.wikipedia.org/wiki/Ceil_function)

 echo(ceil(4.4),ceil(-4.4));     // produces ECHO: 5, -4

### concat
> **Requires:** 2015.03

Return a new vector that is the result of appending the elements of the supplied vectors.

Where an argument is a vector the elements of the vector are individually appended to the result vector.
Strings are distinct from vectors in this case.

**Usage examples:**
 echo(concat("a","b","c","d","e","f"));          // produces ECHO: ["a", "b", "c", "d", "e", "f"]
 echo(concat(["a","b","c"],["d","e","f"]));      // produces ECHO: ["a", "b", "c", "d", "e", "f"]
 echo(concat(1,2,3,4,5,6));                      // produces ECHO: [1, 2, 3, 4, 5, 6]

Vector of vectors
 echo(concat([ [1],[2] ], [ [3] ]));             // produces ECHO: [[1], [2], [3]]

***Note:*** All vectors passed to the function  lose one nesting level. When adding something like a single element [x, y, z] tuples (which are vectors, too), the tuple needs to be enclosed in a vector (i.e. an extra set of brackets) before the concatenation. in the exmple below, a fourth point is added to the polygon path, which used to resemble a triangle, making it a square now:
 polygon(concat([[0,0],[0,5],[5,5]], <nowiki>[5,0](5,0)</nowiki>));
Contrast with strings

 echo(concat([1,2,3],[4,5,6]));                   // produces ECHO: [1, 2, 3, 4, 5, 6]
 echo(concat("abc","def"));                       // produces ECHO: ["abc", "def"]
 echo(str("abc","def"));                          // produces ECHO: "abcdef"

### cross
Calculates the cross product of two vectors in 3D or 2D space. If both vectors are in the 3D, the result is a vector that is perpendicular to both of the input vectors. If both vectors are in 2D space, their cross product has the form [0,0,z] and the cross function returns just the z value of the cross product:  

*cross([x,y], [u,v]) = x*v - y*u*

Note that this is the determinant of the 2×2 matrix [[x,y],[u,v]].  Using any other types, vectors with lengths different from 2 or 3, or vectors not of the same length produces 'undef'.  

**Usage examples:**
 echo(cross([2, 3, 4], [5, 6, 7]));     // produces ECHO: [-3, 6, -3]
 echo(cross([2, 1, -3], [0, 4, 5]));    // produces ECHO: [17, -10, 8]
 echo(cross([2, 1], [0, 4]));           // produces ECHO: 8
 echo(cross([1, -3], [4, 5]));          // produces ECHO: 17
 echo(cross([2, 1, -3], [4, 5]));       // produces ECHO: undef
 echo(cross([2, 3, 4], "5"));           // produces ECHO: undef

For any two vectors *a* and *b* in 2D or in 3D, the following holds:

*cross(a,b) == -cross(b,a)*

### exp
Mathematical **exp** function. Returns the base-e exponential function of x, which is the number e raised to the power x. See: [Exponent](https://en.wikipedia.org/wiki/Exponent)

 echo(exp(1),exp(ln(3)*4));    // produces ECHO: 2.71828, 81

### floor
Mathematical **floor** function.  floor(x) =  is the largest integer not greater than x 

See: [Floor Function](https://en.wikipedia.org/wiki/Floor_function)

 echo(floor(4.4),floor(-4.4));    // produces ECHO: 4, -5

### ln
Mathematical **natural logarithm**.  See: [Natural logarithm](https://en.wikipedia.org/wiki/Natural_logarithm)

### len
Mathematical **length** function.  Returns the length of an array, a vector or a string parameter.

**Usage examples:**
 str1="abcdef"; len_str1=len(str1);
 echo(str1,len_str1);
 
 a=6; len_a=len(a);
 echo(a,len_a);
 
 array1=[1,2,3,4,5,6,7,8]; len_array1=len(array1);
 echo(array1,len_array1);
 
 array2=[[0,0],[0,1],[1,0],[1,1]]; len_array2=len(array2);
 echo(array2,len_array2);
 
 len_array2_2=len(array2[2]);
 echo(array2[2],len_array2_2);

**Results:**
 WARNING: len() parameter could not be converted in file , line 4
 ECHO: "abcdef", 6
 ECHO: 6, undef
 ECHO: [1, 2, 3, 4, 5, 6, 7, 8], 8
 ECHO: [[0, 0], [0, 1], [1, 0], [1, 1]], 4
 ECHO: [1, 0], 2

This function allows (e.g.) the parsing of an array, a vector or a string.

**Usage examples:**
 str2="4711";
 for (i=[0:len(str2)-1])
 	echo(str("digit ",i+1,"  :  ",str2[i]));

**Results:**
 ECHO: "digit 1  :  4"
 ECHO: "digit 2  :  7"
 ECHO: "digit 3  :  1"
 ECHO: "digit 4  :  1"

Note that the len() function is not defined and raises a warning when a simple variable is passed as the parameter. 

This is useful when handling parameters to a module, similar to how shapes can be defined as a single number, or as an [x,y,z] vector; i.e. cube(5) or cube([5,5,5])

For example

 module doIt(size) {
 	if (len(size) == undef) {
 		// size is a number, use it for x,y & z. (or could be undef)
 		do([size,size,size]);
 	} else { 
 		// size is a vector, (could be a string but that would be stupid)
 		do(size);
 	}
  }
  
 doIt(5);	// equivalent to [5,5,5]
 doIt([5,5,5]);	// similar to cube(5) v's cube([5,5,5])

### let
> **Requires:** 2015.03

Sequential assignment of variables inside an expression. The following expression is evaluated in context of the let assignments and can use the variables. This is mainly useful to make complicated expressions more readable by assigning interim results to variables.

**Parameters**
 let (var1 = value1, var2 = f(var1), var3 = g(var1, var2)) expression

**Usage example:**
 echo(let(a = 135, s = sin(a), c = cos(a)) [ s, c ]); // ECHO: [0.707107, -0.707107]
Let can also be used to create variables in a [Function](OpenSCAD User Manual/User-Defined Functions and Modules#letusedinfunction). [(See also: "Let Statement")](OpenSCAD_User_Manual/Conditional_and_Iterator_Functions#Let_Statement)

### log
Mathematical **logarithm** to the base 10. Example: log(1000) = 3. See: [Logarithm](https://en.wikipedia.org/wiki/Logarithm)

### lookup
Look up value in table, and linearly interpolate if there's no exact match.  The first argument is the value to look up.  The second is the lookup table -- a vector of key-value pairs. 

**Parameters**
; key : A lookup key
; &lt;key,value&gt; array : keys and values

There is a bug in which out-of-range keys return the first value in the list. Newer versions of Openscad should use the top or bottom end of the table as appropriate instead.

**Usage example:** Create a 3D chart made from cylinders of different heights.
{| width="100%"
|-
|```javascript

 function get_cylinder_h(p) = lookup(p, [
 		[ -200, 5 ],
 		[ -50, 20 ],
 		[ -20, 18 ],
 		[ +80, 25 ],
 		[ +150, 2 ]
 	]);
 
 for (i = [-100:5:+100]) {
 	// echo(i, get_cylinder_h(i));
 	translate([ i, 0, -30 ]) cylinder(r1 = 6, r2 = 2, h = get_cylinder_h(i)*3);
 }

```
| ![OpenSCAD_Lookup_Function.png](images/OpenSCAD_Lookup_Function.png)
|}

### max
Returns the maximum of the parameters. If a single vector is given as parameter, returns the maximum element of that vector.

**Parameters**
 max(n,n{,n}...)
 max(vector)

; <n> : Two or more decimals
; <vector> : Single vector of decimals > **Requires:** 2014.06.

**Usage example:**
 max(3.0,5.0)
 max(8.0,3.0,4.0,5.0)
 max([8,3,4,5])

**Results:**
 5
 8
 8

### min
Returns the minimum of the parameters. If a single vector is given as parameter, returns the minimum element of that vector.

**Parameters**
 min(n,n{,n}...)
 min(vector)

; <n> : Two or more decimals
; <vector> : Single vector of decimals > **Requires:** 2014.06.

**Usage example:**
 min(3.0,5.0)
 min(8.0,3.0,4.0,5.0)
 min([8,3,4,5])

**Results:**
 3
 3
 3

### mod
Does not exist as a function; included in this document only for clarity.

The 'modulo' operation exists in OpenSCAD as an operator `%`, and **not** as function. See [modulo operator (%)](OpenSCAD_User_Manual/Mathematical_Operators)

### norm
Returns the [Euclidean norm](https://en.wikipedia.org/wiki/Norm_(mathematics)#Euclidean norm) of a vector:
  <math>\text{norm}(v) = \sqrt{v_0^2 + \cdots + v_{n-1}^2}</math>
This returns the actual numeric length while `len()` returns the number of elements in the vector or array.

**Usage examples:**
 a=[1,2,3,4,5,6];
 b="abcd";
 c=[];
 d="";
 e=[[1,2,3,4],[1,2,3],[1,2],[1]];
 echo(norm(a)); //9.53939
 echo(norm(b)); //undef
 echo(norm(c)); //0
 echo(norm(d)); //undef
 echo(norm(e[0])); //5.47723
 echo(norm(e[1])); //3.74166
 echo(norm(e[2])); //2.23607
 echo(norm(e[3])); //1

**Results:**
 ECHO: 9.53939
 ECHO: undef
 ECHO: 0
 ECHO: undef
 ECHO: 5.47723
 ECHO: 3.74166
 ECHO: 2.23607
 ECHO: 1

### pow
Mathematical **power** function.

As of version 2021.01 you can use the [exponentiation operator `^`](OpenSCAD User Manual/Mathematical Operators) instead.

**Parameters**

; &lt;base&gt; : Decimal.  Base. 
; &lt;exponent&gt; : Decimal.  Exponent. 

**Usage examples:**
 
 for (i = [0:5]) {
  translate([i*25,0,0]) {
    cylinder(h = pow(2,i)*5, r=10);
    echo (i, pow(2,i));
  }
 }

 echo(pow(10,2)); // means 10^2 or 10*10
 // result: ECHO: 100
 
 echo(pow(10,3)); // means 10^3 or 10*10*10
 // result: ECHO: 1000
 
 echo(pow(125,1/3)); // means 125^(0.333...), which calculates the cube root of 125
 // result: ECHO: 5

### rands
Random number generator.
Generates a constant vector of pseudo random numbers, much like an array. The numbers are doubles not integers.
When generating only one number, you still call it with variable[0].

The random numbers generated are a "half open interval"; each is greater than or equal to the minimum, and less than the maximum.

**Parameters**
; min_value : Minimum value of random number range
; max_value : Maximum value of random number range
; value_count : Number of random numbers to return as a vector
; seed_value (optional) : Seed value for random number generator for repeatable results. On versions before late 2015, seed_value gets rounded to the nearest integer.

**Usage examples:**

 // get a single number
 single_rand = rands(0,10,1)[0];
 echo(single_rand);

 // get a vector of 4 numbers
 seed=42;
 random_vect=rands(5,15,4,seed);
 echo( "Random Vector: ",random_vect);
 sphere(r=5);
 for(i=[0:3]) {
  rotate(360*i/4) {
    translate([10+random_vect[i],0,0])
      sphere(r=random_vect[i]/2);
  }
 }
 // ECHO: "Random Vector: ", [8.7454, 12.9654, 14.5071, 6.83435]

 // Get a vector of integers between 1 and 10 inclusive.
 // Note that rands(1,10,...) only spans 9 numbers and so it is difficult to get it to yield equal
 // probabilities for 1..10 inclusive.  We widen the range by 1 so that we have the right number
 // of intervals.
 function irands(minimum, maximum, n) =
     let(floats = rands(minimum, maximum+1, n))
     [ for (f = floats) floor(f) ];
 echo(irands(1, 10, 5));
 // ECHO: [9, 6, 2, 4, 1]

### round
The "round" operator returns the greatest or least integer part, respectively, if the numeric input is positive or negative.

**Usage examples:**
 round(5.4);
 round(5.5);
 round(5.6);
 round(-5.4);
 round(-5.5);
 round(-5.6);

**Results:**
 5
 6
 6
 -5
 -6
 -6

### sign
Mathematical **signum** function. Returns a unit value that extracts the sign of a value see: [Signum function](https://en.wikipedia.org/wiki/Sign_function)

**Parameters**
; &lt;x&gt; : Decimal.  Value to find the sign of.

**Usage examples:**
 sign(-5.0);5
 sign(0);9
 sign(8.0);5

**Results:**
 -1.0
 0.0
 1.0

### sqrt
Mathematical **square root** function.
**Usage example**
 translate([sqrt(100),0,0])sphere(100);

## Infinities and NaNs
How does OpenSCAD deal with inputs like (1/0)? Basically, the behavior is inherited from the language OpenSCAD was written in, the C++ language, and its floating point number types and the associated C math library. This system allows representation of both positive and negative infinity by the special values "Inf" or "-Inf". It also allow representation of creatures like sqrt(-1) or 0/0 as "NaN", an abbreviation for "Not A Number". Explanations can be found on the web, for example the [http://pubs.opengroup.org/onlinepubs/009695399/basedefs/math.h.html Open Group's site on math.h] or [ Wikipedia's page on the IEEE 754 number format](https://en.wikipedia.org/wiki/IEEE_754-1985#Representation_of_non-numbers ). However, OpenSCAD is its own language so it may not exactly match everything that happens in C. For example, OpenSCAD uses degrees instead of radians for trigonometric functions. Another example is that sin() does not throw a "domain error" when the input is 1/0, although it does return NaN. 

Here are some examples of infinite input to OpenSCAD math functions and the resulting output, taken from OpenSCAD's regression test system in late 2015.

{| class="wikitable"
|-
| 0/0: nan || sin(1/0): nan || asin(1/0): nan ||ln(1/0): inf ||round(1/0): inf 
|-
| -0/0: nan ||cos(1/0): nan ||acos(1/0): nan ||ln(-1/0): nan ||round(-1/0): -inf 
|-
| 0/-0: nan ||tan(1/0): nan || atan(1/0): 90 ||log(1/0): inf ||sign(1/0): 1 
|-
| 1/0: inf ||ceil(-1/0): -inf ||atan(-1/0): -90 ||log(-1/0): nan ||sign(-1/0): -1 
|-
| 1/-0: -inf ||ceil(1/0): inf ||atan2(1/0, -1/0): 135 ||max(-1/0, 1/0): inf ||sqrt(1/0): inf 
|-
| -1/0: -inf ||floor(-1/0): -inf ||exp(1/0): inf ||min(-1/0, 1/0): -inf ||sqrt(-1/0): nan 
|-
| -1/-0: inf ||floor(1/0): inf ||exp(-1/0): 0 ||pow(2, 1/0): inf ||pow(2, -1/0): 0 
|}
