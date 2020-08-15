import unittest

from .context import importer
from importer import types


class TestAttribute(unittest.TestCase):

    @staticmethod
    def _new_obj(*args):
        data = {}
        if args:
            data = args[0]

        return types.Attribute(importer.Importer(importer.Api("", ""), ""), data)

    def test_mutation_name(self):
        self.assertEqual(self._new_obj().mutation_name, 'attributeCreate')

    def test_query_name(self):
        self.assertEqual(self._new_obj().query_name, 'attribute')

    def test_get_import_query(self):
        data = {"slug": "color", "name": "Color", "filterableInDashboard": False, "inputType": "MULTISELECT"}

        query = "mutation attributeCreate($input: AttributeCreateInput!) { attributeCreate(input: $input) { attribute{ id, slug } } }"
        variables = {
            "availableInGrid": True,
            "filterableInStorefront": True,
            "isVariantOnly": False,
            "valueRequired": True,
            "visibleInStorefront": True,
        }
        variables.update(data)
        variables = {"input": variables}

        self.assertEqual(self._new_obj(data).get_import_query(), (query, variables))


class TestCategory(unittest.TestCase):

    @staticmethod
    def _new_obj(*args):
        data = {}
        if args:
            data = args[0]

        return types.Category(importer.Importer(importer.Api("", ""), ""), data)

    def test_mutation_name(self):
        self.assertEqual(self._new_obj().mutation_name, 'categoryCreate')

    def test_query_name(self):
        self.assertEqual(self._new_obj().query_name, 'category')

    def test_get_import_query(self):
        data = {"slug": "happiness", "name": "Happiness"}

        query = "mutation categoryCreate($input: CategoryInput!) { categoryCreate(input: $input) { category{ id, slug } } }"
        variables = {"input": data}
        self.assertEqual(self._new_obj(data).get_import_query(), (query, variables))


class TestProduct(unittest.TestCase):

    @staticmethod
    def _new_obj(*args):
        data = {}
        if args:
            data = args[0]

        return types.Product(importer.Importer(importer.Api("", ""), ""), data)

    def test_mutation_name(self):
        self.assertEqual(self._new_obj().mutation_name, 'productCreate')

    def test_query_name(self):
        self.assertEqual(self._new_obj().query_name, 'product')

    def test_get_import_query(self):
        data = {"slug": "robot", "name": "Robot", "chargeTaxes": True, "basePrice": 5.99}

        query = "mutation productCreate($input: ProductCreateInput!) { productCreate(input: $input) { product{ id, slug } } }"
        variables = {"isPublished": False, "trackInventory": False}
        variables.update(data)
        variables = {"input": variables}

        self.assertEqual(self._new_obj(data).get_import_query(), (query, variables))


class TestProductType(unittest.TestCase):

    @staticmethod
    def _new_obj(*args):
        data = {}
        if args:
            data = args[0]

        return types.ProductType(importer.Importer(importer.Api("", ""), ""), data)

    def test_mutation_name(self):
        self.assertEqual(self._new_obj().mutation_name, 'productTypeCreate')

    def test_query_name(self):
        self.assertEqual(self._new_obj().query_name, 'productType')

    def test_get_import_query(self):
        data = {"slug": "machine", "name": "Machine", "hasVariants": True}

        query = "mutation productTypeCreate($input: ProductTypeInput!) { productTypeCreate(input: $input) { productType{ id, slug } } }"
        variables = {"isDigital": False, "isShippingRequired": False}
        variables.update(data)
        variables = {"input": variables}

        self.assertEqual(self._new_obj(data).get_import_query(), (query, variables))


class TestWarehouse(unittest.TestCase):

    @staticmethod
    def _new_obj(*args):
        data = {}
        if args:
            data = args[0]

        return types.Warehouse(importer.Importer(importer.Api("", ""), ""), data)

    def test_mutation_name(self):
        self.assertEqual(self._new_obj().mutation_name, 'createWarehouse')

    def test_query_name(self):
        self.assertEqual(self._new_obj().query_name, 'warehouse')

    def test_get_import_query(self):
        data = {"slug": "main", "name": "Main Building", "companyName": "Big Supplier"}

        query = "mutation createWarehouse($input: WarehouseCreateInput!) { createWarehouse(input: $input) { warehouse{ id, slug } } }"
        variables = {"input": data}

        self.assertEqual(self._new_obj(data).get_import_query(), (query, variables))
