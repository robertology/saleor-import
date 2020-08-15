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
