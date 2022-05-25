class Database:
    
    def __init__(self) -> None:
        self.prepared_cache = {}
        self.ready_cache = {}

    def create_cache_for(self, user):
        self.prepared_cache[user.id] = []
        self.ready_cache[user.id] = {"state": False, "name": ""}

    def clear_cache(self, user):
        if self.is_user_prepared(user):
            del self.prepared_cache[user.id]

    def is_user_prepared(self, user):
        return self.prepared_cache.get(user.id) != None

    def prepare(self, user, message):
        self.prepared_cache[user.id].append(message)

    def get_prepared_cache(self, user):
        if self.is_user_prepared(user):
            return self.prepared_cache[user.id]
        return None

    def get_ready_state(self, user):
        if self.is_user_prepared(user):
            return self.ready_cache[user.id]["state"]
        return False
    
    def set_ready_state(self, user, state):
        self.ready_cache[user.id]["state"] = state

    def get_name(self, user):
        if self.is_user_prepared(user):
            return self.ready_cache[user.id]["name"]
        return ""
    
    def set_name(self, user, name):
        self.ready_cache[user.id]["name"] = name
    