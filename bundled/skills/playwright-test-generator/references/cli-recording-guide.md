# playwright-cli Recording Detailed Guide

> Complete operation manual for Phase 2

---

## Section 1: Pre-recording Preparation

### Collaboration Rules

Before starting actual browser operations, confirm the user has prepared the environment. Since tests typically require login state, blindly executing `playwright-cli open` may result in redirect to login page causing failure.

### 3-Step Process

#### Step 1: Output Preparation Checklist

Output the following checklist to the user:

```markdown
📋 CLI Recording Preparation Checklist

Before starting recording, please confirm:

**Environment state:**
- [ ] playwright-cli is installed globally (`npm install -g @playwright/cli@latest`)
- [ ] Mobile configuration file exists (`.playwright/cli.config.json`)
- [ ] Test environment is accessible
- [ ] (If login required) Test account credentials are ready

✋ After confirming all conditions are met, tell me "可以开始了" (ready to start).
```

#### Step 2: Collaborative Waiting

Wait patiently for user confirmation. When user feedback indicates readiness, then start executing specific recording steps.

#### Step 3: Execute CLI Commands

After user confirmation, execute recording operations.

### Correct Workflow

```python
# 1. Output preparation checklist
Output: 📋 CLI Recording Preparation Checklist...

# 2. Wait for user reply "可以开始了"
Wait for user confirmation

# 3. After user confirms, execute CLI commands
Shell("playwright-cli -s=session-name open https://example.com")
```

---

## Section 2: Essential playwright-cli Commands

### 1. playwright-cli open - Navigate to Target Page

**Purpose**: Open test page

**Command example**:
```bash
playwright-cli -s=tc001-recording open "https://example.com/#/project/list"
```

**Return result**:
```
### Browser `tc001-recording` opened with pid 32425.
### Ran Playwright code
```js
await page.goto('https://example.com/#/project/list');
```
### Page
- Page URL: https://example.com/#/project/list
- Page Title: Project List
```

**⚠️ Key**: Record the JavaScript code from "### Ran Playwright code"!

---

### 2. playwright-cli snapshot - Get Page Structure

**Purpose**: Get page DOM structure and element references

**Command example**:
```bash
playwright-cli -s=tc001-recording snapshot
```

**Return result**:
```
### Page
- Page URL: https://example.com/#/project/list
- Page Title: Project List
### Snapshot
- [Snapshot](.playwright-cli/page-2026-03-30T02-31-50-168Z.yml)
```

**YAML snapshot content**:
```yaml
- generic [active] [ref=e1]:
  - generic [ref=e2]:
    - button "plus New Project" [ref=e123]
    - textbox "* Project Name" [ref=e456]
    - button "Create" [ref=e789]
```

**⚠️ Key**: Must call this before any interaction to get element `ref`

---

### 3. playwright-cli click - Click Element

**Purpose**: Click button, link, or other elements

**Command example**:
```bash
playwright-cli -s=tc001-recording click e123
```

**Return result**:
```
✅ Click successful

### Ran Playwright code
```js
await page.getByRole('button', { name: 'plus New Project' }).click();
```
```

**⚠️ Key**: Record the "### Ran Playwright code" section!

---

### 4. playwright-cli type - Input Text

**Purpose**: Input text into input field

**Command example**:
```bash
playwright-cli -s=tc001-recording type "2025 Christmas Campaign"
```

**Return result**:
```
✅ Input successful

### Ran Playwright code
```js
await page.keyboard.type('2025 Christmas Campaign');
```
```

---

### 5. playwright-cli fill - Fill Form Field

**Purpose**: Fill specific form field

**Command example**:
```bash
playwright-cli -s=tc001-recording fill e456 "2025 Christmas Campaign"
```

**Return result**:
```
✅ Fill successful

### Ran Playwright code
```js
await page.getByRole('textbox', { name: '* Project Name' }).fill('2025 Christmas Campaign');
```
```

---

### 6. playwright-cli press - Press Keyboard Key

**Purpose**: Press keyboard key (Enter, Tab, etc.)

**Command example**:
```bash
playwright-cli -s=tc001-recording press Enter
```

**Return result**:
```
✅ Key press successful

### Ran Playwright code
```js
await page.keyboard.press('Enter');
```
```

---

### 7. playwright-cli screenshot - Take Screenshot

**Purpose**: Save page screenshot for verification

**Command example**:
```bash
playwright-cli -s=tc001-recording screenshot --filename=tc001-result.png
```

**Return result**:
```
✅ Screenshot saved
File path: /path/to/tc001-result.png

### Ran Playwright code
```js
await page.screenshot({
  path: 'tc001-result.png',
  scale: 'css',
  type: 'png'
});
```
```

---

### 8. playwright-cli close - Close Browser

**Purpose**: Close browser session

