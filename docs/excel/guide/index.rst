Excel user guide
================

The Excel add-in provides worksheet functions to build markets, define trades,
and calculate values and risk. A pricing workbook holds the inputs and links
them with formulas. When you change a quote, the market and every valuation
that depends on it recalculate. Functions that create objects return a text
handle that refers to the object.

Start with :doc:`context-first`. It shows direct pricing and historical batches.
The later pages use the same functions with explicit contracts, positions and
pricing policies. The :doc:`worksheet reference <../functions/index>` lists the
argument order, defaults, result layout, aliases and errors of every function.

.. toctree::
   :maxdepth: 2

   context-first
   workbook
   markets-and-products
   loans
   risk-and-history

The add-in requires Windows desktop Excel. The example workbooks contain the
complete inputs and formulas used in this guide.
