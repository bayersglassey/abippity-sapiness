report zdata.


data: begin of point,
    x type i,
    y type i,
    begin of address,
        street type c length 10,
        city(20) type c,
    end of address,
end of point.

move: 3 to point-x, 4 to point-y.
write: / 'x:', point-x, 'y:', point-y.

if point-x lt point-y.
    write / 'x < y'.
endif.


data point2 like point.
move: 1 to point2-x, 2 to point2-y.
write: / 'p2:', 'x:', point2-x, 'y:', point2-y.
move: point-x to point2-x, point-y to point2-y.
write: / 'p2:', 'x:', point2-x, 'y:', point2-y.

