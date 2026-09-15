# School Safety Risk Scenario Analysis

학교안전공제중앙회 주관 2026 학교안전사고 데이터 분석·활용 경진대회에 2인 팀으로 참가하여 2021~2025년 전국 학교안전사고 데이터를 바탕으로 반복적으로 나타나는 위험 시나리오를 찾고 예방 우선순위로 연결한 프로젝트입니다.

- **Team**: [7lyomi](https://github.com/7lyomi), [jaebok1211](https://github.com/jaebok1211)
- **Year**: 2026
- **Result**: 결선 진출
- **Data**: 초·중·고 학교안전사고 812,363건, 연도별 학생 수·학교 수 교육통계
- **Tech**: Python, Pandas, NumPy, MLxtend, OpenPyXL

## Contribution

- 문제 정의 및 분석 방향 설계
- 분석 결과 해석과 대표 위험 시나리오 정리
- SAFE-Rx 구조 및 보고서·발표 구성

## 분석 목표

단순 사고건수만 비교하지 않고 학교급·성별·학년·시간·장소·활동을 함께 고려해 구체적인 위험상황을 찾았습니다. 이후 학생 수와 학교 수를 기준으로 사고부담을 보정하고, 반복적으로 나타나는 시나리오를 예방 우선순위로 정리했습니다.

## 분석 흐름

```text
학교안전사고 원자료
        ↓
학교급별 분포 차이 확인
        ↓
분석용 데이터마트 구축
        ↓
FP-Growth + Association Rule Mining
        ↓
학생 수 / 학교 수 모수 보정
        ↓
Support / Confidence / Lift 기준 적용
        ↓
연도·지역 반복성 확인
        ↓
대표 위험 시나리오 정리
        ↓
SAFE-Rx 예방처방·효과환류 체계 제안
```

### 시나리오 선별 기준

| Metric | Threshold | 의미 |
|---|---:|---|
| Support | ≥ 0.50% | 전체 사고에서 해당 시나리오가 차지하는 비율 |
| Confidence | ≥ 30% | 해당 조건에서 특정 사고결과가 나타난 비율 |
| Lift | ≥ 1.50 | 전체 평균 대비 특정 결과의 집중도 |

중복·포함 관계를 정리한 뒤 **457개 위험 시나리오**를 최종 분석 대상으로 정리했습니다.

## 주요 결과

절대 사고건수는 초등학교가 가장 많았지만, 학생 수와 학교 수를 보정하면 **중학교의 상대적 사고부담이 가장 높게** 나타났습니다.

| 학교급 | 학생 1만 명당 연평균 신고건수 | 학교 1개교당 연평균 신고건수 |
|---|---:|---:|
| 초등학교 | 315.77 | 13.39 |
| **중학교** | **393.41** | **16.25** |
| 고등학교 | 205.61 | 11.39 |

대표 시나리오는 서로 다른 기준으로 선정했습니다.

- **Volume**: 걷기·뛰기·오르내리기 → 넘어짐
- **Density**: 중학교 여학생 → 손가락 상해
- **School Burden**: 중학교 체육활동 → 손가락 상해
- **Lift**: 중학교 여학생 + 체육 + 농구 → 손가락 상해 + 충돌
- **Trend**: 고등학교 남학생 + 체육활동 → 발목 상해
<img width="1600" height="900" alt="school_safety_scenarios" src="https://github.com/user-attachments/assets/6d8664c9-84ed-435a-86fc-94d21134846f" />

## 검증

공개 코드에서는 최종 시나리오별로 다음을 확인합니다.

- 몇 개 연도에서 반복되는지
- 몇 개 시·도에서 발생하는지
- 최종 시나리오의 사고건수와 모수보정 지표가 어떻게 분포하는지

연관규칙의 Support / Confidence / Lift는 개인의 사고확률이나 인과관계를 의미하지 않으며, 위험상황을 탐색하고 우선순위를 좁히기 위한 지표로 사용했습니다.

## SAFE-Rx

분석 결과를 실제 예방활동과 연결하기 위해 다음 구조를 제안했습니다.

<img width="1600" height="900" alt="school_safety_safe_rx" src="https://github.com/user-attachments/assets/1d2d860a-8d6b-4510-a636-bddf89914f85" />


## Repository Structure

```text
.
├── README.md
├── requirements.txt
├── run_all.py
├── data/
│   └── README.md
├── outputs/
│   └── .gitkeep
└── src/
    ├── 01_validate_school_level_heterogeneity.py
    ├── 02_build_analysis_datamart.py
    ├── 03_mine_risk_scenarios.py
    ├── 04_adjust_population_denominators.py
    ├── 05_select_final_risk_scenarios.py
    ├── 06_validate_reproducibility.py
    └── 07_build_final_scenario_summary.py
```

## Run

```bash
pip install -r requirements.txt
python run_all.py
```

원자료는 저장소에 포함하지 않습니다. 필요한 파일명과 입력 형식은 [`data/README.md`](data/README.md)를 참고하면 됩니다.

`07_build_final_scenario_summary.py`는 최종 시나리오 마스터를 정리하고, 보고서에서 사용한 대표 5개 사례를 별도 요약표로 저장합니다.

## Limitations

- 분석 대상은 실제 발생 전체가 아니라 신고된 학교안전사고입니다.
- 연관규칙은 변수 간 인과관계를 설명하지 않습니다.
- 모수 보정 지표는 집단 간 비교를 위한 값이며 개인 수준 위험도를 의미하지 않습니다.
- 실제 예방조치 적용 전에는 학교 현장 상황을 추가로 확인해야 합니다.
