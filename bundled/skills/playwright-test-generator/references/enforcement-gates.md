# Phase Output: Proof Artifact Format Definition

> After completing each test case recording, output a "proof artifact."
> This step is critical as it serves as a "data relay baton" connecting pure page operations with the subsequent code generation phase.

---

## Why Proof Artifacts Are Needed

As an AI Agent, when translating actions into code, we often "blindly guess" extremely complex selectors on frontend pages due to overconfidence, leading to frequent subsequent errors.

The role of proof artifacts is to build a trust mechanism:
1. **ref numbers can only be obtained through actual calls to `playwright-cli snapshot`**
2. **JavaScript code can only be obtained from "### Ran Playwright code" returned by CLI**

When you preserve this "physical evidence," stage2B can generate code from recorded facts instead of selector guesses.

---

## Complete Proof Artifact Format

```
━━━━━━━━━━━━━━━━━━━━━━━━
✅ TCxxx Recording Complete (N steps)

【Operation Proof】
- Page URL: https://...
- Pre-operation snapshot ref list: e101(input) e66(trigger) e260(button) ...
  Note: Must list element refs actually interacted with in this test case, cannot be empty

【CLI JavaScript Code】⚠️ Must save - The only source for stage2B code generation
```js
// Copy complete code from "### Ran Playwright code" returned by CLI
// After each playwright-cli click/fill/type operation, CLI returns corresponding JavaScript code
// Must copy line by line, this is the only accurate source for generating Python code

// Example:
await page.goto('https://example.com/#/job/create');
await page.getByRole('textbox', { name: 'Job Title' }).fill('Software Engineer');
await page.getByRole('heading', { name: 'Job Basics' }).click();
await page.getByRole('generic', { name: 'Select Job Functions' }).click();
await page.getByText('Information & Communication Technology').click();
await page.getByText('Developers/Programmers').click();
await page.getByRole('radio', { name: 'Unselected Hybrid' }).click();
await page.getByRole('button', { name: 'Continue' }).click();
```

【Dynamic Behavior Discoveries】(Fill "None" if none)
- Dynamic overlay/recommendation popup appeared: Yes/No
  If yes: Overlay ref=___, Appearance timing: ___, Handling method: ___
- Cascading effect (operation A affects field B): Yes/No
  If yes: Field A ref=___, Affects field B ref=___, Effect description: ___
- Sticky TopBar occludes elements: Yes/No
  If yes: Used JS scrollTo offset 160px

【Verification Proof】
- Verification point text (exact): "___", ref=___
- Page stay/redirect: ___ (URL change situation)
- Verification snapshot timing: ___

【CLI Command Statistics】
open:_ snapshot:_ click:_ fill:_ type:_ press:_ screenshot:_ close:_
━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## `recording_trace.json`

Every `recording_passed` case should have a machine-readable trace saved next to the proof artifact. The path should be recorded in `playwright_recording_outcomes.json` as `details.recording_trace_path`.

QA Agent does not block Stage 2A delivery when the trace is missing, because the bug list and recording result should still be delivered first. Missing or inaccessible traces become Stage 2B blockers: do not invent Python scripts from memory when proof/trace does not contain enough real actions.

Minimum schema:

```json
{
  "tc_id": "TC001",
  "title": "case title",
  "source_doc": "/path/to/textcases.md",
  "environment": {
    "site": "ae",
    "base_url": "https://..."
  },
  "steps": [
    {
      "index": 1,
      "description": "Open target page",
      "cli_command": "playwright-cli -s=tc001 open ...",
      "ran_javascript": "await page.goto('https://...');",
      "before_url": "",
      "after_url": "https://...",
      "snapshot_refs": ["e1", "e2"],
      "verification": {
        "expected": "page title visible",
        "actual": "page title visible",
        "snapshot_path": ".playwright-cli/page-xxx.yml",
        "passed": true
      }
    }
  ],
  "dynamic_behaviors": [
    {
      "type": "overlay",
      "timing": "after filling Job Title",
      "handling": "click heading to dismiss before selecting Job Function"
    }
  ],
  "command_statistics": {
    "open": 1,
    "snapshot": 4,
    "click": 5,
    "fill": 2,
    "type": 0,
    "press": 0,
    "screenshot": 1,
    "close": 1
  }
}
```

Why this exists:
- The Markdown proof is for human review.
- `recording_trace.json` is for stage2B replay-first script generation.
- If a step has no `ran_javascript`, stage2B must not invent code for it; produce `script_blocker_report.md` instead.

---

## Field Descriptions

### ref List (Anti-Tampering Core)

```
# Correct example (output after real recording):
- Pre-operation snapshot ref list: e63(title input) e66(job function trigger) e260(Continue button)

