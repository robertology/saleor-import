from abc import ABC, abstractmethod


class ImportType(ABC):
    def __init__(self, importer, data):
        self.importer = importer
        self.data = data
        super().__init__()

    @abstractmethod
    def get_import_data():
        pass


class Category(ImportType):
    def get_import_data(self):
        # TODO
        pass
