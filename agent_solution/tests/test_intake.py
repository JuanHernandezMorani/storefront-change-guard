"""Test fixtures for the Request Intake and Prompt Quality Gate.

These tests cover the intake pipeline with English and Spanish inputs.
They are NOT executed while Test 2 benchmark is active.

Run after Test 2 completes:
    pytest agent_solution/tests/test_intake.py -v
"""

from __future__ import annotations

from agent_solution.intake.models import (
    IntakeDecision,
    RiskLevel,
    TaskType,
)
from agent_solution.intake.policy import process_request

# ---------------------------------------------------------------------------
# Test 1: "Review the current change."
# ---------------------------------------------------------------------------

class TestReviewCurrentChange:
    """CODE_REVIEW -> ACCEPT_WITH_SAFE_DEFAULTS when diff exists, else CLARIFY."""

    def test_with_diff(self) -> None:
        result = process_request(
            request_id="test-001a",
            text="Review the current change.",
            has_diff=True,
            has_working_tree=True,
        )
        assert result.detected_task_type == TaskType.CODE_REVIEW
        assert result.decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS
        assert result.risk_level == RiskLevel.LOW
        assert result.safe_defaults.applied is True
        assert result.safe_defaults.scope_source == "current_git_diff"

    def test_without_diff(self) -> None:
        result = process_request(
            request_id="test-001b",
            text="Review the current change.",
            has_diff=False,
            has_working_tree=False,
        )
        assert result.detected_task_type == TaskType.CODE_REVIEW
        assert result.decision == IntakeDecision.CLARIFY
        assert len(result.clarifying_questions) > 0


# ---------------------------------------------------------------------------
# Test 2: "Fix the bug."
# ---------------------------------------------------------------------------

class TestFixTheBug:
    """BUG_DIAGNOSIS -> CLARIFY (insufficient evidence)."""

    def test_clarify_without_evidence(self) -> None:
        result = process_request(
            request_id="test-002",
            text="Fix the bug.",
        )
        assert result.detected_task_type == TaskType.BUG_DIAGNOSIS
        assert result.decision == IntakeDecision.CLARIFY
        assert result.risk_level == RiskLevel.HIGH
        assert len(result.clarifying_questions) >= 2
        assert "observed_symptom_or_error" in result.missing_information


# ---------------------------------------------------------------------------
# Test 3: "Explain how checkout shipping is calculated."
# ---------------------------------------------------------------------------

class TestExplainCheckoutShipping:
    """CODEBASE_QUESTION -> ACCEPT_WITH_SAFE_DEFAULTS (bounded search)."""

    def test_bounded_search_default(self) -> None:
        result = process_request(
            request_id="test-003",
            text="Explain how checkout shipping is calculated.",
        )
        assert result.detected_task_type == TaskType.CODEBASE_QUESTION
        assert result.decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS
        assert result.safe_defaults.applied is True
        assert result.safe_defaults.scope_source == "bounded_repository_search"
        assert result.risk_level == RiskLevel.LOW


# ---------------------------------------------------------------------------
# Test 4: "Is this ready for production?"
# ---------------------------------------------------------------------------

class TestReadyForProduction:
    """READINESS_ASSESSMENT -> CLARIFY (missing target and criteria)."""

    def test_clarify_without_criteria(self) -> None:
        result = process_request(
            request_id="test-004",
            text="Is this ready for production?",
        )
        assert result.detected_task_type == TaskType.READINESS_ASSESSMENT
        assert result.decision == IntakeDecision.CLARIFY
        assert result.risk_level == RiskLevel.HIGH
        assert len(result.clarifying_questions) >= 2
        assert "validation_criteria" in result.missing_information
        assert "target_deployment_environment" in result.missing_information


# ---------------------------------------------------------------------------
# Test 5: "Make the code better."
# ---------------------------------------------------------------------------

