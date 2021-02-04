# Cleans up spaces in front and after a string, i.e. turns '       Hello World      '
# into 'Hello World'
def cleanup_spaces(string):
    first_non_space = -1
    last_non_space = 0

    for c_idx in range(len(string)):
        c = string[c_idx]
        if c == ' ':
            continue
        else:
            if first_non_space == -1:
                first_non_space = c_idx
            
            last_non_space = c_idx


    last_non_space += 1

    return string[first_non_space:last_non_space]
