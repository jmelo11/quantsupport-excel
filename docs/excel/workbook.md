# Working in Excel

A pricing workbook holds dated market inputs, defines contracts and trades,
and asks the add-in for values. Both matching XLLs must be loaded. Start with
the [installation instructions](installation.md) and the
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

- B2 creates the context. Each `QS.CONTEXT.ADD.*` formula refers to B2 and adds
  market data to it.
- The quotes must include every observation the SOFR curve needs.
- When you edit or clear an addition, every formula that uses B2 recalculates.
- D2 holds the contract terms. D3 adds the trade date, side and position size.
- `QS.EVALUATE` returns the requested number or table. Use
  `QS.EVALUATE.RESULTS` to store several measures from one valuation.

## Calculation and interpretation

Pricing runs in the background.

- Cells show `#N/A` while their result is pending.
- In Automatic mode, results appear when they are ready.
- In Manual mode, click **Refresh Pricing**. Pressing F9 does not wait for
  background work, and Excel's calculation status does not show it.
- Automation scripts can wait for completion with
  `tools/excel/examples/async_excel.py`.

Objects belong to the current Excel session. Reopening a workbook rebuilds
them. Recalculating without changes reuses finished results. Failed additions
show their error in the object browser.

Units:

- Rates and spreads are annual decimals.
- Sensitivities are derivatives per unit change in each input. Multiply a
  decimal-rate sensitivity by `0.0001` to estimate a one-basis-point change.
- Cashflows keep their own currencies and contractual conventions.

Continue with [contexts and evaluation](guide/context-first.rst),
[markets and products](guide/markets-and-products.rst), or
[historical pricing](historical-pricing.md). The
[editable workbook](https://jmelo11.github.io/quantsupport-excel/downloads/context_pricing_example.xlsx)
provides complete market inputs.
