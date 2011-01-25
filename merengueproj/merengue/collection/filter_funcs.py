def exact_func(value, compare):
    return value == compare


def iexact_func(value, compare):
    return value.lower() == compare.lower()


def contains_func(value, compare):
    return compare in value


def icontains_func(value, compare):
    return compare.lower() in value.lower()


def startswith_func(value, compare):
    return value.startswith(compare)


def istartswith_func(value, compare):
    return value.lower().startswith(compare.lower())


def endswith_func(value, compare):
    return value.endswith(compare)


def iendswith_func(value, compare):
    return value.lower().endswith(compare.lower())


def lt_func(value, compare):
    try:
        return int(value) < int(compare)
    except ValueError:
        return value < compare


def lte_func(value, compare):
    try:
        return int(value) <= int(compare)
    except ValueError:
        return value < compare


def gt_func(value, compare):
    try:
        return int(value) > int(compare)
    except ValueError:
        return value < compare


def gte_func(value, compare):
    try:
        return int(value) >= int(compare)
    except ValueError:
        return value < compare


def in_func(value, compare):
    compare_list = compare.split(',')
    return value in compare_list


def isnull_func(value, compare):
    if value == None or value == '':
        return compare
    return not compare
