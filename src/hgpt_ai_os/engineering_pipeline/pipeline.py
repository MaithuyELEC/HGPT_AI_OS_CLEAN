from __future__ import annotations

import json
import logging
import re
from dataclasses import replace
from typing import Any

from hgpt_ai_os.ai.config_resolver import validate_ai_provider_config
from hgpt_ai_os.ai.gemini_client import AIProviderError
from hgpt_ai_os.knowledge.models import KnowledgeResult
from hgpt_ai_os.providers import ProviderManager
from hgpt_ai_os.topic_engine import TopicContext
from hgpt_ai_os.ai_brain.brain_enricher import BrainEnricher

from .quality_gate import EngineeringQualityGate
from .prompt_composer import PromptComposer, PromptComposerInput
from .record import EngineeringRecord
from .intent import TopicIntent, analyze_topic_intent
from .offline_records import build_offline_engineering_record
from .writers import render_all


logger = logging.getLogger(__name__)


class EngineeringGenerationError(RuntimeError):
    pass


class EngineeringQualityError(EngineeringGenerationError):
    pass


class EngineeringGenerationPipeline:
    ENGINEERING_ROLE_PROMPT = """
You are the Chief Mechanical Engineer of HGPT Steel.

Experience base:
- Steel structures
- Mechanical design
- Maintenance
- Hydraulics
- Pneumatics
- Electrical
- PLC
- Automation
- QA/QC
- Welding
- Root Cause Analysis
- Reliability Engineering
- Lean
- TPM
- Kaizen

Never answer like ChatGPT.
Answer like an engineering expert writing an internal technical report for HGPT Steel.
Use natural Vietnamese: short, professional, actionable, factory ready.
Write in the style of a Chief Maintenance Engineer, industrial troubleshooting
manual, factory SOP, and maintenance handbook.
All user-visible values must be Vietnamese. Keep only approved technical
acronyms/standards such as LOTO, OEM, VFD, PLC, ISO, IEC, AWS, QA/QC, CMMS,
SCADA, RMS, and MPa when they are truly needed.
Return only one EngineeringRecord JSON object. Do not generate Facebook, SEO, checklist,
TikTok, image prompt, video prompt, hashtags, marketing copy, or management filler.
""".strip()

    ENGINEERING_RECORD_PROMPT = """
Given exactly one engineering topic, generate exactly one EngineeringRecord.

The EngineeringRecord must contain all required engineering sections:
- title
- problem
- equipment
- subsystem
- component
- operating_context
- working_principle
- failure_symptom
- failure_mechanisms
- evidence_required
- root_causes
- inspection_procedure
- measurements
- tools_required
- decision_logic
- repair_procedure
- verification
- acceptance_criteria
- common_mistakes
- safety_controls
- preventive_maintenance
- lessons_learned
- kaizen
- digital_factory_recommendations
- applicable_standards
- confidence
- missing_information

Factory-ready section intent:
- Hiện tượng and triệu chứng must be represented by problem and failure_symptom.
- Dấu hiệu nhận biết must be represented by failure_symptom and evidence_required.
- Mức độ nguy hiểm must be represented inside problem, safety_controls, and
  acceptance_criteria when the topic creates safety or production risk.
- Phân tích nguyên nhân gốc must use 5 Why when it helps; otherwise explain the
  physical failure chain clearly.
- Nguyên nhân có khả năng cao nhất must be ranked first in root_causes.
- Quy trình kiểm tra, dụng cụ, thiết bị đo kiểm, thông số cần đo, giá trị tham
  khảo, quy trình sửa chữa, kiểm tra sau sửa, chạy thử, nghiệm thu, phòng ngừa,
  kinh nghiệm thực tế, sai lầm thường gặp, checklist, and tóm tắt kỹ thuật must
  be represented across inspection_procedure, tools_required, measurements,
  decision_logic, repair_procedure, verification, acceptance_criteria,
  preventive_maintenance, lessons_learned, common_mistakes, kaizen, and
  digital_factory_recommendations.

Root cause requirements:
- Provide at least 3 root causes.
- Rank causes by probability.
- Each root_causes item must be a complete cause block, not a short label.
- For every cause include: probability rank, why it happens, physical mechanism,
  inspection method, measurement, required tools, expected values if known, decision
  logic, repair procedure, verification after repair, and acceptance criteria.
- If a measurement value or expected value is unknown, do not invent a number.
  Write exactly: "Không đủ dữ liệu để kết luận. Cần đo..." and state the exact
  measurement required.
- Each root cause must be specific to the equipment, component, energy source,
  operating mode, and failure symptom in the user topic.

Minimum depth requirements:
- At least 4 failure_symptom items.
- At least 3 failure_mechanisms items.
- At least 5 inspection_procedure items in field order.
- At least 4 measurements items.
- At least 4 tools_required items, including measuring instruments when needed.
- At least 4 repair_procedure items.
- At least 3 verification items and 3 acceptance_criteria items.
- At least 3 safety_controls items when electrical, hydraulic, pneumatic,
  lifting, stored pressure, rotating equipment, cutting gas, heat, or suspended
  load risk is present.
- At least 3 preventive_maintenance items.
- At least 3 lessons_learned and 3 common_mistakes items.

Quality requirements:
- Do not fabricate standards.
- Do not fabricate measurements.
- Do not fabricate numbers.
- Do not write generic management paragraphs.
- Do not use filler such as "thiết bị phù hợp", "kiểm tra tổng quát", "xử lý
  theo quy trình", or "cần xác nhận thêm" unless followed by the exact data or
  action required.
- Do not leave domain, equipment, component, tool, or instrument fields blank,
  generic, or in English. Translate "Maintenance" to "Bảo trì công nghiệp",
  "Production" to "Sản xuất công nghiệp", "bearing" to "ổ bi", "motor" to
  "động cơ", "wire rope" to "cáp tải", "regulator" to "bộ điều áp", and
  "nozzle" to "bec cắt" when those terms are applicable.
- Do not repeat the same text across unrelated topics.
- Prefer equipment-specific terms over general words. For example, identify
  bearing, stator winding, hydraulic pump, relief valve, wire rope, hoist brake,
  compressor inlet valve, VFD power module, hydraulic line, cutting gas solenoid,
  regulator, nozzle, pressure switch, or sensor when those are the real suspected
  assets.
- Make the answer topic-specific. A motor bearing noise record, a three-phase
  motor overheating record, a hydraulic pump low-pressure record, a VFD OC record,
  a crane wire-rope break record, an air compressor low-pressure record, a
  hydraulic vibration record, and a laser cutting gas failure record must have substantially different
  causes, inspections, tools, repair actions, verification, lessons, PM, Kaizen,
  and Digital Factory recommendations.

Internal rejection rule:
Reject your own draft and rewrite before returning if the content contract for
topic_intent.topic_type is missing, entity relevance is weak, safety_controls is
missing for hazardous energy, unsupported numeric limits appear, or the same
wording could fit a different machine/process without rewriting.
""".strip()

    TOPIC_TYPE_CONTRACTS = {
        "FAULT_DIAGNOSIS": (
            "Hiện tượng",
            "Mức độ nguy hiểm",
            "Điều kiện dừng máy",
            "Nguyên nhân khả dĩ ranked by likelihood",
            "Evidence needed",
            "Inspection sequence",
            "Tools and instruments",
            "Safe isolation / LOTO",
            "Repair decision tree",
            "Post-repair verification",
            "Acceptance criteria",
            "Prevention",
            "Manufacturer-dependent items",
            "Unknowns requiring confirmation",
        ),
        "DEFECT_ANALYSIS": (
            "Defect description",
            "Location and pattern",
            "Immediate containment",
            "Likely process causes",
            "Material-related causes",
            "Equipment-related causes",
            "Operator-related causes",
            "Inspection/NDT method",
            "WPS/ITP/manual data required",
            "Corrective action",
            "Repair restrictions",
            "Reinspection",
            "Prevention",
            "Lessons learned",
        ),
        "MAINTENANCE_PROCEDURE": (
            "Scope",
            "Frequency",
            "Responsibility",
            "Safety",
            "Preparation",
            "Tools",
            "Step-by-step procedure",
            "Inspection points",
            "Wear limits from manual only",
            "Lubrication requirements from manual only",
            "Record form",
            "Acceptance",
            "Escalation",
            "KPI",
        ),
        "PROCESS_GUIDE": (
            "Purpose",
            "Input",
            "Output",
            "Equipment",
            "Personnel",
            "Process steps",
            "Hold points",
            "Quality controls",
            "Safety controls",
            "Common errors",
            "Acceptance criteria",
            "Records",
            "Improvement opportunities",
        ),
        "MANAGEMENT_METHOD": (
            "Objective",
            "Scope",
            "Roles",
            "Implementation stages",
            "Daily tasks",
            "Abnormality tagging",
            "Escalation rules",
            "Audit mechanism",
            "KPI",
            "Training",
            "Standardization",
            "Sustainment",
            "Digitalization opportunities",
        ),
        "INVESTMENT_EVALUATION": (
            "Business objective",
            "Current state",
            "Technical options",
            "Factory fit",
            "Safety and quality impact",
            "Utility/foundation/interface needs",
            "CAPEX/OPEX items without invented values",
            "Implementation risks",
            "Data required before approval",
            "Recommendation logic",
        ),
        "TECHNICAL_EXPLANATION": (
            "Definition",
            "Working principle",
            "Where it applies",
            "Key components",
            "Benefits",
            "Limits",
            "Common misunderstandings",
            "Inspection or usage notes",
        ),
        "SAFETY_RISK": (
            "Hazard description",
            "Immediate stop condition",
            "Exclusion zone",
            "LOTO/isolation",
            "Evidence required",
            "Emergency response",
            "Inspection sequence",
            "Repair restriction",
            "Return-to-service criteria",
        ),
        "QA_QC_NONCONFORMITY": (
            "Nonconformity description",
            "Applicable drawing/specification",
            "Inspection evidence",
            "Severity",
            "Containment",
            "Root cause",
            "Disposition",
            "Repair/rework",
            "Reinspection",
            "NCR/CAPA",
            "Traceability",
            "Prevention",
        ),
        "LEAN_IMPROVEMENT": (
            "Current condition",
            "Waste identified",
            "Baseline data",
            "Root cause",
            "Improvement proposal",
            "Cost",
            "Safety impact",
            "Productivity impact",
            "Implementation plan",
            "KPI",
            "Standardization",
            "Sustainment",
            "Digital tracking",
        ),
    }

    REQUIRED_AI_FIELDS = (
        "title",
        "problem",
        "symptoms",
        "root_causes",
        "inspection",
        "repair",
        "verification",
        "prevention",
        "lessons_learned",
    )
    RECORD_SCHEMA = {
        "title": "string",
        "topic": "string",
        "problem": "string",
        "domain": "string",
        "equipment": ["string; identify the actual machine or asset class"],
        "subsystem": "string; affected subsystem",
        "component": ["string; affected components"],
        "symptoms": ["string; observed symptoms, topic-specific"],
        "failure_symptom": ["string; observed symptoms, topic-specific"],
        "operating_context": "string",
        "working_principle": "string",
        "failure_mechanisms": ["string; topic-specific physical failure chain"],
        "root_causes": [
            "string; one complete ranked cause block including probability rank, why it happens, physical mechanism, inspection method, measurement, tools, expected values if known, decision logic, repair, verification, and acceptance criteria"
        ],
        "evidence_required": ["string; evidence needed before conclusion"],
        "inspection": ["string; inspection steps"],
        "inspection_procedure": ["string; inspection steps"],
        "measurements": ["string; exact measurements required; no fabricated values"],
        "tools_required": ["string; tools and instruments required"],
        "decision_logic": ["string; if/then logic using evidence and measurement"],
        "repair": ["string; repair steps"],
        "repair_procedure": ["string; repair steps"],
        "verification": ["string; verification after repair"],
        "acceptance_criteria": ["string; pass/fail criteria, no invented values"],
        "prevention": ["string; preventive maintenance actions"],
        "preventive_maintenance": ["string; preventive maintenance actions"],
        "lessons_learned": ["string; technical lessons from the failure"],
        "common_mistakes": ["string; topic-specific mistakes to avoid"],
        "safety_controls": ["string; safety controls before inspection and repair"],
        "kaizen": ["string; practical improvement ideas"],
        "digital_factory_recommendations": ["string; data capture, alarms, trends, CMMS, SCADA, historian recommendations"],
        "applicable_standards": ["string; only standards truly applicable and known; otherwise leave empty"],
        "missing_information": ["string; must include 'Không đủ dữ liệu để kết luận. Cần đo...' when input data is insufficient"],
        "confidence": 0.0,
        "source_keys": ["AI_PROVIDER"],
    }

    FIELD_CONTRACTS = {
        "title": "Vietnamese technical title naming the topic, object, and condition. One concise line.",
        "problem": "Vietnamese problem statement with topic summary, engineering object, observed condition, risk if ignored, and uncertainty when evidence is missing. Minimum two useful sentences.",
        "equipment": "Array of Vietnamese strings identifying only the actual equipment or process in the topic. Do not insert unrelated machines.",
        "subsystem": "Vietnamese affected subsystem or process area. Use 'Không đủ dữ liệu để kết luận. Cần xác nhận...' if the topic does not provide enough evidence.",
        "component": "Array of Vietnamese affected components or process elements. For management/process topics, map to program elements instead of inventing failed parts.",
        "failure_symptom": "Array of observed symptoms or process signals. Fault/defect topics need at least 3 specific items. Management and investment topics must use operational observations, not fake equipment failures.",
        "operating_context": "Vietnamese factory context needed for safe diagnosis or implementation. Include what must be confirmed before action.",
        "working_principle": "Vietnamese technical definition or operating principle relevant to the topic. Explain mechanism, not a generic description.",
        "failure_mechanisms": "Array of physical, process, management, or decision mechanisms. Fault/defect topics need at least 3 topic-specific mechanisms.",
        "root_causes": "Array of Vietnamese strings only, never objects. Each fault/defect item must be one complete ranked cause block with likelihood rank, why it happens, mechanism, evidence, inspection, measurement, tools, action, verification, and acceptance logic.",
        "evidence_required": "Array of evidence needed before conclusions: photos, logs, measurements, drawings, manuals, WPS/ITP, OEM data, quality records, or approval data as applicable.",
        "inspection_procedure": "Array of ordered field inspection or assessment steps. Fault/defect topics need at least 5 actionable steps with safety first.",
        "measurements": "Array of exact measurements or data points required. Do not invent values. State 'Không đủ dữ liệu để kết luận. Cần đo...' plus the specific measurement when limits are unknown.",
        "tools_required": "Array of hand tools, PPE, measuring instruments, records, or software needed. Include instruments, not only generic tools.",
        "decision_logic": "Array of Vietnamese if/then decision rules tied to evidence. Do not recommend repair or approval without the measurement that triggers it.",
        "repair_procedure": "Array of corrective actions or implementation steps. For management/investment topics, use rollout or decision actions instead of fake repair.",
        "verification": "Array of post-action verification checks using the same evidence or approved acceptance method.",
        "acceptance_criteria": "Array of pass/fail acceptance methods. Use OEM, drawing, WPS/ITP, approved internal criterion, or 'Không đủ dữ liệu...' instead of fabricated numbers.",
        "lessons_learned": "Array of field lessons specific to the topic. Avoid generic slogans.",
        "common_mistakes": "Array of topic-specific mistakes and why they are risky.",
        "preventive_maintenance": "Array of recurrence-prevention actions, standards, audits, training, PM/TPM, data capture, or supplier controls as applicable.",
        "safety_controls": "Array of safety controls. Include LOTO, isolation, barricade, PPE, authorization, stored-energy control, or stop-work conditions when relevant.",
        "kaizen": "Array of practical improvement actions connected to the topic.",
        "digital_factory_recommendations": "Array of CMMS, SCADA, sensor, checklist, trend, traceability, or dashboard recommendations that do not invent readings.",
        "applicable_standards": "Array of verified applicable standards only. Leave empty when not verified; never invent AWS/ISO/IEC references.",
        "missing_information": "Array of unknown facts, manufacturer-dependent data, required measurements, and approval records. State uncertainty explicitly.",
        "confidence": "Number 0.0 to 1.0 reflecting evidence confidence, not writing confidence.",
        "source_keys": "Array of source labels such as AI_PROVIDER and retrieved source titles. Do not include secrets.",
    }

    def __init__(
        self,
        ai: Any | None = None,
        provider_manager: ProviderManager | None = None,
        quality_gate: EngineeringQualityGate | None = None,
    ) -> None:
        self.quality_gate = quality_gate or EngineeringQualityGate()
        self.provider_manager = provider_manager or ProviderManager()
        self.prompt_composer = PromptComposer(
            self.TOPIC_TYPE_CONTRACTS,
            self.RECORD_SCHEMA,
            self.FIELD_CONTRACTS,
        )
        self.validation = validate_ai_provider_config()
        self._ai_supplied = ai is not None
        self.ai = ai
        self.free_desktop_mode = (
            self.validation.config.free_desktop_mode
            or self.validation.status == "Free Desktop"
        )
        self.provider = self.validation.config.provider if not self.free_desktop_mode else "Disabled"
        self.model = ""
        self.http_status = ""
        self.error = ""
        self.engineering_record_source = "NONE"
        self.ai_response_length = 0
        self.engineering_record_created = False
        self.docx_created = False
        self.topic_intent: TopicIntent | None = None
        self.request_id = ""
        self.topic_fingerprint = ""
        provider = getattr(self.ai, "provider", None)
        self.provider = getattr(provider, "provider", self.provider)
        self.model = getattr(provider, "model", self.model)

    def generate_documents(
        self,
        topic: str,
        context: str,
        knowledge_items: list[KnowledgeResult],
        topic_context: TopicContext,
    ) -> tuple[EngineeringRecord, dict[str, str]]:
        topic_intent = analyze_topic_intent(topic)
        self.topic_intent = topic_intent
        self.request_id = topic_intent.request_id
        self.topic_fingerprint = topic_intent.topic_fingerprint
        record = self._record_or_safe_failure(topic, context, knowledge_items, topic_context, topic_intent)
        record_report = self.quality_gate.validate_record(record, topic_intent)
        if not record_report.accepted:
            record = self._record_or_safe_failure(
                topic,
                context,
                knowledge_items,
                topic_context,
                topic_intent,
                quality_feedback=record_report.issues,
                rejected_record=record,
            )
            record_report = self.quality_gate.validate_record(record, topic_intent)
            if not record_report.accepted:
                self.error = "Quality Gate failed: " + "; ".join(record_report.issues)
                if not self.free_desktop_mode:
                    raise EngineeringQualityError(self.error)
                record = self._safe_failure_record(topic_intent, record_report.issues)

        documents = render_all(record)
        document_report = self.quality_gate.validate_documents(documents, topic_intent)
        if not document_report.accepted:
            record = self._record_or_safe_failure(
                topic,
                context,
                knowledge_items,
                topic_context,
                topic_intent,
                quality_feedback=document_report.issues,
                rejected_record=record,
            )
            record_report = self.quality_gate.validate_record(record, topic_intent)
            if not record_report.accepted:
                self.error = "Quality Gate failed: " + "; ".join(record_report.issues)
                if not self.free_desktop_mode:
                    raise EngineeringQualityError(self.error)
                record = self._safe_failure_record(topic_intent, record_report.issues)
                documents = render_all(record)
                return record, documents
            documents = render_all(record)
            document_report = self.quality_gate.validate_documents(documents, topic_intent)
            if not document_report.accepted:
                self.error = "Quality Gate failed: " + "; ".join(document_report.issues)
                if not self.free_desktop_mode:
                    raise EngineeringQualityError(self.error)
                record = self._safe_failure_record(topic_intent, document_report.issues)
                documents = render_all(record)
                final_report = self.quality_gate.validate_documents(documents, topic_intent)
                if not final_report.accepted:
                    self.error = "Quality Gate failed: " + "; ".join(final_report.issues)
                    raise EngineeringQualityError(self.error)
        return record, documents

    def _record_or_safe_failure(
        self,
        topic: str,
        context: str,
        knowledge_items: list[KnowledgeResult],
        topic_context: TopicContext,
        topic_intent: TopicIntent,
        quality_feedback: tuple[str, ...] = (),
        rejected_record: EngineeringRecord | None = None,
    ) -> EngineeringRecord:
        offline_record = build_offline_engineering_record(topic_intent)
        if offline_record is not None:
            self.engineering_record_created = True
            self.engineering_record_source = "OFFLINE_ENGINEERING_PROFILE"
            return offline_record
        feedback = quality_feedback
        rejected = rejected_record
        failures: list[str] = []
        for attempt in range(2):
            try:
                return self.build_record(topic, context, knowledge_items, topic_context, topic_intent, feedback, rejected)
            except EngineeringGenerationError as exc:
                failures.append(str(exc))
                if attempt == 0:
                    feedback = (str(exc),)
                    rejected = None
                    continue
        issues = tuple(failures) or ("EngineeringRecord incomplete.",)
        self.error = "Generation failed after retry: " + "; ".join(issues)
        if not self.free_desktop_mode and not self._is_no_internet_failure(issues):
            raise EngineeringGenerationError(self.error)
        if self._is_no_internet_failure(issues):
            print("⚠ Offline Mode")
            print("No internet connection to OpenAI. Using Local Generator.")
            self.error = "Offline Mode: no internet connection to OpenAI."
            self.provider = "Offline"
            self.model = ""
            self.http_status = ""
        self.engineering_record_created = True
        self.engineering_record_source = "OFFLINE_LOCAL_GENERATOR"
        return self._safe_failure_record(topic_intent, issues)

    def _is_no_internet_failure(self, issues: tuple[str, ...]) -> bool:
        if not issues:
            return False
        network_markers = (
            "network error",
            "request timed out",
            "timeout",
            "ssl_error",
            "connection_error",
        )
        return all(
            any(marker in issue.lower() for marker in network_markers)
            for issue in issues
        )

    def build_record(
        self,
        topic: str,
        context: str,
        knowledge_items: list[KnowledgeResult],
        topic_context: TopicContext,
        topic_intent: TopicIntent,
        quality_feedback: tuple[str, ...] = (),
        rejected_record: EngineeringRecord | None = None,
    ) -> EngineeringRecord:
        record = self._ai_record(topic, context, knowledge_items, topic_context, topic_intent, quality_feedback, rejected_record)
        record = self._apply_intent(record, topic_intent)
        self.engineering_record_created = True
        return record

    def _ai_record(
        self,
        topic: str,
        context: str,
        knowledge_items: list[KnowledgeResult],
        topic_context: TopicContext,
        topic_intent: TopicIntent,
        quality_feedback: tuple[str, ...] = (),
        rejected_record: EngineeringRecord | None = None,
    ) -> EngineeringRecord:
        if self.ai is None and self.free_desktop_mode:
            self.error = self.error or "AI_PROVIDER_DISABLED"
            raise EngineeringGenerationError(self.error)

        prompt = self.prompt_composer.compose(
            PromptComposerInput(
                topic=topic,
                domain=topic_intent.primary_domain,
                intent=topic_intent,
                audience=(
                    "Vietnamese practical learners and operators"
                    if topic_intent.primary_domain == "GENERAL_KNOWLEDGE"
                    else "HGPT Steel factory engineers, maintenance leaders, QA/QC, and production supervisors"
                ),
                tone=(
                    "Vietnamese practical guide, concise, safe, evidence-aware"
                    if topic_intent.primary_domain == "GENERAL_KNOWLEDGE"
                    else "Vietnamese factory SOP, concise, technical, evidence-driven"
                ),
                knowledge_blocks=context,
                knowledge_items=knowledge_items,
                output_type="EngineeringRecord JSON",
                topic_context=topic_context,
                quality_feedback=quality_feedback,
                rejected_record=rejected_record,
            )
        )

        prompt = BrainEnricher.enrich(
            prompt=prompt,
            topic=topic,
        )


        if self.ai is not None:
            response = self.ai.generate(prompt.system_prompt, prompt.user_prompt)
        else:
            response = self.provider_manager.generate_real_ai(prompt.system_prompt, prompt.user_prompt)
        if isinstance(response, AIProviderError):
            self.provider = response.provider
            self.model = response.model
            self.http_status = self._http_status(response)
            self.error = self._provider_error_text(response)
            raise EngineeringGenerationError(self.error)

        content = getattr(response, "content", "") or ""
        self.provider = getattr(response, "provider", self.provider)
        self.model = getattr(response, "model", self.model)
        self.http_status = str(getattr(response, "metadata", {}).get("status_code") or "")
        self.ai_response_length = len(content)
        if self.http_status != "200":
            self.error = self.http_status or "missing HTTP 200"
            raise EngineeringGenerationError(self.error)
        data = self._extract_json(content)
        if not data:
            self.error = "empty response" if not content.strip() else "invalid JSON"
            raise EngineeringGenerationError(self.error)
        missing = self._missing_required_fields(data)
        if missing:
            self.error = "Generation Failed: missing field(s): " + ", ".join(missing)
            raise EngineeringGenerationError(self.error)
        try:
            record = EngineeringRecord.from_mapping(data)
        except (TypeError, ValueError):
            self.error = "invalid JSON"
            logger.exception("AI EngineeringRecord parse failed.")
            raise EngineeringGenerationError(self.error)
        self.engineering_record_source = "AI_PROVIDER"
        return record

    def _extract_json(self, content: str) -> dict[str, Any] | None:
        text = content.strip()
        if not text:
            return None
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return None
        if isinstance(data, dict):
            nested = data.get("engineering_record") or data.get("EngineeringRecord")
            if isinstance(nested, dict):
                data = nested
        return data if isinstance(data, dict) else None

    def _missing_required_fields(self, data: dict[str, Any]) -> list[str]:
        missing = []
        for field in self.REQUIRED_AI_FIELDS:
            value = data.get(field)
            if value is None and field == "symptoms":
                value = data.get("failure_symptom")
            if value is None and field == "inspection":
                value = data.get("inspection_procedure")
            if value is None and field == "repair":
                value = data.get("repair_procedure")
            if value is None and field == "prevention":
                value = data.get("preventive_maintenance")
            if not self._has_value(value):
                missing.append(field)
        root_causes = data.get("root_causes")
        if not isinstance(root_causes, (list, tuple)) or len([item for item in root_causes if self._has_value(item)]) < 3:
            missing.append("root_causes_minimum_3")
        return missing

    def _has_value(self, value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, (list, tuple, set)):
            return any(self._has_value(item) for item in value)
        return True

    def _http_status(self, error: AIProviderError) -> str:
        status = error.metadata.get("status_code")
        if status:
            return str(status)
        for provider in error.metadata.get("providers", ()):
            nested = provider.get("metadata", {}) if isinstance(provider, dict) else {}
            status = nested.get("status_code")
            if status:
                return str(status)
        return ""

    def _provider_error_text(self, error: AIProviderError) -> str:
        body = str(error.metadata.get("body", ""))
        if "RESOURCE_EXHAUSTED" in body:
            return "RESOURCE_EXHAUSTED"
        if self.http_status:
            return self.http_status
        if error.error_type == "timeout":
            return "Timeout"
        for provider in error.metadata.get("providers", ()):
            if not isinstance(provider, dict):
                continue
            nested = provider.get("metadata", {})
            body = str(nested.get("body", ""))
            if "RESOURCE_EXHAUSTED" in body:
                return "RESOURCE_EXHAUSTED"
            status = nested.get("status_code")
            if status:
                return str(status)
            if provider.get("error_type") == "timeout":
                return "Timeout"
            message = str(provider.get("message", "")).strip()
            if message:
                return message
        return error.message.strip() or error.error_type

    def _apply_intent(self, record: EngineeringRecord, topic_intent: TopicIntent) -> EngineeringRecord:
        return replace(
            record,
            topic=topic_intent.original_topic,
            domain=topic_intent.primary_domain,
            primary_domain=topic_intent.primary_domain,
            secondary_domain=topic_intent.secondary_domain,
            topic_type=topic_intent.topic_type,
            main_entity=topic_intent.main_entity,
            observed_condition=topic_intent.observed_condition,
            expected_user_goal=topic_intent.expected_user_goal,
            safety_level=topic_intent.safety_level,
            request_id=topic_intent.request_id,
            topic_fingerprint=topic_intent.topic_fingerprint,
            ambiguity_flags=topic_intent.ambiguity_flags,
            prohibited_assumptions=topic_intent.prohibited_assumptions,
        )

    def _safe_failure_record(self, topic_intent: TopicIntent, issues: tuple[str, ...]) -> EngineeringRecord:
        subject = topic_intent.original_topic
        main_entity = topic_intent.main_entity or subject
        component = topic_intent.component or main_entity
        return EngineeringRecord(
            topic=subject,
            domain=topic_intent.primary_domain,
            primary_domain=topic_intent.primary_domain,
            secondary_domain=topic_intent.secondary_domain,
            topic_type=topic_intent.topic_type,
            main_entity=main_entity,
            observed_condition=topic_intent.observed_condition or subject,
            expected_user_goal=topic_intent.expected_user_goal,
            safety_level=topic_intent.safety_level,
            request_id=topic_intent.request_id,
            topic_fingerprint=topic_intent.topic_fingerprint,
            title=subject,
            problem=(
                f"{subject} cần được kiểm soát như một vấn đề kỹ thuật trong sản xuất thép: "
                "dấu hiệu phải được nhận diện sớm, nguyên nhân phải được khóa theo quy trình, "
                "và kết quả phải được xác nhận trước khi chuyển công đoạn hoặc bàn giao."
            ),
            equipment=(main_entity, "khu vực sản xuất thép", "hồ sơ kỹ thuật", "điểm kiểm soát chất lượng"),
            subsystem=component,
            component=(component, "bề mặt/cụm chi tiết liên quan", "hồ sơ nghiệm thu", "điểm dừng kiểm soát"),
            failure_symptom=(
                topic_intent.observed_condition or f"dấu hiệu bất thường liên quan đến {subject}",
                "kết quả kiểm tra hoặc nghiệm thu không ổn định giữa các công đoạn",
                "đội sản xuất phải dừng lại để xác nhận nguyên nhân trước khi tiếp tục",
                "nguy cơ sửa lại, chậm tiến độ hoặc tranh luận tiêu chí bàn giao",
            ),
            operating_context=f"Chủ đề được xử lý theo quy trình kiểm soát chất lượng trong xưởng thép cho {subject}.",
            working_principle=(
                f"Với {subject}, chất lượng phụ thuộc vào việc kiểm soát vật liệu, thiết bị, phương pháp thao tác, "
                "điểm kiểm tra và hồ sơ xác nhận. Khi một mắt xích bị bỏ qua, lỗi có thể đi sang công đoạn sau."
            ),
            failure_mechanisms=(
                "điểm kiểm soát đầu vào không đủ rõ làm lỗi lọt sang công đoạn sau",
                "thao tác sản xuất không thống nhất làm kết quả chất lượng dao động",
                "tiêu chí nghiệm thu không được truyền đạt rõ giữa sản xuất và QA/QC",
                "hồ sơ xác nhận không cập nhật kịp thời làm quyết định sửa chữa bị chậm",
            ),
            root_causes=(
                "điểm kiểm soát trước công đoạn không đủ chặt",
                "tiêu chí kỹ thuật chưa được truyền đạt rõ cho tổ sản xuất",
                "thiếu phối hợp giữa sản xuất, kỹ thuật và QA/QC",
                "áp lực tiến độ làm bỏ qua bước xác nhận quan trọng",
                "hồ sơ nghiệm thu không được cập nhật ngay tại thời điểm phát hiện",
            ),
            evidence_required=(
                "ảnh trước và sau xử lý",
                "kết quả kiểm tra tại điểm lỗi",
                "bản vẽ, WPS/ITP, hướng dẫn hãng sản xuất hoặc tiêu chuẩn áp dụng",
            ),
            inspection_procedure=(
                "xác nhận đúng thiết bị, cấu kiện hoặc công đoạn liên quan",
                "ghi nhận dấu hiệu lỗi bằng ảnh, phiếu kiểm hoặc kết quả đo",
                "đối chiếu với bản vẽ, WPS/ITP hoặc tiêu chí nghiệm thu áp dụng",
                "khoanh vùng phạm vi ảnh hưởng trước khi sửa",
                "xác nhận người chịu trách nhiệm xử lý và kiểm tra lại",
                "lưu kết quả sau xử lý vào hồ sơ chất lượng",
            ),
            measurements=(
                "kích thước hoặc thông số chất lượng liên quan",
                "kết quả kiểm tra trước và sau xử lý",
                "thời gian dừng hoặc thời gian sửa lại",
                "số lượng sản phẩm/cấu kiện bị ảnh hưởng",
                "tỷ lệ lỗi lặp lại theo công đoạn",
            ),
            tools_required=("PPE", "phiếu kiểm QA/QC", "dụng cụ đo phù hợp", "máy ảnh hoặc biểu mẫu ghi nhận", "hồ sơ bản vẽ/WPS/ITP"),
            decision_logic=(
                "ưu tiên xử lý nguyên nhân có bằng chứng trực tiếp tại công đoạn",
                "không chuyển công đoạn khi dấu hiệu lỗi còn mở",
                "mở hành động phòng ngừa nếu lỗi có xu hướng lặp lại",
            ),
            repair_procedure=(
                "khoanh vùng sản phẩm hoặc thiết bị bị ảnh hưởng",
                "thực hiện sửa chữa hoặc điều chỉnh theo quy trình được duyệt",
                "làm sạch và chuẩn bị lại khu vực trước khi kiểm tra",
                "kiểm tra lại bằng cùng tiêu chí đã phát hiện lỗi",
                "cập nhật hồ sơ nguyên nhân và hành động đã thực hiện",
            ),
            verification=(
                "kết quả kiểm tra lại đạt tiêu chí áp dụng",
                "không còn dấu hiệu lỗi tại phạm vi đã khoanh vùng",
                "người phụ trách sản xuất và QA/QC cùng xác nhận",
                "hồ sơ sau sửa thể hiện rõ nguyên nhân, hành động và kết quả",
            ),
            acceptance_criteria=(
                "giảm độ tin cậy của sản phẩm hoặc thiết bị",
                "tăng thời gian sửa lại và chi phí sản xuất",
                "làm chậm tiến độ bàn giao hoặc nghiệm thu",
                "tạo nguy cơ lỗi lặp lại ở công đoạn sau",
            ),
            lessons_learned=(
                "chất lượng đến từ điểm kiểm rõ và kỷ luật thực hiện",
                "lỗi nhỏ ở công đoạn trước có thể tạo chi phí lớn ở công đoạn sau",
                "hồ sơ tốt giúp đội hiện trường ra quyết định nhanh hơn",
                "một bài học sản xuất phải được đưa lại vào checklist",
            ),
            common_mistakes=(
                "chỉ sửa triệu chứng mà không khóa nguyên nhân",
                "chuyển công đoạn khi phiếu kiểm còn điểm mở",
                "không ghi ảnh và kết quả sau xử lý",
                "để áp lực tiến độ thay thế tiêu chí chất lượng",
            ),
            preventive_maintenance=(
                "chuẩn hóa checklist trước khi chuyển công đoạn",
                "đào tạo tổ sản xuất nhận biết dấu hiệu lỗi sớm",
                "khóa trách nhiệm kiểm tra giữa sản xuất và QA/QC",
                "theo dõi lỗi lặp lại theo ca, công đoạn và nguyên nhân",
                "cập nhật bài học vào quy trình hoặc ITP",
                "kiểm tra chất lượng trong quá trình sản xuất thay vì chờ cuối công đoạn",
            ),
            safety_controls=("dùng PPE đúng rủi ro", "kiểm soát khu vực thao tác", "dừng công việc khi phát hiện nguy cơ an toàn"),
            missing_information=(),
            ambiguity_flags=topic_intent.ambiguity_flags,
            prohibited_assumptions=topic_intent.prohibited_assumptions,
            safe_failure=False,
            confidence=0.72,
            source_keys=("GENERIC_CONTENT_DNA_RECORD",),
        )
