"""Exhaustive worksheet topic navigation."""

from collections import defaultdict

from sphinx.errors import ExtensionError


def slug(title):
    return title.lower().replace(",", "").replace(" ", "-")


def excel_section(name):
    if name == "QS.LOAN.SETTINGS":
        return "Instruments", "Fixed Income"
    if name == "QS.LOAN.PRICER" or name.startswith("QS.HISTORY."):
        return "Pricing", "Valuation and Risk"
    if name == "QS.INTERPOLATE" or name.startswith("QS.INTERPOLATE."):
        return "Math", "Interpolation"
    if name.startswith("QS.CALENDAR."):
        return "Time", "Calendars"
    if name.startswith("QS.SCHEDULE"):
        return "Time", "Schedules"
    if name.startswith("QS.DATETIME.") or name in (
        "QS.DATE.ADVANCE",
        "QS.YEAR.FRACTION",
    ):
        return "Time", "Dates and Accrual"
    if name == "QS.TRADE.CREATE":
        return "Instruments", "Positions"
    if name.startswith(("QS.TRADE.", "QS.INSTRUMENT.")):
        product = name.split(".", 2)[2]
        if product in (
            "FIXED.RATE.BOND",
            "FLOATING.RATE.NOTE",
            "FIXED.RATE.DEPOSIT",
            "LOAN",
        ):
            return "Instruments", "Fixed Income"
        if product.startswith("FX."):
            return "Instruments", "Foreign Exchange"
        if product.startswith("EQUITY."):
            return "Instruments", "Equity"
        if product == "CDS":
            return "Instruments", "Credit"
        return "Instruments", "Interest Rates"
    if name in ("QS.SENSITIVITIES", "QS.BOND.SENSITIVITIES"):
        return "Risk", "Sensitivities"
    if name.startswith("QS.DISCOUNT.POLICY."):
        return "Pricing", "Discount Policies"
    if name == "QS.EVALUATE" or name.startswith(
        ("QS.EVALUATE.", "QS.RESULT.", "QS.REQUEST.", "QS.PORTFOLIO.")
    ):
        return "Pricing", "Valuation and Risk"
    if name.startswith("QS.BOND."):
        return "Pricing", "Bond Analytics"
    if name in ("QS.PRICE", "QS.FAIR.RATE", "QS.CASHFLOWS", "QS.SENSITIVITIES"):
        return "Pricing", "Valuation and Risk"
    if name.startswith("QS.FORWARD.") or name == "QS.CONTEXT.ADVANCE":
        return "Pricing", "Forward Markets"
    if name.startswith("QS.CONTEXT."):
        return "Pricing", "Contexts and Constructed Objects"
    if name.startswith(("QS.SNAPSHOT.", "QS.SNAPSHOTS.")):
        return "Market Data", "Historical Snapshots"
    if name.startswith(("QS.QUOTES.", "QS.FIXINGS.", "QS.FX.")):
        return "Market Data", "Quotes, Fixings, and FX"
    if name.startswith(("QS.CURVE.", "QS.CREDIT.CURVE.", "QS.ELEMENTS.")):
        return "Market Data", "Curves and Construction"
    if name.startswith("QS.VOL."):
        return "Market Data", "Volatility"
    if name.startswith("QS.SIMULATION."):
        return "Market Data", "Simulation"
    if name.startswith("QS.PRICER."):
        return "Pricing", "Pricer Configuration"
    if name.startswith("QS.SCENARIOS."):
        return "Risk", "Scenarios"
    if name.startswith("QS.OBJECT."):
        return "System", "Object Lifecycle"
    if name.startswith("QS.ENGINE."):
        return "System", "Background Pricing"
    if name in ("QS.FUNCTIONS", "QS.FUNCTIONS.DETAILS", "QS.HELP", "QS.VERSION"):
        return "System", "Catalog and Help"
    raise ExtensionError(f"Uncategorized worksheet function: {name}")


def write_excel_navigation(output, records):
    groups = defaultdict(lambda: defaultdict(list))
    for record in records:
        domain, section = excel_section(record["name"])
        groups[domain][section].append(record["name"])
    index = [
        "Function Categories",
        "===================",
        "",
        ".. toctree::",
        "   :maxdepth: 2",
        "",
    ]
    for domain, sections in sorted(groups.items()):
        domain_slug = f"section-{slug(domain)}"
        index.append(f"   {domain} <{domain_slug}>")
        lines = [domain, "=" * len(domain), "", ".. toctree::", "   :maxdepth: 1", ""]
        for title, functions in sorted(sections.items()):
            section_slug = f"{domain_slug}-{slug(title)}"
            lines.append(f"   {title} <{section_slug}>")
            content = [
                title,
                "=" * len(title),
                "",
                ".. toctree::",
                "   :maxdepth: 1",
                "",
            ]
            content.extend(
                f"   {name} <{name.lower().replace('.', '-')}>"
                for name in sorted(functions)
            )
            (output / f"{section_slug}.rst").write_text(
                "\n".join(content) + "\n", encoding="utf-8"
            )
        (output / f"{domain_slug}.rst").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )
    (output / "index.rst").write_text("\n".join(index) + "\n", encoding="utf-8")
