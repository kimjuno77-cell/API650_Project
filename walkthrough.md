# Walkthrough - EFRT 메서드 호출 오류 수정

## 문제 설명 (Issue)
`TypeError`를 수정한 직후, 다음과 같은 `AttributeError`가 발생했습니다.
`AttributeError: 'EFRTDesign' object has no attribute 'set_geometry'`

## 원인 분석 (Root Cause)
`app.py`에서 호출하려는 `set_geometry`라는 메서드가 실제 `EFRT_Design.py` 클래스 내부에는 존재하지 않았습니다.
해당 기능을 수행하는 실제 메서드 이름은 `set_pontoon_geometry`였으며, 인자(Arguments) 구성도 달랐습니다.

## 해결 방법 (Solution)
`app.py`의 호출 코드를 `EFRTDesign` 클래스 정의에 맞게 수정했습니다.

### 코드 변경 (`app.py`)
```python
# Before (Error)
efrt.set_geometry(D, h_out_mm, h_in_mm, b_pont_mm, gap_mm)

# After (Correct)
n_pontoons_val = efrt_params_ui.get('N_Pontoons', 16)
efrt.set_pontoon_geometry(width=b_pont_mm, h_out=h_out_mm, h_in=h_in_mm, n_pontoons=n_pontoons_val)
efrt.gap_rim = gap_mm / 1000.0
```

## 검증 (Verification)
- EFRT Design 실행 시 더 이상 AttributeError가 발생하지 않는지 확인.
