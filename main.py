from fastapi import FastAPI, Request, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, Response
from pathlib import Path
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# Импорты для БД
from database import (
    save_subscriber, 
    save_order, 
    save_contact,
    get_all_subscribers,
    get_all_orders
)

load_dotenv()

# ==================== Настройка логирования ====================

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== Создание приложения ====================

app = FastAPI(
    title="Math Mentor API",
    description="API для сайта репетитора по математике",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статические файлы
STATIC_DIR = Path("static")
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")


# ==================== HEAD-запросы (для Render) ====================

@app.head("/")
@app.head("/{path:path}")
async def head_handler():
    return Response(status_code=200, headers={"Content-Type": "text/html"})


# ==================== Страницы ====================

@app.get("/", response_class=HTMLResponse)
async def index():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Math Mentor</h1>")


@app.get("/blog", response_class=HTMLResponse)
async def blog_list():
    blog_path = STATIC_DIR / "blog.html"
    if blog_path.exists():
        return HTMLResponse(content=blog_path.read_text(encoding="utf-8"))
    return RedirectResponse(url="/")


@app.get("/blog/{article_id}", response_class=HTMLResponse)
async def blog_article(article_id: str):
    article_path = STATIC_DIR / "blog" / f"{article_id}.html"
    if article_path.exists():
        return HTMLResponse(content=article_path.read_text(encoding="utf-8"))
    return RedirectResponse(url="/blog")


# ==================== API Health Check ====================

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# ==================== API Подписка (с БД) ====================

@app.post("/api/subscribe")
async def subscribe_email(email: str = Form(...)):
    """Подписка на рассылку"""
    logger.info(f"📧 Новая подписка: {email}")
    
    try:
        saved = save_subscriber(email)
        if saved:
            return {"status": "success", "message": "Подписка оформлена!"}
        else:
            return {"status": "info", "message": "Вы уже подписаны!"}
    except Exception as e:
        logger.error(f"Ошибка сохранения подписки: {e}")
        return {"status": "error", "message": "Ошибка сервера"}


# ==================== API Запись на урок (с БД) ====================

@app.post("/api/order")
async def order_lesson(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    program: str = Form(...),
    preferred_date: str = Form(None),
    comment: str = Form(None)
):
    """Запись на пробный урок"""
    logger.info(f"🎓 Новая заявка: {name} | {program}")
    
    try:
        order_id = save_order({
            "name": name,
            "email": email,
            "phone": phone,
            "program": program,
            "preferred_date": preferred_date,
            "comment": comment
        })
        return {
            "status": "success",
            "message": f"Спасибо, {name}! Заявка №{order_id} принята."
        }
    except Exception as e:
        logger.error(f"Ошибка сохранения заявки: {e}")
        return {"status": "error", "message": "Ошибка сервера"}


# ==================== API Обратная связь (с БД) ====================

@app.post("/api/contact")
async def contact_form(
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    phone: str = Form(None)
):
    """Форма обратной связи"""
    logger.info(f"📨 Сообщение от {name}")
    
    try:
        contact_id = save_contact({
            "name": name,
            "email": email,
            "phone": phone,
            "message": message
        })
        return {
            "status": "success",
            "message": f"Спасибо, {name}! Сообщение #{contact_id} отправлено."
        }
    except Exception as e:
        logger.error(f"Ошибка сохранения сообщения: {e}")
        return {"status": "error", "message": "Ошибка сервера"}


# ==================== Админ-панель (просмотр данных) ====================

@app.get("/admin/subscribers")
async def admin_subscribers(password: str = ""):
    """Просмотр подписчиков (защищено паролем)"""
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
    
    if password != admin_password:
        return {"status": "error", "message": "Неверный пароль"}
    
    subscribers = get_all_subscribers()
    return {
        "count": len(subscribers),
        "subscribers": [{"id": s.id, "email": s.email, "date": str(s.created_at)} for s in subscribers]
    }


@app.get("/admin/orders")
async def admin_orders(password: str = ""):
    """Просмотр заявок (защищено паролем)"""
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
    
    if password != admin_password:
        return {"status": "error", "message": "Неверный пароль"}
    
    orders = get_all_orders()
    return {
        "count": len(orders),
        "orders": [
            {
                "id": o.id,
                "name": o.name,
                "email": o.email,
                "phone": o.phone,
                "program": o.program,
                "date": str(o.created_at),
                "status": o.status
            }
            for o in orders
        ]
    }


# ==================== Запуск ====================

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"🚀 Запуск Math Mentor API на порту {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)