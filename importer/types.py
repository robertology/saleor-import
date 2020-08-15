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

    @staticmethod
    def factory(type, *data):
        if type == "category": return Category(*data)
        if type == "attribute": return Attribute(*data)

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
            value = val if isinstance(val, bool) else None
            value = input_data.get(key, value)

            if value is not None:
                if isinstance(val, dict):
                    value = self._get_data_from_definition(val, value)

                if isinstance(val, bool) and not isinstance(value, bool):
                    value = val

                if isinstance(val, list):
                    if isinstance(value, list):
                        value = None
                    else:
                        temp = ()
                        required_type = type(val[0])
                        recurse = isinstance(val[0], dict)
                        for v in value:
                            if isinstance(v, required_type):
                                if recurse:
                                    v = self._get_data_from_definition(val[0], v)
                                if v:
                                    temp.push = v

                        value = temp

                if val and isinstance(val, str):
                    if value not in val.split("|"):
                        value = None

                if value is not None:
                    data[key] = value

        return data


class Attribute(ImportType):
    @property
    def mutation_name(self):
        return "attributeCreate"

    @property
    def _mutation_return_query(self):
        return "attribute{ id, slug }"

    @property
    def _mutation_input_definition(self):
        return {
            "slug": "",
            "name": "",
            "inputType": "DROPDOWN|MULTISELECT",
            "values": ({"name": ""}),
            "valueRequired": True,
            "isVariantOnly": False,
            "visibleInStorefront": True,
            "filterableInStorefront": True,
            "filterableInDashboard": True,
            "availableInGrid": True,
            "storefrontSearchPosition": 0,
        }

    @property
    def _mutation_input_data(self):
        return {"input": super()._get_import_data()}

    @property
    def _mutation_input_types(self):
        return {
            "input": "AttributeCreateInput!",
        }


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


class Product(ImportType):
    @property
    def mutation_name(self):
        return "productCreate"

    @property
    def _mutation_return_query(self):
        return "product{ id, slug }"

    @property
    def _mutation_input_definition(self):
        return {
            "slug": "",
            "name": "",
            "sku": "",
            "description": "",
            "category": "",
            "productType": "",
            "basePrice": 0.0,
            "stocks": [{"warehouse": "", "quantity": 0}],
            "attributes": [{"slug": "", "values": [""]}],
            "publicationDate": "",
            "chargeTaxes": False,
            "isPublished": False,
            "trackInventory": False,
            "seo": {"title": "", "description": ""},
            "taxCode": "",
            "weight": "",
        }

    @property
    def _mutation_input_data(self):
        data = super()._get_import_data()

        if "attributes" in data:
            temp = []
            for v in data["attributes"]:
                v = self.importer.getAttribute(v)
                if v:
                    temp.append(v)
            if temp:
                data["attributes"] = temp

        if "category" in data:
            obj = self.importer.getCategory(data.get("category"))
            if obj:
                data["category"] = obj["id"]

        if "productType" in data:
            obj = self.importer.getProductType(data.get("productType"))
            if obj:
                data["productType"] = obj["id"]

        if "stocks" in data:
            temp = []
            for v in data["stocks"]:
                warehouse = self.importer.getWarehouse(v["warehouse"])
                if warehouse:
                    v["warehouse"] = warehouse["id"]
                    temp.append(v)
            if temp:
                data["stocks"] = temp

        return {"input": data}

    @property
    def _mutation_input_types(self):
        return {
            "input": "ProductCreateInput!",
        }


class ProductType(ImportType):
    @property
    def mutation_name(self):
        return "productTypeCreate"

    @property
    def _mutation_return_query(self):
        return "productType{ id, slug }"

    @property
    def _mutation_input_definition(self):
        return {
            "slug": "",
            "name": "",
            "productAttributes": [""],
            "variantAttributes": [""],
            "hasVariants": False,
            "isShippingRequired": False,
            "isDigital": False,
            "taxCode": "",
            "weight": "",
        }

    @property
    def _mutation_input_data(self):
        data = super()._get_import_data()

        if "productAttributes" in data:
            temp = []
            for v in data["productAttributes"]:
                v = self.importer.getAttribute(v)
                if v:
                    temp.append(v)

        if "variantAttributes" in data:
            temp = []
            for v in data["variantAttributes"]:
                v = self.importer.getAttribute(v)
                if v:
                    temp.append(v)

        return {"input": data}

    @property
    def _mutation_input_types(self):
        return {
            "input": "ProductTypeInput!",
        }


class Warehouse(ImportType):
    @property
    def mutation_name(self):
        return "createWarehouse"

    @property
    def _mutation_return_query(self):
        return "warehouse{ id, slug }"

    @property
    def _mutation_input_definition(self):
        return {
            "slug": "",
            "name": "",
            "companyName": "",
            "email": "",
            "address": {
                "streetAddress1": "",
                "streetAddress2": "",
                "city": "",
                "cityArea": "",
                "postalCode": "",
                "country": "",
                "countryArea": "",
                "phone": "",
            },
            "shippingZones": [""],
        }

    @property
    def _mutation_input_data(self):
        data = super()._get_import_data()
        return {"input": data}

    @property
    def _mutation_input_types(self):
        return {
            "input": "WarehouseCreateInput!",
        }
