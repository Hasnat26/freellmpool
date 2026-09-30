from freellmpool.industrial import CommercialValue, Requirement, VendorValue, build_report
from freellmpool.industrial_report import render_engineering_report


def test_render_engineering_report_contains_evidence_and_controls() -> None:
    report = build_report(
        [Requirement("R-01", "Rated voltage", "415 V")],
        [VendorValue("Vendor X", "Voltage", "400 V", "quote p.1")],
        [CommercialValue("Vendor X", "10000", "USD", "8 weeks", "12 months", "30% advance", "quote p.3")],
    )
    rendered = render_engineering_report(report)
    assert "# Industrial RFQ Engineering Review" in rendered
    assert "Technical compliance matrix" in rendered
    assert "Commercial information" in rendered
    assert "Evidence register" in rendered
    assert "Engineer review actions" in rendered
    assert "does not select a supplier" in rendered
    assert "Vendor X" in rendered
    assert "quote p.1" in rendered
