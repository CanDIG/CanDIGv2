class IndexableMixin:
    @property
    def index_id(self):
        return f"{self.__class__.__name__}|{self.__str__()}"
