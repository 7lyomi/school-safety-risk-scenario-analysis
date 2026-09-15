"""최종 위험 시나리오의 연도 반복성과 지역 분포를 확인한다."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "outputs"

DATAMART_FILE = OUTPUT_DIR / "초중고_최종_분석용_데이터마트.xlsx"
SCENARIO_FILE = OUTPUT_DIR / "최종_위험_시나리오_선정보고서.xlsx"
OUTPUT_FILE = OUTPUT_DIR / "시나리오_재현성_검증보고서.xlsx"


def main() -> None:
    required_files = [DATAMART_FILE, SCENARIO_FILE]
    missing = [path for path in required_files if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "필요한 입력 파일이 없습니다:\n" + "\n".join(map(str, missing))
        )

    mart = pd.read_excel(DATAMART_FILE)
    scenarios = pd.read_excel(SCENARIO_FILE)

    for col in mart.columns:
        if mart[col].dtype == "object":
            mart[col] = mart[col].astype(str).str.strip()

    value_map = {
        col: set(mart[col].dropna().unique())
        for col in mart.columns
    }
    results = []

    for _, row in scenarios.iterrows():
        matched = mart.copy()

        condition_items = [
            item.strip()
            for item in str(row["위험상황(조건)"]).split(",")
        ]
        result_items = [
            item.strip()
            for item in str(row["사고결과"]).split(",")
        ]

        for item in condition_items:
            for col, values in value_map.items():
                if item in values:
                    matched = matched[matched[col] == item]
                    break

        for item in result_items:
            for col in ["사고형태", "사고부위"]:
                if col in value_map and item in value_map[col]:
                    matched = matched[matched[col] == item]
                    break

        years = matched["연도"].astype(str).unique()
        regions = matched["지역"].unique()
        year_count = len(years)

        if year_count == 5:
            risk_type = "구조적 위험 (5년 연속 발생)"
        elif year_count >= 3:
            risk_type = "지속적 위험 (3~4년 반복)"
        elif any("2025" in year for year in years) and year_count <= 2:
            risk_type = "최근 신흥 위험 (최근 집중)"
        else:
            risk_type = "일시적/우연적 노이즈"

        results.append(
            {
                "위험상황(조건)": row["위험상황(조건)"],
                "사고결과": row["사고결과"],
                "원본_전체건수": len(matched),
                "학생_1만명당_연평균_발생건수": row.get(
                    "학생_1만명당_연평균_발생건수"
                ),
                "학교_1개교당_연평균_발생건수": row.get(
                    "학교_1개교당_연평균_발생건수"
                ),
                "지지도(%)": row.get("지지도(%)"),
                "신뢰도(%)": row.get("신뢰도(%)"),
                "향상도(Lift)": row.get("향상도(Lift)"),
                "지속연도수(5점만점)": year_count,
                "발생연도종류": ", ".join(sorted(years)),
                "확산지역수(시도단위)": len(regions),
                "위험시나리오_판정": risk_type,
            }
        )

    output = pd.DataFrame(results).sort_values(
        ["지속연도수(5점만점)", "원본_전체건수"],
        ascending=[False, False],
    ).reset_index(drop=True)

    output.to_excel(OUTPUT_FILE, index=False)
    print(f"저장 완료: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
