from block.models import RegisteredBlock


def get_block(name):
    return RegisteredBlock.objects.get(name=name)
