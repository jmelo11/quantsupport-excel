Contexts, inputs and evaluation
===============================

A **context** is the market for one valuation date. It holds dated quotes,
historical fixings, FX rates and the settings used to build curves. It
corresponds to ``PricingContext`` in the Rust library. The context's date is
the valuation date for everything priced in it.

Create one context per market. Then add market data to it with
``QS.CONTEXT.ADD.*`` formulas. Each of these formulas refers to the context
cell and adds one piece of data.

Create the market
-----------------

With quote identifiers in A10:A20 and decimal Mid values in F10:F20:

.. code-block:: text

   B2 =QS.CONTEXT.CREATE("usd","2026-01-15","USD","SOFR","Mid")
   B3 =QS.CONTEXT.ADD.QUOTES(B2,A10:A20,TRANSPOSE(F10:F20))
   B4 =QS.CONTEXT.ADD.CURVE(B2,"SOFR")
   B5 =B2

Every addition refers to B2. B5 is an optional second reference to the same
context.

- The market is built when a formula first needs it.
- When you edit or clear an addition, every formula that uses B2 recalculates.
- If an addition fails, the error and its source cell appear in the object
  browser.
- Recalculating without changes keeps the existing market data and results.

Waiting for results
~~~~~~~~~~~~~~~~~~~

Pricing runs in the background. Both matching XLLs must be loaded.

- Evaluations and market views show ``#N/A`` while pending. In Automatic mode
  they update when the result is ready.
- In Manual mode, click **Refresh Pricing**. Pressing F9 does not wait for
  background work, and Excel's calculation status does not show it either.
- Automation scripts should wait with the helper in
  ``tools/excel/examples/async_excel.py``.

Adding quotes, fixings and FX rates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For a single quote, give the identifier, value and quote side:

.. code-block:: text

   =QS.CONTEXT.ADD.QUOTE(B2,"FixedRateDeposit_USD_SOFR_6M",0.04,"Mid")
   =QS.CONTEXT.ADD.FIXINGS(B2,A30:A40,F30:F40,J30:J40)
   =QS.CONTEXT.ADD.FX(B2,A50:A55,F50:F55,J50:J55)

Rules for the field ranges:

- Each field can be a single value, a row, a column or a spilled array.
- Fields can have different orientations and locations, but must have the same
  number of entries.
- A blank cell inside a range keeps its position.
- An omitted quote side (Bid or Ask) has no value.
- Do not include header cells or pass a whole table.

Rules for duplicates:

- Adding the same observation twice is an error.
- Separate Mid, Bid and Ask additions for the same identifier are combined.
  Adding the same side twice is an error.

An addition belongs only to the context it refers to. You can reuse the same
fixing ranges in several dated contexts without copying them. Fixings are used
as entered; they are not filtered by publication date.

Evaluate a contract or trade
----------------------------

.. code-block:: text

   D2 =QS.INSTRUMENT.FIXED.RATE.DEPOSIT("deposit",B2,"2026-01-15","2026-07-15","USD",,1000,0.05,"Actual360","Simple","Annual")
   D3 =QS.TRADE.CREATE("position",B2,D2,"2026-01-15","Receive")
   D4 =QS.EVALUATE(B2,D3,"Value")
   D5 =QS.EVALUATE(B5,D3,"Cashflows")
   D6 =QS.EVALUATE(B5,D3,"Sensitivities")
   D7 =QS.EVALUATE.RANGE(B5,D10:D100,"Value")

``QS.EVALUATE`` takes the context, the instrument or trade, the request, and an
optional pricer and discount policy. It returns the requested number or table.

- The default request is ``Value``.
- An instrument passed directly is valued as a Receive position, traded on the
  context date, with its contractual notional.
- A trade uses its own position terms.
- A bond must be wrapped in a trade with a pricing anchor before you can
  evaluate it.

Many valuation dates at once
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To price each trade on its own date, give one context per trade:

.. code-block:: text

   G2 =QS.EVALUATE.RANGE(C2:C10001,F2:F10001,"Value")

The context range and the trade range must have the same number of entries.
Each context keeps its own market and curves. The trades are priced in
parallel, and the formula spills one value per row, in input order. For large
books, this is faster than one formula per row.

Choosing a pricer and policy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you leave the pricer blank, the add-in uses the standard pricer for the
product, discounting on the context's base curve. A policy argument can change
the discount curve.

For explicit model or funding settings, create a pricer once and pass it. The
pricer already contains its policy, so leave the policy argument blank.

.. code-block:: text

   H2 =QS.DISCOUNT.POLICY.CSA("csa","USD","SOFR")
   H3 =QS.PRICER.CREATE("pricer","DiscountedCashflowPricer",H2)
   H4 =QS.EVALUATE(B5,D3,"Value",H3)
   H5 =QS.EVALUATE.RESULTS(B5,D3,{"Value","Cashflows","Sensitivities"},H3)
   H6 =QS.RESULT.VALUE(H5)

Use ``QS.EVALUATE.RESULTS`` when you need several measures from one valuation,
or want to read the same result in several ways. It stores one
``EvaluationResults`` object. Plain ``QS.EVALUATE`` does not store a result
object, so it is lighter for one value per row.

Built markets are cached, up to a fixed limit. A cached market is reused only
while its inputs are unchanged.

For complete editable formulas, open ``context_pricing_example.xlsx``. Continue
with :doc:`workbook` for installation and debugging, :doc:`markets-and-products`
for construction conventions, or :doc:`risk-and-history` for snapshots and
historical batches.

Forward market contexts
-----------------------

You can roll a context forward to a future date to price under projected
market conditions.

``QS.FORWARD.CONFIG(name, target_date, curve_roll, volatility_roll, fixing_roll)``
sets the horizon date and how each part of the market rolls forward:

- ``curve_roll``: ``ImpliedForward`` (default) or ``ConstantTenor``.
- ``volatility_roll``: ``ConstantTenor`` (default) or ``ForwardVariance``.
- ``fixing_roll``: ``Project`` (default) or ``Preserve``.

``QS.CONTEXT.ADVANCE(name, context, configuration)`` creates a new, ordinary
context from the source context and this configuration.

- Use the new context with the usual curve and valuation functions.
- It updates when the source context or the configuration changes. With
  identical inputs it returns the existing context.
- The source's historical observations are unchanged.
- Sensitivities from the new context refer to the rolled-forward quotes.
