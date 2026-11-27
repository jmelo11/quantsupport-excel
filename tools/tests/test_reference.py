"""Regression checks for declarations and complete parameter documentation."""

import json
import re
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "docs/_ext"))
from api_navigation import excel_section
from excel_api import function_page, result_type, worksheet_type

ROOT = Path(__file__).resolve().parents[2]


def formulas(text):
    for match in re.finditer(r"=(QS\.[A-Z0-9.]+)\(", text):
        arguments, current, quoted, depth = [], "", False, 0
        for char in text[match.end() :]:
            if char == '"':
                quoted = not quoted
            if not quoted:
                if char in "({":
                    depth += 1
                elif char in ")}":
                    if char == ")" and depth == 0:
                        if current or arguments:
                            arguments.append(current.strip())
                        break
                    depth -= 1
                elif char == "," and depth == 0:
                    arguments.append(current.strip())
                    current = ""
                    continue
            current += char
        else:
            raise AssertionError(f"Unclosed formula: {match[0]}")
        yield match[1], arguments


class Text(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.parts = []
        self.ids = set()
        self.hrefs = []
        self.images = []
        self.feed(source)

    def handle_data(self, data):
        self.parts.append(data)

    def handle_starttag(self, tag, attrs):
        self.ids.update(value for key, value in attrs if key == "id")
        if tag == "a":
            self.hrefs.extend(value for key, value in attrs if key == "href")
        if tag == "img":
            self.images.extend(value for key, value in attrs if key == "src")

    @property
    def text(self):
        return " ".join(" ".join(self.parts).split())


class ExcelReferenceTests(unittest.TestCase):
    def test_workbook_walkthrough_uses_current_context_signature(self):
        text = (ROOT / "docs/excel/workbook.md").read_text()
        contexts = [
            args for name, args in formulas(text) if name == "QS.CONTEXT.CREATE"
        ]
        self.assertEqual(len(contexts), 1)
        self.assertEqual(contexts[0][2:4], ['"USD"', '"SOFR"'])

    @classmethod
    def setUpClass(cls):
        output = subprocess.run(
            [
                "cargo",
                "run",
                "--quiet",
                "-p",
                "quantsupport-xll",
                "--example",
                "function_catalog",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        cls.records = json.loads(output.stdout)

    def test_catalog_has_complete_symbol_and_parameter_details(self):
        self.assertEqual(len(self.records), 116)
        for record in self.records:
            with self.subTest(function=record["name"]):
                for field in (
                    "name",
                    "category",
                    "help",
                    "return_type",
                    "returns",
                    "errors",
                    "declaration",
                    "source",
                ):
                    self.assertTrue(record[field])
                self.assertNotIn("See the function description", json.dumps(record))
                for argument in record["arguments"]:
                    self.assertTrue(argument["help"])
                    self.assertTrue(worksheet_type(argument["type"]))

    def test_every_function_renders_structured_fields(self):
        for record in self.records:
            page = function_page(record)
            with self.subTest(function=record["name"]):
                self.assertIn(f".. excel:function:: {record['name']}", page)
                self.assertIn(":returns:", page)
                self.assertIn(":errors:", page)
                for argument in record["arguments"]:
                    self.assertIn(f":param {argument['name']}:", page)

    def test_ranges_are_not_automatically_optional(self):
        self.assertEqual(worksheet_type("* const XLOPER12"), "cell or range")
        self.assertEqual(worksheet_type("Option < f64 >"), "number or blank")
        for record in self.records:
            self.assertNotIn("XLOPER12", result_type(record))

    def test_simulation_vectors_are_spilled_ranges(self):
        path = next(
            record for record in self.records if record["name"] == "QS.SIMULATION.PATH"
        )
        self.assertEqual(result_type(path), "spilled range")

    def test_each_function_has_domain_and_subsection(self):
        for record in self.records:
            domain, subsection = excel_section(record["name"])
            self.assertTrue(domain)
            self.assertTrue(subsection)
        self.assertEqual(excel_section("QS.CALENDAR.HOLIDAYS"), ("Time", "Calendars"))
        self.assertEqual(
            excel_section("QS.INSTRUMENT.FIXED.RATE.BOND"),
            ("Instruments", "Fixed Income"),
        )
        for name in ("QS.ENGINE.STATUS", "QS.ENGINE.PROBE"):
            self.assertEqual(excel_section(name), ("System", "Background Pricing"))
        for name in ("QS.FORWARD.CONFIG", "QS.CONTEXT.ADVANCE"):
            self.assertEqual(excel_section(name), ("Pricing", "Forward Markets"))

    def test_interpolation_methods_have_defaults_and_math_navigation(self):
        records = {
            record["name"]: record
            for record in self.records
            if record["name"].startswith("QS.INTERPOLATE")
        }
        self.assertCountEqual(
            records,
            [
                "QS.INTERPOLATE",
                "QS.INTERPOLATE.LINEAR",
                "QS.INTERPOLATE.LOG.LINEAR",
                "QS.INTERPOLATE.CUBIC.SPLINE",
                "QS.INTERPOLATE.BILINEAR",
                "QS.INTERPOLATE.TRILINEAR",
            ],
        )
        for name, record in records.items():
            with self.subTest(function=name):
                self.assertEqual(excel_section(name), ("Math", "Interpolation"))
                self.assertEqual(record["category"], "QuantSupport - Math")
                self.assertEqual(result_type(record), "number")
                self.assertIn("#VALUE!", record["errors"])
                arguments = {
                    argument["name"]: argument for argument in record["arguments"]
                }
                policy = arguments.get(
                    "extrapolation", arguments.get("enable_extrapolation")
                )
                self.assertIn("defaults to", policy["help"])
                self.assertNotIn("\\", record["source"])
        method = next(
            argument
            for argument in records["QS.INTERPOLATE"]["arguments"]
            if argument["name"] == "method"
        )
        self.assertIn("defaults to Linear", method["help"])

    def test_guides_use_registered_formulas_and_correct_context_positions(self):
        records = {
            name: record
            for record in self.records
            for name in (record["name"], *record["aliases"])
        }
        paths = [*(ROOT / "docs/excel/guide").glob("*.rst"), ROOT / "README.md"]
        contexts = []
        count = 0
        for path in paths:
            for name, arguments in formulas(path.read_text()):
                with self.subTest(path=path.name, formula=name):
                    self.assertIn(name, records)
                    self.assertLessEqual(
                        len(arguments), len(records[name]["arguments"])
                    )
                    count += 1
                    if name == "QS.CONTEXT.CREATE":
                        self.assertIn(arguments[2], ['"USD"', '"EUR"'])
                        self.assertIn(arguments[3], ['"SOFR"', '"ESTR"'])
                        contexts.append(arguments)
        self.assertGreater(count, 70)
        self.assertGreaterEqual(len(contexts), 4)
        model_pricer = next(
            arguments
            for name, arguments in formulas(
                (ROOT / "docs/excel/guide/markets-and-products.rst").read_text()
            )
            if name == "QS.PRICER.CREATE"
            and '"ClosedFormHullWhiteSwaptionPricer"' in arguments
        )
        self.assertEqual(model_pricer[2:5], ["L3", "AC30:AC31", "AD30:AD31"])
        for name, arguments in (
            (
                "QS.EVALUATE",
                [
                    "context",
                    "instrument",
                    "request_name",
                    "pricer",
                    "policy",
                    "transpose",
                    "headers",
                ],
            ),
            (
                "QS.EVALUATE.RANGE",
                [
                    "context",
                    "instruments",
                    "request_name",
                    "pricer",
                    "policy",
                    "transpose",
                ],
            ),
            (
                "QS.EVALUATE.RESULTS",
                ["context", "trade", "requests", "pricer", "policy"],
            ),
        ):
            with self.subTest(function=name):
                self.assertEqual(
                    [a["name"] for a in records[name]["arguments"]], arguments
                )
        self.assertNotIn("QS.CONTEXT.PREPARE", records)
        self.assertNotIn("QS.CONTEXT.FROM.COMPONENTS", records)
        self.assertEqual(
            [a["name"] for a in records["QS.CONTEXT.CREATE"]["arguments"]],
            [
                "name",
                "reference_date",
                "base_currency",
                "base_index",
                "quote_level",
                "anchor_fixings",
            ],
        )

    def test_catalog_financial_units_and_range_threading_are_precise(self):
        records = {record["name"]: record for record in self.records}
        futures = records["QS.INSTRUMENT.RATE.FUTURES"]
        size = next(
            argument
            for argument in futures["arguments"]
            if argument["name"] == "contract_size"
        )
        self.assertIn("per one futures price point", size["help"])
        self.assertIn(
            "positive for receipts and negative for payments",
            records["QS.RESULT.CASHFLOWS"]["returns"],
        )
        self.assertIn("tenor text", records["QS.SIMULATION.CALIBRATION"]["returns"])
        self.assertIn(
            "includes every complete intervening year",
            records["QS.YEAR.FRACTION"]["returns"],
        )
        self.assertIn(
            "no unit conversion, interpolation", records["QS.CONTEXT.FIXING"]["returns"]
        )
        calendar = function_page(records["QS.CALENDAR.HOLIDAYS"])
        self.assertIn("Thread-safe worksheet function", calendar)
        self.assertNotIn("Thread-safe scalar", calendar)
        self.assertIn("Category: **QuantSupport - Time**", calendar)


class RenderedReferenceTests(unittest.TestCase):
    def test_strict_build_renders_real_signatures_and_fields(self):
        build_root = ROOT / "docs/_build"
        build_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(
            prefix="reference-", dir=build_root
        ) as temporary:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "sphinx",
                    "-q",
                    "-E",
                    "-a",
                    "-W",
                    "--keep-going",
                    "-b",
                    "html",
                    "docs",
                    temporary,
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            output = Path(temporary)
            self.assertFalse((output / "python").exists())
            excel = Text((output / "excel/index.html").read_text())
            workbook = Text((output / "excel/guide/workbook.html").read_text())
            downloads = "https://jmelo11.github.io/quantsupport-excel/downloads/"
            self.assertIn(downloads + "quantsupport.xll", excel.hrefs)
            self.assertIn(downloads + "quantsupport-excel-windows-x64.zip", excel.hrefs)
            for name in (
                "quantsupport.xll",
                "quantsupport-excel-windows-x64.zip",
                "swap_pricing_example.xlsx",
                "historical_pricing_example.xlsx",
            ):
                self.assertIn(downloads + name, workbook.hrefs)
            for path in (
                "excel/functions/section-time-calendars.html",
                "excel/functions/section-math-interpolation.html",
                "excel/functions/section-system-background-pricing.html",
                "excel/functions/qs-engine-status.html",
                "excel/functions/qs-engine-probe.html",
            ):
                self.assertTrue((output / path).is_file(), path)
            price = Text((output / "excel/functions/qs-evaluate.html").read_text())
            for field in ("Parameters", "Returns", "Errors"):
                self.assertRegex(price.text, field + "\\s*:")
            for error in ("#N/A", "#VALUE!"):
                self.assertIn(error, price.text)
            interpolation = Text(
                (output / "excel/functions/qs-interpolate.html").read_text()
            )
            self.assertIn("defaults to Linear", interpolation.text)
            self.assertIn("strictly increasing", interpolation.text)
            self.assertIn("#VALUE!", interpolation.text)
            self.assertEqual(
                len(list((output / "excel/functions").glob("qs-*.html"))), 116
            )
            for index in (
                "genindex.html",
                "excel-functionindex.html",
                "search.html",
                "objects.inv",
            ):
                self.assertTrue((output / index).is_file(), index)
            function_index = Text((output / "excel-functionindex.html").read_text())
            for name in (
                "QS.CONTEXT.CREATE",
                "QS.CONTEXT.ADD.QUOTE",
                "QS.EVALUATE",
                "QS.SNAPSHOT.FROM.RANGE",
            ):
                self.assertIn(name, function_index.text)
            for removed in (
                "QS.CREATE.FX.STORE",
                "QS.GET.FX.QUOTE",
                "QS.ADD.FX.QUOTE",
                "QS.STORE.RESET",
            ):
                self.assertNotIn(removed, function_index.text)


if __name__ == "__main__":
    unittest.main()
