from __future__ import annotations

import hashlib


MOTION_LIBRARY = (
    "slow handoff from operator pointing to the defect, to engineer measuring, to supervisor confirming the safe condition",
    "measured wrist movement placing the probe, a second hand logging evidence, and a final controlled step away from the hazard zone",
    "operator pauses the line, engineer kneels beside the component, then both reset posture after the verification mark is recorded",
    "technician wipes the surface, positions the gauge, checks the reading angle, and tags the part for controlled follow-up",
)

CAMERA_LIBRARY = (
    "3/4 chest-height documentary angle, controlled push-in, macro insert on the evidence, then a clean pull-back to show the safe work area",
    "low industrial foreground with tools in front, over-the-shoulder inspection view, shallow macro detail, then locked-off verification frame",
    "wide establishing view through steel columns, lateral track beside the machine, close insert on the measurement, then static sign-off shot",
    "handheld-stable factory documentary framing with a parallax move past guardrails, a tight insert, and a final rule-of-thirds composition",
)

INDUSTRIAL_EFFECT_LIBRARY = (
    "fine metal dust in light beams, soft vibration from running equipment in the background, faint oil sheen on nearby parts, no unsafe sparks",
    "subtle welding haze far behind the controlled area, warning beacon reflection on painted steel, realistic shop-floor scuffs",
    "compressed-air hiss, mild heat shimmer near fabrication equipment, dust on boots, clean LOTO tag movement in foreground",
    "overhead crane shadow passing slowly across steel beams, small gauge beep, paper checklist flutter from ventilation",
)

LIGHTING_LIBRARY = (
    "high-bay factory lighting with a focused inspection lamp, soft highlights on brushed steel, neutral color temperature, no theatrical neon",
    "overhead LED strips mixed with side light from an open bay door, crisp texture on PPE, readable but minimal labels",
    "cool morning shop light, practical task lamp on the defect, controlled contrast, no blown highlights on reflective metal",
    "diffused industrial light with a small rim on helmets and gloves, clear visibility inside machine guards and steel structures",
)

VOICE_LIBRARY = (
    "calm Vietnamese engineering narrator, concise and firm, speaking like a senior QA/QC lead during a shift briefing",
    "steady maintenance supervisor voice, practical and low-drama, emphasizing evidence before handover",
    "clear shop-floor trainer voice, direct and reassuring, turning the inspection into one memorable field rule",
    "focused production engineer voice, measured pace, confident but never sales-like",
)

HOOK_LIBRARY = (
    "Do not restart the line until the evidence matches the repair.",
    "A small surface sign can decide whether this part is released or held.",
    "The safest repair starts before the first wrench moves.",
    "If the measurement is unclear, the handover is not ready.",
)

CTA_LIBRARY = (
    "Save this as a shift-start inspection reminder.",
    "Use this sequence before releasing the equipment back to production.",
    "Bring this checklist into the next QA/QC handover.",
    "Share this with the maintenance team before the next restart.",
)


def choose(library: tuple[str, ...], seed_text: str, offset: int = 0) -> str:
    if not library:
        return ""
    digest = hashlib.sha256(seed_text.encode("utf-8")).hexdigest()
    seed = int(digest[:8], 16)
    return library[(seed + offset) % len(library)]


def concise(value: str, max_words: int = 18) -> str:
    words = str(value or "").replace("\n", " ").split()
    if len(words) <= max_words:
        return " ".join(words)
    return " ".join(words[:max_words]) + "..."


