from dotenv import load_dotenv
import os

load_dotenv()

def _normalize_db_url(url: str) -> str:
    """
    Render/Heroku often supply URLs like `postgres://...` or `postgresql://...`.
    SQLAlchemy + psycopg prefers the explicit driver `postgresql+psycopg://`.
    This makes the minimal rewrite while keeping credentials/host intact.
    """
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    if url.startswith('postgresql://') and '+psycopg' not in url.split('://', 1)[0]:
        url = url.replace('postgresql://', 'postgresql+psycopg://', 1)
    return url

DATABASE_URL = _normalize_db_url(os.getenv('DATABASE_URL', 'postgresql+psycopg://postgres:postgres@localhost:5432/evjourney'))
CSV_BASE_DIR = os.getenv('CSV_BASE_DIR', r'D:\\')
PORT = int(os.getenv('PORT', '8000'))

PROVINCE_SEED = [
    ('chiang-mai','เชียงใหม่'),
    ('lamphun','ลำพูน'),
    ('lampang','ลำปาง'),
    ('mae-hong-son','แม่ฮ่องสอน'),
]

_origins_env = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000')
# Split by comma and strip spaces; if you really want wildcard, set ALLOWED_ORIGINS=*
ALLOWED_ORIGINS = [o.strip() for o in _origins_env.split(',') if o.strip()]
