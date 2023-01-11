from PyAsoka.src.Database.DatabaseProfile import DatabaseProfile


class ADatabaseColumn:
    class Constraints:
        pass

    def __init__(self, name, datatype):
        self.name = name
        self.type = datatype

    def column_declaration(self):
        pass


class ADatabaseTable:
    def __init__(self, profile: DatabaseProfile):
        self.profile = profile