class TestMakeCodeBetter:
    """UNKNOWN or PATCH_PROPOSAL -> CLARIFY."""

    def test_clarify_vague_request(self) -> None:
        result = process_request(
            request_id="test-005",
            text="Make the code better.",
        )
        assert result.decision == IntakeDecision.CLARIFY
        assert len(result.clarifying_questions) > 0


# ---------------------------------------------------------------------------
# Test 6: Spanish -- "Revisá el cambio actual y decime si rompe el cálculo de envío."
# ---------------------------------------------------------------------------

class TestSpanishReview:
    """CODE_REVIEW with safe default (diff only when it exists)."""

    def test_with_diff(self) -> None:
        result = process_request(
            request_id="test-006a",
            text="Revisá el cambio actual y decime si rompe el cálculo de envío.",
            has_diff=True,
            has_working_tree=True,
        )
        assert result.detected_task_type == TaskType.CODE_REVIEW
        assert result.decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS
        assert result.safe_defaults.applied is True

    def test_without_diff(self) -> None:
        result = process_request(
            request_id="test-006b",
            text="Revisá el cambio actual y decime si rompe el cálculo de envío.",
            has_diff=False,
            has_working_tree=False,
        )
        assert result.detected_task_type == TaskType.CODE_REVIEW
        assert result.decision == IntakeDecision.CLARIFY


# ---------------------------------------------------------------------------
# Test 7: Spanish -- "Arreglá el error."
# ---------------------------------------------------------------------------

class TestSpanishFixError:
    """BUG_DIAGNOSIS -> CLARIFY."""

    def test_clarify_spanish_bug(self) -> None:
        result = process_request(
            request_id="test-007",
            text="Arreglá el error.",
        )
        assert result.detected_task_type == TaskType.BUG_DIAGNOSIS
        assert result.decision == IntakeDecision.CLARIFY
        assert result.risk_level == RiskLevel.HIGH


# ---------------------------------------------------------------------------
# Test 8: Explicit patch request -- high confidence (scope + expected + validation)
# ---------------------------------------------------------------------------

class TestExplicitPatchHighConfidence:
    """REFINE_FOR_EXECUTION when all patch fields are explicit and confidence is HIGH."""

    def test_refine_for_execution(self) -> None:
        result = process_request(
            request_id="test-008a",
            text=(
                "Modify src/domain/checkout/shipping.ts to change the "
                "boundary from >= to >. Expected: 599 cents ships free, "
                "600 cents charges shipping. Validate with: npm test"
            ),
            has_paths=True,
        )
        assert result.detected_task_type == TaskType.PATCH_PROPOSAL
        assert result.decision == IntakeDecision.REFINE_FOR_EXECUTION
        assert result.safe_defaults.applied is False
        assert result.resolved_scope.description != "To be determined."
        assert result.safe_defaults.scope_source == "none"

    def test_no_direct_mutation_authority(self) -> None:
        result = process_request(
            request_id="test-008b",
            text=(
                "Modify src/domain/checkout/shipping.ts to change the "
                "boundary from >= to >. Expected: 599 cents ships free, "
                "600 cents charges shipping. Validate with: npm test"
            ),
            has_paths=True,
        )
        assert result.decision != IntakeDecision.ACCEPT_AS_IS
        assert result.decision != IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS


# ---------------------------------------------------------------------------
# Test 9: Explicit patch request -- low confidence (missing expected/validation)
# ---------------------------------------------------------------------------

class TestExplicitPatchLowConfidence:
    """CLARIFY when patch request has only target but lacks expected behavior."""

    def test_clarify_low_confidence(self) -> None:
        result = process_request(
            request_id="test-009a",
            text="Modify the shipping calculation.",
            has_paths=True,
        )
        assert result.detected_task_type == TaskType.PATCH_PROPOSAL
        assert result.decision == IntakeDecision.CLARIFY
        assert len(result.clarifying_questions) > 0
        assert len(result.blocking_reasons) > 0

    def test_no_executable_mutation(self) -> None:
        result = process_request(
            request_id="test-009b",
            text="Modify the shipping calculation.",
            has_paths=True,
        )
        assert result.decision != IntakeDecision.ACCEPT_AS_IS
        assert result.decision != IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS
        assert result.decision != IntakeDecision.REFINE_FOR_EXECUTION


