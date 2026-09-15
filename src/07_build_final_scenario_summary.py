"""재현성 결과를 정제하고 보고서용 대표 시나리오 요약표를 생성한다."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "outputs"

INPUT_FILE = OUTPUT_DIR / "시나리오_재현성_검증보고서.xlsx"
MASTER_OUTPUT = OUTPUT_DIR / "최종_정제_위험시나리오_마스터.xlsx"
SUMMARY_OUTPUT = OUTPUT_DIR / "대표_시나리오_요약표.xlsx"


def clean_condition(condition_str: str) -> str:
    """세부 학년군이 있을 때 중복되는 상위 학교급 조건을 제거한다."""
    items = [item.strip() for item in str(condition_str).split(",")]
    has_specific_group = any(
        any(prefix in item for prefix in ["초등학교_", "중학교_", "고등학교_"])
        for item in items
    )

    return ", ".join(
        item
        for item in items
        if not (
            has_specific_group
            and item in ["초등학교", "중학교", "고등학교"]
        )
    )


def build_representative_table() -> pd.DataFrame:
    """최종 보고서에서 사용한 대표 5개 시나리오를 요약한다."""
    rows = [
        [
            "Volume",
            "초·중·고 공통 × 걷기/뛰기·오르내리기 → 넘어짐",
            215_097,
            26.48,
            52.37,
            1.98,
        ],
        [
            "Density",
            "중학교 여학생 → 손가락 상해",
            35_171,
            4.33,
            33.57,
            1.53,
        ],
        [
            "School Burden",
            "중학교 × 체육활동 → 손가락 상해",
            46_147,
            5.68,
            32.99,
            1.50,
        ],
        [
            "Lift",
            "중학교 여학생 × 체육·농구 → 손가락 상해·충돌",
            4_357,
            0.54,
            39.81,
            5.09,
        ],
        [
            "Trend",
            "고등학교 남학생 × 체육활동 → 발목 상해",
            15_030,
            1.85,
            31.45,
            1.57,
        ],
    ]

    return pd.DataFrame(
        rows,
        columns=[
            "선정유형",
            "대표 위험 시나리오",
            "5개년 건수",
            "지지도(%)",
            "신뢰도(%)",
            "Lift",
        ],
    )


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"입력 파일을 찾을 수 없습니다: {INPUT_FILE}")

    scenarios = pd.read_excel(INPUT_FILE)
    scenarios["정제_위험상황"] = scenarios["위험상황(조건)"].apply(clean_condition)

    scenarios = scenarios.drop_duplicates(
        subset=["정제_위험상황", "사고결과", "원본_전체건수"]
    ).copy()
    scenarios["위험상황(조건)"] = scenarios.pop("정제_위험상황")

    if "지지도(%)" in scenarios.columns:
        scenarios = scenarios[
            scenarios["지지도(%)"] >= 0.50
        ].reset_index(drop=True)

    scenarios.to_excel(MASTER_OUTPUT, index=False)

    representative = build_representative_table()
    representative.to_excel(SUMMARY_OUTPUT, index=False)

    print(f"저장 완료: {MASTER_OUTPUT}")
    print(f"저장 완료: {SUMMARY_OUTPUT}")


if __name__ == "__main__":
    main()
