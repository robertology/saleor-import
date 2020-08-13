from abc import ABC, abstractmethod


class ImportType(ABC):
    def __init__(self, importer, data):
        self.importer = importer
        self.data = data
        super().__init__()

    @property
    @abstractmethod
    def mutation_name(self):
        pass

    @property
    @abstractmethod
    def _mutation_return_query(self):
        pass

    @property
    @abstractmethod
    def _mutation_input_definition(self):
        pass

    @property
    @abstractmethod
    def _mutation_input_types(self):
        pass

    @property
    def query_name(self):
        return self._mutation_return_query.split('{', 1)[0]

    def get_import_query(self):
        data = self._mutation_input_data
        input_types = {name: type for name, type in self._mutation_input_types.items() if name in data}

        mutation_name = self.mutation_name
        if input_types:
            inputs = []
            for (name, type) in input_types.items():
                inputs.append("${}: {}".format(name, type))
            mutation_name = mutation_name + "({})".format(','.join(inputs))

        inputs = []
        for name in input_types:
            inputs.append("{}: ${}".format(name, name))

        return (
            "mutation {} {{ {}({}) {{ {} }} }}".format(
                mutation_name,
                self.mutation_name,
                ",".join(inputs),
                self._mutation_return_query,
            ),
            data
        )

    def _get_import_data(self):
        return self._get_data_from_definition(self._mutation_input_definition, self.data)

    def _get_data_from_definition(self, keys, input_data):
        data = {}

        for key, val in keys.items():
            value = input_data.get(key, None)
            if value is not None:
                if isinstance(val, dict):
                    value = self._get_data_from_definition(val, value)

                data[key] = value

        return data

class Category(ImportType):
    @property
    def mutation_name(self):
        return "categoryCreate"

    @property
    def _mutation_return_query(self):
        return "category{ id, slug }"

    @property
    def _mutation_input_definition(self):
        # TODO: image upload
        return {
            "slug": "",
            "name": "",
            "description": "",
            "seo": {"title": "", "description": ""},
        }

    @property
    def _mutation_input_data(self):
        data = {"input": super()._get_import_data()}

        if self.data.get("parent"):
            parent = self.importer.getCategory(self.data.get("parent"))
            if parent:
                data["parent"] = parent["id"]

        return data

    @property
    def _mutation_input_types(self):
        return {
            "input": "CategoryInput!",
            "parent": "ID",
        }
