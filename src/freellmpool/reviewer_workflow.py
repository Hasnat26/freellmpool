"""Explicit reviewer workflow state machine for Industrial RFQ Intelligence."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ReviewState(str, Enum):
    UPLOAD = "UPLOAD"
    EXTRACTION = "EXTRACTION"
    REVIEW = "REVIEW"
    REPORT = "REPORT"


_ALLOWED_TRANSITIONS = {
    ReviewState.UPLOAD: frozenset({ReviewState.EXTRACTION}),
    ReviewState.EXTRACTION: frozenset({ReviewState.REVIEW}),
    ReviewState.REVIEW: frozenset({ReviewState.REVIEW, ReviewState.REPORT}),
    ReviewState.REPORT: frozenset(),
}


@dataclass(frozen=True)
class ReviewSession:
    """Server/local-neutral reviewer session; no credentials or procurement actions."""

    session_id: str
    state: ReviewState = ReviewState.UPLOAD
    input_reference: str | None = None
    extraction_reference: str | None = None
    report_reference: str | None = None
    human_approved: bool = False

    def transition(self, target: ReviewState, *, reference: str | None = None) -> "ReviewSession":
        if target not in _ALLOWED_TRANSITIONS[self.state]:
            raise ValueError(f"invalid reviewer transition: {self.state.value} -> {target.value}")
        if target is ReviewState.EXTRACTION and not self.input_reference:
            raise ValueError("UPLOAD -> EXTRACTION requires an input_reference")
        if target is ReviewState.REVIEW and not self.extraction_reference:
            raise ValueError("EXTRACTION -> REVIEW requires an extraction_reference")
        if target is ReviewState.REPORT and not self.human_approved:
            raise ValueError("REPORT requires explicit human approval")
        return ReviewSession(
            session_id=self.session_id,
            state=target,
            input_reference=self.input_reference,
            extraction_reference=(
                reference if target is ReviewState.REVIEW else self.extraction_reference
            ),
            report_reference=reference if target is ReviewState.REPORT else self.report_reference,
            human_approved=self.human_approved,
        )

    def with_input(self, input_reference: str) -> "ReviewSession":
        if self.state is not ReviewState.UPLOAD:
            raise ValueError("input can only be attached in UPLOAD state")
        if not input_reference.strip():
            raise ValueError("input_reference must not be empty")
        return ReviewSession(self.session_id, ReviewState.UPLOAD, input_reference)

    def approve_review(self) -> "ReviewSession":
        if self.state is not ReviewState.REVIEW:
            raise ValueError("human approval is only available in REVIEW state")
        return ReviewSession(
            session_id=self.session_id,
            state=self.state,
            input_reference=self.input_reference,
            extraction_reference=self.extraction_reference,
            report_reference=self.report_reference,
            human_approved=True,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "state": self.state.value,
            "input_reference": self.input_reference,
            "extraction_reference": self.extraction_reference,
            "report_reference": self.report_reference,
            "human_approved": self.human_approved,
        }


__all__ = ["ReviewSession", "ReviewState"]
