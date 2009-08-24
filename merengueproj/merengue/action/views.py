from merengue.action import get_action


def dispatcher(request, name):
    action_item = get_action(name=name)
    item_class = action_item.get_registry_item_class()
    return item_class.get_response(request)
