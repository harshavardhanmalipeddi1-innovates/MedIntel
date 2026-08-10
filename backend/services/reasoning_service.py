import logging
from backend.app.config.settings import settings
from backend.app.schemas.reasoning_schema import (
    ClinicalReasoningRequest,
    ClinicalReasoningResponse,
)
from backend.services.local_medgemma_provider import LocalMedGemmaProvider
from backend.services.mock_reasoning_provider import MockReasoningProvider
from backend.app.modules.reasoning_engine.context_builder import ContextBuilder
from backend.app.modules.reasoning_engine.evidence_semantic_normalizer import (
    EvidenceSemanticNormalizer,
)
from backend.app.modules.reasoning_engine.prompt_builder import PromptBuilder
from backend.app.modules.reasoning_engine.response_parser import ResponseParser
from backend.app.modules.reasoning_engine.safety_validator import SafetyValidator
from backend.services.reasoning_provider import ReasoningProviderError
from pydantic import ValidationError

logger = logging.getLogger(__name__)

class ReasoningService:
    """
    Coordinates the clinical reasoning process, enforcing safety gates.
    """

    def __init__(self):
        provider_name = settings.AI_PROVIDER.strip().lower()

        if provider_name == "local":
            self.provider = LocalMedGemmaProvider()
        elif provider_name == "mock":
            self.provider = MockReasoningProvider()
        else:
            raise ValueError(
                f"Unsupported AI_PROVIDER: {settings.AI_PROVIDER!r}. "
                "Expected 'local' or 'mock'."
            )

    async def generate_reasoning(self, request: ClinicalReasoningRequest) -> ClinicalReasoningResponse:
        """
        Executes the reasoning pipeline. Returns a safe degraded result if
        the provider fails.
        """
        if not settings.AI_REASONING_ENABLED:
            return self._build_degraded_response(request, "AI Reasoning is disabled in configuration.")

        try:
            # 1. Context Building
            context_str = ContextBuilder.build_context(request)

            # 2. Prompt Building
            prompt = PromptBuilder.build_prompt(context_str)

            # 3. Model Inference
            raw_response = await self.provider.generate_reasoning(prompt)

            # 4. Parsing
            parsed_json = ResponseParser.parse(raw_response)

            # 5. Schema Validation
            response_obj = ClinicalReasoningResponse(**parsed_json)

            # 6. Deterministic evidence semantic normalization
            response_obj = EvidenceSemanticNormalizer.normalize(
                request,
                response_obj,
            )

            # 7. Safety Validation
            SafetyValidator.validate(request, response_obj)

            return response_obj

        except ReasoningProviderError:
            logger.warning("Clinical reasoning provider unavailable.")
            return self._build_degraded_response(
                request,
                "Local clinical reasoning provider is unavailable.",
            )
        except ValidationError:
            logger.warning("Clinical reasoning output failed schema validation.")
            return self._build_degraded_response(
                request,
                "Clinical reasoning output failed schema validation.",
            )
        except ValueError as exc:
            logger.warning(
                "Clinical reasoning output failed parsing or safety validation: %s",
                exc,
            )
            return self._build_degraded_response(
                request,
                "Clinical reasoning output failed safety validation.",
            )
        except Exception:
            logger.exception("Unexpected clinical reasoning service failure.")
            return self._build_degraded_response(
                request,
                "Clinical reasoning is temporarily unavailable.",
            )

    def _build_degraded_response(self, request: ClinicalReasoningRequest, reason: str) -> ClinicalReasoningResponse:
        """
        Creates a safe, degraded response when the AI reasoning pipeline fails,
        preserving the existing differential without injecting AI rationale.
        """
        return ClinicalReasoningResponse(
            candidate_reasoning=[],
            reasoning_summary=f"Reasoning unavailable: {reason}",
            limitations=["AI Reasoning engine was unavailable or failed validation.", reason],
            requires_doctor_review=True
        )
