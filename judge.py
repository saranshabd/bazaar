from typing import Literal
from phoenix.client import Client

from langchain_google_genai import ChatGoogleGenerativeAI

from pydantic import BaseModel, Field

from prompt import get_judge_prompt
import constants

from openinference.instrumentation import suppress_tracing

phoenix_client = Client(base_url=constants.PHOENIX_CLIENT_URL)


class IncidentEvaluation(BaseModel):
    label: Literal["pass", "fail"] = Field(
        description="Whether the answer completely diagnosed the incident."
    )
    score: int = Field(
        description="A score between 0 and 1 representing the confidence in the incident report correctness."
    )
    explanation: str = Field(
        description="A concise explanation of the judgement."
    )


judge_model = (
    ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        temperature=0,
    )
    .with_structured_output(
        IncidentEvaluation,
        method="json_schema",
    )
)

judge_system_prompt_version = constants.JudgePrompts["GOOD"]


def evaluate_agent_response(span_id: str, question: str, agent_response: str) -> None:
    judge_prompt = get_judge_prompt(
        version_id=judge_system_prompt_version,
        question=question,
        agent_response=agent_response,
    )

    with suppress_tracing():
        eval_opt = judge_model.invoke(judge_prompt)

    phoenix_client.spans.add_span_annotation(
        span_id=span_id,
        annotation_name="diagnosis_completeness",
        annotator_kind="LLM",
        label=eval_opt.label,
        score=eval_opt.score,
        explanation=eval_opt.explanation,
    )
