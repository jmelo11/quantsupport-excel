# Historical pricing

Historical pricing evaluates positions against complete dated market inputs.
Each snapshot records a market observation timestamp separately from its
valuation date. The [risk and history guide](guide/risk-and-history.rst)
contains the full construction and selection workflow.

## Archive and evaluate markets

Prepare one context for each market observation. Put their handles in
`contexts` and their offset-aware RFC 3339 timestamps in `timestamps`:

```text
=QS.SNAPSHOT.FROM.RANGE("history",contexts,timestamps)
=QS.EVALUATE.FROM.SNAPSHOT(history,trades,dates,pricer,"Value")
```

The trade and requested timestamp arrays have matching entry counts. The
batch groups requests by selected snapshot and constructs each market once,
returning scalar results in input order. Historical batches complete
synchronously during Excel calculation.

Selection defaults to Previous/Mid: use the latest complete observation at or
before each request. Exact requires the requested instant; Closest may select
a future observation. Selecting a market preserves its reference date as the
valuation date; it does not advance that market to the requested timestamp.
Missing Bid or Ask observations do not fall back to Mid.

Snapshots retain construction inputs, including serializable curve and model
configuration. Runtime-only constructed objects and fixing publication vintages
are excluded. Supply the appropriate fixing contribution or committed context
through the optional `fixings` argument when needed.

## Reproduce the example

Open the [historical pricing workbook](https://jmelo11.github.io/quantsupport-excel/downloads/historical_pricing_example.xlsx)
with both matching XLLs loaded. Rebuild its objects after opening. The market
uses explicit illustrative zero-rate observations rather than a live feed.

Regenerate the examples from this repository root:

```sh
python -m pip install -r examples/requirements.txt
python tools/excel/examples/create_examples.py
```

The [worksheet reference](functions/index.rst) documents all arguments, result
shapes and errors. [Market construction](guide/context-first.rst) explains
independent context contributions and background evaluation.
