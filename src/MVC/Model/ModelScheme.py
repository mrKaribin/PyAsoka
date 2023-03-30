from PyAsoka.src.Database.DatabaseProfile import DatabaseProfile


class ModelScheme:
    def __init__(self, profile: DatabaseProfile, table_name):
        self.profile = profile
        self.database = profile.getDriver()
        self.table = self.database.Table(self.profile, table_name)
        self.fields = {}
        self.simpleFields = {}
        self.references = {}
        self.OTM_refs = {}
        self.MTM_refs = {}

