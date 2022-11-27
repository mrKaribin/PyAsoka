from PyAsoka.Id import Id


class ADatabaseRequest:
    def __init__(self, receiver_id, profile, request):
        self.id = receiver_id
        self.profile = profile
        self.request = request
        self.reply = None