def image_prompt(
    *,
    topic: str,
    subject: str,
    problem: str,
    objects: str,
    signs: str,
    action: str,
    equipment: str = "steel-structure factory equipment",
    tools: str = "measuring tools, checklist, camera, and LOTO tag",
    safety: str = "energy isolation, barricade, warning sign, and complete PPE",
    evidence: str = "visible defect, measurement point, inspection record, and controlled handover status",
) -> str:
    topic = concise(topic, 16)
    subject = concise(subject, 14)
    problem = concise(problem, 20)
    objects = concise(objects, 18)
    signs = concise(signs, 18)
    action = concise(action, 20)
    equipment = concise(equipment, 12)
    tools = concise(tools, 14)
    safety = concise(safety, 14)
    evidence = concise(evidence, 18)
    seed = f"image:{topic}:{subject}:{problem}:{objects}:{signs}"
    camera = choose(CAMERA_LIBRARY, seed)
    lighting = choose(LIGHTING_LIBRARY, seed, 1)
    effects = choose(INDUSTRIAL_EFFECT_LIBRARY, seed, 2)
    secondary_motion = choose(MOTION_LIBRARY, seed, 3)
    return "\n".join(
        [
            f"Chủ thể: Create a photorealistic industrial documentary image about {topic}. The main subject is a Vietnamese QA/QC or maintenance engineer, gender female or male as fits the scene, about 30-45 years old, wearing a dark factory uniform, helmet, safety glasses, cut-resistant gloves, safety shoes, and reflective vest or workshop jacket. The face shows focused concern. The engineer stands in a stable half-crouch or forward-leaning inspection posture, one hand controlling {tools}, the other keeping records clear of the hazard zone.",
            f"Bối cảnh: Place the scene inside a steel-structure factory with overhead cranes, welded beams, jigs, guarded machines, tool cabinets, cable trays, pallets, floor markings, warning signs, and worn concrete. Show {equipment} as the dominant industrial object, with {objects} and surrounding steel structures visible enough to avoid a generic office or showroom look. The atmosphere is busy but controlled, with 5S discipline and no clutter blocking evidence.",
            f"Hành động chính: The engineer is performing {action} to investigate {problem}. Show the relationship between person, equipment, evidence, and decision point. Make {signs} visually readable through surface condition, tool placement, alignment marks, gauge position, weld zone, bearing area, DFT check area, or another topic-specific clue.",
            f"Chuyển động phụ: Include small believable motions: {secondary_motion}. Background machines may be idle, guarded, or moving slowly only when safe; a beacon may glow or ventilation may move dust, but the main work area remains controlled. Avoid unsafe reaching, bypassed interlocks, missing guards, or hands inside pinch points.",
            f"Góc máy: Use {camera}. Keep subject and evidence in one coherent composition. The viewer should understand the workflow in one look: detect, isolate, measure, decide. Use a 35mm documentary feel and macro-like sharpness on technical detail.",
            f"Ánh sáng: Use {lighting}. Light must reveal metal surface detail, PPE material, labels, tool edges, and evidence. Keep color natural, crisp, and industrial; no neon, stage lighting, fantasy glow, overexposure, or dark shadows.",
            f"Vật liệu: Emphasize painted structural steel, scratched bare metal, weld beads, bolts, rubber hoses, cable insulation, hydraulic or pneumatic fittings, paper checklists, tag holders, dust, oil film, and worn concrete. Materials must look tactile and physically plausible.",
            f"Hiệu ứng công nghiệp: Add {effects}. Effects must support realism without hiding the subject. No dramatic fire, fake sparks, smoke clouds, broken machinery explosion, or disaster imagery unless the topic explicitly requires controlled welding or cutting.",
            "Bố cục: Rule of thirds, layered foreground-middle-background, clean leading lines from tool to defect to checklist, readable negative space for a small caption. The image should work as a technical training visual.",
            "Phong cách hình ảnh: Photorealistic industrial field documentation, high-detail factory realism, professional QA/QC training image, grounded Vietnamese steel-fabrication environment, serious but constructive mood.",
            f"Chất lượng hình ảnh: Ultra sharp, high dynamic range but natural, 4:5 vertical composition, no watermark, no fake brand, no misspelled Vietnamese text, no distorted hands, no duplicated tools, no unrelated equipment, no cartoon, no cheap CGI, no blur. Safety requirements visible: {safety}. Evidence to show: {evidence}.",
        ]
    )


