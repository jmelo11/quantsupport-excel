# QuantSupport Excel add-in

QuantSupport for Excel lets you price trades from worksheet formulas. You enter
market quotes in cells, build a dated market from them, define instruments and
trades, and request values, cashflows and sensitivities. The pricing itself is
done by the QuantSupport Rust library.

**Requirements:**

- 64-bit Windows desktop Excel. Excel for macOS and Excel in the browser cannot
  load the add-in.
- .NET Framework 4.6.2 or later, for the ribbon and IntelliSense companions.

## Install

1. Download the complete [Excel ZIP](https://jmelo11.github.io/quantsupport-excel/downloads/quantsupport-excel-windows-x64.zip)
   and extract all files into a stable folder.
2. In Excel, open **File > Options > Add-ins > Excel Add-ins > Go > Browse**.
3. Load these three files from that folder:
   - `quantsupport.xll` (the worksheet functions)
   - `QuantSupport.Ribbon64.xll` (the ribbon, panel and background results)
   - `ExcelDna.IntelliSense64.xll` (argument hints while typing)
4. Keep `quantsupport.intellisense.xml` in the same folder.
5. Restart Excel.

Use workbooks and add-ins from the same build. Load the add-in before you open a
workbook. If you replace the add-in with a newer build, press **Ctrl+Alt+F9** to
rebuild every formula.

## Your first workbook

A pricing workbook has three parts:

1. A **context**: the market for one valuation date. It holds quotes, fixings,
   FX rates and curve settings.
2. An **instrument** (the contract terms) and a **trade** (your position in it:
   trade date, side and size).
3. An **evaluation** that prices the trade in the context.

This example values a six-month USD deposit:

```text
B2 =QS.CONTEXT.CREATE("usd","2026-01-15","USD","SOFR")
B3 =QS.CONTEXT.ADD.QUOTE(B2,"FixedRateDeposit_USD_SOFR_6M",0.04,"Mid")
B4 =QS.CONTEXT.ADD.CURVE(B2,"SOFR")
D2 =QS.INSTRUMENT.FIXED.RATE.DEPOSIT("deposit",B2,"2026-01-15","2026-07-15","USD",,1000,0.05,"Actual360","Simple","Annual")
D3 =QS.TRADE.CREATE("position",B2,D2,"2026-01-15","Receive")
D4 =QS.EVALUATE(B2,D3,"Value")
D5 =QS.EVALUATE(B2,D3,"Cashflows")
D6 =QS.EVALUATE.RESULTS(B2,D3,{"Value","Cashflows","Sensitivities"})
D7 =QS.RESULT.VALUE(D6)
```

- B2 creates the context. Its date, 2026-01-15, is the valuation date.
- B3 and B4 add a quote and a SOFR curve to that context. Every
  `QS.CONTEXT.ADD.*` formula refers to the context cell (B2) and adds one piece
  of market data.
- D2 defines the deposit and D3 makes it a receive position.
- D4 and D5 return the value and the cashflow table.
- D6 stores several results at once. D7 reads the value from it.

### Adding market data from ranges

You can add many quotes, fixings or FX rates with one formula. Pass each field
as its own range:

```text
=QS.CONTEXT.ADD.QUOTES(B2,A10:A20,TRANSPOSE(F10:F20),G10:G20,H10:H20)
=QS.CONTEXT.ADD.FIXINGS(B2,A30:A40,F30:F40,TRANSPOSE(J30:J40))
=QS.CONTEXT.ADD.FX(B2,A50:A55,F50:F55,J50:J55)
=QS.CONTEXT.ADD.CURVE(B2,"SOFR",A10:A20,F10:F20)
```

- Each range can be a row or a column, and the ranges do not need to be next to
  each other. Do not include header cells.
- All ranges in one formula must have the same number of entries.
- A blank cell inside a range keeps its position.
- If you omit a quote side (for example Bid or Ask), that side has no value.

The context also accepts zero-rate and composite curves, credit curves,
volatility surfaces and cubes, and model and pricer configurations. Use
`QS.CONTEXT.QUOTE` and `QS.CONTEXT.FIXING` to read back values from a context.

### Editing market data

- When you edit, replace or delete a `QS.CONTEXT.ADD.*` formula, every formula
  that uses the context recalculates. This includes formulas that refer only to
  the context cell.
- If an addition fails, the market is marked invalid. The error and its source
  cell appear in the object browser.
- Adding the same quote side, fixing or configuration twice is an error.
  Separate Mid, Bid and Ask additions for the same quote are combined.
- Recalculating without changes keeps existing market data and finished results.

## How results are calculated

Pricing runs in the background so that Excel stays responsive. Both
`quantsupport.xll` and `QuantSupport.Ribbon64.xll` must be loaded for results to
reach the worksheet.

- A cell shows `#N/A` while its result is pending.
- In **Automatic** calculation mode, results appear in the cells when they are
  ready.
- In **Manual** calculation mode, click **QuantSupport > Refresh Pricing**. It
  waits for pending work and refreshes dependent cells. Pressing F9 starts the
  work but does not wait for it to finish.
- Errors show as normal Excel errors (for example `#VALUE!`). The error message
  and its source cell appear in the object browser.

Excel's `CalculationState` does not show whether background pricing has
finished. For automation scripts, use `tools/excel/examples/async_excel.py`, or
read `QS.ENGINE.STATUS()`. It reports `pending`, `pending_delivery`, `settled`,
errors and timing for each stage.

The add-in keeps Excel's application-wide RTD throttle setting (typically
2,000 ms). By default it uses up to eight pricing threads. To change this, set
the `QS_ENGINE_WORKERS` environment variable to a value from 1 to 32 before you
start Excel.

