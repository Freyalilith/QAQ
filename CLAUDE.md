# CLAUDE.md

This file provides Claude Code-specific instructions for working on the **User-Named Elderly AI Companion** repository.

Use this together with `AGENTS.md`. `AGENTS.md` contains global product, safety, and architecture rules. This file adds Claude Code workflow expectations.

---

## 1. Session startup checklist

At the start of a coding session:

1. Read `AGENTS.md`.
2. Read `docs/06_collaboration_workflow.md`.
3. Skim the relevant sections of:

```text
docs/00_overview_elderly_companion_ai.md
docs/01_prd_elderly_multi_agent_companion_ai.md
docs/02_technical_roadmap_elderly_multi_agent_companion_ai.md
docs/05_reference_project_structure.md
```

4. Identify the target issue number.
5. Confirm whether the task is P0, P1, or Future.
6. Refuse to expand scope silently.
7. Prefer a small, testable change over broad refactoring.

Current project direction:

```text
relationship-first voice companion for older adults
product targets older adults broadly, not a narrow subgroup
not a generic assistant
not a medical chatbot
not an addictive companion
not a real emergency system
```

---

## 2. Current collaboration model

This repo is optimized for AI-first development with asynchronous review.

Assume the practical model is:

```text
one main completer advances P0 vertical slices
reviewer checks PR behavior and safety in daily batches
other contributors may later add non-blocking docs / QA / test cases
```

Do not assume every issue has a stable owner. Do not wait for a human assignment if the user asks you to implement the next slice.

---

## 3. Mainline execution order

When asked what to do next, follow this order unless the user explicitly changes priority:

```text
Slice 1: #1 docs entry → #2 frontend shell → #3 FastAPI chat baseline
Slice 2: #21 first-run onboarding → #6 CompanionAgent persona
Slice 3: #5 Coordinator → #8 Safety → #9 Agent Trace
Slice 4: #10 Memory → #11 Reminder
Slice 5: #22 SensorAdapter / StateEvent → #12 GuardianAgent
Slice 6: #13 controlled retrieval
Slice 7: #4 mock voice UI → #23 real ASR/TTS provider
Slice 8: #14 tests → #16 final demo materials
```

P1 issues are only after the related P0 slice is stable:

```text
#17 voice experience enhancement
#18 proactive care preference / quiet hours / topic library
#19 caregiver mock dashboard
#20 evaluation data export / video polish
```

If a requested issue depends on an unfinished earlier issue, mention the dependency risk before implementing.

---

## 4. How Claude should work on one issue

Do not attempt to implement the whole project at once.

For each issue:

```text
1. Restate the requested change briefly.
2. Inspect relevant files.
3. Make a minimal implementation plan.
4. Edit only relevant files.
5. Run tests or explain why tests could not run.
6. Prepare a PR using .github/pull_request_template.md.
7. Leave a handoff summary.
```

Prefer:

```text
small interfaces
fake providers first
unit tests alongside implementation
clear schema contracts
trace output for behavior-changing logic
```

Avoid:

```text
large rewrites
unrequested architecture changes
changing product docs casually
adding new dependencies without justification
hardcoding provider-specific logic everywhere
```

---

## 5. Branch and PR expectations

Use short-lived branches:

```text
feat/21-onboarding
feat/5-coordinator
feat/6-companion-agent
feat/22-state-event
feat/13-retrieval-gating
fix/safety-medication-template
docs/demo-script
```

Do not use broad branches such as:

```text
feat/full-system
feat/all-agents
refactor-everything
misc-updates
```

A main completer may open several small PRs before reviewer feedback arrives, as long as:

```text
- each PR is issue-scoped or slice-scoped;
- dependencies are stated clearly;
- DEMO_MODE=true remains runnable;
- no unrelated files are refactored;
- no fixed companion name, medical advice, or real emergency action is introduced.
```

Use `.github/pull_request_template.md` for every PR.

---

## 6. Required handoff after each AI coding session

At the end of every session, include this in the PR or issue:

```md
## Handoff
Completed:
- ...

Tested:
- ...

Not done:
- ...

Risks / questions:
- ...

Next recommended step:
- ...
```

This allows asynchronous daily review without blocking the main completer.

---

## 7. Product behavior Claude must preserve

### 7.1 User-named companion persona

The companion display name must be stored as `companion_display_name` and chosen by the user during onboarding or settings.

If the user has not named the companion yet, use:

```text
陪伴 AI / AI Companion
```

Do not invent or hardcode a fixed default name in prompts, UI copy, seed data, snapshots, tests, or demo scripts.

The companion persona is warm, patient, concise, emotionally grounding, and stable. It can feel like a familiar community junior, kind neighbor, or patient old friend, but it must not pretend to be a real person, doctor, family member, or caregiver.

Do not make the companion persona:

```text
sarcastic
flirty
toxic
overly cute
meme-heavy
youth-slang-heavy
medical-authoritative
emotionally possessive
```

### 7.2 Role-first response style

For emotional or personal messages, responses should follow:

```text
1. emotional grounding
2. content response
3. optional memory or context
4. one gentle follow-up question
```

For factual or task messages, still keep wording warm and short.

### 7.3 Well-being over stickiness

Do not write code or prompts that intentionally maximize dependency or endless chat.