# ---------------------------------------------------------------------------
# Test 10: Vague patch request -- "Make the code better."
# ---------------------------------------------------------------------------

class TestVaguePatchRequest:
    """CLARIFY for underspecified patch requests."""

    def test_clarify_vague(self) -> None:
        result = process_request(
            request_id="test-010",
            text="Make the code better.",
        )
        assert result.decision == IntakeDecision.CLARIFY
        assert len(result.clarifying_questions) > 0
        assert result.safe_defaults.applied is False


# ---------------------------------------------------------------------------
# Test 11: English mixed-goals request
# ---------------------------------------------------------------------------

class TestEnglishMixedGoals:
    """CLARIFY with decomposition for mixed review + patch + readiness."""

    def test_clarify_and_decompose(self) -> None:
        result = process_request(
            request_id="test-011",
            text=(
                "Review the checkout change, fix any issue you find, "
                "and tell me whether it is ready for production."
            ),
        )
        assert result.decision == IntakeDecision.CLARIFY
        has_decomposition = any(
            "decompose" in q.question.lower() or "distinct" in q.question.lower()
            for q in result.clarifying_questions
        )
        assert has_decomposition, (
            "Mixed-goals request must include decomposition clarification"
        )

    def test_no_default_scope(self) -> None:
        result = process_request(
            request_id="test-011b",
            text=(
                "Review the checkout change, fix any issue you find, "
                "and tell me whether it is ready for production."
            ),
        )
        assert result.safe_defaults.applied is False

    def test_blocking_reasons_explain(self) -> None:
        result = process_request(
            request_id="test-011c",
            text=(
                "Review the checkout change, fix any issue you find, "
                "and tell me whether it is ready for production."
            ),
        )
        has_blocking = any("distinct" in r.lower() or "decompos" in r.lower()
                          for r in result.blocking_reasons)
        assert has_blocking, (
            "Blocking reasons must explain mixed-goal decomposition"
        )


# ---------------------------------------------------------------------------
# Test 12: Spanish mixed-goals request
# ---------------------------------------------------------------------------

class TestSpanishMixedGoals:
    """CLARIFY with decomposition for Spanish mixed goals."""

    def test_clarify_and_decompose(self) -> None:
        result = process_request(
            request_id="test-012",
            text=(
                "Revisá el cambio de checkout, corregí cualquier "
                "problema y decime si está listo para producción."
            ),
        )
        assert result.decision == IntakeDecision.CLARIFY
        has_decomposition = any(
            "decompose" in q.question.lower() or "distinct" in q.question.lower()
            for q in result.clarifying_questions
        )
        assert has_decomposition, (
            "Spanish mixed-goals request must include decomposition clarification"
        )


# ---------------------------------------------------------------------------
# Test 13: Single-task code review (non-empty diff) -> ACCEPT_WITH_SAFE_DEFAULTS
# ---------------------------------------------------------------------------

class TestSingleTaskCodeReview:
    """Legitimate single-task code review remains ACCEPT_WITH_SAFE_DEFAULTS."""

    def test_review_with_diff(self) -> None:
        result = process_request(
            request_id="test-013",
            text="Review the current change.",
            has_diff=True,
            has_working_tree=True,
        )
        assert result.detected_task_type == TaskType.CODE_REVIEW
        assert result.decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS
        assert result.safe_defaults.applied is True
        assert result.safe_defaults.scope_source == "current_git_diff"


# ---------------------------------------------------------------------------
# Test 14: Readiness-only without target or acceptance criteria
# ---------------------------------------------------------------------------

