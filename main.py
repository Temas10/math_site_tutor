from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, Response
from pathlib import Path
import logging
import os
from datetime import datetime

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
    description="API для сайта репетитора по математике (ЕГЭ/ОГЭ)",
    version="2.0.0"
)

# ==================== CORS ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Статические файлы ====================

STATIC_DIR = Path("static")
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")


# ==================== HEAD-запросы (для Render) ====================

@app.head("/")
@app.head("/{path:path}")
async def head_handler(request: Request, path: str = ""):
    """Обрабатывает HEAD-запросы от Render для проверки доступности"""
    return Response(
        status_code=200,
        headers={
            "Content-Type": "text/html",
            "Cache-Control": "no-cache"
        }
    )


@app.head("/api/health")
async def health_head():
    """HEAD-запрос для health check"""
    return Response(status_code=200)


# ==================== Страницы ====================

@app.get("/", response_class=HTMLResponse)
async def index():
    """Главная страница"""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Math Mentor - Сайт в разработке</h1>")


@app.get("/blog", response_class=HTMLResponse)
async def blog_list():
    """Страница со списком статей"""
    blog_path = STATIC_DIR / "blog.html"
    if blog_path.exists():
        return HTMLResponse(content=blog_path.read_text(encoding="utf-8"))
    return RedirectResponse(url="/")


@app.get("/blog/{article_id}", response_class=HTMLResponse)
async def blog_article(article_id: str):
    """Отдельная статья"""
    article_path = STATIC_DIR / "blog" / f"{article_id}.html"
    if article_path.exists():
        return HTMLResponse(content=article_path.read_text(encoding="utf-8"))
    return RedirectResponse(url="/blog")


@app.get("/about", response_class=HTMLResponse)
async def about():
    """Страница Обо мне"""
    about_path = STATIC_DIR / "about.html"
    if about_path.exists():
        return HTMLResponse(content=about_path.read_text(encoding="utf-8"))
    return RedirectResponse(url="/#about-us")


# ==================== API Health Check ====================

@app.get("/api/health")
async def health_check():
    """Проверка работоспособности"""
    return {
        "status": "healthy",
        "service": "Math Mentor API",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }


# ==================== API Подписка ====================

@app.post("/api/subscribe")
async def subscribe_email(email: str = Form(...)):
    """Подписка на рассылку"""
    logger.info(f"📧 Новая подписка: {email}")
    
    # Сохраняем в файл
    subscribers_file = LOG_DIR / "subscribers.txt"
    with open(subscribers_file, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} | {email}\n")
    
    return {
        "status": "success",
        "message": "Подписка оформлена! Спасибо!"
    }


# ==================== API Запись на урок ====================

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
    logger.info(f"🎓 Новая заявка: {name} | {program} | {phone}")
    
    # Сохраняем в файл
    orders_file = LOG_DIR / "orders.txt"
    with open(orders_file, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
        f.write(f"Имя: {name}\n")
        f.write(f"Email: {email}\n")
        f.write(f"Телефон: {phone}\n")
        f.write(f"Программа: {program}\n")
        f.write(f"Желаемая дата: {preferred_date or 'не указана'}\n")
        f.write(f"Комментарий: {comment or 'нет'}\n")
    
    return {
        "status": "success",
        "message": f"Спасибо, {name}! Ваша заявка принята. Скоро свяжусь с вами."
    }


# ==================== API Обратная связь ====================

@app.post("/api/contact")
async def contact_form(
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    phone: str = Form(None)
):
    """Форма обратной связи"""
    logger.info(f"📨 Сообщение от {name} ({email})")
    
    # Сохраняем в файл
    contacts_file = LOG_DIR / "contacts.txt"
    with open(contacts_file, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
        f.write(f"Имя: {name}\n")
        f.write(f"Email: {email}\n")
        f.write(f"Телефон: {phone or 'не указан'}\n")
        f.write(f"Сообщение: {message}\n")
    
    return {
        "status": "success",
        "message": f"Спасибо за сообщение, {name}! Я отвечу в ближайшее время."
    }


# ==================== Обработка favicon ====================

@app.get("/favicon.ico")
async def favicon():
    """Иконка сайта"""
    favicon_path = STATIC_DIR / "images" / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(favicon_path)
    return Response(status_code=204)


# ==================== Обработка robots.txt ====================

@app.get("/robots.txt")
async def robots():
    """Файл для поисковых роботов"""
    content = """User-agent: *
Allow: /
Sitemap: /sitemap.xml
"""
    return Response(content=content, media_type="text/plain")


# ==================== Обработка sitemap.xml ====================

@app.get("/sitemap.xml")
async def sitemap():
    """Карта сайта для SEO"""
    base_url = os.environ.get("BASE_URL", "https://math-mentor.onrender.com")
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>{base_url}/</loc>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>{base_url}/blog</loc>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>{base_url}/blog/article-1</loc>
        <priority>0.7</priority>
    </url>
    <url>
        <loc>{base_url}/blog/article-2</loc>
        <priority>0.7</priority>
    </url>
    <url>
        <loc>{base_url}/blog/article-3</loc>
        <priority>0.7</priority>
    </url>
</urlset>"""
    return Response(content=content, media_type="application/xml")


# ==================== Запуск ====================

if __name__ == "__main__":
    import uvicorn
    
    # Получаем порт из переменной окружения (для Render)
    port = int(os.environ.get("PORT", 8000))
    
    logger.info(f"🚀 Запуск Math Mentor API на порту {port}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # В production reload должен быть False
        log_level="info"
    )