def video_storyboard(
    *,
    topic: str,
    subject: str,
    problem: str,
    objects: str,
    signs: str,
    action: str,
    equipment: str = "steel-structure factory equipment",
    tools: str = "measuring tools, checklist, camera, and LOTO tag",
    repair: str = "corrective action on the confirmed root cause",
    verification: str = "final measurement and safe handover confirmation",
    safety: str = "energy isolation, barricade, warning sign, and complete PPE",
) -> str:
    topic = concise(topic, 16)
    subject = concise(subject, 14)
    problem = concise(problem, 20)
    objects = concise(objects, 16)
    signs = concise(signs, 16)
    action = concise(action, 18)
    equipment = concise(equipment, 12)
    tools = concise(tools, 14)
    repair = concise(repair, 18)
    verification = concise(verification, 18)
    safety = concise(safety, 14)
    seed = f"video:{topic}:{subject}:{problem}:{objects}:{signs}"
    camera = choose(CAMERA_LIBRARY, seed)
    lighting = choose(LIGHTING_LIBRARY, seed, 1)
    effect = choose(INDUSTRIAL_EFFECT_LIBRARY, seed, 2)
    voice = choose(VOICE_LIBRARY, seed, 3)
    hook = choose(HOOK_LIBRARY, seed, 4)
    cta = choose(CTA_LIBRARY, seed, 5)
    motion = choose(MOTION_LIBRARY, seed, 6)
    return "\n".join(
        [
            f"Tiêu đề: Mini documentary - {topic}",
            "Thời lượng: 45-60 giây",
            "",
            f"Cảnh 1 - Hook: Góc máy di chuyển: {camera}; start with a controlled push-in from the factory aisle toward {equipment}. Worker movement: operator freezes the task, raises one hand to signal hold, then points from outside the hazard zone. Machine movement: machine is idle or slowing under control; guarded background equipment continues softly. Ambient sound: low factory ambience, one short equipment wind-down, faint checklist paper movement. Voice: \"{hook}\" Emotion: alert, serious, immediate.",
            "",
            f"Cảnh 2 - Failure: Góc máy di chuyển: over-the-shoulder shift into a macro insert on {signs}; hold long enough for the failure evidence to register. Worker movement: engineer in full PPE places {tools}, checks the angle, and records the finding. Machine movement: no unsafe moving parts near hands; only distant guarded motion and a small beacon reflection. Ambient sound: gauge beep, marker tap, soft metal contact. Voice: \"Do not guess the cause; isolate, measure, and compare.\" Emotion: focused concern.",
            "",
            f"Cảnh 3 - Diagnosis: Góc máy di chuyển: lateral track beside the engineer, then a tight insert as the confirmed diagnosis begins. Worker movement: team performs {action}, points from symptom to root-cause area, then separates assumption from evidence. Machine movement: if a test movement is needed, it is slow, guarded, and observed from a safe distance. Ambient sound: tool click, low ventilation, restrained industrial beat. Voice: \"The cause is not the loudest symptom; it is the condition that makes the symptom return.\" Emotion: disciplined investigation.",
            "",
            f"Cảnh 4 - Repair: Góc máy di chuyển: close handheld-stable move on the repair point, then a wider shot showing safe body position. Worker movement: team starts {repair} without shortcut, one worker controls tools while another watches the hazard boundary. Machine movement: equipment remains isolated or moves only in a controlled test. Ambient sound: wrench click, low motor hum, ventilation, short supervisor confirmation. Voice: \"The repair follows the evidence, not habit.\" Emotion: practical confidence.",
            "",
            f"Cảnh 5 - Result: Góc máy di chuyển: pull back to a stable rule-of-thirds sign-off frame showing engineer, equipment, and checklist together. Worker movement: engineer completes {verification}, operator nods, and both step back from the equipment. Machine movement: equipment remains controlled or returns to a safe ready state only after confirmation. Ambient sound: final gauge beep, pen tick on checklist, ambience settles. Voice: \"Record the result before handover.\" Emotion: relief, trust, professional closure.",
            "",
            f"Kết thúc: On-screen text: \"Dừng - Đo - Xử lý - Xác nhận\" plus small CTA: \"{cta}\" Voice style: {voice}. Lighting: {lighting}. Industrial effects: {effect}. Avoid: one-paragraph prompt, slideshow, static image sequence, unsafe action, missing PPE, distorted text, watermark, unrelated machines, cartoon or cheap CGI.",
        ]
    )