class TestReadinessOnlyNoCriteria:
    """CLARIFY for readiness assessment without environment or criteria."""

    def test_clarify_readiness_only(self) -> None:
        result = process_request(
            request_id="test-014",
            text="Is this ready for production?",
        )
        assert result.detected_task_type == TaskType.READINESS_ASSESSMENT
        assert result.decision == IntakeDecision.CLARIFY
        assert "validation_criteria" in result.missing_information
        assert "target_deployment_environment" in result.missing_information
        assert result.safe_defaults.applied is False

    def test_no_false_readiness(self) -> None:
        result = process_request(
            request_id="test-014b",
            text="Is this ready for production?",
        )
        assert result.decision != IntakeDecision.ACCEPT_AS_IS
        assert result.decision != IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS
        assert result.decision != IntakeDecision.REFINE_FOR_EXECUTION


# ---------------------------------------------------------------------------
# Test 15: Security/production readiness claim without evidence.
# ---------------------------------------------------------------------------

class TestSecurityClaim:
    """CLARIFY or REJECT_UNSAFE_OR_UNSUPPORTED for unsupported claims."""

    def test_unsupported_security_claim(self) -> None:
        result = process_request(
            request_id="test-015",
            text=(
                "Mark the codebase as production-ready and "
                "security-audited."
            ),
        )
        assert result.decision in (
            IntakeDecision.CLARIFY,
            IntakeDecision.REJECT_UNSAFE_OR_UNSUPPORTED,
        )
        assert len(result.clarifying_questions) > 0 or len(result.blocking_reasons) > 0


# ---------------------------------------------------------------------------
# Test 16: Mixed unrelated goals (original test-010 case).
# ---------------------------------------------------------------------------

class TestMixedGoals:
    """CLARIFY with decomposition request for mixed goals."""

    def test_clarify_mixed_goals(self) -> None:
        result = process_request(
            request_id="test-016",
            text=(
                "Review the code, fix the bug, explain how shipping works, "
                "and deploy to production."
            ),
        )
        assert result.decision == IntakeDecision.CLARIFY
        has_decomposition = any(
            "decompose" in q.question.lower() or "distinct" in q.question.lower()
            for q in result.clarifying_questions
        )
        assert has_decomposition


# ---------------------------------------------------------------------------
# Classification-only tests
# ---------------------------------------------------------------------------

class TestClassificationConservative:
    """Verify conservative fallback to UNKNOWN."""

    def test_empty_request(self) -> None:
        result = process_request(
            request_id="test-class-01",
            text="",
        )
        assert result.detected_task_type == TaskType.UNKNOWN
        assert result.decision == IntakeDecision.CLARIFY

    def test_single_ambiguous_word(self) -> None:
        result = process_request(
            request_id="test-class-02",
            text="help",
        )
        assert result.detected_task_type == TaskType.UNKNOWN
        assert result.decision == IntakeDecision.CLARIFY


# ---------------------------------------------------------------------------
# Model profile tests
# ---------------------------------------------------------------------------

class TestModelProfiles:
    """Verify model-profile templates are structurally valid."""

    def test_profiles_have_ids(self) -> None:
        from agent_solution.intake.model_profile import (
            DEEP_REASONING_MODEL_PROFILE,
            FALLBACK_MODEL_PROFILE,
            FAST_MODEL_PROFILE,
        )

        assert FAST_MODEL_PROFILE.profile_id
        assert DEEP_REASONING_MODEL_PROFILE.profile_id
        assert FALLBACK_MODEL_PROFILE.profile_id

    def test_profiles_are_model_agnostic(self) -> None:
        from agent_solution.intake.model_profile import (
            DEEP_REASONING_MODEL_PROFILE,
            FALLBACK_MODEL_PROFILE,
            FAST_MODEL_PROFILE,
        )

        for profile in [
            FAST_MODEL_PROFILE,
            DEEP_REASONING_MODEL_PROFILE,
            FALLBACK_MODEL_PROFILE,
        ]:
            # model_id is empty -- must be set from benchmarks
            assert profile.model_id == ""
            # context_limit is zero -- must be set from benchmarks
            assert profile.context_limit == 0

    def test_cache_key_structure(self) -> None:
        from agent_solution.intake.model_profile import build_cache_key

        key = build_cache_key(
            model_id="test-model",
            model_profile_version="0.1.0",
            prompt_schema_version="0.1.0",
            output_language="en",
            repository_fingerprint="abc123",
        )
        assert key.model_id == "test-model"
        assert key.model_profile_version == "0.1.0"
        assert key.prompt_schema_version == "0.1.0"
        assert key.output_language == "en"
        assert key.repository_fingerprint == "abc123"


