# @Time    : 2026/02/17  (Refactored for LiteLocker)
# @Author  : xiaoguo141106
# @File    : main.py

# Derived from FileCodeBox by vastsa (https://github.com/vastsa/FileCodeBox)
# Modified by xiaoguo141106

import asyncio
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise

from apps.admin.views import admin_api
from apps.base.models import KeyValue
from apps.base.utils import ip_limit
from apps.base.views import share_api, chunk_api, presign_api
from core.config import ensure_settings_row, refresh_settings
from core.database import db_startup_lock, get_db_config, init_db
from core.logger import logger
from core.response import APIResponse
from core.settings import settings, BASE_DIR, DEFAULT_CONFIG
from core.tasks import delete_expire_files, clean_incomplete_uploads
from core.utils import hash_password, is_password_hashed

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("LiteLocker 引擎正在初始化...")
    await init_db()
    async with db_startup_lock():
        await load_config()
    
    # --- UI 关键点 1: 资产路径挂载 ---
    # 确保你的静态资源放在项目根目录下的 /assets 文件夹
    app.mount(
        "/assets",
        StaticFiles(directory=f"./{settings.themesSelect}/assets"),
        name="assets",
    )

    task = asyncio.create_task(delete_expire_files())
    chunk_cleanup_task = asyncio.create_task(clean_incomplete_uploads())
    logger.info("LiteLocker UI 加载完成")

    try:
        yield
    finally:
        logger.info("正在关闭应用...")
        task.cancel()
        chunk_cleanup_task.cancel()
        await asyncio.gather(task, chunk_cleanup_task, return_exceptions=True)
        await Tortoise.close_connections()

async def load_config():
    await ensure_settings_row()
    await KeyValue.update_or_create(
        key="sys_start", defaults={"value": int(time.time() * 1000)}
    )
    await refresh_settings()
    await migrate_password_to_hash()
    ip_limit["error"].minutes = settings.errorMinute
    ip_limit["error"].count = settings.errorCount
    ip_limit["upload"].minutes = settings.uploadMinute
    ip_limit["upload"].count = settings.uploadCount

async def migrate_password_to_hash():
    if not is_password_hashed(settings.admin_token):
        hashed = hash_password(settings.admin_token)
        settings.admin_token = hashed
        config_record = await KeyValue.filter(key="settings").first()
        if config_record and config_record.value:
            config_record.value["admin_token"] = hashed
            await config_record.save()
            logger.info("密码安全策略已同步")

app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def refresh_settings_middleware(request, call_next):
    await refresh_settings()
    return await call_next(request)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_tortoise(
    app,
    config=get_db_config(),
    generate_schemas=False,
    add_exception_handlers=True,
)

# 核心逻辑 API 全量保留，确保功能不崩
app.include_router(share_api)
app.include_router(chunk_api)
app.include_router(presign_api)
app.include_router(admin_api)

# --- UI 关键点 2: 定制首页渲染 ---
@app.exception_handler(404)
@app.get("/")
async def index(request=None, exc=None):
    # 这里加载你定制的主题 index.html
    theme_path = BASE_DIR / f"{settings.themesSelect}/index.html"
    with open(theme_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 注入 LiteLocker 的定制内容
    content = content.replace("{{title}}", "LiteLocker") \
                     .replace("{{description}}", "轻量级文件快递柜") \
                     .replace("{{keywords}}", "FileLocker, PrivateShare") \
                     .replace("{{opacity}}", str(settings.opacity)) \
                     .replace('"/assets/', '"assets/') \
                     .replace("{{background}}", str(settings.background))
    
    return HTMLResponse(content=content, media_type="text/html", headers={"Cache-Control": "no-cache"})

@app.get("/robots.txt")
async def robots():
    return HTMLResponse(content=settings.robotsText, media_type="text/plain")

# 保持前端配置接口的原汁原味，防止 Vue 报错
@app.post("/")
async def get_config():
    return APIResponse(
        detail={
            "name": "LiteLocker", 
            "description": settings.description,
            "explain": settings.page_explain,
            "uploadSize": settings.uploadSize,
            "expireStyle": settings.expireStyle,
            "enableChunk": settings.enableChunk,
            "openUpload": settings.openUpload,
            "notify_title": settings.notify_title,
            "notify_content": settings.notify_content,
            "show_admin_address": settings.showAdminAddr,
            "max_save_seconds": settings.max_save_seconds,
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app="main:app",
        host=settings.serverHost,
        port=settings.serverPort,
        reload=False,
        workers=settings.serverWorkers,
    )
