"""สคริปต์ bootstrap ระหว่าง container start: init schema + ETL (option)"""
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

ETL_SCRIPTS = [
    ROOT / 'etl' / 'import_provinces.py',
    ROOT / 'etl' / 'import_pois.py',
    ROOT / 'etl' / 'import_activities.py',
    ROOT / 'etl' / 'import_foods.py',
    ROOT / 'etl' / 'import_cafes.py',
    ROOT / 'etl' / 'import_hotels.py',
    ROOT / 'etl' / 'import_chargers.py',
    ROOT / 'etl' / 'import_agents.py',
]

def env_flag(name: str, default: bool = False) -> bool:
    """อ่าน env เป็น boolean (0/false/no => False)"""
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() not in ('0', 'false', 'no', '')

def run_step(label: str, path: Path) -> int:
    """รันสคริปต์ย่อยพร้อมตั้ง PYTHONPATH ให้ถูกต้อง"""
    if not path.exists():
        print(f"[bootstrap] Skip missing script: {path}")
        return 0
    print(f"[bootstrap] Running {label} …", flush=True)
    env = os.environ.copy()
    env.setdefault('PYTHONPATH', str(ROOT))
    result = subprocess.run([sys.executable, str(path)], cwd=str(ROOT), env=env)
    if result.returncode != 0:
        print(f"[bootstrap] {label} exited with code {result.returncode}")
    return result.returncode


def main():
    run_etl = env_flag('RUN_BOOTSTRAP_ETL', default=False)
    run_init_db = env_flag('RUN_INIT_DB', default=True)

    # Apply schema
    if run_init_db:
        schema_rc = run_step('init_db', ROOT / 'scripts' / 'init_db.py')
        if schema_rc != 0:
            sys.exit(schema_rc)
    else:
        print("[bootstrap] Skipping init_db (RUN_INIT_DB disabled)")

    # Load data (best-effort so the app can still start)
    if run_etl:
        for script in ETL_SCRIPTS:
            run_step(script.stem, script)
    else:
        print("[bootstrap] Skipping ETL imports (RUN_BOOTSTRAP_ETL disabled)")


if __name__ == '__main__':
    main()
