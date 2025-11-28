from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from .routers import search, agents, chargers, routes, pois
from . import config

app = FastAPI(title='EV Journey API')

# Configure CORS: allowlist via env ALLOWED_ORIGINS (comma-separated). Wildcard `*` disables credentials.
allow_all = '*' in config.ALLOWED_ORIGINS
cors_origins = ['*'] if allow_all else config.ALLOWED_ORIGINS
cors_allow_credentials = not allow_all

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_allow_credentials,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Compress large JSON responses to speed up transfers
app.add_middleware(GZipMiddleware, minimum_size=1024)

app.include_router(search.router)
app.include_router(agents.router)
app.include_router(chargers.router)
app.include_router(routes.router)
app.include_router(pois.router)

@app.get('/api/health')
def health():
    return { 'ok': True }
