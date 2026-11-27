Markets, instruments and pricing conventions
============================================

Start every market with ``QS.CONTEXT.CREATE``. The context's quote reference
date is the valuation date. The base currency, base index and quote side
control how curves are built. Each ``QS.CONTEXT.ADD.*`` formula refers to the
context cell and adds data to that context. When you evaluate, the add-in
builds only the parts of the market that the evaluation needs.

Bootstrapped and explicit curves
--------------------------------

To bootstrap a curve, pass the quote identifiers and values as separate ranges.
Mid, Bid and Ask ranges can be in different places and orientations, but must
have the same number of entries. Requesting a quote side that is missing is an
error. The quote identifiers follow the Rust library's naming conventions,
which encode the product, index and tenor.

.. code-block:: text

   B2 =QS.CONTEXT.CREATE("usd","2026-01-15","USD","SOFR")
   B3 =QS.CONTEXT.ADD.CURVE(B2,"SOFR",A10:A20,F10:F20)
   B4 =B2

If you already added the quotes with ``ADD.QUOTES``, leave the identifier and
value arguments of ``ADD.CURVE`` empty. The curve then uses the context's quotes
for that index, and always selects the same ones. Adding the same curve index or
quote side twice is an error; the second addition does not replace the first.

For an explicit zero curve, pass the pillars and rates as separate ordered
ranges:

.. code-block:: text

   =QS.CONTEXT.ADD.ZERO.CURVE(B2,"SOFR",A30:A34,F30:F34,"Actual360","Linear",TRUE,"Continuous","Annual")
   =QS.CONTEXT.ADD.COMPOSITE.CURVE(B2,"OTHER:FUNDING","SOFR","OTHER:FUNDINGSPREAD")

- Pillars can be ISO dates or tenors such as 0D, 1Y and 10Y.
- Rates are annual decimals with the given compounding and frequency.
- The zero curve is stored as a curve definition. A snapshot can therefore
  rebuild it for a different market date.
- A composite curve multiplies the discount factors of its base curve and its
  spread curve.
- FUNDING is an ordinary curve index. Select it with a discount policy, not
  through the loan's contract settings.

``QS.CURVE.GET`` returns a curve from a context. Use ``DISCOUNT``,
``ZERO.RATE``, ``FORWARD`` and ``TABLE`` in the same ``QS.CURVE.*`` namespace to
inspect it. The table shows pillar dates, discount factors, zero rates and
forward rates. Displayed rates default to Simple/Annual with the curve's own day
count. A curve is evaluated outside its pillars only if it was added with
``extrapolate`` set to TRUE.

Fixings, FX, credit and volatility
----------------------------------

.. code-block:: text

   =QS.CONTEXT.ADD.FIXINGS(B2,A40:A50,F40:F50,J40:J50)
   =QS.CONTEXT.ADD.FX(B2,A60:A65,F60:F65,J60:J65)
   =QS.CONTEXT.ADD.CREDIT.CURVE(B2,"CREDIT:BORROWER","USD","SOFR",0.4,A70:A75,F70:F75)
   =QS.CONTEXT.ADD.VOL.SURFACE(B2,"SOFR","Black","Strike",A80:A90,F80:F90)
   =QS.CONTEXT.ADD.VOL.CUBE(B2,"SOFR","Black","Strike",A100:A110,F100:F110)

- **Fixings**: market index, ISO fixing date and value. Values are in the
  index's own units.
- **FX**: base currency, quote currency and a positive rate, in quote-currency
  units per one unit of base currency.
- **Credit curves** are calibrated from CDS quote identifiers, with the
  recovery rate and discounting you specify.
- **Black volatility** is annualized, in decimals. **Normal volatility** is in
  rate or price units per square root of a year. The quote identifiers and the
  configuration must use the same convention.

Volatility surfaces and cubes use the matching data in the context. To attach
model and pricer settings, use ``ADD.SIMULATION.CONFIGURATION`` and
``ADD.PRICER.CONFIGURATION``. Each takes one JSON object in the Rust library's
format.

Keep contracts separate from positions
--------------------------------------

