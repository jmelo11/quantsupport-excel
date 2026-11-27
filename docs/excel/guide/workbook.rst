Install and build a pricing workbook
====================================

Install the add-in
------------------

The add-in requires 64-bit Windows desktop Excel.

1. Download the complete Excel ZIP from the project's download page.
2. Extract it into a stable folder.
3. Load ``quantsupport.xll``, ``QuantSupport.Ribbon64.xll`` and
   ``ExcelDna.IntelliSense64.xll`` through Excel's Add-ins dialog.
4. Keep ``quantsupport.intellisense.xml`` in the same folder as the XLLs.
5. Restart Excel.

The ribbon and IntelliSense add-ins need .NET Framework 4.6.2 or later.

Use workbooks and add-ins from the same release. The repository's generated
example workbooks match the current development build. A released workbook
opened with an unreleased development build, or the other way round, can show
unknown-function errors.

Start with a dated market
-------------------------

A context holds the market data and curve settings for one valuation date. Put
the valuation date in B1, quote identifiers in A10:A20 and Mid levels in
F10:F20:

.. code-block:: text

   B2 =QS.CONTEXT.CREATE("usd",B1,"USD","SOFR")
   B3 =QS.CONTEXT.ADD.QUOTES(B2,A10:A20,F10:F20)
   B4 =QS.CONTEXT.ADD.CURVE(B2,"SOFR")
   B5 =B2

The base currency and index (here USD and SOFR) set the collateral assumption
used to build curves. Use one context per independent market. For example, a
EUR OIS curve inside a USD collateral context needs an FX collateral curve. For
an independent EUR market, create a separate EUR/ESTR context. The swap example
shows both markets side by side.

Quote conventions:

- Quote identifiers encode the instrument conventions and tenor.
- Interest rates are decimals: ``0.04`` means 4%.
- Futures prices are in price points, for example ``95.25``.
- Bid and Ask have no value unless you supply them. Requesting a missing quote
  side is an error. The add-in does not substitute another side or an average.

Define the contract, then its position
--------------------------------------

.. code-block:: text

   D2 =QS.INSTRUMENT.SWAP("swap",B2,"2026-01-15","2031-01-15","USD","SOFR",1000000,0.04,0,"Actual360","Simple","Annual","Semiannual","Quarterly")
   D3 =QS.TRADE.CREATE("position",B2,D2,B1,"Receive")
   H2 =QS.DISCOUNT.POLICY.CSA("csa","USD","SOFR")
   H3 =QS.PRICER.CREATE("pricer","DiscountedCashflowPricer",H2)
   H4 =QS.EVALUATE(B5,D3,"Value",H3)
   H5 =QS.EVALUATE(B5,D3,"FairRate(0)",H3)
   H6 =QS.EVALUATE.RESULTS(B5,D3,{"Value","Cashflows","Sensitivities"},H3)

Each object has one job:

- The **instrument** (D2) holds the contract terms: dates, rates, indices and
  notional.
- The **trade** (D3) adds the trade date, direction, any quantity override and,
  for bonds, a pricing anchor.
- The **discount policy** (H2) chooses the discount curves.
- The **pricer** (H3) chooses the valuation model.

Result views and financial units
--------------------------------

.. code-block:: text

   =QS.RESULT.VALUE(H6)
   =QS.RESULT.CASHFLOWS(H6)
   =QS.RESULT.COUPONS(H6)
   =QS.RESULT.SENSITIVITIES(H6)
   =QS.RESULT.CASHFLOW.SUMMARY(H6)
   =QS.CURVE.GET(B5,"SOFR")

- **Cashflows** are undiscounted amounts in each row's currency. Receipts are
  positive and payments negative.
- **Value** (PV) is in the pricer's valuation units.
- **Sensitivities** are raw derivatives per unit change in each market input.
  For rates in decimals, multiply by 0.0001 to estimate a +1 bp change.
- **Coupons** show accrual dates, rate conventions and fixing indices.
- **Cashflow summary** totals Interest, Capital, Other and Total by payment
  date and currency. It does not spread income over accrual periods and does
  not convert currencies.

Tables accept two optional flags at the end: ``transpose`` (default FALSE) and
``headers`` (default TRUE). Leave enough empty cells for the result to spill.
If a spill is blocked, clear the cells in the way; the market does not need to
be rebuilt.

Use the ribbon and panel
------------------------

The **QuantSupport** ribbon tab has these groups:

- **Market**: browse pricing contexts and curves.
- **Pricing**: open pricing for an instrument or trade.
- **Workbook**: browse objects, inspect the selected cell and refresh the
  browser.
- **Calculation**: **Refresh Pricing** and **Reset Memory & Rebuild**.
- **Setup & help**: links to this guide and the function reference.

Working in the panel:

- Tables have resizable columns. Ctrl+A selects all rows, and Ctrl+C copies
  values with their headings. The copy menu can also copy the whole table.
- Numbers use Excel's decimal separator, including custom settings.
- Details show an object's financial data. **Copy handle** copies its
  reference, and **Go to cell** jumps to its formula.
- Object, context and pricer selectors open searchable lists. Search by name,
  type or valuation date, then click a row or press Enter. Escape closes the
  list without changing the selection. The lists show every object, even in
  large workbooks.
- While the browser loads, it shows a loading message. Clicking refresh again
  during a load does not start a second one.

Errors and recalculation:

- When a worksheet function fails, the panel shows its sheet, cell and the
  library's error message. The message disappears when you correct the input
  or clear the formula.
- Pricing in the panel runs only when you click **Run**. Browsing never
  recalculates the workbook.
- After you change inputs, recalculate the worksheet before pricing in the
  panel.

Build and verification
----------------------

On Windows, install stable Rust, Visual Studio Build Tools and .NET SDK 8 or
later, then run:

.. code-block:: powershell

   powershell -ExecutionPolicy Bypass -File tools/excel/build.ps1

The output includes the add-in XLL, the ribbon, the pinned IntelliSense add-in,
the XML metadata and the licenses.

On any platform, regenerate the example workbooks with
``python tools/excel/examples/create_examples.py``. The portable tests check
market construction, object handling and workbook formulas. Loading the add-in
and the panel's display can only be tested in Windows Excel. See
:doc:`risk-and-history` for historical snapshot selection and batch evaluation.

Downloads
---------

* `Complete Excel ZIP <https://jmelo11.github.io/quantsupport-excel/downloads/quantsupport-excel-windows-x64.zip>`_
* `Native XLL <https://jmelo11.github.io/quantsupport-excel/downloads/quantsupport.xll>`_
* `Swap workbook <https://jmelo11.github.io/quantsupport-excel/downloads/swap_pricing_example.xlsx>`_
* `Historical workbook <https://jmelo11.github.io/quantsupport-excel/downloads/historical_pricing_example.xlsx>`_
* `10,000 valuations in one batch <https://jmelo11.github.io/quantsupport-excel/downloads/origination_10000_batch.xlsx>`_

These downloads match the published release. The workbooks in
``examples/workbooks`` match the development source; use them with an add-in
you built locally.
