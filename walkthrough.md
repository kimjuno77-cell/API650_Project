# Walkthrough - Shell Thickness 입력 개선 (일괄 적용)

## 문제 설명 (Issue)
이전 수정에도 불구하고, 사용자가 값을 입력할 때마다 화면이 "새로고침(Refresh)"되어 불편함을 겪었습니다. 사용자는 여러 값을 수정한 후 한번에 적용(Batch Apply)하는 방식을 요청했습니다.

## 해결 방법 (Solution)
Streamlit의 `st.data_editor`는 기본적으로 값이 변경될 때마다 앱을 다시 실행(Rerun)합니다. 이를 방지하기 위해 데이터 에디터를 `st.form` 내부로 이동시켰습니다.

### 변경 사항 (Changes)
1.  **Form 도입**: Shell Course 입력 테이블을 `st.form`으로 감쌌습니다.
2.  **일괄 적용 버튼**: 폼 내부에 `st.form_submit_button` ("일괄 적용 (Apply Updates)")을 추가했습니다.

이제 사용자가 테이블에서 여러 셀(두께, 재질 등)을 수정하더라도, **"일괄 적용"** 버튼을 누르기 전까지는 화면이 새로고침되지 않습니다.

### 코드 변경 (`app.py`)
```python
with st.form("shell_course_form"):
    edited_df = st.data_editor( ... )
    st.form_submit_button("일괄 적용 (Apply Updates)")
```

## 검증 (Verification)
-   **동작 확인**: 테이블 값을 여러 개 수정해도 화면이 깜빡이지 않음.
-   **데이터 반영**: "일괄 적용" 버튼 클릭 시에만 계산 로직이 실행되고 결과가 업데이트됨.
-   **이중 입력 문제 해소**: 폼 제출 시에만 동기화되므로, 입력 도중 데이터가 초기화되는 문제도 자연스럽게 해결됨.
