# Working in Excel

A workbook supplies dated market inputs, defines contracts and trades, and
requests values from the native pricing engine. Both matching XLLs must be
loaded. Start with the [installation instructions](installation.md) and the
[complete workbook guide](guide/workbook.rst).

## Create a market and position

With quote identifiers in A10:A20 and decimal Mid values in F10:F20:

```text
B2 =QS.CONTEXT.CREATE("usd","2026-01-15","USD","SOFR","Mid")
B3 =QS.CONTEXT.ADD.QUOTES(B2,A10:A20,F10:F20)
B4 =QS.CONTEXT.ADD.CURVE(B2,"SOFR")
D2 =QS.INSTRUMENT.FIXED.RATE.DEPOSIT("deposit",B2,"2026-01-15","2026-07-15","USD",,1000,0.05,"Actual360","Simple","Annual")
D3 =QS.TRADE.CREATE("position",B2,D2,"2026-01-15","Receive")
D4 =QS.EVALUATE(B2,D3,"Value")
D5 =QS.EVALUATE(B2,D3,"Cashflows")
D6 =QS.EVALUATE(B2,D3,"Sensitivities")
```

Each addition references the same root context. The engine commits cell-owned
contributions and constructs dependencies on demand. Editing or clearing an
addition invalidates consumers of that context. Quote arrays must contain the
market observations needed by the selected curve configuration.

A contract describes its terms; a trade adds execution date, side and position
size. Direct evaluation returns the requested scalar or table. Use
`QS.EVALUATE.RESULTS` when several measures should share a stored result.

## Calculation and interpretation

While a background request is pending its cells show `#N/A`. Automatic mode
receives completed results through RTD. In Manual mode use **Refresh Pricing**;
F9 and Excel's calculation status do not await background work. Automation uses
`tools/excel/examples/async_excel.py` to await explicit completion.

Handles belong to the current workbook session. Reopening a workbook rebuilds
its native objects. Unchanged inputs reuse ready results; failed contributions
produce diagnostics in the object browser.

Rates and spreads use annual decimals. Sensitivities are derivatives per unit
input; multiplying a decimal-rate derivative by `0.0001` estimates a one-basis-
point change. Cashflows retain their currencies and contractual conventions.

Continue with [contexts and evaluation](guide/context-first.rst),
[markets and products](guide/markets-and-products.rst), or
[historical pricing](historical-pricing.md). The
[editable workbook](https://jmelo11.github.io/quantsupport-excel/downloads/context_pricing_example.xlsx)
provides complete market inputs.
