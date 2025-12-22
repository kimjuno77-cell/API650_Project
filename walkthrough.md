# Walkthrough - Results 요약 표시 오류 수정 및 EFRT 결과 추가

## 문제 설명 (Issue)
`roof_design` 변수 초기화 문제를 해결한 뒤, 결과 요약(Summary) 섹션에서 다시 `AttributeError`가 발생했습니다.
`roof_res = roof_design.results.get('Roof Plate', {})`
이 코드는 EFRT 모드에서도 `roof_design` 객체에 접근하려 했으나, EFRT 모드에서는 해당 객체가 `None`이므로 오류가 발생했습니다.

## 해결 방법 (Solution)
결과 표시 코드를 Roof Type에 따라 분기 처리했습니다.
1. `roof_design` 객체가 있으면 (Fixed Roof) -> 기존 결과 표시.
2. `efrt_design_res` 객체가 있으면 (EFRT) -> EFRT 결과(부력 등) 표시.

### 코드 변경 (`app.py`)
```python
st.write(f"- Type: {roof_type}")

if roof_design:
    # ... (기존 Fixed Roof 결과)
    st.write(f"- Status: {roof_res.get('Status', 'N/A')}")
elif efrt_design_res:
    # [NEW] EFRT 결과 표시
    e_res = efrt_design_res.results
    st.write(f"- Deck Thk: {e_res.get('Deck_Thickness_Check', {}).get('Provided')} mm")
    st.write(f"- Buoyancy Safety Factor: {e_res.get('Safety_Factor', 0):.2f}")
else:
    st.write("No Design Results")
```

## 검증 (Verification)
- EFRT 모드에서 결과 탭을 볼 때 오류 없이 "Deck Thk", "Safety Factor" 등이 표시되는지 확인.
- Fixed Roof 모드에서도 기존 결과가 정상적으로 표시되는지 확인.
