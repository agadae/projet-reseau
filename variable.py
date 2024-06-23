stri=''

def transform_string(stri_var):#return tuple ("index", position in tuple)
    position = (0,0)
    entity = ''

    string = stri_var.split(',')

    if len(string)>2:
        entity = string[0]
        print(f"the entity is {entity}")
        position = (int(string[1].translate({ord(i): None for i in '[]()'})),int(string[2].translate({ord(i): None for i in '[]()'})))
        str_test = ''
    return (entity,position)


