from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from pathlib import Path
import logging
from datetime import datetime

# Настройка логирования
Path("logs").mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Math Mentor", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")


# ==================== Страницы ====================

@app.get("/", response_class=HTMLResponse)
async def index():
    """Главная страница"""
    return FileResponse("static/index.html")


@app.get("/blog", response_class=HTMLResponse)
async def blog_list():
    """Страница со списком всех статей"""
    blog_path = Path("static/blog.html")
    if blog_path.exists():
        return HTMLResponse(content=blog_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Блог в разработке</h1>")


@app.get("/blog/{article_id}", response_class=HTMLResponse)
async def blog_article(article_id: str):
    """Отдельная статья"""
    article_path = Path(f"static/blog/{article_id}.html")
    if article_path.exists():
        return HTMLResponse(content=article_path.read_text(encoding="utf-8"))
    return RedirectResponse(url="/blog")


@app.get("/about", response_class=HTMLResponse)
async def about():
    """Страница Обо мне"""
    # Можно создать отдельную страницу или перенаправить на главную
    return RedirectResponse(url="/#about-us")


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# ==================== API ====================

@app.post("/api/subscribe")
async def subscribe_email(email: str = Form(...)):
    """Подписка на рассылку"""
    logger.info(f"📧 Новая подписка: {email}")
    
    with open("logs/subscribers.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} | {email}\n")
    
    return {"status": "success", "message": "Подписка оформлена!"}


@app.post("/api/order")
async def order(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    program: str = Form(...),
    preferred_date: str = Form(None),
    comment: str = Form(None)
):
    """Запись на пробный урок"""
    logger.info(f"🎓 Заявка: {name} | {program}")
    
    with open("logs/orders.txt", "a", encoding="utf-8") as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
        f.write(f"Имя: {name}\n")
        f.write(f"Email: {email}\n")
        f.write(f"Телефон: {phone}\n")
        f.write(f"Программа: {program}\n")
        f.write(f"Дата: {preferred_date or 'не указана'}\n")
        f.write(f"Комментарий: {comment or 'нет'}\n")
    
    return {"status": "success", "message": "Заявка принята!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)