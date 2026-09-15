"""위험 시나리오에 실제 학생 수·학교 수 모수를 적용해 신고부담을 보정한다."""

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

STUDENT_FILE = DATA_DIR / "2025_연도별 학생수.xlsx"
SCHOOL_FILE = DATA_DIR / "2025_연도별 학교수.xlsx"
RULE_FILE = OUTPUT_DIR / "2단계_다차원_위험_시나리오_결과.xlsx"
OUTPUT_FILE = OUTPUT_DIR / "전학교급_성별_실제모수보정_위험_시나리오.xlsx"

YEARS = [2021, 2022, 2023, 2024, 2025]
TOTAL_TRANSACTIONS = 812_363
MIN_SUPPORT_PERCENT = 0.50


def get_exact_denominators(condition_str: str) -> tuple[str, str]:
    """시나리오 조건에 맞는 학생 수·학교 수 분모 컬럼을 반환한다."""
    cond = str(condition_str)
    is_female = "여" in cond or "여학생" in cond
    is_male = "남" in cond or "남학생" in cond

    if "초등학교" in cond and "중학교" not in cond and "고등학교" not in cond:
        student_col = "초등_여" if is_female else ("초등_남" if is_male else "초등_전체")
        school_col = "학교_초등"
    elif "중학교" in cond:
        student_col = "중학_여" if is_female else ("중학_남" if is_male else "중학_전체")
        school_col = "학교_중학"
    elif "고등학교" in cond:
        student_col = "고등_여" if is_female else ("고등_남" if is_male else "고등_전체")
        school_col = "학교_고등"
    else:
        student_col = "초중고_여" if is_female else ("초중고_남" if is_male else "초중고_전체")
        school_col = "학교_초중고_전체"

    return student_col, school_col


def normalize_rule_key(row) -> str:
    """조건/결과 순서 차이로 생기는 중복 규칙을 비교하기 위한 키를 만든다."""
    condition = ", ".join(
        sorted(item.strip() for item in str(row["위험상황(조건)"]).split(","))
    )
    result = ", ".join(
        sorted(item.strip() for item in str(row["사고결과"]).split(","))
    )
    return f"{condition} ➡️ {result}"


def safe_float(value) -> float:
    value_str = str(value).replace("건", "").replace(",", "").strip()
    if value_str in {"-", "nan", "None", ""}:
        return 0.0

    try:
        return float(value_str)
    except (TypeError, ValueError):
        return 0.0


def main() -> None:
    required_files = [STUDENT_FILE, SCHOOL_FILE, RULE_FILE]
    missing = [path for path in required_files if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "필요한 입력 파일이 없습니다:\n" + "\n".join(map(str, missing))
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    students = pd.read_excel(STUDENT_FILE, sheet_name="Sheet0")
    schools = pd.read_excel(SCHOOL_FILE, sheet_name="Sheet0")

    national_students = students[
        students["연도"].astype(str).isin([str(year) for year in YEARS])
        & (students["시도"] == "전국")
    ].copy()
    national_schools = schools[
        schools["연도"].astype(str).isin([str(year) for year in YEARS])
        & (schools["시도"] == "전국")
    ].copy()

    population = pd.DataFrame(
        {
            "연도": YEARS,
            "초등_전체": national_students["초등학교"].astype(float).values,
            "초등_여": national_students["초등학교.1"].astype(float).values,
            "중학_전체": national_students["중학교"].astype(float).values,
            "중학_여": national_students["중학교.1"].astype(float).values,
            "고등_전체": national_students["고등학교"].astype(float).values,
            "고등_여": national_students["고등학교.1"].astype(float).values,
            "학교_초등": national_schools["초등학교"].astype(float).values,
            "학교_중학": national_schools["중학교"].astype(float).values,
            "학교_고등": national_schools["고등학교"].astype(float).values,
        }
    ).set_index("연도")

    for level in ["초등", "중학", "고등"]:
        population[f"{level}_남"] = (
            population[f"{level}_전체"] - population[f"{level}_여"]
        )

    population["초중고_전체"] = population[
        ["초등_전체", "중학_전체", "고등_전체"]
    ].sum(axis=1)
    population["초중고_여"] = population[
        ["초등_여", "중학_여", "고등_여"]
    ].sum(axis=1)
    population["초중고_남"] = population[
        ["초등_남", "중학_남", "고등_남"]
    ].sum(axis=1)
    population["학교_초중고_전체"] = population[
        ["학교_초등", "학교_중학", "학교_고등"]
    ].sum(axis=1)

    rules = pd.read_excel(RULE_FILE)
    rules["rule_key"] = rules.apply(normalize_rule_key, axis=1)
    rules = rules.drop_duplicates(subset=["rule_key"]).copy()

    support_col = "support" if "support" in rules.columns else "지지도(%)"
    multiplier = 1.0 if support_col == "support" else 0.01
    rules["원본_전체건수"] = (
        rules[support_col] * multiplier * TOTAL_TRANSACTIONS
    ).round().astype(int)
    rules["지지도(%)"] = np.round(
        rules["원본_전체건수"] / TOTAL_TRANSACTIONS * 100,
        2,
    )
    rules = rules[
        rules["지지도(%)"] >= MIN_SUPPORT_PERCENT
    ].reset_index(drop=True)

    has_yearly_counts = all(f"{year}년" in rules.columns for year in YEARS)
    student_rates = []
    school_rates = []

    for _, row in rules.iterrows():
        student_col, school_col = get_exact_denominators(row["위험상황(조건)"])

        if has_yearly_counts:
            yearly_counts = [safe_float(row[f"{year}년"]) for year in YEARS]
        else:
            yearly_counts = [safe_float(row["원본_전체건수"]) / 5.0] * 5

        yearly_student_rates = [
            (count / population.loc[year, student_col]) * 10_000
            for year, count in zip(YEARS, yearly_counts)
        ]
        yearly_school_rates = [
            count / population.loc[year, school_col]
            for year, count in zip(YEARS, yearly_counts)
        ]

        student_rates.append(round(sum(yearly_student_rates) / 5.0, 2))
        school_rates.append(round(sum(yearly_school_rates) / 5.0, 2))

    rules["학생_1만명당_연평균_발생건수"] = student_rates
    rules["학교_1개교당_연평균_발생건수"] = school_rates
    rules.drop(columns=["rule_key"], errors="ignore", inplace=True)

    rules.to_excel(OUTPUT_FILE, index=False)
    print(f"저장 완료: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