## Evaluation functions

| Function | Result |
| --- | --- |
| `QS.EVALUATE` | One value, or a cashflow or sensitivity table |
| `QS.EVALUATE.RANGE` | One value per trade, priced in parallel. Pass one context, or a range of contexts paired row by row with the trades |
| `QS.EVALUATE.RESULTS` | A stored result with several measures; read it with the `QS.RESULT.*` functions |
| `QS.EVALUATE.PORTFOLIO` | A stored result combining all trades in a portfolio |
| `QS.EVALUATE.FROM.SNAPSHOT` | One value per trade from historical markets, each at its own timestamp |

`QS.EVALUATE` takes its arguments in this order: **context, instrument or trade,
request, pricer, policy**, then optional layout flags.

- **Request** defaults to `Value`.
- **Pricer**: leave it blank to use the standard pricer for the product.
- **Policy** chooses discount curves. Leave it blank to use the context's base
  curve.

To control funding curves or model parameters, create a policy, create a pricer
with that policy, and pass the pricer. The pricer already contains its policy,
so leave the policy argument blank. Passing both a pricer and a separate policy
is an error.

```text
=QS.DISCOUNT.POLICY.CSA("csa","USD","SOFR")
=QS.DISCOUNT.POLICY.FIXED.INCOME("funding","EUR","FUNDING")
=QS.PRICER.CREATE("pricer","DiscountedCashflowPricer",policy)
=QS.EVALUATE(context,trade,"FairRate(0)",pricer)
=QS.EVALUATE.RANGE(context,trades,"Value",pricer)
=QS.EVALUATE.RESULTS(context,trade,requests,pricer)
=QS.EVALUATE.PORTFOLIO(context,portfolio,pricer,requests,"USD")
```

Conventions:

- If you pass an instrument directly, it is valued as a Receive position, with
  its own notional, traded on the context date.
- Use `QS.TRADE.CREATE` to set the side, trade date or quantity. Bonds need a
  trade with a price or spread anchor.
- Swaptions need an explicitly configured pricer.
- `FairRate(index)` solves for one swap leg or loan segment. The index starts
  at 0. Use a separate evaluation for each leg or segment.
- Sensitivities are raw derivatives per unit change in each market input. For
  rates in decimals, multiply by `0.0001` to estimate the effect of a +1 bp move.
- Table results accept two optional flags at the end: `transpose` (default
  FALSE) and `headers` (default TRUE). List results accept only `transpose`.

## Historical pricing with snapshots

To price trades on past dates, build one complete context per market date. Then
archive them in a snapshot together with their observation timestamps:

```text
=QS.SNAPSHOT.FROM.RANGE("history",contexts,timestamps)
=QS.EVALUATE.FROM.SNAPSHOT(history,trades,dates,pricer,"Value")
```

- Each trade has one RFC 3339 timestamp with a time zone, such as
  `2026-01-15T16:00:00Z`.
- By default the add-in uses the latest complete market at or before each
  timestamp (`Previous`), with Mid quotes.
- `Exact` and `Closest` are also available. `Closest` may pick a later market.
- The valuation date is the selected market's date, not the requested timestamp.
- A missing Bid or Ask quote is an error. It is not replaced by Mid.
- Snapshots keep the market inputs and curve settings. They do not keep built
  curves or fixing history. Pass fixings in the optional `fixings` argument,
  either as a fixing addition or as a context.

Each market is built once and shared by all trades that use it. The function
returns one value per trade, in input order. Historical batches finish during
Excel's normal calculation; they do not run in the background.

## Ribbon and panel

The **QuantSupport** ribbon tab has these groups:

- **Market**: browse pricing contexts and curves.
- **Pricing**: browse instruments and trades, or price the selected one.
- **Workbook**: browse all objects, inspect the selected cell, refresh the
  browser.
- **Calculation**: **Refresh Pricing** and **Reset Memory & Rebuild**.
- **Setup & help**: open the setup guide and function reference.

In the panel:

