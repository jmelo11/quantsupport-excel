Loan contracts, funding and fair rates
======================================

A loan is set up in three parts, matching ``Loan``, ``LoanTrade`` and
``LoanPricer`` in the Rust library:

- The **loan contract** holds the principal, dates, coupon rules and repayment
  structure.
- The **trade** adds the position direction and trade date.
- The **loan pricer** chooses the discount curve, the refinancing assumptions
  and how amortization is handled when solving for a fair rate.

Read the constructor arguments
------------------------------

- Rates and spreads are annual decimals: ``0.05`` means 5%, and ``0.01`` means
  100 basis points.
- Principal is in currency units.
- A blank optional argument uses the default in the table below. Zero is a
  value, not a blank.

For help in Excel, type the function name and press **Ctrl+A** to open Function
Arguments. Or enter ``=QS.HELP("QS.INSTRUMENT.LOAN")`` to show the same help in
cells.

.. list-table:: QS.INSTRUMENT.LOAN, in worksheet argument order
   :header-rows: 1
   :widths: 20 20 60

   * - Argument
     - Required / blank default
     - Meaning
   * - ``name``
     - Required
     - Your object name, e.g. ``"mortgage"``; the function returns a loan handle.
   * - ``context``
     - Required
     - Market context used to work out dates and the initial amortization.
   * - ``start_date``
     - Required
     - Advance/accrual start, as ISO text ``"2026-02-24"``; distinct from trade date.
   * - ``maturity_date``
     - Required
     - Final accrual date, after start; payment-date adjustment is a separate setting.
   * - ``currency``
     - Required
     - Principal/payment currency, e.g. ``"EUR"``.
   * - ``notional``
     - Required
     - Positive original principal, e.g. ``10000`` means EUR 10,000 for EUR.
   * - ``rate``
     - Required
     - Fixed coupon if ``market_index`` is blank; spread over the index otherwise.
       Coupon arrays, when supplied, replace these scalar coupon terms.
   * - ``market_index``
     - Fixed coupon
     - Floating projection index, e.g. ``"EURIBOR12m"``; this is not the discount curve.
   * - ``repayment``
     - ``"French"``
     - French: level initial instalments. Bullet: interest with all principal at
       maturity. Balloon: amortization leaving a final fraction of original principal.
   * - ``payment_frequency``
     - ``"Monthly"``
     - Payment/accrual frequency, e.g. Monthly, Quarterly, Semiannual or Annual.
       Index resets and observation tenor are separate settings.
   * - ``day_counter``
     - Index convention for floating coupons; ``"Actual365"`` for fixed coupons
     - Optional coupon accrual basis for interest and initial principal amortization.
   * - ``settings``
     - No optional overrides
     - Handle returned by ``QS.LOAN.SETTINGS``; see the defaults below.
   * - ``coupon_periods``
     - No segment schedule
     - Payment count for each successive coupon segment; ``12`` means 12 payments,
       not 12 years. Only the final count may be blank to fill maturity.
   * - ``coupon_rates``
     - Use scalar ``rate``
     - Annual coupon/spread for each segment. Supplied segments must cover the loan.
   * - ``coupon_indices``
     - All segments fixed
     - Projection index per segment; a blank entry means fixed. An omitted array
       makes every segment fixed even if scalar ``market_index`` is supplied.
   * - ``prepayment_dates``
     - No dated CPR model
     - Strictly increasing ISO observation dates, aligned with ``prepayment_cprs``.
   * - ``prepayment_cprs``
     - No dated CPR model
     - Annual conditional prepayment fractions in [0,1], e.g. ``0.10`` = 10% per year.

Rules for the array arguments:

- Each array can be a row, a column or a spilled range.
- Arrays in the same group (coupon or prepayment) must have the same number of
  entries.
- Do not include header cells.
- Only the final coupon count can be blank. Other blank cells keep their
  position.
- Coupon arrays cannot be combined with introductory terms or a floor/cap in
  Loan Settings.

Choose optional settings
-------------------------

``QS.LOAN.SETTINGS(name, ...)`` returns a settings handle that you pass to the
loan. All arguments after the name are optional, in the order below. Leave
unused positions empty, or use cell references to keep the formula readable.

