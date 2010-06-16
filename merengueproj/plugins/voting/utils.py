from plugins.voting.models import Vote


def get_can_vote(content, user):
    try:
        vote = content.vote_set.get()
    except Vote.DoesNotExist:
        vote = None
    return (not vote and not user.is_anonymous()) or (vote and not user.is_anonymous() and not user in vote.users.all())
