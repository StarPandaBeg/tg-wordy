class User:
    def __init__(self, id, name, first_name, last_name):
        self.id = id
        self.username = name
        self.first_name = first_name
        self.last_name = last_name

    @staticmethod
    def from_message(message):
        user = message.from_user
        return User(user.id, user.username, user.first_name, user.last_name)

class Message:
    def __init__(self, message):
        self.raw = message
        self.user = User.from_message(message)
        self.text = message.text
        self.chat_id = message.chat.id
        self.message_id = message.message_id
        self.media_group_id = message.media_group_id
        self.photo = self._get_photo(message)
        self.photo_unique_id = self._get_photo_unique(message)

    def _get_photo(self, message):
        if message.photo != None:
            return message.photo[len(message.photo)-1].file_id

    def _get_photo_unique(self, message):
        if message.photo != None:
            return message.photo[len(message.photo)-1].file_unique_id
