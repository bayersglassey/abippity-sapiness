report zstruct.

data: begin of example_data,
  id       type i,      " identification
  name     type string, " last, first name
  age      type i,      " age in years
  birthday type d,      " birthdate
end of example_data.

example_data-id       = 1.
example_data-name     = 'Some Guy'.
example_data-age      = 26.
example_data-birthday = sy-datum.
write : / 'Hello, ', example_data-name.
write : / 'It''s your birthday!', example_data-birthday.
