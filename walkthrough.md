# Walkthrough - Shell 재질 입력 시 초기화 문제 수정

## 문제 설명 (Issue)
"Shell Thickness" 자동 초기화 문제를 해결하기 위해 경고 메시지를 추가했는데, 재질(Material)을 변경하고 "일괄 적용"을 누를 때 값이 원래대로 돌아가는(Revert) 현상이 발생했습니다.

## 원인 분석 (Root Cause)
수정된 코드에서 "너비 불일치 경고(Warning)"가 발생할 경우, 기존에 저장된 데이터(`saved_df`)를 불러오는 코드를 건너뛰는(Skip) 논리적 오류가 있었습니다.
이로 인해 경고가 떠 있는 상태에서는 세션에 저장된 사용자 입력값(변경한 재질) 대신, 항상 새로 생성된 기본값(`default_data`)이 테이블에 표시되었습니다.

```python
if abs(first_width - std_width) > 0.001:
    st.warning(...)
    # 여기서 saved_df를 로드하지 않고 코드가 끝나버림 -> df_shell_input은 default_data가 됨
else:
    saved_df = pd.DataFrame(stale_data)
    df_shell_input = saved_df
```

## 해결 방법 (Solution)
너비 불일치 경고가 발생하더라도, 세션에 저장된 사용자 데이터를 **항상 로드**하도록 로직 구조를 변경했습니다.

### 코드 변경 (`app.py`)
```python
if abs(first_width - std_width) > 0.001:
    st.warning(...)

# 경고 여부와 상관없이 항상 저장된 데이터 로드
saved_df = pd.DataFrame(stale_data)
# ...
df_shell_input = saved_df
```

## 검증 (Verification)
- 너비 설정과 테이블 너비가 달라서 경고가 표시되는 상황에서도, 재질을 변경하고 "일괄 적용"을 누르면 변경된 재질이 정상적으로 유지됩니다.
