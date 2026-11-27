Risk, portfolios and historical snapshots
=========================================

Evaluation requests correspond to ``Request`` and ``EvaluationResults`` in the
Rust library. ``QS.EVALUATE`` returns one number or table. When you need several
measures from the same valuation, store them once with
``QS.EVALUATE.RESULTS`` and read each one from the stored result:

.. code-block:: text

   H2 =QS.EVALUATE.RESULTS(context,trade,{"Value","Cashflows","Sensitivities"},pricer)
   H3 =QS.RESULT.VALUE(H2)
   H4 =QS.RESULT.SENSITIVITIES(H2)
   H5 =QS.RESULT.COUPONS(H2)
   H6 =QS.RESULT.CASHFLOW.SUMMARY(H2)

Sensitivities and cashflows
---------------------------

**Sensitivities** are raw derivatives: the change in value, in the pricer's
value units, per unit change in each market input.

- For an input quoted as a decimal rate, multiply by 0.0001 to estimate the
  effect of a +1 bp move.
- Each input keeps its own units. Futures price points, FX spots, volatilities
  and rates are not interchangeable.
- Risk is calculated from the full trade and model, not from the cashflow
  report.
- Rows are sorted by tenor or pillar date, shortest first. Rows without a
  recognizable maturity come after the dated rows.

**Cashflows** are signed, undiscounted amounts in each payment currency.
Receipts are positive and payments negative.

- The coupon report shows accrual dates, fixing and contract indices, notional
  and rate conventions.
- The cashflow summary totals Interest, Capital, Other and Total by payment date
  and currency. It does not convert currencies or spread net interest income
  over accrual periods.

**FairRate(index)** solves for one swap leg or loan coupon segment, numbered
from 0.

- For a swap, leg 0 solves the fixed coupon and leg 1 the floating spread. The
  solve sets the PV of all legs and principal to zero.
- Loan segments are solved in order, fixing each earlier rate before the next.
  Loans with a floor or cap cannot be solved.
- Use a separate evaluation for each leg or segment.

.. code-block:: text

   =QS.EVALUATE(context,trade,"FairRate(0)",pricer)
   =QS.EVALUATE(context,trade,"FairRate(1)",pricer)
   =QS.REQUEST.FAIR.RATE(0)

Portfolio aggregation
---------------------

.. code-block:: text

   B2 =QS.PORTFOLIO.CREATE("book",A10:A100)
   B3 =QS.EVALUATE.PORTFOLIO(context,B2,pricer,requests,"USD")
   B4 =QS.RESULT.VALUE(B3)
   B5 =QS.RESULT.COUPONS(B3)
   B6 =QS.RESULT.CASHFLOW.SUMMARY(B3)

``QS.PORTFOLIO.CREATE`` takes a name and an ordered range of trades.

- A trade that appears twice counts as two positions.
- Pass one pricer for all trades, or one pricer per trade.
- Value and Sensitivities are in the context's base currency and include FX
  risk. The optional currency argument must match that base currency.
- A measure that is not supported for every trade is left out of the result.

How results are combined:

- Trades are priced one at a time, so memory use stays low for large books.
- Coupons with the same terms are combined, using notional-weighted rates or
  spreads.
- Coupons with opposite pay/receive directions, nonlinear payoffs or different
  conventions stay on separate rows.

To get one value per trade instead of a combined result, use
``QS.EVALUATE.RANGE`` with a single context.

Archive complete dated markets
------------------------------

Build one complete context for each market date. Put references to these
contexts in A2:A10 and their observation timestamps in F2:F10:

.. code-block:: text

   C2 =first_root
   C3 =next_root
   H2 =QS.SNAPSHOT.FROM.RANGE("history",A2:A10,TRANSPOSE(F2:F10))
   H3 =QS.EVALUATE.FROM.SNAPSHOT(H2,trades,dates,pricer,"Value")

Timestamps:

- Timestamps use RFC 3339 with an explicit time-zone offset, for example
  2026-01-15T16:00:00Z.
- The valuation date is the selected context's date, even if the timestamp
  falls on a different UTC day.
- Two contexts with the same UTC timestamp are an error.

Trades and dates:

- Each trade has one requested date, in the same position in its range.
- Blank entries are errors; rows are never shifted.
- Results come back in the original input order.

Selecting a market:

- The default is ``Previous`` with ``Mid`` quotes.
- ``Previous`` picks the latest complete market at or before the requested
  time.
- ``Exact`` requires a market at exactly that time.
- ``Closest`` picks the nearest market, which may be later. On a tie it picks
  the earlier one.
- A missing Bid or Ask quote is an error. It is not replaced by Mid.

To select and inspect a single market:

.. code-block:: text

   J2 =QS.SNAPSHOT.SELECTOR("selection","2026-01-16T17:00:00Z","Previous","Mid")
   J3 =QS.SNAPSHOT.SELECT("matched",H2,J2)
   J4 =QS.SNAPSHOT.TIMESTAMP(J3)
   J5 =QS.SNAPSHOT.REFERENCE.DATE(J3)
   J6 =QS.CONTEXT.FROM.SNAPSHOT("historical",H2,J2,fixings)

What a snapshot contains:

- Quotes, FX rates and curve settings, including zero-rate quotes, credit,
  volatility and simulation settings.
- Not curves supplied as already-built objects. Curves defined from quotes or
  zero rates are rebuilt from the stored inputs.
- Not fixings. Pass fixings to historical pricing as a fixing addition or a
  context. Fixings are used as entered; they are not filtered by publication
  date.

To save or load snapshots as JSON, use ``SNAPSHOT.FROM.JSON`` and
``SNAPSHOT.TO.JSON``. Excel limits the exported text in one cell to 32,767
UTF-16 characters.

Historical batch performance
----------------------------

``QS.EVALUATE.FROM.SNAPSHOT`` builds each selected market once and shares it
across all trades that use it. It returns one value per trade, in input order,
without creating a context or result object for each row. It finishes during
Excel's normal calculation; it does not run in the background.

The historical and context example workbooks use this function. Running the
worksheets requires Windows Excel.
