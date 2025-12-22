# Walkthrough - Shell Thickness 입력 문제 수정

## 문제 설명
사용자가 "Shell Thickness"를 입력할 때 값을 두 번 입력해야 하는 문제가 보고되었습니다. 첫 번째 입력 시 화면이 "새로고침"되면서 값이 원래대로 돌아가고, 두 번째 입력해야만 값이 적용되는 현상이었습니다.

## 원인 분석 (Root Cause Analysis)
`app.py`를 조사한 결과, 테이블의 첫 번째 코스 너비(width)와 입력된 "Standard Plate Width"를 비교하여 데이터 불일치(Stale Data)를 감지하는 코드가 과도하게 엄격하게 작동하고 있었습니다.
```python
if abs(first_width - std_width) > 0.001:
    # ...
    st.session_state.pop("shell_courses_data", None)
    st.rerun()
```
이 코드는 데이터의 일관성을 위한 것이었으나, 미세한 오차나 사용자의 수정으로 인해 `first_width`(테이블 값)와 `std_width`(입력값)가 다를 경우 다음과 같이 작동했습니다:
1. 사용자가 두께를 입력하여 실행되는 순간 불일치 감지.
2. `shell_courses_data`를 즉시 초기화 (사용자의 두께 입력값 삭제).
3. `st.rerun()`으로 강제 새로고침.
4. 기본값(두께 0)으로 화면 리로드.

이로 인해 첫 번째 입력은 무시되고, 초기화된 상태에서 다시 입력해야만(두 번째) 저장이 되었습니다.

## 해결 방법 (Resolution)
자동 초기화 로직을 비활성화했습니다. 이제 불일치가 감지되면 데이터를 삭제하고 새로고침하는 대신, 경고 메시지만 표시하고 사용자의 입력값은 안전하게 유지합니다.

### `app.py` 변경 사항
```python
<<<<
if abs(first_width - std_width) > 0.001:
      st.warning(f"⚠️ Detected Stale Data (Table: {first_width}m vs Input: {std_width}m). Use 'Auto-Generate' if needed.")
      st.session_state.pop("shell_courses_data", None)
      st.rerun()
====
if abs(first_width - std_width) > 0.001:
      st.warning(f"⚠️ Table width ({first_width}m) differs from Input ({std_width}m). Value preserved to avoid data loss. Click 'Auto-Generate' to reset.")
      # Auto-fix REMOVED to prevent double-entry issue
>>>>
```

## 검증 (Verification)
- 불일치 시 `st.rerun()`이 더 이상 호출되지 않음.
- 자동 초기화 코드(`st.session_state.pop`)가 비활성화됨.
- 이제 너비가 일치하지 않아도 사용자의 입력값이 정상적으로 반영됩니다.