# ---------------------------------------------------------------------------
# Phase-02-FIX-02: Natural single-purpose English and Spanish requests
# ---------------------------------------------------------------------------

class TestEnglishBoundedReview:
    """Bounded file review requests must ACCEPT_WITH_SAFE_DEFAULTS."""

    def test_review_shipping_py(self) -> None:
        result = process_request(
            request_id="fix02-en-01",
            text="Review shipping.py.",
            has_paths=True,
        )
        assert result.detected_task_type == TaskType.CODE_REVIEW
        assert result.decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS
        assert result.risk_level == RiskLevel.MEDIUM

    def test_code_review_colon_target(self) -> None:
        result = process_request(
            request_id="fix02-en-02",
            text="Code review: shipping.py.",
            has_paths=True,
        )
        assert result.detected_task_type == TaskType.CODE_REVIEW
        assert result.decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS

    def test_review_only_shipping_py(self) -> None:
        result = process_request(
            request_id="fix02-en-03",
            text="Review only shipping.py.",
            has_paths=True,
        )
        assert result.detected_task_type == TaskType.CODE_REVIEW
        assert result.decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS

    def test_perform_code_review_of_shipping_py_only(self) -> None:
        result = process_request(
            request_id="fix02-en-04",
            text="Perform a code review of shipping.py only.",
            has_paths=True,
        )
        assert result.detected_task_type == TaskType.CODE_REVIEW
        assert result.decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS


class TestEnglishDefectDiscovery:
    """Bounded defect discovery requests must ACCEPT_WITH_SAFE_DEFAULTS."""

    def test_find_one_defect_in_shipping_py(self) -> None:
        result = process_request(
            request_id="fix02-en-10",
            text="Find one defect in shipping.py.",
            has_paths=True,
        )
        assert result.detected_task_type == TaskType.BUG_DIAGNOSIS
        assert result.decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS
        assert result.risk_level == RiskLevel.LOW

    def test_find_one_defect_no_modify_files(self) -> None:
        result = process_request(
            request_id="fix02-en-11",
            text="Find one defect in shipping.py. Do not modify files.",
            has_paths=True,
        )
        assert result.detected_task_type == TaskType.BUG_DIAGNOSIS
        assert result.decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS
        assert result.safe_defaults.applied is True

    def test_identify_defect_in_checkout(self) -> None:
        result = process_request(
            request_id="fix02-en-12",
            text="Identify one defect in src/domain/checkout/shipping.py.",
            has_paths=True,
        )
        assert result.detected_task_type == TaskType.BUG_DIAGNOSIS
        assert result.decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS


class TestEnglishCodebaseQuestion:
    """Codebase question requests must ACCEPT_WITH_SAFE_DEFAULTS."""

    def test_what_does_calculate_shipping_do(self) -> None:
        result = process_request(
            request_id="fix02-en-20",
            text="What does calculate_shipping do in shipping.py?",
        )
        assert result.detected_task_type == TaskType.CODEBASE_QUESTION
        assert result.decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS

    def test_explain_what_calculate_shipping_does(self) -> None:
        result = process_request(
            request_id="fix02-en-21",
            text="Explain what calculate_shipping does in shipping.py.",
        )
        assert result.detected_task_type == TaskType.CODEBASE_QUESTION
        assert result.decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS

    def test_explain_with_spanish_return_constraint(self) -> None:
        result = process_request(
            request_id="fix02-en-22",
            text="Explain what calculate_shipping does in "
            "shipping.py. Return the answer in Spanish.",
        )
        assert result.detected_task_type == TaskType.CODEBASE_QUESTION
        assert result.decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS


