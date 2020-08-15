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

    def fetchObject(self, obj, key, identity):
        (query, variables) = obj.get_search_query(key, identity)
        for node in self.fetchList(obj.search_query_name, query, variables):
            entry = node.get("node")
            if entry.get(key) == identity:
                return entry

    def post(self, query, variables):
        client = GraphqlClient(
            endpoint=self.url,
            headers={"Authorization": "JWT {}".format(self.token)}
        )
        return client.execute(query=query, variables=variables)

    def fetchList(self, key, query, variables):
        client = GraphqlClient(
            endpoint=self.url,
            headers={"Authorization": "JWT {}".format(self.token)}
        )
        result = client.execute(query=query, variables=variables)
        return result.get("data", {}).get(key, {}).get("edges", {})


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

    def getItemBySlug(self, type, slug):
        obj = self.cache.get(type, {}).get(slug)
        if not obj:
            obj = self.api.fetchObject(ImportType.factory(type, self, {}), "slug", slug)
            if obj:
                self._cache(type, obj, slug)

        return obj
