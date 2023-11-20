
class JSONException(Exception):
    def __init__(self, id, detail):
        self.id = id
        self.detail = detail