# Wrong example (fabricated without recording):
- Pre-operation snapshot ref list: (empty)
- Pre-operation snapshot ref list: No need to record
```

User verification method: Find corresponding numbered elements in screenshot, confirm type and position match description.

### CLI JavaScript Code (Code Generation Core)

**⚠️ This is the only accurate source for stage2B code generation**

Each time a CLI command is called (click, fill, type, etc.), CLI returns:
```
### Ran Playwright code
```js
await page.getByRole('radio', { name: 'Unselected Hybrid' }).click();
```
```

**Must do**:
1. Find `### Ran Playwright code` code block in CLI output
2. Copy complete JavaScript code (including all await statements)
3. Paste into the 【CLI JavaScript Code】 field in proof artifact
4. Maintain original format and order of code

**Why must save**:
- Stage2B generates Python code by directly converting this JavaScript code
- Avoid AI "guessing" selectors based on ref numbers (accuracy <50%)
- Ensure generated Python code is completely consistent with recorded operations (accuracy 90%+)

**Wrong example**:
```
【CLI JavaScript Code】
// Not provided (AI skipped save step)
```
→ This will cause stage2B to be unable to generate accurate code, can only guess selectors

### Dynamic Behavior Discoveries (Most Important New Addition)

This is the core new addition of this optimization, solving the "didn't discover during recording, error after generation" problem:

```
# Scenario 1: Job Title fill triggers Job Function recommendation overlay
Dynamic overlay: Yes
Overlay ref=e123, Appearance timing: ~400ms after clicking preset autocomplete option
Handling method: Call heading.click() at start of select_job_function to close overlay

# Scenario 2: Pay Type switch automatically clears Min/Max amount
Cascading effect: Yes
Field A=Pay Type(ref=e221), Affects field B=Min/Max Amount(ref=e227/e235)
Effect description: After switch, both Amount fields restore initial state, div with textContent exactly matching "Amount($)" becomes 4

# Scenario 3: Location field clear behavior
Special discovery: fill("") does not clear React internal coordinate state, clicking Continue still jumps to Step2
Conclusion: This test scenario cannot be automated through standard UI operations, mark as skip
```

### CLI Command Statistics (Prevent AI from Only Describing Without Executing)

```
# Normal recording (real calls):
open:1 snapshot:4 click:5 fill:2 type:1 screenshot:1 close:1

# Abnormal (AI describing plan):
open:0 snapshot:0 click:0 fill:0 type:0 screenshot:0 close:0

# Too few (incomplete recording):
open:1 snapshot:1 click:1 close:1
→ Note: Only did operations, didn't record verification steps
```

---

## Stage2A Completion Summary Report Format

After all test case recordings are completed, before QA Agent asks the user to confirm stage2A, output:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【Stage2A Recording Completion Report - Batch X: XXX Feature】

Test Case Summary:
TCxxx ✅  Trigger:e66  Verification:"Please fill out..."  snapshot:4  Discovery: Job Function recommendation overlay
TCyyy ✅  Trigger:e227 Verification:"Please fill out..."  snapshot:3  Discovery: None
TCzzz ⊘  Skipped: Not automatable (Location uses Google Maps coordinates)

Cross-case Common Issues (Note for next batch):
1. fill_job_title → select_job_function sequence has recommendation overlay interception
   → All test cases involving this sequence have handling method annotated in proof artifact

Total CLI calls: open:N snapshot:N click:N (total N times)

Please review the above recording results and bug list. QA Agent will ask for confirmation before stage2B code generation.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Abnormal Self-Check Mechanism

As an AI Agent, perform self-verification before outputting artifact:
- **ref column empty**? Indicates didn't actually call `playwright-cli snapshot`. At this time, the selectors you obtained are just guesses, please re-record.
- **CLI statistics all 0**? Indicates only output plan, didn't actually interact through tools, this will make the finally generated code invalid.
- When dynamic behaviors are all filled with "None", reflect again whether complex Single Page Applications (SPA) really have no asynchronous changes.

Treat this artifact as the cornerstone of our high-quality delivery!

---

**Last updated**: 2026-03-30  
**Purpose**: Proof artifact and recording trace format definition for stage2A recording using playwright-cli
