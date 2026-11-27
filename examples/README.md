# Excel examples

These workbooks show complete pricing setups that you can open, edit and
recalculate.

## Before you open a workbook

1. Load the matching `quantsupport.xll` and `QuantSupport.Ribbon64.xll` in
   **64-bit Windows Excel**. See the [add-in setup](../README.md#install).
2. Open the workbook's **Start Here** tab. Follow the linked, numbered tabs from
   left to right.
3. Click **QuantSupport > Refresh Pricing** to calculate the workbook and
   receive the background results. This also works in Manual mode.

Result cells are blank until Excel calculates. The files do not store prices or
live objects. Each study suggests three changes to try and tells you where to
see their effect.

## Workbooks

**Large valuation example:** [10,000 valuations in one batch](workbooks/origination_10000_batch.xlsx).
It contains 10,000 different five-year USD SOFR swaps, each with its own
origination date and its own dated context. One `QS.EVALUATE.RANGE` formula
pairs the context and trade ranges, prices them in parallel and spills 10,000
values. Open **Start Here**, then **Origination**. The
[row-by-row version](workbooks/origination_10000_valuations.xlsx) has a
separate PV formula in every row for comparison.

| Workbook | What to follow |
| --- | --- |
| [10,000 valuations in one batch](workbooks/origination_10000_batch.xlsx) | Same dated contexts and trades, with one parallel batch and a 10,000-row spill. Inspect G2 for the paired context/trade formula. |
| [10,000 valuations at origination](workbooks/origination_10000_valuations.xlsx) | Price a different swap at each of 10,000 origination dates; inspect the context, curve contribution, trade and PV for every row. |
| [Context-first pricing](workbooks/context_pricing_example.xlsx) | Create a short context, add independent inputs, request direct loan values and run a historical batch without per-row contexts or evaluation handles. |
| [Portfolio aggregation](workbooks/portfolio_aggregation_example.xlsx) | Pass a range of six trade handles, reconcile PV, and inspect weighted coupon rates/spreads, distinct SOFR/TermSOFR3m fixing indices, sensitivities and separate interest/capital payments. |
| [Swap pricing](workbooks/swap_pricing_example.xlsx) | Bootstrap SOFR under USD collateral and value a receive-fixed USD swap. Bootstrap ESTR in a separate EUR context for curve comparisons. |
| [Loan pricing](workbooks/loan_pricing_example.xlsx) | Compare 12 agreements: repayment styles, floating and mixed coupons, prepayment, borrower credit, funding and stepped coupons. |
| [Bond pricing](workbooks/bond_pricing_example.xlsx) | Keep one bond contract and compare separately anchored positions using Z-spread or clean price. |
| [Historical pricing](workbooks/historical_pricing_example.xlsx) | Archive two dated markets and reprice one unchanged trade. Compare the requested timestamp with the actual selected market date. |
| [Interpolation and schedules](workbooks/interpolation_example.xlsx) | Compare three interpolation methods, check a bilinear surface against its formula, and compare adjusted and transposed schedules. |

Start with **Context-first pricing**. It is the shortest example. The other
studies build the same kind of context step by step:
**instrument → trade → discount policy → pricer → evaluation → result**.

## Reading the sheets

- **Inputs / Cases:** blue cells are editable; labels explain units and conventions. Loan settings and coupon fields are labelled in each case's block. Rates and spreads are annual decimals: enter `0.04` for 4%. Dates are ISO text such as `2026-02-24`.
- **Market / Markets:** market assumptions come first, followed by the curve-construction steps that use them.
- **Build / Archive / Pricing:** read the objects from top to bottom. Each grey object cell has its purpose beside it and its Excel formula immediately below. Named cells such as `Swap_Context` make dependencies easier to follow in the formula bar or Excel's Name Manager.
- **Results:** green cells contain financial measures. Loan and bond rows link directly to their inputs and build steps. Their **Inspect one case** dropdown controls both the Cashflows and Risk tabs.
- **Cashflows / Risk / Curves:** tables have dedicated space to spill. Sensitivities are raw derivatives per unit market input; multiplying a decimal-rate sensitivity by `0.0001` approximates the effect of a +1 bp move.
- **Layouts** in the loan study shows the same small curve table with all four combinations of `transpose` and `headers`. The schedule study also shows a transposed date list.

## Notes on individual studies

**Contexts.** In every study, each `QS.CONTEXT.ADD.*` formula refers to the
same context cell. Evaluation uses all of that context's additions. FUNDING is
an ordinary composite curve, chosen through a discount policy. Coupon schedules
use separate period, rate and index ranges. Loan contract settings use the named
arguments of `QS.LOAN.SETTINGS`.

**Swaps.** The swap study keeps USD/SOFR and EUR/ESTR in separate contexts. The
ESTR context is only for comparing curves; it does not affect the USD swap's
value. Bootstrapping EUR OIS inside a USD collateral context would need a
`COLL:EUR/USD` curve built from additional market data.

**Loans.** Fair-rate columns correspond to coupon segments, numbered from 0.
Each `QS.REQUEST.FAIR.RATE(index)` evaluation returns one number. For mixed or
stepped coupons, earlier segments are fixed before the requested segment is
solved. An empty column means the loan has no such segment. Floating coupons
with a floor or cap have no fair-rate solve.

**Historical pricing.** `QS.SNAPSHOT.FROM.RANGE` takes a range of contexts and a
range of matching observation timestamps.

**Portfolio.** This workbook shows aggregation across trades, currencies and
risk factors. Its default USD book contains:

- two deposits: 100,000 at 4% and 300,000 at 6%;
- two receive-fixed SOFR swaps: 100,000 with a 10 bp floating spread and
  300,000 with 30 bp;
- one 200,000 TermSOFR3m swap;
- one 50,000 short SOFR swap.

All payments are discounted on SOFR. TermSOFR3m has its own projection curve.
The deposits combine to **400,000 at 5.5%**. The paid SOFR coupons combine to
**-400,000 at 25 bp**. The TermSOFR3m coupons and positions in opposite
directions stay separate.

- **3 Build** shows the `Portfolio_Members` range passed to
  `QS.PORTFOLIO.CREATE`.
- **5 Coupons** shows the combined coupon terms.
- **6 Cashflows** shows interest and capital by payment date. It does not spread
  interest across accrual periods for net interest income (NII).

## Regenerate and check

The workbook generators, the migration script, the automation helper and the
benchmark runner are in [`tools/excel/examples/`](../tools/excel/examples).
Tests are in `tests/`. From the repository root:

```sh
python -m pip install -r examples/requirements.txt
python tools/excel/examples/create_examples.py
python -m unittest discover -s examples/tests -p 'test_*.py'
```

Generators write to `workbooks/` by default.

- Regenerate the large workbook with `python tools/excel/examples/create_origination_example.py`.
- Generate the faster batch version with `python tools/excel/examples/create_origination_example.py --layout batch --output examples/workbooks/origination_10000_batch.xlsx`.
- Use `--example context`, `portfolio`, `swap`, `historical`, `loans`, `bonds`, or `interpolation` to generate one file, and `--output-dir PATH` to choose a destination.

The tests need Rust and Cargo and run on any platform. They check:

- navigation between tabs, formula dependencies and registered signatures;
- the pricing workflow;
- that the swap workbook's quotes, curve settings and context assumptions
  bootstrap correctly in Rust, including a regression check for the earlier
  missing-collateral-curve error.

### Live Excel tests (Windows)

Running the worksheets requires Windows Excel. Install `pywin32` and add
`--xll-path dist/quantsupport.xll` to check objects, numerical results,
selected-case tables and recalculation without changes.

Automation scripts must wait for background pricing. Call
`async_excel.await_engine`; it also waits for cells that depend on stored
results. [`tests/test_async_live.py`](tests/test_async_live.py) tests result
delivery in desktop Excel.

## Benchmark 10,000 distinct dated contexts

From the repository root, with Windows Excel, `pywin32` and `psutil` installed:

```sh
python -m pip install -r examples/requirements-live.txt
python tools/excel/examples/benchmark_async.py --xll dist/quantsupport.xll --count 10000 --layout batch --workers 8 --output target/excel-benchmarks/origination-10000.json
```

See [`tools/excel/examples/benchmark_async.py`](../tools/excel/examples/benchmark_async.py)
for the options.

- The benchmark generates the example next to its report and runs it in a
  separate Excel instance.
- Use `--layout rows` to measure individual PV formulas instead.
- It checks that every price is a number and that recalculating without changes
  starts no new pricing jobs.
- Add `--reference PATH.json` to compare all prices with a previous run.
- Inputs are synthetic. Each swap starts seven days after its valuation date.

The optional `tests/test_ribbon_large_live.py` test checks that the panel stays
responsive with the same 10,000-context workbook. It needs a test build of the
ribbon companion made with `-p:QuantSupportLiveTests=true`. It checks the full
object lists, that the selection is kept, and that closing the panel during a
pending load is safe.
