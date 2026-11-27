# Build the Excel documentation

Run from this repository root:

```sh
python -m pip install -r docs/requirements.txt
python -m unittest discover -s tools/tests -p test_reference.py -v
python -m sphinx -W -b html docs docs/_build/html
```

The site is published at https://jmelo11.github.io/quantsupport-excel/ by this
repository's Documentation workflow. Function declarations are exported from local registration metadata.
Install stable Rust to compile the portable catalog exporter. Windows, Excel
and the Python binding are not needed for this documentation build.
Only this repository's interface is built. Documentation deployment follows a
successful local Release workflow and uses its exact source tag. Pull requests
and pushes validate documentation; manual runs can select a published tag and
optionally a newer documentation revision for corrections.
