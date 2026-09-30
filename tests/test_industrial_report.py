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


def test_render_engineering_report_includes_commercial_risk_review() -> None:
    report = build_report(
        [Requirement("R-01", "Rated voltage", "415 V")],
        [VendorValue("Vendor X", "Rated voltage", "415 V", "quote p.1", "VERIFIED")],
        [CommercialValue(
            "Vendor X", "10,500", "usd", "14 weeks", "6 months",
            "30% advance", "quote p.3", "VERIFIED"
        )],
    )
    rendered = render_engineering_report(report)
    assert "Commercial risk review" in rendered
    assert "LEAD_TIME_REVIEW" in rendered
    assert "WARRANTY_REVIEW" in rendered
    assert "not supplier rankings or selection criteria" in rendered


def test_render_engineering_report_keeps_evidence_and_review_controls_visible() -> None:
    report = build_report(
        [Requirement("R-01", "Rated voltage", "415 V")],
        [VendorValue("Vendor X", "Rated voltage", "415 V", "quote p.1", "VERIFIED")],
    )
    rendered = render_engineering_report(report)
    assert "Evidence register" in rendered
    assert "Controls and limitations" in rendered
    assert "Compliance status is calculated by the deterministic comparison engine." in rendered
