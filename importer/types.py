from abc import ABC, abstractmethod


class ImportType(ABC):
    def __init__(self, importer, data):
        self.importer = importer
        self.data = data
        super().__init__()

    @abstractmethod
    def _get_import_data_keys(self):
        pass

    def get_import_data(self):
        return self._get_data_from_keys(self._get_import_data_keys(), self.data)

    def _get_data_from_keys(self, keys, input_data):
        data = {}

        for key, val in keys.items():
            value = input_data.get(key, None)
            if value is not None:
                if isinstance(val, dict):
                    value = self._get_data_from_keys(val, value)

                data[key] = value

        return data

class Category(ImportType):
    def _get_import_data_keys(self):
        # TODO: image upload
        return {
            "slug": "",
            "name": "",
            "description": "",
            "seo": {"title": "", "description": ""},
        }
