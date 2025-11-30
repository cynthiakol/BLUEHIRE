from django.db.backends.mysql.base import DatabaseWrapper as BaseMySQLWrapper

class DatabaseWrapper(BaseMySQLWrapper):
    @property
    def data_types(self):
        types = super().data_types.copy()
        types['CharField'] = 'varchar(190)'
        types['EmailField'] = 'varchar(190)'
        return types
