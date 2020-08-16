import json
import tempfile

from aiogqlc import GraphQLClient
from .types import ImportType


class Api:
    def __init__(self, url, token):
        self.url = url
        self.token = token

    async def import_object(self, obj):
        (query, variables) = await obj.get_import_query()
        return await self.post(query, variables)

    async def fetchObject(self, obj, key, identity):
        (query, variables) = obj.get_search_query(key, identity)
        result = await self.fetchList(obj.search_query_name, query, variables)

        for node in result:
            entry = node.get("node")
            if entry.get(key) == identity:
                return entry

    async def post(self, query, variables):
        client = GraphQLClient(
            endpoint=self.url,
            headers={"Authorization": "Bearer {}".format(self.token)}
        )
        result = await client.execute(query=query, variables=variables)
        return await result.json()

    async def fetchList(self, key, query, variables):
        client = GraphQLClient(
            endpoint=self.url,
            headers={"Authorization": "Bearer {}".format(self.token)}
        )
        result = await client.execute(query=query, variables=variables)
        result = await result.json()
        return result.get("data", {}).get(key, {}).get("edges", {})


class Importer:
    def __init__(self, api, filepath):
        self.api = api
        self.filepath = filepath
        self.cache = {}

    async def process(self):
        self.log_file = tempfile.NamedTemporaryFile(mode="w", delete=False, prefix="saleor_import_")

        with open(self.filepath, 'r') as f:
            for line in f:
                await self._process_entry(json.loads(line.rstrip()))

        self.log_file.close()
        return self.log_file

    async def _process_entry(self, entry):
        obj = ImportType.factory(entry["type"], self, entry["data"])

        if obj is not None:
            result = await self.api.import_object(obj)
            result = result["data"]
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

    async def getItemBySlug(self, type, slug):
        obj = self.cache.get(type, {}).get(slug)
        if not obj:
            obj = await self.api.fetchObject(ImportType.factory(type, self, {}), "slug", slug)
            if obj:
                self._cache(type, obj, slug)

        return obj
