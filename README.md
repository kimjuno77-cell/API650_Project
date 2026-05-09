# API 650 Tank Design Calculation Engine (Python)

이 프로그램은 **API 650 13th Edition (2020)** Standard에 따라 Storage Tank의 설계 적합성, 하중(Wind/Seismic), 내부 압력(Appendix F), 앵커 볼트 필요 여부 등을 자동으로 계산하고 엑셀 리포트를 생성하는 도구입니다.

## 1. 주요 기능 (Features)
- **Shell Design**: 1-Foot Method 및 Variable Design Point Method (VDM) 자동 판별 및 두께 계산.
- **Roof Design**: Cone Roof 두께 적합성 및 Frangible Roof(5.10.2.6) 평가.
- **Load Analysis**:
  - **Wind**: ASCE 7 기반 풍하중 및 전도 모멘트 계산.
  - **Seismic**: API 650 Annex E (13th Ed) 기준 지진 하중($V, M, A_v$) 계산.
- **Internal Pressure**: Appendix F 기준 압력 초과 여부 및 Anchor 필요성 검토.
- **Excel Report**: 계산된 모든 데이터를 **Target 형식의 엑셀 파일(.xlsx)**로 출력 (요약 시트 포함).

## 2. 설치 및 실행 환경 (Installation)
이 프로그램은 Python 3 환경에서 동작합니다. 다음 라이브러리 설치가 필요합니다.

```bash
pip install pandas openpyxl xlrd
```
*Note: `xlrd`는 구버전 엑셀(`.xls`) 입력 파일을 읽기 위해 필요합니다.*

## 3. 사용 방법 (Usage)

### 3.1 입력 파일 준비 (Input)
프로젝트 폴더 내에 입력 엑셀 파일이 있어야 합니다.
기본 설정된 파일명: `Excel_Logic_input_03-1 i-070936-67-T-0319-0327-Type4-78x18-(For_Education)-Ver. 1.05.xls`

> **Tip**: 다른 파일을 사용하려면 `Main.py` 파일의 `input_file` 변수 경로를 수정하면 됩니다.

**주요 입력 항목 (Input Sheet):**
- **Tank Geometry**: Diameter (Row 13), Height (Row 14).
- **Design Conditions**: SG (Row 23), CA (Row 38), Design Pressure (Row 31).
- **Wind/Seismic**: Wind Speed (Row 11/18), Seismic Factors ($S_{DS}, S_1$ 등).

### 3.2 프로그램 실행 (Execution)
터미널(또는 CMD)에서 다음 명령어를 실행합니다.

```bash
python Main.py
```

### 3.3 결과물 확인 (Output)
실행이 완료되면 폴더에 타임스탬프가 찍힌 엑셀 리포트가 생성됩니다.
- **파일명 예시**: `Calc_Report_Excel_Logic_input..._2025-12-05_19-30-00.xlsx`

## 4. 리포트 구성 (Report Structure)
생성된 엑셀 파일은 다음과 같은 시트로 구성됩니다.

| 시트명 (Sheet Name) | 내용 (Contents) |
| :--- | :--- |
| **Ch_1_Summary** | 프로젝트 요약, 앵커 볼트 필요 여부, 주요 설계 조건, Frangible 평가 결과. |
| **Ch_2_DesignData** | 입력된 설계 상세 데이터 (Geometry, Material info, Pressures). |
| **Ch_3_Shell_Design** | 각 Course 별 두께 계산 결과 및 Shell 중량 테이블. |
| **Ch_4_Roof_Bottom..** | Roof 재질/두께, 전체 중량(Shell+Roof+Liquid) 집계. |
| **Ch_5_Loads** | Wind & Seismic 하중 계산 상세 ($V, M, A_v, T_c$ 등). |
| **Ch_6_Pressure..** | Internal Pressure 검토 결과 (Appendix F) 및 Frangible Joint 상세. |
| **Ch_7_Anchor_Design** | Uplift Force 계산 및 Anchor Bolt 필요 수량/규격 설계 결과. |

## 5. 문제 해결 (Troubleshooting)
- **오류: `FileNotFoundError`**: 입력 엑셀 파일명이 `Main.py`에 지정된 이름과 일치하는지 확인하십시오.
- **오류: `ImportError`**: `pandas` 등의 라이브러리가 설치되었는지 확인하십시오 (`pip list`).
- **값이 이상할 때**: `InputReader.py`가 엑셀의 특정 행(Row)을 읽도록 하드코딩 되어 있습니다. 사용 중인 엑셀 양식의 행 번호가 변경되지 않았는지 확인하십시오.

---
**개발자**: Gemini Agent
**최종 업데이트**: 2025-12-05 (API 650 13th Ed 반영)