The ``QS.INSTRUMENT.*`` functions follow the product families of the Rust
library. Fixed income uses ``FIXED.RATE.BOND``, ``FIXED.RATE.DEPOSIT`` and
``FLOATING.RATE.NOTE``. Rate futures use ``RATE.FUTURES``. Create the position
with ``QS.TRADE.CREATE``.

.. code-block:: text

   D2 =QS.INSTRUMENT.FX.FORWARD("fx",B2,"2027-01-15","EUR","USD",1.10)
   D3 =QS.TRADE.CREATE("position",B2,D2,"2026-01-15","Receive",1000000)
   D4 =QS.EVALUATE(B4,D3,"Value")

- How FX carry is treated depends on the selected pricer.
- FX outright rates are quote currency per unit of base currency.
- FX forward points are the raw forward minus spot. They are not scaled to pips.
- Equity indices use identifiers such as ``EQ:SPX``.
- Futures contract size is in currency per price point, not per basis point.

Relative dates
--------------

Most date arguments of ``QS.INSTRUMENT.*`` have a matching tenor argument. To
use a tenor, leave the date blank and supply the tenor. Instrument and trade
functions take the context right after the name; it is used to turn tenors into
dates.

.. code-block:: text

   D2 =QS.INSTRUMENT.FX.FORWARD("fx",B2,"","EUR","USD",1.10,"1Y")
   D3 =QS.TRADE.CREATE("position",B2,D2,"","Receive",1000000)
   D4 =QS.EVALUATE(B4,D3,"Value")

- Scheduled products use ``start_tenor`` and ``tenor``.
- Options use ``expiry_tenor``; forwards use ``delivery_tenor``.
- ``QS.TRADE.CREATE`` accepts ``trade_tenor``.
- If both the date and the tenor are blank, the tenor is ``0D`` from the
  context date.

The dates and initial principal are fixed when the instrument is created. They
do not move during valuation. If the instrument formula recalculates, it
creates a new contract.

Historical fixings
~~~~~~~~~~~~~~~~~~

``QS.CONTEXT.CREATE`` has a final ``anchor_fixings`` argument (TRUE by
default).

- **TRUE**: index fixings before the valuation date must be stored in the
  context. A missing past fixing is an error. Fixings on or after the
  valuation date are projected from the curve.
- **FALSE**: all index fixings are projected from the curve, within the
  curve's supported date range.

Policies and explicit model choices
-----------------------------------

.. code-block:: text

   L3 =QS.DISCOUNT.POLICY.CSA("csa","USD","SOFR")
   L4 =QS.PRICER.CREATE("dcf","DiscountedCashflowPricer",L3)
   L5 =QS.PRICER.CREATE("swaption","ClosedFormHullWhiteSwaptionPricer",L3,AC30:AC31,AD30:AD31)
   L6 =QS.DISCOUNT.POLICY.FIXED.INCOME("fixed.income",A120:A122,F120:F122)

- Pricer settings are passed as a range of names and a range of values. For
  Hull-White alpha and sigma, put the setting names in AC30:AC31 and their
  values in AD30:AD31.
- The swaption pricer requires its model parameters.
- ``RateFuturesPricer`` does not use a discount policy. Passing one is an
  error.
- A fixed-income policy maps each currency to a curve index. It can optionally
  prefer the instrument's own discount index.

Bonds
~~~~~

- A bond trade needs an anchor type (``CleanPrice``, ``DirtyPrice`` or
  ``ZSpread``) and an anchor value.
- Clean and dirty prices are in quotation units. PV is a money amount.
- Supported requests include ``YieldToMaturity``, ``ModifiedDuration`` and
  ``ZSpread``, depending on the pricer.
- The bond functions do not include call schedules, so they cannot be used for
  OAS. ``BondPricer`` does not support ``FairRate``.

The swap, bond and loan example workbooks explain the conventions next to each
input. The generated worksheet reference is the authority on argument order,
defaults and errors. Unsupported products and pricers return an error. The
worksheet functions do not include custom scripted products or an exposure/XVA
engine.
