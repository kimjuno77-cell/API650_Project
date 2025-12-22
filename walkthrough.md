# Walkthrough - Structure Material 표시 개선

## 문제 설명 (Issue)
"Structure Material Yield (MPa)" 선택 항목이 단순히 숫자(235, 250 등)로만 표시되어, 사용자가 어떤 재질(Grade)인지 직관적으로 알기 어려웠습니다.

## 해결 방법 (Solution)
Streamlit의 `selectbox` 기능 중 `format_func`를 활용하여, 실제 값(숫자)은 유지하되 화면에 표시되는 라벨(Label)만 재질명을 포함하도록 개선했습니다.

### 코드 변경 (`app.py`)
```python
yield_map = {
    235: "SS400 / S235 (235 MPa)",
    250: "ASTM A36 (250 MPa)",
    345: "ASTM A572-50 / S355 (345 MPa)"
}
# ...
st.selectbox(..., options=[235, 250, 345], format_func=format_yield)
```

## 검증 (Verification)
- 드롭다운 메뉴에서 "235" 대신 "SS400 / S235 (235 MPa)"와 같이 표시되는지 확인.
- 선택 후 실제 계산에는 여전히 235.0 (float) 값이 사용되는지 확인 (기존 로직 호환성 유지).
