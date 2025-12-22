# Walkthrough - Roof Design 변수 참조 오류 수정

## 문제 설명 (Issue)
"External Floating Roof" 선택 시 계산 후반부 시각화(Visualization) 단계에서 다음과 같은 오류가 발생했습니다.
`NameError: name 'roof_design' is not defined`

## 원인 분석 (Root Cause)
`roof_design` 변수는 일반 지붕(Fixed Roof)인 경우에만 생성되는데, 시각화 코드에서는 이 변수의 존재 여부를 확인하지 않고 무조건 참조(`roof_design.t_used`)하려고 했습니다. EFRT일 경우 `roof_design`이 생성되지 않아 오류가 발생했습니다.

## 해결 방법 (Solution)
1.  계산 로직 시작 전 `roof_design`을 `None`으로 초기화하여 변수 스코프 문제 해결.
2.  참조하는 부분에서 `roof_design`이 존재하는지 확인하는 안전 장치 추가.

### 코드 변경 (`app.py`)
```python
# 1. 초기화 추가
roof_design = None
if roof_type == "External Floating Roof":
    # ...

# 2. 안전한 참조 (Safe Access)
# Before
t_roof_mm = roof_design.t_used 
# After
t_roof_mm = roof_design.t_used if roof_design else 0.0 
```

## 검증 (Verification)
- EFRT 모드에서 전체 계산 및 시각화 생성 단계까지 중단 없이 완료되는지 확인.
