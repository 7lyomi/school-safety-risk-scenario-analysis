"""Run the school-safety analysis pipeline in order."""
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parent
SCRIPTS = [
    "01_validate_school_level_heterogeneity.py",
    "02_build_analysis_datamart.py",
    "03_mine_risk_scenarios.py",
    "04_adjust_population_denominators.py",
    "05_select_final_risk_scenarios.py",
    "06_validate_reproducibility.py",
    "07_build_final_scenario_summary.py",
]

for script in SCRIPTS:
    path = ROOT / "src" / script
    print(f"\n[RUN] {script}")
    runpy.run_path(str(path), run_name="__main__")
