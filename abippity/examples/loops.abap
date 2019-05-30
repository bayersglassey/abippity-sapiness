report zloops.

data:
    x type i value 0,
    y type i value 0.

while x < 3.
    write: / 'x: ', x.

    if x = 1.
        add 1 to x.
        continue.
    endif.

    move 0 to y.
    do 5 times.
        check y < 4.
        write: / '  y: ', y.
        add 1 to y.
    enddo.

    add 1 to x.
endwhile.