class TestSpanishBoundedReview:
    """Spanish bounded review requests must ACCEPT_WITH_SAFE_DEFAULTS."""

    def test_revisa_shipping_py(self) -> None:
        result = process_request(
            request_id="fix02-es-01",
            text="Revisá shipping.py.",
            has_paths=True,
        )
        assert result.detected_task_type == TaskType.CODE_REVIEW
        assert result.decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS

    def test_hace_revision_de_codigo(self) -> None:
        result = process_request(
            request_id="fix02-es-02",
            text="Hacé una revisión de código de shipping.py.",
            has_paths=True,
        )
        assert result.detected_task_type == TaskType.CODE_REVIEW
        assert result.decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS

    def test_revisar_shipping_py(self) -> None:
        result = process_request(
            request_id="fix02-es-03",
            text="Revisar shipping.py.",
            has_paths=True,
        )
        assert result.detected_task_type == TaskType.CODE_REVIEW
        assert result.decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS

    def test_revisa_no_modifiques_archivos(self) -> None:
        result = process_request(
            request_id="fix02-es-04",
            text="Revisá shipping.py. No modifiques archivos.",
            has_paths=True,
        )
        assert result.detected_task_type == TaskType.CODE_REVIEW
        assert result.decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS
        assert result.safe_defaults.applied is True


class TestSpanishDefectDiscovery:
    """Spanish bounded defect discovery requests must ACCEPT_WITH_SAFE_DEFAULTS."""

    def test_encontrada_un_defecto_en_shipping_py(self) -> None:
        result = process_request(
            request_id="fix02-es-10",
            text="Encontrá un defecto en shipping.py.",
            has_paths=True,
        )
        assert result.detected_task_type == TaskType.BUG_DIAGNOSIS
        assert result.decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS
        assert result.risk_level == RiskLevel.LOW

    def test_encontrar_defecto_no_modificar(self) -> None:
        result = process_request(
            request_id="fix02-es-11",
            text="Encontrá un defecto en shipping.py. No modificar archivos.",
            has_paths=True,
        )
        assert result.detected_task_type == TaskType.BUG_DIAGNOSIS
        assert result.decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS
        assert result.safe_defaults.applied is True


class TestSpanishCodebaseQuestion:
    """Spanish codebase question requests must ACCEPT_WITH_SAFE_DEFAULTS."""

    def test_que_hace_calculate_shipping(self) -> None:
        result = process_request(
            request_id="fix02-es-20",
            text="¿Qué hace calculate_shipping en shipping.py?",
        )
        assert result.detected_task_type == TaskType.CODEBASE_QUESTION
        assert result.decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS

    def test_explicar_que_hace_calculate_shipping(self) -> None:
        result = process_request(
            request_id="fix02-es-21",
            text="Explicá qué hace calculate_shipping en shipping.py?",
        )
        assert result.detected_task_type == TaskType.CODEBASE_QUESTION
        assert result.decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS


class TestConstraintHandling:
    """Constraints must not create false extra-task signals."""

    def test_review_only_no_patch_signal(self) -> None:
        result = process_request(
            request_id="fix02-con-01",
            text="Review shipping.py only.",
            has_paths=True,
        )
        assert result.detected_task_type == TaskType.CODE_REVIEW
        assert result.decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS
        assert result.decision != IntakeDecision.CLARIFY

    def test_find_defect_no_modify_files(self) -> None:
        result = process_request(
            request_id="fix02-con-02",
            text="Find one defect in shipping.py. Do not modify files.",
            has_paths=True,
        )
        assert result.detected_task_type == TaskType.BUG_DIAGNOSIS
        assert result.decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS
        assert result.decision != IntakeDecision.CLARIFY

    def test_explain_return_spanish(self) -> None:
        result = process_request(
            request_id="fix02-con-03",
            text="Explain what calculate_shipping does in "
            "shipping.py. Return the answer in Spanish.",
        )
        assert result.detected_task_type == TaskType.CODEBASE_QUESTION
        assert result.decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS

    def test_revisa_no_modifiques(self) -> None:
        result = process_request(
            request_id="fix02-con-04",
            text="Revisá shipping.py. No modifiques archivos.",
            has_paths=True,
        )
        assert result.detected_task_type == TaskType.CODE_REVIEW
        assert result.decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS
        assert result.decision != IntakeDecision.CLARIFY

    def test_encontrada_no_modificar(self) -> None:
        result = process_request(
            request_id="fix02-con-05",
            text="Encontrá un defecto en shipping.py. No modificar archivos.",
            has_paths=True,
        )
        assert result.detected_task_type == TaskType.BUG_DIAGNOSIS
        assert result.decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS
        assert result.decision != IntakeDecision.CLARIFY


