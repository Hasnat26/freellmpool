from industrial_demo import build_matrix


def test_build_matrix_detects_vendor_deviation() -> None:
    matrix = build_matrix()
    deviations = [row for row in matrix if row["status"] == "DEVIATION"]

    assert len(matrix) == 8
    assert len(deviations) == 1
    assert deviations[0]["vendor"] == "Vendor B"
    assert deviations[0]["parameter"] == "Efficiency class"
    assert deviations[0]["offered"] == "IE2"
    assert deviations[0]["required"] == "IE3"
    assert deviations[0]["evidence"] == "Quotation p.2"


def test_missing_fields_are_unverified() -> None:
    matrix = build_matrix()
    assert all(row["evidence"] for row in matrix)
    assert all(
        row["status"] in {"COMPLIANT", "DEVIATION", "UNVERIFIED"}
        for row in matrix
    )
