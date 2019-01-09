
* Big scary example from https://help.sap.com/doc/abapdocu_750_index_htm/7.50/en-US/abapread_table.htm

* ...this will certainly not run in Abippity yet.


DATA itab TYPE STANDARD TABLE OF i 
          WITH EMPTY KEY 
          WITH NON-UNIQUE SORTED KEY sort_key COMPONENTS table_line. 

itab = VALUE #( ( 2 ) ( 5 ) ( 1 ) ( 3 ) ( 4 ) ). 

DATA(output) = ``. 
DATA(idx) = lines( itab ). 
WHILE idx > 0. 
  READ TABLE itab INDEX idx USING KEY sort_key 
             ASSIGNING FIELD-SYMBOL(<fs>). 
  idx = idx  - 1. 
  CHECK <fs> > 2. 
  output = output && <fs> && ` `. 
ENDWHILE. 

cl_demo_output=>display( output ). 