**Command example**:
```bash
playwright-cli -s=tc001-recording close
```

**Return result**:
```
Browser 'tc001-recording' closed
```

---

## 🎬 Complete Recording Example

### TC001: Create Project

#### Step 1: Navigate to Page

```bash
playwright-cli -s=tc001 open "https://example.com/#/project/list"
```

Return: ✅ Page loaded successfully

**Record JavaScript**:
```js
await page.goto('https://example.com/#/project/list');
```

---

#### Step 2: Get Page Structure

```bash
playwright-cli -s=tc001 snapshot
```

Return snapshot, find the following elements:
- ref="e123": button "plus New Project"
- ref="e456": textbox "* Project Name"
- ref="e789": button "Create"

---

#### Step 3: Click "New Project" Button

```bash
playwright-cli -s=tc001 click e123
```

Return:
```
✅ Click successful

### Ran Playwright code
```js
await page.getByRole('button', { name: 'plus New Project' }).click();
```
```

**Record selector**: `page.getByRole('button', { name: 'plus New Project' })`

---

#### Step 4: Input Project Name

```bash
playwright-cli -s=tc001 fill e456 "2025 Christmas Campaign"
```

Return:
```
✅ Fill successful

### Ran Playwright code
```js
await page.getByRole('textbox', { name: '* Project Name' }).fill('2025 Christmas Campaign');
```
```

**Record selector**: `page.getByRole('textbox', { name: '* Project Name' })`

---

#### Step 5: Click "Create" Button

```bash
playwright-cli -s=tc001 click e789
```

Return:
```
✅ Click successful

### Ran Playwright code
```js
await page.getByRole('button', { name: 'Create' }).click();
```
```

**Record selector**: `page.getByRole('button', { name: 'Create' })`

---

#### Step 6: Take Screenshot for Verification

```bash
playwright-cli -s=tc001 screenshot --filename=tc001-create-success.png
```

Return: ✅ Screenshot saved

---

#### Step 7: Close Browser

```bash
playwright-cli -s=tc001 close
```

Return: Browser closed

---

## 📝 Operation Record Template

For each test case, record the following information:

```json
{
  "tc_id": "TC001",
  "title": "First time creating project - fill complete information",
  "operations": [
    {
      "step": 1,
      "action": "open",
      "url": "https://example.com/#/project/list",
      "playwright_code": "await page.goto('https://example.com/#/project/list');"
    },
    {
      "step": 2,
      "action": "click",
      "element": "New Project button",
      "ref": "e123",
      "playwright_code": "await page.getByRole('button', { name: 'plus New Project' }).click();"
    },
    {
      "step": 3,
      "action": "fill",
      "element": "Project Name input",
      "ref": "e456",
      "value": "2025 Christmas Campaign",
      "playwright_code": "await page.getByRole('textbox', { name: '* Project Name' }).fill('2025 Christmas Campaign');"
    },
    {
      "step": 4,
      "action": "click",
      "element": "Create button",
      "ref": "e789",
      "playwright_code": "await page.getByRole('button', { name: 'Create' }).click();"
    }
  ],
  "screenshot": "tc001-create-success.png"
}
```

**⚠️ Most critical is recording the `playwright_code` field for each operation!**

---

## ⚠️ Common Errors

### Error 1: Not Recording CLI-Returned Code

❌ **Wrong approach**:
```
✓ Click "New Project" button
✓ Input project name
```

Only recorded descriptions, did not record Playwright code returned by CLI.

✅ **Correct approach**:
```
✓ Click "New Project" button
  CLI returned: await page.getByRole('button', { name: 'plus New Project' }).click();
  
✓ Input project name
  CLI returned: await page.getByRole('textbox', { name: '* Project Name' }).fill('xxx');
```

---

### Error 2: Ignoring Chained Calls

If CLI returns:
```javascript
await page.getByRole('button', { name: 'Select Year' }).first().click();
```

❌ **Wrong**: Only record `getByRole('button', { name: 'Select Year' })`
✅ **Correct**: Fully record including `.first()`

---

### Error 3: Not Calling snapshot

❌ **Wrong flow**:
```
1. playwright-cli open
2. playwright-cli click e123  ← No ref, will fail
```

✅ **Correct flow**:
```
1. playwright-cli open
2. playwright-cli snapshot  ← Must get ref first
3. playwright-cli click e123
```

---

## 🎯 Recording Checklist

After each test case recording is completed, confirm:

- [ ] Recorded all CLI command executions
- [ ] Recorded "### Ran Playwright code" returned by each operation
- [ ] Selectors include complete information (getByRole, name parameter, chained calls)
- [ ] Recorded screenshot file path
- [ ] Recorded wait time or wait conditions

---

**Last updated**: 2026-03-30  
**Purpose**: Detailed operation guide for Phase 2 browser recording using playwright-cli
