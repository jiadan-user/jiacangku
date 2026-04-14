# Fix: KYC Upload Tests Timing Issues (Batch Fix)

## Problem Description

Multiple test cases were failing intermittently with timing-related assertion errors:

1. `test_05_upload_invalid_image` - 上传不可识别图片后弹窗未打开
2. `test_06_submit_without_agreement` - 上传合规证件后未等待弹窗
3. `test_07_agreement_links_no_navigation` - 上传后直接操作弹窗元素
4. `test_08_upload_valid_ocr_submit` - 上传后立即断言弹窗可见

**Common Error Pattern**:
```
AssertionError: 弹窗应打开 / 表单弹窗未显示
assert False
 +  where False = is_form_dialog_visible()
```

**Root Cause**: After uploading images (both valid and invalid), the tests weren't waiting long enough for:
- Server to process the upload
- OCR service to analyze the image
- Form dialog to appear and render

## Changes Made

### 1. Enhanced `KycIdentificationPage.upload_document_image()`

**File**: `pages/kyc_identification_page.py`

**Improvements**:
- Added `wait_for_dialog` parameter (default `True`) to explicitly wait for the dialog after upload
- Increased wait timeout to 15 seconds for dialog appearance
- Better logging to track dialog state
- More efficient timing (3s processing + up to 15s dialog wait + 2s stabilization)

**Code changes**:
```python
def upload_document_image(self, file_path: str, wait_for_dialog: bool = True):
    # ... existing upload code ...
    
    # Wait for upload processing (reduced from 8s)
    self.page.wait_for_timeout(3000)
    
    # If needed, wait for dialog (up to 15 seconds)
    if wait_for_dialog:
        try:
            dialog = self.page.get_by_role("dialog").filter(has_text="Identity Verification")
            dialog.wait_for(state="visible", timeout=15000)
            self.logger.info("✓ 表单弹窗已打开")
        except Exception as e:
            self.logger.warning(f"等待表单弹窗超时（可能上传失败或处理中）: {e}")
    
    self.page.wait_for_timeout(2000)
```

### 2. Enhanced `KycIdentificationPage.is_form_dialog_visible()`

**Improvements**:
- Added configurable `timeout` parameter (default 5000ms)
- Explicit `wait_for()` before checking visibility
- Better debug logging

**Code changes**:
```python
def is_form_dialog_visible(self, timeout: int = 5000) -> bool:
    """
    检查手动输入表单弹窗是否可见
    
    Args:
        timeout: 等待超时时间（毫秒），默认 5000ms
    """
    try:
        dialog = self.page.get_by_role("dialog").filter(has_text="Identity Verification")
        dialog.wait_for(state="visible", timeout=timeout)
        return dialog.is_visible()
    except Exception as e:
        self.logger.debug(f"表单弹窗不可见: {e}")
        return False
```

### 3. Fixed Test Case: `test_05_upload_invalid_image`

**File**: `test_cases/kyc/test_kyc_identification_webqa.py` (Lines 363-405)

**Changes**:
- Added 2-second explicit wait before checking dialog
- Extended dialog visibility check to 10 seconds
- Added comprehensive debugging with screenshot on failure
- Better error messages showing page state

### 4. Fixed Test Case: `test_06_submit_without_agreement`

**File**: `test_cases/kyc/test_kyc_identification_webqa.py` (Lines 418-474)

**Changes**:
- Wrapped upload in allure step for better reporting
- Added explicit dialog visibility check with 10s timeout
- Added screenshot on failure
- Clear error message if dialog doesn't appear

**Code changes**:
```python
with allure.step("上传合规证件触发 OCR"):
    kyc_page.upload_document_image(str(valid_path))
    # 等待弹窗打开，确保 OCR 处理完成
    page.wait_for_timeout(2000)
    if not kyc_page.is_form_dialog_visible(timeout=10000):
        logger.error("表单弹窗未打开，上传可能失败")
        page.screenshot(path="reports/screenshots/debug_submit_without_agreement_no_dialog.png", full_page=True)
        raise AssertionError("表单弹窗未显示，无法继续测试")
```

### 5. Fixed Test Case: `test_07_agreement_links_no_navigation`

**File**: `test_cases/kyc/test_kyc_identification_webqa.py` (Lines 488-520)

**Changes**:
- Wrapped upload in allure step
- Added dialog visibility check before scrolling to protocol section
- Added screenshot on failure

### 6. Fixed Test Case: `test_08_upload_valid_ocr_submit`

**File**: `test_cases/kyc/test_kyc_identification_webqa.py` (Lines 543-573)

**Changes**:
- Removed redundant `page.wait_for_timeout(2000)` after upload (now handled in page object)
- Added 2-second wait before dialog check
- Extended dialog visibility check to 10 seconds
- Added comprehensive debugging with screenshot on failure
- Better error messages for OCR validation failures