.. list-table:: Loan Settings defaults and units
   :header-rows: 1
   :widths: 24 22 54

   * - Argument
     - Blank default
     - Meaning / when to supply
   * - ``balloon_fraction``
     - Unset
     - Residual fraction in [0,1] of original principal, e.g. ``0.25`` = 25%.
       Required for Balloon; invalid for French/Bullet.
   * - ``amortization_rate``
     - Initial coupon built by the instrument constructor
     - Optional annual all-in rate used to build principal instalments, e.g. ``0.05``.
       Blank floating-first French/Balloon uses the initial fixing or forecast;
       not needed for Bullet.
       It does not set the coupon spread or forecast market rates.
   * - ``credit_index``
     - No borrower default
     - Borrower survival curve, e.g. ``"CREDIT:BORROWER"``.
   * - ``recovery``
     - ``0.40``
     - Fraction of opening principal recovered on default; [0,1].
   * - ``fixing_frequency``
     - Index metadata
     - Floating reset frequency; daily indices use payment frequency by default.
       Each reset must fall on a payment accrual boundary.
   * - ``fixing_lag``
     - ``0``
     - Nonnegative whole business days backwards from reset to fixing.
   * - ``index_tenor``
     - Index metadata
     - Positive observation period, e.g. ``"3M"`` or ``"12M"``; separate from
       payment frequency and reset frequency.
   * - ``calendar``
     - ``NullCalendar``
     - Payment/fixing calendar, e.g. ``"TARGET"``. NullCalendar treats every day
       as a business day. Accrual boundaries stay unadjusted.
   * - ``business_day_convention``
     - ``"Unadjusted"``
     - Payment adjustment: Following, ModifiedFollowing, Preceding,
       ModifiedPreceding or Unadjusted.
   * - ``floor`` / ``cap``
     - No bounds
     - Annual decimal bounds on the all-in floating coupon (index plus spread),
       e.g. ``0`` / ``0.06``. Require scalar ``market_index``; incompatible with
       coupon arrays and FairRate solving.
   * - ``introductory_periods``
     - No introduction
     - Positive number of initial fixed payments; must leave at least one floating
       payment. Supply ``introductory_rate`` too on a floating loan.
   * - ``introductory_rate``
     - No introduction
     - Annual fixed coupon during the introduction; afterwards scalar ``rate``
       is a spread over ``market_index``. Incompatible with coupon arrays.
   * - ``annual_cpr``
     - No prepayment
     - Constant annual prepayment fraction, [0,1], e.g. ``0.10`` = 10% per year.
       Do not also supply dated CPRs or refinancing settings.
   * - ``base_cpr``
     - No refinancing model
     - Base annual CPR, [0,1]. Supply all three refinancing fields together and
       a benchmark index on ``QS.LOAN.PRICER``.
   * - ``incentive_multiplier``
     - No refinancing model
     - Nonnegative CPR increase per unit of positive coupon-minus-benchmark
       incentive; ``4`` adds 0.04 CPR for a 0.01 rate incentive.
   * - ``maximum_cpr``
     - No refinancing model
     - Annual CPR ceiling, [0,1], at least ``base_cpr``. Refinancing settings
       cannot be combined with constant or dated CPRs.

How prepayment rates are applied:

- With no prepayment inputs, the loan has no prepayment.
- An annual CPR is converted to a probability for each period as
  ``1 - (1 - CPR)^year_fraction``. It is not a percentage per payment.
- Dated CPRs use the latest date at or before the start of each period. Before
  the first date the rate is zero; after the last date the last rate applies.

Build a market context
----------------------

For illustrative continuous zero rates, put ordered pillars in A10:A14 and rates
in F10:F14. A pillar can be ISO text or a tenor such as 0D or 10Y.

.. code-block:: text

   B2 =QS.CONTEXT.CREATE("eur","2026-02-24","EUR","ESTR")
   B3 =QS.CONTEXT.ADD.ZERO.CURVE(B2,"ESTR",A10:A14,F10:F14,"Actual360","Linear",TRUE,"Continuous","Annual")
   B4 =QS.CONTEXT.ADD.ZERO.CURVE(B2,"EURIBOR12m",A10:A14,J10:J14,"Actual360","Linear",TRUE,"Continuous","Annual")
   H2 =B2

In this example, ESTR discounts the payments and EURIBOR12m projects the
floating coupon. The rates are for illustration only; use calibrated inputs for
production work. Each curve addition refers to B2. H2 is another reference to
the same context.

Create fixed and floating contracts
-----------------------------------

.. code-block:: text

   D2 =QS.LOAN.SETTINGS("balloon.options",0.25)
   D3 =QS.INSTRUMENT.LOAN("balloon",B2,"2026-02-24","2031-02-24","EUR",10000,0.05,,"Balloon","Monthly","Actual365",D2)
   D4 =QS.TRADE.CREATE("receipt",B2,D3,"2026-02-24","Receive")
   D5 =QS.LOAN.PRICER("loan.pricer","EUR","ESTR")
   D6 =QS.EVALUATE(H2,D4,"Value",D5)
   D7 =QS.EVALUATE(H2,D4,"FairRate(0)",D5)

- ``rate`` is the fixed coupon when ``market_index`` is blank. Otherwise it is
  the spread over the index. Both are annual decimals.
- Repayment can be French, Bullet or Balloon.
- Balloon repayment needs the residual principal fraction in Loan Settings
  (D2 above).
