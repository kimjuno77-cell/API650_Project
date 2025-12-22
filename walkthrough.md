# Walkthrough - EFRT 두께 설정 오류 수정

## 문제 설명 (Issue)
EFRT 메서드 호출 오류 수정 후, 다음과 같은 `AttributeError`가 발생했습니다.
`AttributeError: 'EFRTDesign' object has no attribute 'set_thicknesses'`

## 원인 분석 (Root Cause)
`app.py`에서 호출하려는 `set_thicknesses` (복수형) 메서드가 `EFRT_Design.py`에는 `set_thickness` (단수형)으로 정의되어 있었습니다. 또한 인자 이름도 일부 달랐으며, `t_bulkhead`와 같이 정의되지 않은 인자를 전달하고 있었습니다.

## 해결 방법 (Solution)
`app.py`의 호출 코드를 `EFRTDesign` 클래스의 `set_thickness` 정의에 맞게 수정했습니다.

### 코드 변경 (`app.py`)
```python
# Before (Error)
efrt.set_thicknesses(
    t_rim_outer=..., t_rim_inner=..., 
    t_pon_top=..., t_pon_btm=..., 
    t_bulkhead=..., t_deck=...
)

# After (Correct)
efrt.set_thickness(
    t_rim_out=..., t_rim_in=...,  # 이름 변경 (outer->out)
    t_pon_top=..., t_pon_btm=..., 
    # t_bulkhead 제거 (정의되지 않음)
    t_deck=...
)
```

## 검증 (Verification)
- EFRT Design 실행 시 더 이상 AttributeError가 발생하지 않고 두께 설정이 정상적으로 수행되는지 확인.
