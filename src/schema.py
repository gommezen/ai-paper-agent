from typing import List, Optional

from pydantic import BaseModel, Field


class FieldWithEvidence(BaseModel):
    text: str = Field(default_factory=str)
    evidence_pages: List[int] = Field(
        default_factory=list,
        description="Page numbers (1-indexed) supporting the text.",
    )


class ArticleSummary(BaseModel):
    citation: str = ""
    about_main_questions: FieldWithEvidence = Field(default_factory=FieldWithEvidence)
    about_purpose: FieldWithEvidence = Field(default_factory=FieldWithEvidence)
    about_theory: FieldWithEvidence = Field(default_factory=FieldWithEvidence)

    methods_design: FieldWithEvidence = Field(default_factory=FieldWithEvidence)
    methods_data_sources: FieldWithEvidence = Field(default_factory=FieldWithEvidence)
    methods_sample: FieldWithEvidence = Field(default_factory=FieldWithEvidence)
    methods_instruments: FieldWithEvidence = Field(default_factory=FieldWithEvidence)

    analysis_type: FieldWithEvidence = Field(default_factory=FieldWithEvidence)
    analysis_techniques: FieldWithEvidence = Field(default_factory=FieldWithEvidence)
    analysis_validation: FieldWithEvidence = Field(default_factory=FieldWithEvidence)

    results_core: FieldWithEvidence = Field(default_factory=FieldWithEvidence)
    results_surprising: FieldWithEvidence = Field(default_factory=FieldWithEvidence)
    results_contributions: FieldWithEvidence = Field(default_factory=FieldWithEvidence)
    results_limitations: FieldWithEvidence = Field(default_factory=FieldWithEvidence)

    future_gaps: FieldWithEvidence = Field(default_factory=FieldWithEvidence)
    future_extensions: FieldWithEvidence = Field(default_factory=FieldWithEvidence)
    future_your_ideas: FieldWithEvidence = Field(default_factory=FieldWithEvidence)

    # raw artifacts (optional)
    raw_sections: Optional[dict] = None
    raw_llm_json: Optional[dict] = None
