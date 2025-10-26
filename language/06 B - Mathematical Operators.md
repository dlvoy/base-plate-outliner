> **Note:** This section is incomplete.

## Scalar arithmetic operators
The scalar arithmetic operators take numbers as operands and produce a new number.

{| class="wikitable"
|&#43;
|add
|-
|&#45;
|subtract
|-
|*
|multiply
|-
|/
|divide
|-
|%
|modulo
|-
|^
|exponent > **Requires:** 2021.01
|}

The `-` can also be used as prefix operator to negate a number.

Prior to version 2021.01, the builtin mathematical function `[pow()](OpenSCAD User Manual/Mathematical Functions#pow)` is used instead of the `^` exponent operator.
   **Example:**
```javascript

a=[ for(i=[0:10]) i%2 ];
echo(a);//ECHO: [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]

```
A number modulo 2 is zero if even and one if odd.

## Binary arithmetic
> **Requires:** Development snapshot

{| class="wikitable"
|&#124;
|OR
|-
|&amp;
|AND
|-
|<<
|Left shift
|-
|>>
|Right shift (sign preserving)
|-
|~
|Unary NOT
|}
Numbers are converted to 64-bit signed integers for binary arithmetic, and then converted back.  Note that OpenSCAD numbers have 53 bits of precision; binary arithmetic exceeding 2^53 will be imprecise.

## Relational operators
Relational operators produce a boolean result from two operands.

{| class="wikitable"
|<
|less than
|-
|<=
|less or equal
|-
|==
|equal
|-
|!=
|not equal
|-
|>=
|greater or equal
|-
|>
|greater than
|}

If both operands are simple numbers, the meaning is self-evident.  

If both operands are strings, alphabetical sorting determines 
equality and order.  E.g., "ab" > "aa" > "a".  

If both operands are Booleans, *true* > *false*.  In an inequality comparison between a Boolean 
and a number *true* is treated as 1 and *false* is treated as 0.  Other inequality tests involving Booleans 
return false.    

If both operands are vectors, an equality test returns *true* when the vectors are identical and *false* otherwise.  
Inequality tests involving one or two vectors always return *false*, so for example [1] < [2] is *false*.  

Dissimilar types always test as unequal with '==' and '!='.   
Inequality comparisons between dissimilar types, except for Boolean and numbers as noted above, always result in *false*.  
Note that [1] and 1 are different types so [1] == 1 is false.  

`undef` doesn't equal anything but *undef*.  Inequality comparisons involving *undef* result in *false*.

`nan` doesn't equal anything (not even itself) and inequality tests all produce *false*.  See [Numbers](OpenSCAD_User_Manual/General#Numbers).

## Logical operators
All logical operators take Booleans as operands and produce a Boolean.  
Non-Boolean quantities are converted to Booleans before the operator is evaluated. 

{| class="wikitable"
|&&
| logical AND
|-
|&#124;&#124;
| logical OR
|-
|!
| logical unary NOT
|-
|}

Since `[false]` is `true`, `false || [false]` is also `true`.

Logical operators deal with vectors differently than relational operators:

`[1, 1] > [0, 2]` is `false`, but 

`[false, false] && [false, false]` is `true`.

## Conditional operator
The <tt>?:</tt> operator can be used to conditionally evaluate one or another expression.
It works like the <tt>?:</tt> operator from the family of C-like programming languages.

{| class="wikitable"
|&nbsp;?&nbsp;:
|Conditional operator
|}
{| width="75%"
|**Usage Example:**
|-
|
```javascript

a=1;
b=2;
c= a==b ? 4 : 5;

```
If a equals b, then c is set to 4, else c is set to 5.

The part "a==b" must be something that evaluates to a boolean value.
|}

## Vector-number operators
The vector-number operators take a vector and a number as operands and produce a new vector.
{| class="wikitable"
|*
|multiply all vector elements by number
|-
|/
|divide all vector elements by number
|}
   **Example**
 L = [1, [2, [3, "a"] ] ];
 echo(5*L);
 // ECHO: [5, [10, [15, undef]]]

## Vector operators
The vector operators take vectors as operands and produce a new vector.
{| class="wikitable"
|&#43;
|add element-wise
|-
|&#45;
|subtract element-wise
|}

The `-` can also be used as prefix operator to element-wise negate a vector.
   **Example**
 L1 = [1, [2, [3, "a"] ] ];
 L2 = [1, [2, 3] ];
 echo(L1+L1); // ECHO: [2, [4, [6, undef]]]
 echo(L1+L2); // ECHO: [2, [4, undef]]
Using + or - with vector operands of different sizes produce a result vector that is the size of the smaller vector.

## Vector dot-product operator
If both operands of multiplication are simple vectors, the result is a number according to the linear algebra rule for [dot product](https://en.wikipedia.org/wiki/Dot_product).  
`c = u*v;` results in <math>c = \sum u_iv_i</math>.  If the operands' sizes don't match, the result is `undef`.

## Matrix multiplication
If one or both operands of multiplication are matrices, the result is a simple vector or matrix according to the linear algebra rules for [matrix product](https://en.wikipedia.org/wiki/Matrix_multiplication#Matrix_product_.28two_matrices.29).  
In the following, {{math|A, B, C...}} are matrices, {{math|u, v, w...}} are vectors.  Subscripts {{math|i, j}} denote element indices.  

For {{math|A}} a matrix of size {{math|n × m}} and 
{{math|B}} a matrix of size {{math|m × p}}, their product
`C = A*B;` is a matrix of size {{math|n × p}} with elements

<math>C_{ij} = \sum_{k=0}^{m-1} A_{ik}B_{kj}</math>.

`C = B*A;` results in `undef` unless {{math|n}} = {{math|p}}.

For {{math|A}} a matrix of size {{math|n × m}} and 
{{math|v}} a vector of size {{math|m}}, their product
`u = A*v;` is a vector of size {{math|n}} with elements

<math>u_{i} = \sum_{k=0}^{m-1} A_{ik}v_{k}</math>. 

In linear algebra, this 
is the [product of a matrix and a column vector](https://en.wikipedia.org/wiki/Matrix_multiplication#Square_matrix_and_column_vector).

For {{math|v}} a vector of size {{math|n}} and 
{{math|A}} a matrix of size {{math|n × m}}, their product
`u = v*A;` is a vector of size {{math|m}} with elements

<math>u_{j} = \sum_{k=0}^{n-1} v_{k}A_{kj}</math>. 

In linear algebra, this 
is the product of a row vector and a matrix.

Matrix multiplication is not commutative: <math>AB \neq BA</math>,  <math>Av \neq vA</math>.
