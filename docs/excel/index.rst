Excel
=====

`Download the Excel add-in and IntelliSense ZIP for 64-bit Windows Excel <https://jmelo11.github.io/quantsupport-excel/downloads/quantsupport-excel-windows-x64.zip>`_
or the `standalone quantsupport.xll <https://jmelo11.github.io/quantsupport-excel/downloads/quantsupport.xll>`_.

Every function has its own reference page. It lists the arguments in order,
their input types, what happens when an argument is blank, the result, the
errors, any aliases, and a link to the Rust source. The pages are generated from
the add-in's source code, so names and argument order match what Excel shows.

.. toctree::
   :maxdepth: 2

   guide/index
   Worksheet reference <functions/index>

Handles and calculation
-----------------------

Functions that create objects return a text **handle**, such as
``QSObject:PricingContext:usd:4``. Pass this cell to other functions to use the
object.

- A handle is valid only in the Excel session that created it. Reopening a
  workbook recreates its objects.
- The last number is a revision. It increases when the object's inputs change.
- A function given an out-of-date handle returns an error.
- Leave an optional argument blank only where its description allows it.

Calculation threads:

- Date, schedule and interpolation functions do not use stored objects. Excel
  can run them on several threads, and they return single values or spills.
- Functions that use stored objects run on Excel's main calculation thread.
- Each function page states which kind it is.

Errors:

- ``#VALUE!`` means an invalid input, or that building or evaluating an object
  failed.
- ``#N/A`` means a query found no result, as described on each function page.

Excel for macOS and Excel in the browser cannot load the XLL.
:doc:`guide/workbook` explains installation, how to write the formulas and a
complete valuation. Developers can also start from the
`binding README <https://github.com/jmelo11/quantsupport-excel/blob/main/README.md>`_.
