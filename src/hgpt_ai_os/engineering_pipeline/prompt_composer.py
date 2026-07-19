from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from hgpt_ai_os.knowledge.models import KnowledgeResult
from hgpt_ai_os.topic_engine import TopicContext

from .intent import TopicIntent
from .record import EngineeringRecord


@dataclass(frozen=True)
class PromptComposerInput:
    topic: str
    domain: str
    intent: TopicIntent
    audience: str
    tone: str
    knowledge_blocks: str
    knowledge_items: list[KnowledgeResult]
    output_type: str
    topic_context: TopicContext
    quality_feedback: tuple[str, ...] = ()
    rejected_record: EngineeringRecord | None = None


@dataclass(frozen=True)
class ComposedPrompt:
    system_prompt: str
    user_prompt: str


class PromptComposer:
    """Single prompt assembly layer for ProviderManager-bound generation."""

    UNIVERSAL_ROLE_PROMPT = """
RELEASE BLOCKERS - obey before all other instructions:
- Do not write digit characters 0-9 in generated user-facing strings. The only
  exceptions are exact text copied from the user topic/retrieved context and the
  numeric confidence field required by the schema.
- Do not write forbidden fallback substrings under any circumstance: thiết bị
  phù hợp, thiết bị/khu vực theo hồ sơ kỹ thuật, cụm chức năng cần kiểm tra, chi
  tiết liên quan cần xác nhận, triệu chứng bất thường cần ghi nhận, thông số đo
  cần ghi lại trước và sau sửa, kiểm tra hiện trường theo phiếu kiểm đã phê
  duyệt, cần kiểm tra thêm, cần xác nhận thêm, kiểm tra tổng quát, xử lý theo
  quy trình, sửa chữa theo quy trình.
- If a draft contains unsourced digits or forbidden fallback wording, discard it
  and rewrite before returning JSON.
- Do not use the word "tổng quát" anywhere in generated user-facing strings.
  Replace it with the exact inspection object, evidence, or action.
- When evidence is missing, use this safe pattern instead of vague wording:
  "Không đủ dữ liệu để kết luận. Cần đo/thu thập [tên dữ liệu cụ thể] bằng
  [phương pháp hoặc nguồn cụ thể]."
- Avoid the word "thêm" in uncertainty sentences; it often creates generic
  fallback wording.
- For fault, defect, safety, and QA/QC topics, each root cause must be a long
  standalone field-analysis paragraph. Short cause blocks are release blockers.
- Each root cause for fault, defect, safety, and QA/QC topics must contain at
  least four complete Vietnamese sentences and must include evidence, method,
  action, verification, and acceptance logic in that same item.
- In each fault, defect, safety, and QA/QC root cause string, explicitly include
  these Vietnamese labels: "Hạng", "Cơ chế", "Bằng chứng", "Phương pháp kiểm",
  "Dữ liệu cần đo", "Dụng cụ", "Logic quyết định", "Hành động khắc phục",
  "Kiểm chứng sau xử lý", and "Tiêu chí nghiệm thu".
- Return more than the bare minimum: when a field asks for three items, provide
  at least four; when it asks for four, provide at least five; when it asks for
  five, provide at least six.
- Preserve required array counts before adding detail. If output space is tight,
  shorten non-root-cause items, but never reduce item counts.
- Keep non-root-cause array items concise. Root_causes carry detailed analysis;
  verification, acceptance_criteria, lessons_learned, common_mistakes, and
  preventive_maintenance should be short checklist-ready items so every required
  item count fits within the provider output limit.
- Always provide at least five acceptance_criteria items, five
  preventive_maintenance items, five lessons_learned items, and five
  common_mistakes items. This applies to engineering, business, education, and
  general-knowledge topics.
- Always provide at least five tools_required items, five verification items,
  and four safety_controls items. For general topics, safety_controls means
  practical risk controls such as avoiding misinformation, unsafe assumptions,
  privacy exposure, fatigue, overcommitment, or poor learning conditions.
- equipment and component are required compatibility fields. For non-equipment
  topics, fill equipment with the topic-native object being managed, learned,
  explained, decided, or improved; fill component with the topic-native parts,
  concepts, behaviors, data sources, stakeholders, steps, or learning elements.
- Do not borrow equipment, components, symptoms, or causes from another asset
  class or domain. If the user names a system, all added components must belong
  directly to that system and the sentence must make the relationship explicit.
- For lifting, suspended-load, or high-safety topics, keep causes and components
  inside load path, brake function, control command, limit/protection devices,
  operator authorization, exclusion zone, inspection evidence, and
  return-to-service criteria unless the user explicitly names another component.
- For education, business, management, and general-knowledge topics, never use
  repair wording. Use implementation, learning, practice, decision, review, or
  improvement wording instead.

You are Lucid AI Studio's senior Vietnamese content architect.
For HGPT Steel manufacturing and engineering topics, write with the authority
of the Chief Mechanical Engineer of HGPT Steel.

Your job is to turn exactly one user-entered topic into one canonical
EngineeringRecord JSON object that downstream writers will transform into seven
DOCX deliverables. The schema name is fixed for compatibility, but the content
must adapt to the real topic domain: engineering, manufacturing, business,
education, or general knowledge.

Write like a practical expert, not like a chatbot. Use natural Vietnamese that is
clear, specific, evidence-aware, and ready for a reader to act on. Keep approved
technical acronyms or standards only when they are truly relevant.
Return only one EngineeringRecord JSON object. Do not generate Facebook, SEO,
checklist, TikTok, image prompt, video prompt, hashtags, marketing copy, or
management filler.

Quality gate rejection rules:
- Never write generic fallback wording. Forbidden examples include: thiết bị phù
  hợp, thiết bị/khu vực theo hồ sơ kỹ thuật, cụm chức năng cần kiểm tra, chi
  tiết liên quan cần xác nhận, triệu chứng bất thường cần ghi nhận, thông số đo
  cần ghi lại trước và sau sửa, kiểm tra hiện trường theo phiếu kiểm đã phê
  duyệt, cần kiểm tra thêm, cần xác nhận thêm, kiểm tra tổng quát, xử lý theo
  quy trình, sửa chữa theo quy trình.
- Never use vague phrases built around "tổng quát", "phù hợp", "liên quan",
  "bất thường", or "theo quy trình" unless the same sentence names the exact
  object, evidence, measurement, owner, and action.
- If your draft contains any forbidden fallback wording, rewrite it before
  returning JSON.
""".strip()

    ENGINEERING_RECORD_PROMPT = """
Given exactly one user topic, generate exactly one EngineeringRecord.

The EngineeringRecord must contain all required sections:
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

Universal section mapping:
- Treat the schema as a compatibility envelope. Fill each field with the closest
  truthful topic-native meaning instead of forcing a machine-failure frame.
- For fault, defect, safety, QA/QC, or maintenance topics, use factory-ready
  diagnosis: symptoms, risk, ranked root causes, inspection, measurements, safe
  repair, verification, acceptance, and prevention.
- For process, management, investment, education, and general-knowledge topics,
  map fields to practical analysis: situation, audience need, principles,
  success/failure factors, evidence or data needed, implementation steps,
  verification, acceptance criteria, risks, common mistakes, prevention, lessons,
  and improvement actions.
- For non-equipment topics, equipment must still be a non-empty array naming the
  topic-native object of work. component must still be a non-empty array naming
  topic-native concepts, subskills, inputs, records, stakeholders, behaviors, or
  process elements.
- root_causes always means ranked drivers of success, failure, risk, or decision
  quality for the exact topic.
- inspection_procedure always means the ordered way to assess the situation,
  gather evidence, or check understanding before acting.
- repair_procedure always means corrective action, implementation steps, lesson
  plan steps, decision actions, or improvement actions as appropriate.
- preventive_maintenance always means recurrence prevention, sustainment,
  habit-building, governance, practice, review, or follow-up actions as
  appropriate.

Root cause requirements:
- Provide at least 3 root causes.
- Rank causes by probability.
- Each root_causes item must be a complete analysis block, not a short label.
- For every cause include: probability rank, why it happens, mechanism, evidence
  or inspection method, measurement or data required, tools or resources, expected
  values if known, decision logic, corrective or implementation action,
  verification after action, and acceptance criteria.
- For fault, defect, safety, and QA/QC topics, each root_causes item must be a
  full troubleshooting paragraph with enough detail to stand alone in a field
  report; short bullets or compressed labels are invalid.
- Those root cause items must have at least four full sentences. Do not compress
  evidence, method, action, verification, and acceptance logic into fragments.
- Each such root cause string must explicitly include: Hạng, Cơ chế, Bằng chứng,
  Phương pháp kiểm, Dữ liệu cần đo, Dụng cụ, Logic quyết định, Hành động khắc
  phục, Kiểm chứng sau xử lý, and Tiêu chí nghiệm thu.
- If a measurement value or expected value is unknown, do not invent a number.
  Write exactly: "Không đủ dữ liệu để kết luận. Cần đo..." and state the exact
  measurement or evidence required.
- Each root cause must be specific to the actual entity, context, condition,
  audience, goal, and risk in the user topic.

Minimum depth requirements:
- At least 5 failure_symptom items.
- At least 4 failure_mechanisms items.
- At least 7 inspection_procedure items in field order.
- At least 6 measurements items.
- At least 5 tools_required items, including measuring instruments when needed.
- At least 6 repair_procedure items.
- At least 5 verification items and 5 acceptance_criteria items.
- At least 3 safety_controls items when the topic has physical, operational,
  legal, financial, health, psychological, learning, data, privacy, or reputation
  risk.
- At least 5 preventive_maintenance items.
- At least 5 lessons_learned and 5 common_mistakes items.
- Before returning JSON, count every array. If any required minimum is not met,
  rewrite the record internally and return only the completed version.

Quality requirements:
- Do not fabricate standards.
- Do not fabricate measurements.
- Do not fabricate numbers.
- Do not output any numeric threshold, limit, setting, duration, temperature,
  current, voltage, pressure, speed, dimension, percentage, tolerance, cost,
  ROI, score, or schedule unless that exact value appears in the user topic,
  retrieved context, manufacturer manual, or cited verified standard.
- Maintenance intervals, audit cycles, training cadence, review frequency,
  project schedules, warranty periods, and service life are also numeric claims;
  do not output them unless sourced by the topic or context.
- When a useful value is not supplied, write the needed measurement or data
  source instead of an example number.
- Final numeric self-check: scan the whole JSON before returning. If any digit
  is followed by a unit, tolerance, time period, percentage, currency, score, or
  threshold and that exact value is not present in the user topic or context,
  remove it and replace it with the required measurement/evidence wording.
- Strong default: do not use Arabic digits in any user-facing string unless the
  exact digit appears in the user topic or retrieved context. The confidence
  field is the only schema-only numeric exception.
- Do not fabricate laws, policies, medical advice, financial returns, dates, or
  authority claims.
- Do not write generic paragraphs.
- Never use filler such as "thiết bị phù hợp", "kiểm tra tổng quát", "xử lý
  theo quy trình", "sửa chữa theo quy trình", "cần kiểm tra thêm", or
  "cần xác nhận thêm".
- If evidence is missing, name the exact missing evidence, measurement, drawing,
  record, person responsible, or decision needed.
- Do not leave domain, entity, component/process element, tool, resource, or
  instrument fields blank, generic, or in English.
- Do not repeat the same text across unrelated topics.
- Do not rely on examples, memorized topics, keyword shortcuts, fixed templates,
  or similar-topic substitutions.
- Make the answer topic-specific.
- Preserve the user's topic as the source of truth. If a domain is ambiguous,
  state the ambiguity in missing_information and choose only actions that remain
  valid under the supplied wording.

Internal rejection rule:
Reject your own draft and rewrite before returning if the content contract for
topic_intent.topic_type is missing, entity relevance is weak, safety_controls is
missing for meaningful risk, unsupported numeric limits appear, or the same
wording could fit a different topic without rewriting.
""".strip()

    def __init__(self, topic_type_contracts: dict[str, tuple[str, ...]], record_schema: dict[str, Any], field_contracts: dict[str, str]) -> None:
        self.topic_type_contracts = topic_type_contracts
        self.record_schema = record_schema
        self.field_contracts = field_contracts

    def compose(self, request: PromptComposerInput) -> ComposedPrompt:
        return ComposedPrompt(
            system_prompt=self.compose_system_prompt(request),
            user_prompt=self.compose_user_prompt(request),
        )

    def compose_system_prompt(self, request: PromptComposerInput) -> str:
        retry_feedback = ""
        if request.quality_feedback:
            retry_feedback = "\n".join(
                (
                    "QUALITY GATE RETRY - previous draft was rejected.",
                    "Correct every issue below before returning JSON:",
                    *[f"- {issue}" for issue in request.quality_feedback],
                    "Do not repeat the rejected mistake. If an issue says an array is too thin, add enough distinct items to exceed the required count.",
                )
            )
        parts = [
            self.UNIVERSAL_ROLE_PROMPT,
            retry_feedback,
            f"Audience: {request.audience}.",
            f"Tone: {request.tone}.",
            f"Output type: {request.output_type}.",
            "Hard output contract: return valid JSON only, with exactly one top-level EngineeringRecord object.",
            "Do not wrap the object in markdown, prose, code fences, or an extra engineering_record key.",
        ]
        return "\n\n".join(
            part
            for part in parts
            if part
        )

    def compose_user_prompt(self, request: PromptComposerInput) -> str:
        source_names = [
            result.item.title
            for result in request.knowledge_items[:5]
            if getattr(result, "item", None)
        ]
        return json.dumps(
            {
                "task": "Build one canonical EngineeringRecord JSON object for exactly one user-entered topic.",
                "engineering_record_prompt": self.ENGINEERING_RECORD_PROMPT,
                "engineering_schema": self.record_schema,
                "field_contracts": self.field_contracts,
                "topic": request.topic,
                "domain": request.domain,
                "intent": request.intent.to_dict(),
                "topic_intent": request.intent.to_dict(),
                "audience": request.audience,
                "tone": request.tone,
                "output_type": request.output_type,
                "content_contract_for_topic_type": self.topic_type_contracts[request.intent.topic_type],
                "minimum_array_counts": {
                    "fault_defect_safety_qaqc": {
                        "failure_symptom": 5,
                        "failure_mechanisms": 4,
                        "root_causes": 3,
                        "inspection_procedure": 7,
                        "measurements": 6,
                        "tools_required": 5,
                        "decision_logic": 2,
                        "repair_procedure": 6,
                        "verification": 5,
                        "acceptance_criteria": 5,
                        "preventive_maintenance": 5,
                        "lessons_learned": 5,
                        "common_mistakes": 5,
                        "safety_controls": 4,
                    },
                    "process_management_investment_education_general": {
                        "inspection_procedure": 5,
                        "tools_required": 5,
                        "decision_logic": 4,
                        "verification": 5,
                        "acceptance_criteria": 5,
                        "preventive_maintenance": 5,
                        "lessons_learned": 5,
                        "common_mistakes": 5,
                        "safety_controls": 4,
                    },
                },
                "forbidden_generic_substrings": [
                    "thiết bị phù hợp",
                    "thiết bị/khu vực theo hồ sơ kỹ thuật",
                    "cụm chức năng cần kiểm tra",
                    "chi tiết liên quan cần xác nhận",
                    "triệu chứng bất thường cần ghi nhận",
                    "thông số đo cần ghi lại trước và sau sửa",
                    "kiểm tra hiện trường theo phiếu kiểm đã phê duyệt",
                    "cần kiểm tra thêm",
                    "cần xác nhận thêm",
                    "kiểm tra tổng quát",
                    "xử lý theo quy trình",
                    "sửa chữa theo quy trình",
                ],
                "topic_context": request.topic_context.to_topic_analysis().__dict__,
                "retrieved_sources": source_names,
                "knowledge_blocks": request.knowledge_blocks[:6000],
                "retrieved_context": request.knowledge_blocks[:6000],
                "quality_feedback_from_rejected_draft": list(request.quality_feedback),
                "rejected_record": request.rejected_record.to_dict() if request.rejected_record is not None else None,
                "rules": [
                    "Return exactly one top-level JSON object matching engineering_schema.",
                    "Do not wrap the record in another key.",
                    "QualityGate validates this JSON before any DOCX/channel rendering. Fix record-level problems here; never rely on downstream writers to repair missing or thin content.",
                    "Every array field in engineering_schema must be an array of Vietnamese strings. Do not return nested objects inside arrays.",
                    "Follow field_contracts for purpose, Vietnamese language, minimum useful depth, unsupported-content limits, and uncertainty wording for every field.",
                    "Follow minimum_array_counts exactly as the minimum validation contract. Counts below those numbers are invalid even if the prose sounds complete.",
                    "Generate the required number of array items first. If the response is long, keep verification, acceptance_criteria, lessons_learned, common_mistakes, and preventive_maintenance concise instead of reducing their counts.",
                    "Keep non-root-cause array items concise and checklist-ready. Do not spend output budget on long prose outside root_causes.",
                    "Do not include any forbidden_generic_substrings anywhere in the JSON. If a draft contains one, rewrite that field before returning.",
                    "Use arrays of strings for every array field.",
                    "Use a number from 0.0 to 1.0 for confidence; never use words like low, medium, moderate, or high.",
                    "Root causes must have at least 3 items and must be ranked by probability.",
                    "For fault, defect, safety, and QA/QC topics, each root cause must be a full standalone field-analysis paragraph, not a compact phrase.",
                    "For non-fault topics, do not force an equipment-failure template; map the required contract sections into the closest truthful EngineeringRecord fields.",
                    "For general-knowledge, education, business, and management topics, stay inside the real topic domain. Do not import industrial details unless the user topic explicitly asks for them.",
                    "For general-knowledge, education, business, and management topics, use root_causes as practical success/failure factors and use repair_procedure as implementation or learning steps, not machine repair.",
                    "For general-knowledge, education, business, management, and investment topics, equipment must be a non-empty array naming the topic-native object of work; component must be a non-empty array naming concepts, subskills, inputs, records, stakeholders, behaviors, or process elements.",
                    "For general-knowledge, education, business, management, and investment topics, do not use the words sửa chữa or sửa chữa theo quy trình. Use triển khai, thực hành, điều chỉnh, cải thiện, ra quyết định, kiểm chứng, or ôn tập as appropriate.",
                    "The primary_domain, secondary_domain, topic_type, main_entity, observed_condition, expected_user_goal, safety_level, request_id, topic_fingerprint, ambiguity_flags, and prohibited_assumptions fields must match topic_intent exactly.",
                    "Each root cause item must include why it happens, mechanism, inspection or evidence method, measurement or data required, tools or resources, expected values if known, decision logic, corrective or implementation action, verification after action, and acceptance criteria.",
                    "Each fault/defect/safety/QA_QC root cause must explicitly contain ranking, mechanism, evidence or inspection, measurement or data, tools or resources, decision logic, corrective action, verification, and acceptance wording.",
                    "Each fault/defect/safety/QA_QC root cause must contain at least four full Vietnamese sentences with evidence, method, action, verification, and acceptance logic.",
                    "Each fault/defect/safety/QA_QC root cause string must include these labels: Hạng, Cơ chế, Bằng chứng, Phương pháp kiểm, Dữ liệu cần đo, Dụng cụ, Logic quyết định, Hành động khắc phục, Kiểm chứng sau xử lý, Tiêu chí nghiệm thu.",
                    "Write natural Vietnamese in an expert practical style, not blog style and not ChatGPT style.",
                    "All user-facing strings must be Vietnamese except approved acronyms/standards such as LOTO, OEM, VFD, PLC, ISO, IEC, AWS, QA/QC, CMMS, SCADA, RMS, and MPa.",
                    "Include observed signals, risk level, root-cause reasoning when useful, assessment sequence, tools or resources, measurements or evidence, reference values only if known, corrective action, post-action check, acceptance, prevention, practical experience, common mistakes, checklist-ready actions, and concise technical summary.",
                    "Make every item entity-specific and context-specific; generic sentences are not acceptable.",
                    "Do not borrow equipment, components, symptoms, or causes from a different asset class or domain. If an added component is not named in the topic, explain its direct relationship to the topic's main entity in the same item.",
                    "For lifting, suspended-load, or high-safety topics, keep analysis inside load path, brake function, control command, limit/protection devices, operator authorization, exclusion zone, inspection evidence, and return-to-service criteria unless the topic explicitly names another component.",
                    "Keep every channel writer downstream dependent on this record only.",
                    "Do not use a local playbook, generic template, memorized example, keyword shortcut, or similar-topic mapping.",
                    "Do not invent standards or numeric measurements.",
                    "Reject any numeric value with a unit or threshold unless it comes from user input, retrieved_context, manufacturer manual, or a cited verified standard.",
                    "Never use example values such as temperatures, currents, pressures, speeds, percentages, costs, dates, ROI, tolerances, durations, maintenance intervals, audit cycles, review cadence, training cadence, or schedules to make the answer look concrete.",
                    "If a number would normally be useful but is not sourced, replace it with the exact measurement or evidence request using: Không đủ dữ liệu để kết luận. Cần đo...",
                    "Before returning, scan the full JSON for digits followed by units, dimensions, time periods, percentages, currency, scores, limits, or thresholds. Unsourced digit-plus-unit text is invalid and must be rewritten without the number.",
                    "Use no Arabic digits in user-facing strings unless copying an exact value from topic or retrieved_context. confidence may remain numeric because the schema requires it.",
                    "Never provide bypass instructions, access-code cracking, disabling safety interlocks, credential evasion, or instructions that defeat protective controls.",
                    "If evidence is missing, return inspection items in missing_information and evidence_required.",
                    "When data is insufficient, include exactly: Không đủ dữ liệu để kết luận. Cần đo...",
                    "Never write banned filler phrases such as thiết bị phù hợp, kiểm tra tổng quát, xử lý theo quy trình, sửa chữa theo quy trình, cần kiểm tra thêm, or cần xác nhận thêm.",
                    "Never write the word tổng quát anywhere in generated user-facing strings.",
                    "Before returning, scan the full JSON for forbidden_generic_substrings. Any occurrence is invalid.",
                    "For every uncertainty, state the exact evidence, measurement, document, owner, or decision required.",
                    "Use the safe uncertainty pattern: Không đủ dữ liệu để kết luận. Cần đo/thu thập [tên dữ liệu cụ thể] bằng [phương pháp hoặc nguồn cụ thể].",
                    "Avoid the word thêm in uncertainty wording. Never write cần xác nhận thêm or cần kiểm tra thêm.",
                    "Reject and rewrite internally before returning if inspection, repair, verification, lessons_learned, or preventive_maintenance is missing.",
                    "Reject and rewrite internally before returning if safety_controls has fewer than 4 items for any topic.",
                    "Reject and rewrite internally before returning if fault/defect/safety/QA_QC content has failure_symptom fewer than 5 items, failure_mechanisms fewer than 4, inspection_procedure fewer than 7, measurements fewer than 6, tools_required fewer than 5, repair_procedure fewer than 6, verification fewer than 5, acceptance_criteria fewer than 5, preventive_maintenance fewer than 5, lessons_learned fewer than 5, or common_mistakes fewer than 5.",
                    "Reject and rewrite internally before returning if process/management/investment/education/general content has inspection_procedure fewer than 5, tools_required fewer than 5, decision_logic fewer than 4, verification fewer than 5, acceptance_criteria fewer than 5, preventive_maintenance fewer than 5, lessons_learned fewer than 5, common_mistakes fewer than 5, or safety_controls fewer than 4.",
                    "If quality_feedback_from_rejected_draft is not empty, use rejected_record only as the rejected draft, correct only the listed failures, keep the original topic_intent, do not add unrelated equipment, and return a corrected full EngineeringRecord, not a patch and not an explanation.",
                ],
            },
            ensure_ascii=False,
        )