- Tables have resizable columns. Ctrl+A and Ctrl+C, and the table's copy menu,
  copy values with their headings.
- Details show the financial inputs and dates of an object. **Go to cell** jumps
  to its formula, and **Copy handle** copies its reference.
- Worksheet errors appear with their source cell. They disappear when the cell
  recalculates successfully or is cleared. Query errors show the library's
  message.
- Browsing never recalculates the workbook.

**Reset Memory & Rebuild** clears all QuantSupport objects and recalculates
every open workbook. It works in Manual mode too and keeps your calculation-mode
setting.

## Examples

[Ready-to-open workbooks](examples/README.md) cover contexts, swaps, history,
loans, bonds, portfolio aggregation and interpolation. Each workbook opens on a
**Start Here** tab. The [10,000-valuation example](examples/workbooks/origination_10000_batch.xlsx)
prices a different swap at each of 10,000 origination dates, each with its own
dated context.

- Workbooks: `examples/workbooks/`
- Generators and the benchmark: `tools/excel/examples/`
- Checks: `examples/tests/`

[The guide](docs/excel/guide/index.rst) explains the financial conventions. The
[generated reference](https://jmelo11.github.io/quantsupport-excel/excel/functions/index.html)
lists the exact signature of every function.

## Building and testing

To build on Windows, install stable Rust for 64-bit MSVC, Visual Studio Build
Tools and .NET SDK 8 or later. Then run:

```powershell
rustup target add x86_64-pc-windows-msvc
powershell -ExecutionPolicy Bypass -File tools/excel/build.ps1
```

The build writes the add-in files to `dist`.

To regenerate the example workbooks and run the portable tests (any platform):

```sh
python -m pip install -r examples/requirements.txt
python tools/excel/examples/create_examples.py
cargo test -p quantsupport-xll --lib --example function_catalog
python -m unittest discover -s examples/tests -p 'test_*.py'
```

The portable tests check market construction, object updates, historical
batches and workbook formulas. Loading the add-in in Excel and the panel's
behavior can only be checked on Windows. Use the Windows smoke and lifecycle
tests with matching XLLs. These need pywin32 and the `QS_XLL_PATH` environment
variable.

See [Build the Excel documentation](docs/README.md) to build the documentation
site. Financial concepts are explained in the
[QuantSupport Book](https://jmelo11.github.io/quantsupport/).

## Releases (maintainers)

This repository uses the core Rust library at the exact Git revision set in
`Cargo.toml`. Building, releasing and publishing documentation all run from
this repository.

To use a newer core revision:

1. Update `dependencies.quantsupport.rev` in `Cargo.toml`.
2. Run `cargo update -p quantsupport`.
3. If the core change adds APIs you want in Excel, add the worksheet wrappers
   and documentation.
4. Run this repository's checks.
5. Commit `Cargo.toml` and `Cargo.lock` together and merge.

The binding version is in `[workspace.package]` in `Cargo.toml`.

- Each merge to `main` takes the next patch version and builds a release. The
  signed release commit updates both the manifest and the lockfile.
- Add `[skip release]` to the commit message for documentation-only changes.
  Add `[release]` to force a release.
- GitHub Pages must be set to deploy from GitHub Actions.
- If `main` is protected, the signed version commit may need a `RELEASE_TOKEN`
  secret.

## Migrating older workbooks

Workbooks built for earlier versions use functions that this version does not
include. Update them using this table. `tools/excel/examples/migrate_async_api.py`
updates old example formulas and keeps the workbook layout.

Earlier versions also used `QS.CONTEXT.PREPARE` and an `inputs` argument on the
evaluation functions. Remove both: evaluation reads the context's additions
directly.

| Previous API | Replacement |
| --- | --- |
| Quote/fixing/FX stores and curve configuration collections | Context creation and `QS.CONTEXT.ADD.*` |
| `QS.CONTEXT.FROM.COMPONENTS` | `QS.CONTEXT.CREATE` and context-owned additions |
| `QS.CONTEXT.PRICE`, `QS.CONTEXT.VALUES` | `QS.EVALUATE`, `QS.EVALUATE.RANGE` |
| Stored `QS.EVALUATE` with name/pricer/trade/context/requests | `QS.EVALUATE.RESULTS` with context/trade/requests/pricer |
| `QS.HISTORY.VALUES` | `QS.EVALUATE.FROM.SNAPSHOT` |
| `QS.SNAPSHOTS.*` | Singular `QS.SNAPSHOT.*`; archive construction is `.ARCHIVE` |
| Product trade constructors and direct pricing/risk shortcuts | `QS.INSTRUMENT.*`, `QS.TRADE.CREATE`, evaluation requests |
| Fixed bond/deposit and floating note names | `FIXED.RATE.BOND`, `FIXED.RATE.DEPOSIT`, `FLOATING.RATE.NOTE` |
