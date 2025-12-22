# Walkthrough - Shell 재질 유지 기능 개선 (Auto-Generate)

## 문제 설명 (Issue)
사용자가 Shell 재질을 변경한 상태에서 "Auto-Generate Courses" 버튼을 누르거나 "Standard Plate Width"를 변경하면, 재질 설정이 초기값("A 283 C")으로 리셋되는 불편함이 있었습니다.

## 해결 방법 (Solution)
"Auto-Generate"가 실행되기 직전에 기존 테이블의 첫 번째 코스(Course 1)의 재질 정보를 세션 상태(`preserved_shell_material`)에 저장하도록 수정했습니다.
새로운 데이터가 생성될 때 이 저장된 재질 정보를 기본값으로 사용합니다.

### 코드 변경 (`app.py`)
1. **재질 저장**: 코스 데이터 초기화(`pop`) 전에 현재 재질을 백업합니다.
```python
if "shell_courses_data" in st.session_state:
    st.session_state['preserved_shell_material'] = st.session_state["shell_courses_data"][0].get('Material', 'A 283 C')
st.session_state.pop("shell_courses_data", None)
```

2. **재질 적용**: 새로운 코스 생성 시 백업된 재질을 사용합니다.
```python
default_mat = st.session_state.get('preserved_shell_material', 'A 283 C')
# ...
default_data.append({
    # ...
    "Material": default_mat,
    # ...
})
```

## 검증 (Verification)
- 재질을 "A 36" 등으로 변경 후 "Auto-Generate" 클릭 시, 새로 생성된 코스들의 재질이 "A 36"으로 유지되는지 확인합니다.
