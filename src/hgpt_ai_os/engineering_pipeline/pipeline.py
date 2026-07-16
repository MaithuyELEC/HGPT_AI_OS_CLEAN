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

from .quality_gate import EngineeringQualityGate
from .record import EngineeringRecord
from .intent import TopicIntent, analyze_topic_intent
from .writers import render_all


logger = logging.getLogger(__name__)


class EngineeringGenerationError(RuntimeError):
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
        self.validation = validate_ai_provider_config()
        self._ai_supplied = ai is not None
        self.ai = ai
        self.provider = self.validation.config.provider if not self.validation.config.free_desktop_mode else "Disabled"
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
                self.error = "Safe limitation record: " + "; ".join(record_report.issues)
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
                self.error = "Safe limitation record: " + "; ".join(record_report.issues)
                record = self._safe_failure_record(topic_intent, record_report.issues)
                documents = render_all(record)
                return record, documents
            documents = render_all(record)
            document_report = self.quality_gate.validate_documents(documents, topic_intent)
            if not document_report.accepted:
                self.error = "Safe limitation record: " + "; ".join(document_report.issues)
                record = self._safe_failure_record(topic_intent, document_report.issues)
                documents = render_all(record)
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
        self.error = "Safe limitation record: " + "; ".join(issues)
        self.engineering_record_created = True
        self.engineering_record_source = "SAFE_LIMITATION_RECORD"
        return self._safe_failure_record(topic_intent, issues)

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
        if self.ai is None and self.validation.config.free_desktop_mode:
            self.error = self.error or "AI_PROVIDER_DISABLED"
            raise EngineeringGenerationError(self.error)

        system_prompt = self._system_prompt()
        user_prompt = self._user_prompt(topic, context, knowledge_items, topic_context, topic_intent, quality_feedback, rejected_record)
        if self.ai is not None:
            response = self.ai.generate(system_prompt, user_prompt)
        else:
            response = self.provider_manager.generate_real_ai(system_prompt, user_prompt)
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

    def _system_prompt(self) -> str:
        return "\n\n".join(
            (
                self.ENGINEERING_ROLE_PROMPT,
                "Hard output contract: return valid JSON only, with exactly one top-level EngineeringRecord object.",
                "Do not wrap the object in markdown, prose, code fences, or an extra engineering_record key.",
            )
        )

    def _user_prompt(
        self,
        topic: str,
        context: str,
        knowledge_items: list[KnowledgeResult],
        topic_context: TopicContext,
        topic_intent: TopicIntent,
        quality_feedback: tuple[str, ...] = (),
        rejected_record: EngineeringRecord | None = None,
    ) -> str:
        source_names = [result.item.title for result in knowledge_items[:5] if getattr(result, "item", None)]
        return json.dumps(
            {
                "task": "Build one canonical EngineeringRecord JSON object for exactly one engineering topic.",
                "engineering_record_prompt": self.ENGINEERING_RECORD_PROMPT,
                "engineering_schema": self.RECORD_SCHEMA,
                "field_contracts": self.FIELD_CONTRACTS,
                "topic_intent": topic_intent.to_dict(),
                "content_contract_for_topic_type": self.TOPIC_TYPE_CONTRACTS[topic_intent.topic_type],
                "topic": topic,
                "topic_context": topic_context.to_topic_analysis().__dict__,
                "retrieved_sources": source_names,
                "retrieved_context": context[:6000],
                "quality_feedback_from_rejected_draft": list(quality_feedback),
                "rejected_record": rejected_record.to_dict() if rejected_record is not None else None,
                "rules": [
                    "Return exactly one top-level JSON object matching engineering_schema.",
                    "Do not wrap the record in another key.",
                    "Every array field in engineering_schema must be an array of Vietnamese strings. Do not return nested objects inside arrays.",
                    "Follow field_contracts for purpose, Vietnamese language, minimum useful depth, unsupported-content limits, and uncertainty wording for every field.",
                    "Use arrays of strings for every array field.",
                    "Use a number from 0.0 to 1.0 for confidence; never use words like low, medium, moderate, or high.",
                    "Root causes must have at least 3 items and must be ranked by probability.",
                    "For MANAGEMENT_METHOD, PROCESS_GUIDE, INVESTMENT_EVALUATION, and TECHNICAL_EXPLANATION, do not force an equipment-failure template; map the required contract sections into the closest EngineeringRecord fields.",
                    "The primary_domain, secondary_domain, topic_type, main_entity, observed_condition, expected_user_goal, safety_level, request_id, topic_fingerprint, ambiguity_flags, and prohibited_assumptions fields must match topic_intent exactly.",
                    "Each root cause item must include why it happens, physical mechanism, inspection method, measurement, required tools, expected values if known, decision logic, repair procedure, verification after repair, and acceptance criteria.",
                    "Write natural Vietnamese in factory SOP style, not blog style and not ChatGPT style.",
                    "All user-facing strings must be Vietnamese except approved acronyms/standards such as LOTO, OEM, VFD, PLC, ISO, IEC, AWS, QA/QC, CMMS, SCADA, RMS, and MPa.",
                    "Include symptoms, danger level, 5 Why when useful, inspection sequence, tools, measuring instruments, measurements, reference values only if known, repair, post-repair check, trial run, acceptance, prevention, field experience, common mistakes, checklist-ready actions, and technical summary.",
                    "Make every item equipment-specific; generic maintenance sentences are not acceptable.",
                    "Keep every channel writer downstream dependent on this record only.",
                    "Do not use a local playbook, generic template, or similar-topic mapping.",
                    "Do not invent standards or numeric measurements.",
                    "Reject any numeric value unless it comes from user input, retrieved_context, manufacturer manual, or a cited verified standard.",
                    "For MHI/HMI or control-interface lock topics, never provide password bypass, access-code cracking, or disabling safety interlocks.",
                    "If evidence is missing, return inspection items in missing_information and evidence_required.",
                    "When data is insufficient, include exactly: Không đủ dữ liệu để kết luận. Cần đo...",
                    "Reject and rewrite internally before returning if inspection, repair, verification, lessons_learned, or preventive_maintenance is missing.",
                    "If quality_feedback_from_rejected_draft is not empty, use rejected_record only as the rejected draft, correct only the listed failures, keep the original topic_intent, do not add unrelated equipment, and return a corrected full EngineeringRecord, not a patch and not an explanation.",
                ],
            },
            ensure_ascii=False,
        )

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
        missing = (
            "Không đủ dữ liệu để kết luận. Cần đo thực tế trước khi quyết định.",
            "Đối chiếu tài liệu nhà sản xuất, bản vẽ, WPS/ITP hoặc tiêu chuẩn áp dụng trước khi đặt tiêu chí nghiệm thu.",
            "Các lỗi kiểm tra chất lượng: " + "; ".join(issues[:6]),
        )
        return EngineeringRecord(
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
            title=f"Hồ sơ giới hạn kỹ thuật: {topic_intent.original_topic}",
            problem="Chưa đủ bằng chứng để kết luận kỹ thuật hoặc đưa ra thông số nghiệm thu.",
            equipment=(topic_intent.main_entity,),
            subsystem=topic_intent.component,
            component=(topic_intent.component,) if topic_intent.component else (),
            failure_symptom=(topic_intent.observed_condition,),
            operating_context="Chỉ ghi nhận phạm vi có thể xác nhận từ chủ đề đầu vào.",
            working_principle="Không suy diễn nguyên lý, thông số hoặc model thiết bị khi thiếu hồ sơ kỹ thuật.",
            failure_mechanisms=("Chưa xác nhận cơ chế lỗi; cần kiểm tra thực tế và hồ sơ kỹ thuật.",),
            root_causes=("Chưa kết luận nguyên nhân gốc khi thiếu bằng chứng đo kiểm.",),
            evidence_required=(
                "Ảnh hiện trường trước xử lý",
                "Dữ liệu đo thực tế liên quan đến chủ đề",
                "Bản vẽ, WPS/ITP, hướng dẫn OEM hoặc tiêu chuẩn áp dụng",
            ),
            inspection_procedure=(
                "Cô lập năng lượng nguy hiểm trước khi kiểm tra.",
                "Xác nhận đúng thiết bị/cấu kiện/chủ thể chính.",
                "Ghi nhận hiện tượng bằng ảnh, video, log vận hành hoặc phiếu kiểm.",
                "Đo các thông số cần thiết bằng dụng cụ phù hợp.",
                "Chỉ quyết định sửa chữa khi dữ liệu khớp với hiện tượng.",
            ),
            measurements=(
                "Thông số đo phụ thuộc thiết bị, quy trình hoặc bản vẽ được phê duyệt.",
                "Không sử dụng giá trị tham khảo thay cho tiêu chí nghiệm thu.",
                "Giá trị giới hạn phụ thuộc model thiết bị.",
                "Cần đo thực tế trước khi quyết định.",
            ),
            tools_required=("PPE", "phiếu LOTO", "dụng cụ đo phù hợp", "máy ảnh hoặc biểu mẫu ghi nhận"),
            decision_logic=(
                "Nếu thiếu hồ sơ hoặc dữ liệu đo thì không kết luận nguyên nhân.",
                "Nếu phát hiện rủi ro an toàn thì dừng và escalates cho người có thẩm quyền.",
            ),
            repair_procedure=("Không thực hiện sửa chữa suy đoán; chỉ làm hành động an toàn và bảo toàn hiện trường.",),
            verification=("Xác nhận lại bằng cùng phương pháp đo sau khi có hành động khắc phục được phê duyệt.",),
            acceptance_criteria=("Chỉ bàn giao khi tiêu chí nghiệm thu có nguồn xác nhận.",),
            lessons_learned=("Không ép chủ đề vào mẫu sự cố thiết bị khi topic_type không phải FAULT_DIAGNOSIS.",),
            common_mistakes=("Bịa thông số hoặc tiêu chuẩn để hoàn thành biểu mẫu.",),
            preventive_maintenance=("Cập nhật danh mục dữ liệu cần thu thập cho chủ đề tương tự.",),
            safety_controls=("Dừng công việc khi chưa kiểm soát năng lượng nguy hiểm.", "Không bypass liên động an toàn.", "Dùng PPE đúng rủi ro."),
            missing_information=missing,
            ambiguity_flags=topic_intent.ambiguity_flags,
            prohibited_assumptions=topic_intent.prohibited_assumptions,
            safe_failure=True,
            confidence=0.0,
            source_keys=("SAFE_LIMITATION_RECORD",),
        )