Avoid:

```text
“只有我最懂您。”
“您不用找别人，我会一直陪您。”
“别结束，我们再聊一会儿。”
```

Prefer:

```text
“我可以陪您说一会儿，也可以帮您想想要不要联系家人。”
“您想先休息也可以，我可以晚点再提醒。”
```

---

## 8. Architecture Claude should implement

Use this conceptual architecture:

```text
User voice/text
→ Voice I/O service if voice
→ InputRuleGuard
→ CoordinatorAgent
   ├── CompanionAgent
   ├── GuardianAgent
   ├── SafetyCriticAgent when needed
   └── tools/services
→ OutputRuleGuard
→ TTS if voice
→ AgentTracePanel
```

Only these should appear as autonomous agents in code and trace:

```text
CoordinatorAgent
CompanionAgent
GuardianAgent
SafetyCriticAgent
```

These should be named as tools or services:

```text
EmotionClassifierTool
MemoryTool / MemoryStore
ReminderTool / ReminderScheduler
InfoRetrievalTool
SensorSimulatorTool
SensorAdapter / StateEncoder
InputRuleGuard / OutputRuleGuard
VoiceIOService
ASRService
TTSService
LLMProvider
```

Do not implement old-style `EmotionAgent`, `MemoryAgent`, `StateAgent`, or `InfoRetrievalAgent` unless the task explicitly asks for compatibility aliases.

---

## 9. Safety implementation instructions

Do not run SafetyCritic on every turn by default.

Use:

```text
InputRuleGuard: always cheap deterministic checks
OutputRuleGuard: always cheap deterministic checks
SafetyCriticAgent: only on detected risk or uncertainty
Safety templates: high-risk fallback
```

These inputs must not receive direct medical advice:

```text
“我胸口痛，是不是心脏病？”
“我忘了吃药，现在能不能吃两片？”
“我药吃多了怎么办？”
“我不想活了。”
“我摔倒了，起不来。”
“救命。”
```

Correct behavior:

```text
acknowledge concern calmly
state the system cannot diagnose or advise dosage
recommend contacting doctor/pharmacist/family/emergency service as appropriate
offer safe help such as recording a reminder or showing a mock emergency contact
in demo mode, clearly state no real emergency call is placed
```

Do not implement real phone calls, SMS, hospital dispatch, or emergency automation.

---

## 10. GuardianAgent instructions

GuardianAgent replaces the old simple State Agent + Proactive Policy idea.

Important boundary:

```text
raw/mock signal → SensorAdapter / StateEncoder → StateEvent → GuardianAgent decision
```

Guardian must consume structured `StateEvent`, not directly interpret raw sensor values.

Required output shape:

```json
{
  "care_proposal": "...",
  "restraint_critique": "...",
  "decision": "check_in | defer | silent_log | safety_escalation",
  "reason": "...",
  "cooldown_applied": true,
  "trace_visible_summary": "..."
}
```

Default constraints:

```text
same type cooldown: 2 hours
casual check-ins per day: max 3
quiet hours: 22:00–07:00
refusal pause: 24 hours for same topic
```

Do not use sensor presets to make diagnoses.

Use phrases like:

```text
“看起来可能比平时少一点”
“如果现在方便，我可以陪您聊两句”
```

Avoid:

```text
“您今天身体不好。”
“您可能生病了。”
“您一定很孤独。”
```

---

## 11. Controlled retrieval instructions

InfoRetrievalTool should be gated by Coordinator.

Call retrieval for:

```text
weather
air quality
nearby or opening hours if implemented
current community information
latest factual verification
```

Do not call retrieval for:

```text
emotional disclosure
reminiscence
simple reminders
memory deletion
relationship/persona chat
```

Medication dosage questions must not search for dosage answers.

Here, “do not retrieve” means **do not call web search / browser / external retrieval tools**. It does not mean the system cannot call an existing hosted LLM API.

In tests, retrieval must use fake/mock provider.

---

## 12. Testing expectations

Claude should add tests when implementing non-trivial logic.

Minimum backend tests should cover:

```text
rule guards for health and medication risk
coordinator routing
companion modes
first-run onboarding / companion_display_name fallback
guardian cooldown
SensorAdapter raw signal → StateEvent
memory delete / pause
reminder CRUD
trace schema
retrieval gating
DEMO_MODE provider fallback
```

Tests must pass in demo/fake-provider mode and must not call real LLM, ASR, TTS, or web APIs.

---

## 13. Suggested repository commands

These may change as the repo is initialized. Keep them updated in `README.md`.

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload
pytest
```

Frontend:

```bash
cd frontend
npm install
npm run dev
npm run lint
npm run test
```

Full local demo:

```bash
cp .env.example .env
# ensure DEMO_MODE=true
make dev
```

Do not assume these commands exist; create or update them when implementing project skeleton.

---

## 14. Documentation rules

When code changes alter behavior, update relevant docs:

```text
README.md for setup and commands
.env.example for env vars
API docs or OpenAPI schemas for endpoints
prompt files for model behavior
docs/05_reference_project_structure.md if folder structure changes significantly
docs/06_collaboration_workflow.md if collaboration/order changes significantly
```

Do not edit canonical product docs `00`–`04` unless the user explicitly asks for product-document changes.
