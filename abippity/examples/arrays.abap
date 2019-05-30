
* Fancy modern ABAP from https://blogs.sap.com/2016/05/11/logging-expressions/
* Looks like the canonical way to make an array is: standard table with empty key.

* We definitely don't support the fancy list comprehensions yet.


TYPES itab TYPE STANDARD TABLE OF i WITH EMPTY KEY.

DATA(itab) =
  VALUE itab(
    FOR i = 1 UNTIL i > 3
    FOR j = 1 UNTIL j > 3
      ( i * 10 + j ) ).