- A French or Balloon loan that starts with a floating coupon needs an
  amortization rate in Loan Settings. This rate is used only to build the
  principal schedule; it does not affect projected coupons.

A simple fixed-rate French loan needs only the required arguments. A floating
French loan sets its all-in amortization rate in Loan Settings, and its
``rate`` is the spread. You can pass a loan directly to ``QS.EVALUATE``, which
values it as a Receive position on the context date, or wrap it in
``QS.TRADE.CREATE`` as above.

.. code-block:: text

   F2 =QS.INSTRUMENT.LOAN("fixed",B2,"2026-02-24","2031-02-24","EUR",10000,0.05)
   F3 =QS.LOAN.SETTINGS("floating.options",,0.05)
   F4 =QS.INSTRUMENT.LOAN("floating",B2,"2026-02-24","2031-02-24","EUR",10000,0.01,"EURIBOR12m","French","Monthly","Actual365",F3)

For a stepped fixed coupon, put ``12`` and a blank in A40:A41, and ``0.03`` and
``0.05`` in F40:F41. The first 12 monthly payments use 3%; the remainder use 5%:

.. code-block:: text

   F5 =QS.INSTRUMENT.LOAN("stepped",B2,"2026-02-24","2031-02-24","EUR",10000,0.03,,,,,,A40:A41,F40:F41)

To make the second segment floating, put a blank and ``EURIBOR12m`` in J40:J41
and pass that range as ``coupon_indices``. Its ``0.05`` would then mean a 500 bp
spread, so change it to the spread you want, for example ``0.01`` for 100 bp.

IntelliSense shows the names of the optional ``QS.LOAN.SETTINGS`` arguments.
Omitted settings use the defaults in the table above.

Funding and borrower credit
---------------------------

Funding is an ordinary curve, chosen by the pricer or a discount policy. To
fund at a treasury spread, add the spread curve to the same context and combine
it with the base curve into a FUNDING index:

.. code-block:: text

   B6 =QS.CONTEXT.ADD.ZERO.CURVE(B2,"OTHER:FUNDINGSPREAD",A10:A14,N10:N14,"Actual360","Linear",TRUE,"Continuous","Annual")
   B7 =QS.CONTEXT.ADD.COMPOSITE.CURVE(B2,"OTHER:FUNDING","EURIBOR12m","OTHER:FUNDINGSPREAD")
   B8 =B2
   D8 =QS.LOAN.PRICER("funded.loan","EUR","OTHER:FUNDING")
   D9 =QS.EVALUATE(B8,D4,"Value",D8)

A composite curve multiplies the discount factors of the base and spread
curves. The funding curve is chosen when pricing, not in the loan's contract
settings.

For borrower credit, add a credit curve from CDS identifiers and spreads:

.. code-block:: text

   =QS.CONTEXT.ADD.CREDIT.CURVE(B2,"CREDIT:BORROWER","EUR","ESTR",0.4,A30:A36,F30:F36)
   =QS.DISCOUNT.POLICY.FIXED.INCOME("policy","EUR","OTHER:FUNDING")

Then set the same credit index and a matching recovery rate in Loan Settings.
Credit and prepayment change the expected future receipts. When you compare
prices or risk, compare cashflows produced with the same model settings.

Prepayment and fair-rate interpretation
---------------------------------------

Three prepayment models are available through Loan Settings: a constant annual
CPR, dated CPRs, and a refinancing model. The refinancing model needs a
benchmark index on ``QS.LOAN.PRICER``. Supplying settings for more than one
model is an error.

``FairRate(index)`` solves for the coupon or spread of one segment, numbered
from 0. It works through the segments in order:

1. For each earlier segment, it solves the rate as if the remaining principal
   were repaid at the end of that segment, then fixes that rate.
2. It then solves the requested segment.

Each evaluation returns one number, ``fair_rate``. Use a separate request for
each segment. Loans with a floor or cap cannot be solved. The pricer's
``rebuild_amortization`` option controls whether the principal schedule is
rebuilt while solving.

.. code-block:: text

   =QS.LOAN.PRICER("refinancing","EUR","OTHER:FUNDING","EURIBOR12m",TRUE)
   =QS.EVALUATE.RESULTS(H2,D4,{"Value","Cashflows","Sensitivities"},D5)

- **Value** is the signed PV of the future receipts. It does not include the
  original principal advance.
- **Cashflows** are signed, undiscounted amounts. Scheduled receipts,
  prepayments and recoveries are shown separately.
- **Sensitivities** are raw derivatives per unit change. For rates in decimals,
  multiply by 0.0001 to estimate a +1 bp change.

The loan example workbook includes fixed, floating, balloon, stepped, mixed,
credit, bounded and prepayment cases. A selector chooses which case the
cashflow and risk tabs show. The context example shows row and column inputs
and historical batch pricing. See :doc:`risk-and-history` for snapshot
selection and batch evaluation.
