name = 'rifat'

def check_string(val):
    try:
        return name[5]
    except SyntaxError:
        return 'syntax error'
    except IndexError:
        return 'index error'

print(check_string(name))