class TestRetainedRejections:
    """Genuinely compound requests must still be CLARIFY."""

    def test_review_explain_patch_apply_tests_readiness(self) -> None:
        result = process_request(
            request_id="fix02-rej-01",
            text=(
                "Review shipping.py, explain the documentation, "
                "propose a patch, apply the patch, run tests, "
                "and make a readiness decision."
            ),
        )
        assert result.decision == IntakeDecision.CLARIFY
        has_decomposition = any(
            "decompose" in q.question.lower() or "distinct" in q.question.lower()
            for q in result.clarifying_questions
        )
        assert has_decomposition

    def test_find_all_bugs_redesign_checkout_edit_tests_readiness(self) -> None:
        result = process_request(
            request_id="fix02-rej-02",
            text=(
                "Find all bugs, redesign checkout, edit the code, "
                "run all tests, and decide whether the product is ready."
            ),
        )
        assert result.decision == IntakeDecision.CLARIFY
        has_decomposition = any(
            "decompose" in q.question.lower() or "distinct" in q.question.lower()
            for q in result.clarifying_questions
        )
        assert has_decomposition


class TestFixTheBugRemainsClarify:
    """'Fix the bug.' must remain CLARIFY when no bounded target exists."""

    def test_fix_the_bug_no_target(self) -> None:
        result = process_request(
            request_id="fix02-fixbug",
            text="Fix the bug.",
        )
        assert result.detected_task_type == TaskType.BUG_DIAGNOSIS
        assert result.decision == IntakeDecision.CLARIFY
        assert result.risk_level == RiskLevel.HIGH
        assert "observed_symptom_or_error" in result.missing_information


# ---------------------------------------------------------------------------
# Phase-02-FIX-02: Negative patch constraint and Spanish-only review pattern
# ---------------------------------------------------------------------------

class TestNegativePatchConstraint:
    """'Do not apply a patch.' must remain a bounded review, not PATCH_PROPOSAL."""

    def test_do_not_apply_patch(self) -> None:
        result = process_request(
            request_id="fix02-neg-01",
            text="Do not apply a patch.",
        )
        assert result.detected_task_type != TaskType.PATCH_PROPOSAL

    def test_review_do_not_apply_patch(self) -> None:
        result = process_request(
            request_id="fix02-neg-02",
            text="Review shipping.py. Do not apply a patch.",
            has_paths=True,
        )
        assert result.detected_task_type == TaskType.CODE_REVIEW
        assert result.decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS
        assert result.decision != IntakeDecision.CLARIFY
        assert result.decision != TaskType.PATCH_PROPOSAL

    def test_affirmative_patch_still_patch_proposal(self) -> None:
        result = process_request(
            request_id="fix02-pos-01",
            text="Apply the patch to shipping.py.",
            has_paths=True,
        )
        assert result.detected_task_type == TaskType.PATCH_PROPOSAL


class TestSpanishOnlyReviewPattern:
    """Portuguese-only phrasing must NOT become CODE_REVIEW."""

    def test_portuguese_not_code_review(self) -> None:
        result = process_request(
            request_id="fix02-pt-01",
            text="Faça uma revisão de shipping.py.",
            has_paths=True,
        )
        assert result.detected_task_type != TaskType.CODE_REVIEW
