import json
import tempfile
from .types import *


class Api:
    def __init__(self, url, token):
        self.url = url
        self.token = token

    def import_object(self, obj):
        return self.post(self._get_import_query(obj.get_import_data()))

    def _get_import_query(self, data):
        return {"mutation": {"data": data}}

    def post(self, data):
        # TODO
        return data


class Importer:
    def __init__(self, api, filepath):
        self.api = api
        self.filepath = filepath

    def process(self):
        self.log_file = tempfile.NamedTemporaryFile(mode="w", delete=False, prefix="saleor_import_")

        with open(self.filepath, 'r') as f:
            for line in f:
                self._process_entry(json.loads(line.rstrip()))

        self.log_file.close()
        return self.log_file

    def _process_entry(self, entry):
        if entry["type"] == "category":
            entry["result"] = self.api.import_object(Category(self, entry["data"]))
            self._log(entry)

    def _log(self, data):
        self.log_file.write(json.dumps(data) + "\n")
