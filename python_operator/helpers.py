
def convert_list_tomap(containers):
    cont_map = dict()
    for cont in containers:
        cont_map[cont["name"]] = cont
    return cont_map
