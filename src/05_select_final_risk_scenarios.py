"""지지도·신뢰도·향상도 기준을 적용해 최종 위험 시나리오를 선별한다."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "outputs"

INPUT_FILE = OUTPUT_DIR / "전학교급_성별_실제모수보정_위험_시나리오.xlsx"
OUTPUT_FILE = OUTPUT_DIR / "최종_위험_시나리오_선정보고서.xlsx"

MIN_CONFIDENCE = 0.30
MIN_LIFT = 1.50


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"입력 파일을 찾을 수 없습니다: {INPUT_FILE}")

    df = pd.read_excel(INPUT_FILE)
    confidence_col = "confidence" if "confidence" in df.columns else "신뢰도(%)"
    lift_col = "lift" if "lift" in df.columns else "향상도(Lift)"

    confidence_threshold = (
        MIN_CONFIDENCE
        if df[confidence_col].max() <= 1.0
        else MIN_CONFIDENCE * 100
    )

    result = df[
        (df[confidence_col] >= confidence_threshold)
        & (df[lift_col] >= MIN_LIFT)
    ].copy()

    if "support" in result.columns:
        result["지지도(%)"] = (result["support"] * 100).round(2)
    if "confidence" in result.columns:
        result["신뢰도(%)"] = (result["confidence"] * 100).round(2)
    if "lift" in result.columns:
        result["향상도(Lift)"] = result["lift"].round(2)

    result = result.sort_values(
        ["향상도(Lift)", "지지도(%)"],
        ascending=[False, False],
    ).reset_index(drop=True)

    columns = [
        "위험상황(조건)",
        "사고결과",
        "원본_전체건수",
        "학생_1만명당_연평균_발생건수",
        "학교_1개교당_연평균_발생건수",
        "지지도(%)",
        "신뢰도(%)",
        "향상도(Lift)",
    ]
    available_columns = [col for col in columns if col in result.columns]

    result[available_columns].to_excel(OUTPUT_FILE, index=False)
    print(f"저장 완료: {OUTPUT_FILE} ({len(result):,}개 시나리오)")


if __name__ == "__main__":
    main()
