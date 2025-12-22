# Walkthrough - EFRT Design 오류 수정

## 문제 설명 (Issue)
"External Floating Roof"를 선택했을 때, 다음과 같은 오류가 발생하며 앱이 중단되었습니다.
`TypeError: EFRTDesign.__init__() missing 3 required positional arguments: 'diameter', 'material_yield', and 'specific_gravity'`

## 원인 분석 (Root Cause)
`app.py`에서 `EFRTDesign` 클래스를 인스턴스화할 때, 필수 인자(지름, 항복강도, 비중)를 전달하지 않고 빈 괄호 `()`로 호출했기 때문입니다.
```python
efrt = EFRTDesign() # Error
```

## 해결 방법 (Solution)
`EFRTDesign` 생성자에 필요한 Tank 정보를 전달하도록 수정했습니다.

### 코드 변경 (`app.py`)
```python
# Before
efrt = EFRTDesign()

# After
efrt = EFRTDesign(diameter=D, material_yield=struct_yield, specific_gravity=G)
```

## 검증 (Verification)
- "External Floating Roof" 선택 시 더 이상 TypeError가 발생하지 않고 계산이 진행되는지 확인.
