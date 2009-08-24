from django.dispatch import Signal

item_registered = Signal(providing_args=["registered_item"])
item_unregistered = Signal(providing_args=[])
