names = ['rifat', 'fahad', 'zulker']

def check_list(name_list):
    try:
        return name_list[3]
    # except IndexError:
    #     return 'index error'
    except IndexError:
        raise IndexError('hello rifat, index out of range')

print(check_list(names))