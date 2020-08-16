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
    @abstractmethod
    def search_query_name(self):
        pass

    @property
    @abstractmethod
    def _search_query_input_name(self):
        pass

    @property
    def query_name(self):
        return self._mutation_return_query.split('{', 1)[0]

    @staticmethod
    def factory(type, *data):
        if type == "attribute": return Attribute(*data)
        if type == "category": return Category(*data)
        if type == "product": return Product(*data)
        if type == "productType": return ProductType(*data)
        if type == "productVariant": return ProductVariant(*data)
        if type == "warehouse": return Warehouse(*data)

    def get_search_query(self, key, identity):
        variables = {"filter": {"search": identity}}
        query = "query fetch($filter: {}) {{ {} (filter: $filter, first: 99) {{ edges {{ node {{ id, {} }} }} }} }}".format(self._search_query_input_name, self.search_query_name, key)

        return (query, variables)

    async def get_import_query(self):
        data = await self._mutation_input_data
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
    def search_query_name(self):
        return "attributes"

    @property
    def _search_query_input_name(self):
        return "AttributeFilterInput"

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
    async def _mutation_input_data(self):
        return {"input": super()._get_import_data()}

    @property
    def _mutation_input_types(self):
        return {
            "input": "AttributeCreateInput!",
        }


class Category(ImportType):
    @property
    def search_query_name(self):
        return "categories"

    @property
    def _search_query_input_name(self):
        return "CategoryFilterInput"

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
    async def _mutation_input_data(self):
        data = {"input": super()._get_import_data()}

        if self.data.get("parent"):
            parent = await self.importer.getItemBySlug("category", self.data.get("parent"))
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
    def search_query_name(self):
        return "products"

    @property
    def _search_query_input_name(self):
        return "ProductFilterInput"

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
    async def _mutation_input_data(self):
        data = super()._get_import_data()

        if "attributes" in data:
            temp = []
            for v in data["attributes"]:
                v = await self.importer.getItemBySlug("attribute", v)
                if v:
                    temp.append(v["id"])
            if temp:
                data["attributes"] = temp

        if "category" in data:
            obj = await self.importer.getItemBySlug("category", data.get("category"))
            if obj:
                data["category"] = obj["id"]

        if "productType" in data:
            obj = await self.importer.getItemBySlug("productType", data.get("productType"))
            if obj:
                data["productType"] = obj["id"]

        if "stocks" in data:
            temp = []
            for v in data["stocks"]:
                warehouse = await self.importer.getItemBySlug("warehouse", v["warehouse"])
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
    def search_query_name(self):
        return "productTypes"

    @property
    def _search_query_input_name(self):
        return "ProductTypeFilterInput"

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
    async def _mutation_input_data(self):
        data = super()._get_import_data()

        if "productAttributes" in data:
            temp = []
            for v in data["productAttributes"]:
                v = await self.importer.getItemBySlug("attribute", v)
                if v:
                    temp.append(v.get("id"))
            data["productAttributes"] = temp

        if "variantAttributes" in data:
            temp = []
            for v in data["variantAttributes"]:
                v = await self.importer.getItemBySlug("attribute", v)
                if v:
                    temp.append(v.get("id"))
            data["variantAttributes"] = temp

        return {"input": data}

    @property
    def _mutation_input_types(self):
        return {
            "input": "ProductTypeInput!",
        }


class ProductVariant(ImportType):
    @property
    def search_query_name(self):
        return "attributes"

    @property
    def _search_query_input_name(self):
        return ""

    @property
    def mutation_name(self):
        return "productVariantCreate"

    @property
    def _mutation_return_query(self):
        return "productVariant{ id, sku }"

    @property
    def _mutation_input_definition(self):
        return {
            "sku": "",
            "product": "",
            "costPrice": 0.0,
            "priceOverride": 0.0,
            "stocks": [{"warehouse": "", "quantity": 0}],
            "attributes": [{"slug": "", "values": [""]}],
            "trackInventory": False,
            "weight": "",
        }

    @property
    async def _mutation_input_data(self):
        data = super()._get_import_data()

        if "attributes" in data:
            temp = []
            for v in data["attributes"]:
                attr = await self.importer.getItemBySlug("attribute", v)
                if attr:
                    temp.append({"id": attr.get("id"), "values": v.get("values", [])})
            if temp:
                data["attributes"] = temp

        if "stocks" in data:
            temp = []
            for v in data["stocks"]:
                warehouse = await self.importer.getItemBySlug("warehouse", v["warehouse"])
                if warehouse:
                    v["warehouse"] = warehouse["id"]
                    temp.append(v)
            if temp:
                data["stocks"] = temp

        return {"input": data}

    @property
    def _mutation_input_types(self):
        return {
            "input": "ProductVariantCreateInput!",
        }


class Warehouse(ImportType):
    @property
    def search_query_name(self):
        return "warehouses"

    @property
    def _search_query_input_name(self):
        return "WarehouseFilterInput"

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
    async def _mutation_input_data(self):
        data = super()._get_import_data()
        return {"input": data}

    @property
    def _mutation_input_types(self):
        return {
            "input": "WarehouseCreateInput!",
        }
