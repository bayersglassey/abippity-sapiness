report zhello defining database lolo.

write 'Hello' quickinfo 'Moused over!'.
skip.
write: 'LA', 'LA' NO-GAP, 'LA', 'LAAA!'.
uline.

DATA: W_NUR(10) TYPE N.
      MOVE 50 TO W_NUR.
      WRITE W_NUR NO-ZERO.

DATA text_line TYPE C LENGTH 40.
text_line = 'A Chapter on Data Types'.
Write text_line.

DATA text_string TYPE STRING.
text_string = 'A Program in ABAP'.
Write / text_string.

DATA text_string2 LIKE text_string.
text_string2 = 'Prooooogram'.
Write / text_string2.

ULINE.
