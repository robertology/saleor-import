#!/usr/bin/env python3

import importer

print("""
Welcome to the Saleor Importer!

To import data into Saleor, I will need three pieces of information from you:

1. The URL of your Saleor API
2. An API token (see https://docs.saleor.io/docs/dashboard/configuration/service-accounts)
3. The path to a file containing the data to import (link to format To Be Provided)
""")

url = input('URL: ')
token = input('API Token: ')
filepath = input('Path to File: ')

output_file = importer.Importer(
    importer.Api(url, token),
    filepath,
).process()

print("Results are in: {}".format(output_file.name))
