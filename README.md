# saleor-import
A script to import data into [Saleor](https://saleor.io)

I intended to create documentation and examples, but do not have the time to dedicate to this. The unit tests included no longer work due to a change to using async calls, but it all should work (or at least it did with whatever version of Saleor I was using at the time). If people are actually interested in using this but can't figure it out, I will attempt to refresh my memory and maybe whip up some docs. But even better if *you* did that so you can learn it intimately (and improve it) as you go.

The basic idea is to make a [jsonl](https://jsonlines.org/) file with each line of the file being a json object for the product, image, warehouse, etc. Any of those objects can reference another by "slug" but of course those would need to appear first in the jsonl file, or should already have been imported/created. For example, put your categories before the products so that the product can reference the category.
