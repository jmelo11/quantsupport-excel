# Download and install

**[Download the Excel add-in and IntelliSense ZIP for 64-bit Windows
Excel](https://jmelo11.github.io/quantsupport-excel/downloads/quantsupport-excel-windows-x64.zip)**

The ZIP includes `quantsupport.xll`, its matching XML metadata,
`ExcelDna.IntelliSense64.xll`, installation instructions and license notices.
The [standalone XLL](https://jmelo11.github.io/quantsupport-excel/downloads/quantsupport.xll)
is in the same download directory.

Older versions are available from the
[release history](https://github.com/jmelo11/quantsupport-excel/releases).
Excel for macOS and Excel in the browser cannot load an XLL.

1. Extract all files from the ZIP into a stable local folder.
2. In Excel open **File > Options > Add-ins**.
3. Select **Excel Add-ins**, click **Go**, then **Browse**, and load both XLLs.
   Keep `quantsupport.intellisense.xml` beside `quantsupport.xll`, then restart Excel.
4. Enter `=QS.VERSION()` to check that it loaded.
5. Open the [swap example workbook](https://jmelo11.github.io/quantsupport-excel/downloads/swap_pricing_example.xlsx)
   and press **Ctrl+Alt+F9** to rebuild its object handles.

The workbook includes pricing, curve tables, cashflows, and sensitivities.

## Discover functions

- `=QS.FUNCTIONS()` lists all function names.
- `=QS.FUNCTIONS.DETAILS()` spills the full function catalog.
- `=QS.HELP("QS.INSTRUMENT.SWAP")` shows a function's argument help in cells.

The same help appears in Excel's Function Arguments dialog and in the
[worksheet
reference](https://jmelo11.github.io/quantsupport-excel/excel/functions/index.html).

To see argument hints **while typing**:

1. Load `ExcelDna.IntelliSense64.xll` from the ZIP together with QuantSupport.
2. Keep `quantsupport.intellisense.xml` next to `quantsupport.xll`.
3. Restart Excel with both add-ins enabled.
4. Type `=QS.EVALUATE` followed by an opening parenthesis. The signature and
   help for the current argument appear.

The IntelliSense add-in needs .NET Framework 4.6.2 or later. Without it, type
the function name and press **Ctrl+A** for the Function Arguments dialog, or
**Ctrl+Shift+A** to insert the argument names.

Date functions can run on several calculation threads. Functions that create or
price objects run on Excel's main thread.

## Build from source

On Windows, install the 64-bit MSVC Rust toolchain and Visual Studio Build Tools,
then run from the repository root:

```powershell
rustup target add x86_64-pc-windows-msvc
powershell -ExecutionPolicy Bypass -File tools/excel/build.ps1
```

The build creates `dist/quantsupport-excel-windows-x64.zip` and the individual
XLL, XML and companion files. It downloads a fixed
[Excel-DNA IntelliSense](https://github.com/Excel-DNA/IntelliSense/releases)
release and checks its SHA-256 hash. If you move the add-in, move all the files
together.
