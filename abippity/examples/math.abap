REPORT ZMATH.

data sum type i.

*sum = 0.
*sum = sum + : 1, 2, 3, 4.

move 0 to sum.
add: 1 to sum, 2 to sum, 3 to sum, 4 to sum.

write: /    'sum: ', sum.
assert sum eq 10.

data x type i value 1.
write: / 'x =', x.
add 2 to x.
write: / '+ 2 -> ', x.
multiply x by 10.
write: / '* 10 -> ', x.
divide x by 5.
write: / '/ 5 -> ', x.
subtract 3 from x.
write: / '- 3 -> ', x.

assert 1 eq 1 and ( 0 eq 1 or 2 ne 3 )
    and 3 le 4
    and not 4 <= 1
    and not ( ( ( 4 < 1 ) ) ).
