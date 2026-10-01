"""Explicit reviewer workflow state machine for Industrial RFQ Intelligence."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ReviewState(str, Enum):
    """States in the human-reviewed RFQ workflow."""

    UPLOAD = "UPLOAD"
    EXTRACTION = "EXTRACTION"
    REVIEW = "REVIEW"
    REPORT = "REPORT"


_ALLOWED_TRANSITIONS = {
    ReviewState.UPLOAD: frozenset({ReviewState.EXTRACTION}),
    ReviewState.EXTRACTION: frozenset({ReviewState.REVIEW}),
    ReviewState.REVIEW: frozenset(
        {
            ReviewState.REVIEW,
            ReviewState.REPORT,
        }
    ),
    ReviewState.REPORT: frozenset(),
}


@dataclass(frozen=True)
class ReviewSession:
    """
    Server/local-neutral reviewer session.

    The workflow deliberately contains no credentials, procurement actions,
    supplier-selection logic, or autonomous engineering decisions.
    """

    session_id: str
    state: ReviewState = ReviewState.UPLOAD
    input_reference: str | None = None
    extraction_reference: str | None = None
    report_reference: str | None = None
    human_approved: bool = False

    def transition(
        self,
        target: ReviewState,
        *,
        reference: str | None = None,
    ) -> "ReviewSession":
        """Move the session to an allowed state with required references."""

        if target not in _ALLOWED_TRANSITIONS[self.state]:
            raise ValueError(
                f"invalid reviewer transition: "
                f"{self.state.value} -> {target.value}"
            )

        if target is ReviewState.EXTRACTION:
            if not self.input_reference:
                raise ValueError(
                    "UPLOAD -> EXTRACTION requires an input_reference"
                )

            return ReviewSession(
                session_id=self.session_id,
                state=ReviewState.EXTRACTION,
                input_reference=self.input_reference,
                extraction_reference=self.extraction_reference,
                report_reference=self.report_reference,
                human_approved=self.human_approved,
            )

        if target is ReviewState.REVIEW:
            extraction_reference = (
                reference.strip()
                if reference is not None
                else self.extraction_reference
            )

            if not extraction_reference:
                raise ValueError(
                    "EXTRACTION -> REVIEW requires an extraction_reference"
                )

            return ReviewSession(
                session_id=self.session_id,
                state=ReviewState.REVIEW,
                input_reference=self.input_reference,
                extraction_reference=extraction_reference,
                report_reference=self.report_reference,
                human_approved=self.human_approved,
            )

        if target is ReviewState.REPORT:
            if not self.human_approved:
                raise ValueError("REPORT requires explicit human approval")

            report_reference = (
                reference.strip()
                if reference is not None
                else self.report_reference
            )

            if not report_reference:
                raise ValueError(
                    "REVIEW -> REPORT requires a report_reference"
                )

            return ReviewSession(
                session_id=self.session_id,
                state=ReviewState.REPORT,
                input_reference=self.input_reference,
                extraction_reference=self.extraction_reference,
                report_reference=report_reference,
                human_approved=self.human_approved,
            )

        raise ValueError(
            f"unsupported reviewer transition target: {target.value}"
        )

    def with_input(self, input_reference: str) -> "ReviewSession":
        """Attach the source RFQ reference during the upload state."""

        if self.state is not ReviewState.UPLOAD:
            raise ValueError("input can only be attached in UPLOAD state")

        cleaned_reference = input_reference.strip()
        if not cleaned_reference:
            raise ValueError("input_reference must not be empty")

        return ReviewSession(
            session_id=self.session_id,
            state=ReviewState.UPLOAD,
            input_reference=cleaned_reference,
            extraction_reference=None,
            report_reference=None,
            human_approved=False,
        )

    def approve_review(self) -> "ReviewSession":
        """Record explicit human approval while remaining in REVIEW."""

        if self.state is not ReviewState.REVIEW:
            raise ValueError(
                "human approval is only available in REVIEW state"
            )

        return ReviewSession(
            session_id=self.session_id,
            state=ReviewState.REVIEW,
            input_reference=self.input_reference,
            extraction_reference=self.extraction_reference,
            report_reference=self.report_reference,
            human_approved=True,
        )

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the session."""

        return {
            "session_id": self.session_id,
            "state": self.state.value,
            "input_reference": self.input_reference,
            "extraction_reference": self.extraction_reference,
            "report_reference": self.report_reference,
            "human_approved": self.human_approved,
        }


__all__ = ["ReviewSession", "ReviewState"]