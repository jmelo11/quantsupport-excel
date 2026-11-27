# Build the Excel documentation

You need stable Rust to build the documentation. The build compiles a small
program that exports the function list from the add-in's source. Windows, Excel
and the Python binding are not needed.

Run from the repository root:

```sh
python -m pip install -r docs/requirements.txt
python -m unittest discover -s tools/tests -p test_reference.py -v
python -m sphinx -W -b html docs docs/_build/html
```

## Publishing

The site is published at https://jmelo11.github.io/quantsupport-excel/ by this
repository's Documentation workflow.

- After a successful Release workflow, the site is deployed from that release's
  source tag.
- Pull requests and pushes build and check the documentation without deploying
  it.
- A manual run can deploy a published tag. To publish corrections, it can
  optionally use a newer documentation revision.
