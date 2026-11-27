# Historical pricing

Historical pricing values trades against markets from past dates. You build
one complete market (a context) per date and store them together in a
snapshot. Each market in the snapshot has an observation timestamp and its own
valuation date. The [risk and history guide](guide/risk-and-history.rst)
describes the full workflow.

## Archive and evaluate markets

Create one context for each market observation. Put the context cells in
`contexts` and their RFC 3339 timestamps, with time-zone offset, in
`timestamps`:

```text
=QS.SNAPSHOT.FROM.RANGE("history",contexts,timestamps)
=QS.EVALUATE.FROM.SNAPSHOT(history,trades,dates,pricer,"Value")
```

- `trades` and `dates` must have the same number of entries.
- Each market is built once and shared by all trades that use it.
- The function returns one value per trade, in input order.
- It finishes during Excel's normal calculation; it does not run in the
  background.

How a market is selected:

- The default is `Previous` with `Mid` quotes: the latest complete market at or
  before each requested time.
- `Exact` requires a market at exactly the requested time.
- `Closest` picks the nearest market, which may be later.
- The valuation date is the selected market's own date. The market is not
  rolled forward to the requested time.
- A missing Bid or Ask quote is an error. It is not replaced by Mid.

Snapshots keep the market inputs and curve and model settings. They do not keep
objects supplied already built, or fixings. When fixings are needed, pass them
in the optional `fixings` argument, as a fixing addition or as a context.

## Reproduce the example

Open the [historical pricing workbook](https://jmelo11.github.io/quantsupport-excel/downloads/historical_pricing_example.xlsx)
with both matching XLLs loaded. If the add-in was loaded after the workbook,
press **Ctrl+Alt+F9** to rebuild its objects. The market uses illustrative
zero rates entered in the workbook, not a live feed.

Regenerate the examples from this repository root:

```sh
python -m pip install -r examples/requirements.txt
python tools/excel/examples/create_examples.py
```

The [worksheet reference](functions/index.rst) documents all arguments, result
layouts and errors. [Market construction](guide/context-first.rst) explains how
to add market data to a context and how background evaluation works.
