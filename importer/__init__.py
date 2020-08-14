import json
import tempfile

from python_graphql_client import GraphqlClient
from .types import ImportType


class Api:
    def __init__(self, url, token):
        self.url = url
        self.token = token

    def import_object(self, obj):
        (query, variables) = obj.get_import_query()
        return self.post(query, variables)

    def post(self, query, variables):
        client = GraphqlClient(
            endpoint=self.url,
            headers={"Authorization": "JWT {}".format(self.token)}
        )
        return client.execute(query=query, variables=variables)


class Importer:
    def __init__(self, api, filepath):
        self.api = api
        self.filepath = filepath
        self.cache = {}

    def process(self):
        self.log_file = tempfile.NamedTemporaryFile(mode="w", delete=False, prefix="saleor_import_")

        with open(self.filepath, 'r') as f:
            for line in f:
                self._process_entry(json.loads(line.rstrip()))

        self.log_file.close()
        return self.log_file

    def _process_entry(self, entry):
        obj = ImportType.factory(entry["type"], self, entry["data"])

        if obj is not None:
            result = self.api.import_object(obj)["data"]
            if result:
                result = result[obj.mutation_name][obj.query_name]
                self._cache(entry["type"], result, "slug")

            entry["result"] = result
            self._log(entry)

    def _cache(self, type, data, key):
        if not data or key not in data:
            return

        if type not in self.cache:
            self.cache[type] = {}

        self.cache[type][data[key]] = data

    def _log(self, data):
        self.log_file.write(json.dumps(data) + "\n")

    def getCategory(self, slug):
        # TODO get from API if not cached
        return self.cache.get("category", {}).get(slug)