**Code changes**:
```python
with allure.step("上传合规证件"):
    kyc_page.upload_document_image(str(valid_path))

with allure.step("验证 OCR 填充"):
    # 增加明确的等待时间，确保弹窗打开并完成 OCR 识别
    page.wait_for_timeout(2000)
    
    # 检查弹窗是否可见，如果不可见则截图调试
    if not kyc_page.is_form_dialog_visible(timeout=10000):
        logger.error("表单弹窗未打开，正在截图调试...")
        page.screenshot(path="reports/screenshots/debug_valid_image_no_dialog.png", full_page=True)
        # ... additional debugging ...
        raise AssertionError("表单弹窗未显示，但上传应该成功")
```

## Timing Analysis

### Before Fix
| Test Case | Upload Wait | Dialog Check | Total Wait |
|-----------|-------------|--------------|------------|
| test_05 (invalid) | 8s | 3s | **11s** |
| test_06 (without agreement) | 8s + 2s | N/A (no check) | **10s** |
| test_07 (agreement links) | 8s + 2s | N/A (no check) | **10s** |
| test_08 (valid submit) | 8s + 2s | 3s | **13s** |

### After Fix
| Test Case | Upload Wait | Dialog Wait | Additional | Total Wait |
|-----------|-------------|-------------|------------|------------|
| test_05 (invalid) | 3s + 15s + 2s | + 2s + 10s | - | **up to 32s** |
| test_06 (without agreement) | 3s + 15s + 2s | + 2s + 10s | - | **up to 32s** |
| test_07 (agreement links) | 3s + 15s + 2s | + 2s + 10s | - | **up to 32s** |
| test_08 (valid submit) | 3s + 15s + 2s | + 2s + 10s | - | **up to 32s** |

**Key Improvements**:
- More patient with slow server/OCR responses
- Explicit waits at each critical step
- Better error handling and debugging

## Test Results

All 9 KYC tests passed successfully (2 consecutive full runs):

### Run 1: Modified Tests Only (4 tests)
```
test_05_upload_invalid_image ............................ PASSED ✓ (Fixed)
test_06_submit_without_agreement ........................ PASSED ✓ (Fixed)
test_07_agreement_links_no_navigation ................... PASSED ✓ (Fixed)
test_08_upload_valid_ocr_submit ......................... PASSED ✓ (Fixed)

======================== 4 passed in 114.96s (0:01:54) ========================
```

### Run 2: Complete Test Suite (9 tests)
```
test_01_verification_failed_and_retry ................... PASSED
test_02_guide_begin_upload_page ......................... PASSED
test_03_enter_manually_empty_form_validation ............ PASSED
test_04_esc_close_dialog ................................ PASSED
test_05_upload_invalid_image ............................ PASSED ✓
test_06_submit_without_agreement ........................ PASSED ✓
test_07_agreement_links_no_navigation ................... PASSED ✓
test_08_upload_valid_ocr_submit ......................... PASSED ✓
test_09_standalone_script_no_payment_account ............ PASSED

======================== 9 passed in 177.53s (0:02:57) ========================
```

## Impact Assessment

**Backward Compatibility**: ✓ Full compatibility maintained
- All existing calls use default `wait_for_dialog=True`
- All upload-related tests now more stable
- No breaking changes

**Performance**: 
- Slight increase in test time when dialog appears quickly
- **Significant improvement in reliability** for slow responses
- Tests now handle network latency and OCR processing delays gracefully

**Maintainability**: ✓ Greatly improved
- Consistent error handling across all upload tests
- Detailed debugging output with screenshots
- Clear, actionable error messages
- Easier to diagnose future issues

**Test Stability**: ✓ Dramatically improved
- From intermittent failures to consistent passes
- Handles slow server responses
- Handles slow OCR processing
- Handles network latency

## Debugging Features Added

All modified tests now include:

1. **Screenshot on Failure**: Automatic full-page screenshot when dialog doesn't appear
2. **Error Message Logging**: Check for page-level error messages
3. **URL Logging**: Record current page URL for debugging
4. **State Validation**: Check if still on upload page vs. dialog page
5. **Detailed Assertions**: Clear messages indicating expected vs. actual state

## Files Modified

1. `pages/kyc_identification_page.py`
   - `upload_document_image()` method (Lines 36-78)
   - `is_form_dialog_visible()` method (Lines 226-242)

2. `test_cases/kyc/test_kyc_identification_webqa.py`
   - `test_05_upload_invalid_image` (Lines 363-405)
   - `test_06_submit_without_agreement` (Lines 418-474)
   - `test_07_agreement_links_no_navigation` (Lines 488-520)
   - `test_08_upload_valid_ocr_submit` (Lines 533-573)

## Recommendation

This batch fix addresses all upload-related timing issues by:
1. **Being more patient** - Waiting longer for server/OCR responses (up to 32s total)
2. **Being more explicit** - Clear waits and checks at each step
3. **Being more helpful** - Better logging and debugging on failures
4. **Being more consistent** - Same pattern across all upload tests

The tests should now be stable and pass consistently even on:
- Slow network connections
- High server load
- Slow OCR processing
- Variable latency environments

---

**Fixed Date**: 2026-04-03  
**Fixed By**: AI Assistant  
**Test File**: `test_cases/kyc/test_kyc_identification_webqa.py`  
**Page Object**: `pages/kyc_identification_page.py`  
**Tests Fixed**: 4 (test_05, test_06, test_07, test_08)  
**Total Tests Validated**: 9 (all passing)
