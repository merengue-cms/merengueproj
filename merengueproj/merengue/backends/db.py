from django.contrib.sessions.backends.db import SessionStore as SessionStoreDjango


class SessionStore(SessionStoreDjango):
    MESSAGES_NAME = '_messages'

    def get_messages(self):
        return self.get(self.MESSAGES_NAME, [])

    def get_and_delete_messages(self):
        return self.pop(self.MESSAGES_NAME, [])

    def create_message(self, message):
        messages = self.get(self.MESSAGES_NAME, [])
        self[self.MESSAGES_NAME] = messages
        messages.append(message)
        self.modified = True
