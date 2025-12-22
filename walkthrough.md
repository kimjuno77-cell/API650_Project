# Walkthrough - 종합적 EFRT 오류 수정 및 안정화

## 문제 설명 (Issue)
External Floating Roof (EFRT) 선택 시, 프로그램 곳곳에서 지속적으로 `AttributeError` 및 `NameError`가 발생했습니다.
이는 EFRT가 선택되었음에도 불구하고, 일반 지붕(Fixed Roof) 전용 계산 모듈(파열성 검사, 상부 앵글 검사 등)이 실행되거나, 존재하지 않는 객체(`roof_design`)를 참조하려고 했기 때문입니다.

## 해결 방법 (Solution)
EFRT 모드와 Fixed Roof 모드를 명확히 구분하여 로직을 분기 처리했습니다.

### 1. 중량 요약 및 검사 UI 분기 (`app.py`)
Fixed Roof 전용 검사 항목인 "Annex F (Top Angle)"와 "Frangible Roof Check"는 EFRT 모드에서 **표시되지 않도록** 변경했습니다.
```python
if roof_design:
    # Fixed Roof 전용 로직
    # Annex F 표시
    # 파열성 검사 수행 및 표시
else:
    # EFRT Case
    # 해당 검사 생략 (EFRT는 별도의 부력 검사 등을 수행함)
```

### 2. 보고서 데이터 생성 로직 강화
리포트 생성 시 전달되는 데이터 구조(`report_data`)가 두 가지 지붕 타입을 모두 수용하도록 개선했습니다.
```python
'results': {
    # ...
    'roof_res': roof_design.results if roof_design else {},  # Fixed Roof 결과 (없으면 빈 딕셔너리)
    'efrt_res': efrt_design_res.results if efrt_design_res else {}, #[NEW] EFRT 결과 추가
    # ...
}
```

## 검증 (Verification)
- **EFRT 모드**: 계산 실행 시 더 이상 오류 없이 완료되며, 결과 탭에 부력 안전율 등이 표시되고, 파열성 검사 등 불필요한 항목은 숨겨집니다.
- **Fixed Roof 모드**: 기존과 동일하게 모든 검사 항목이 정상적으로 표시됩니다.
