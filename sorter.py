def sort_dict(dict):
    sorted_dict = {}
    if dict:
        for keys, values in dict.items():
            for i in range(len(dict)):
                if keys == str(i):
                    sorted_dict[i] = values
        return sort_dict


