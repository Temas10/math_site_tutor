# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, Response
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

# ==================== Попытка подключения к БД ====================

DB_ENABLED = False

try:
    DATABASE_URL = os.environ.get("DATABASE_URL", "")
    
    if DATABASE_URL:
        # Исправляем URL для SQLAlchemy
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        
        from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy.sql import func
        
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base = declarative_base()
        
        # Модели
        class Subscriber(Base):
            __tablename__ = "subscribers"
            id = Column(Integer, primary_key=True, index=True)
            email = Column(String(255), unique=True, nullable=False)
            created_at = Column(DateTime, server_default=func.now())
        
        class Order(Base):
            __tablename__ = "orders"
            id = Column(Integer, primary_key=True, index=True)
            name = Column(String(255), nullable=False)
            email = Column(String(255), nullable=False)
            phone = Column(String(50), nullable=False)
            program = Column(String(100), nullable=False)
            preferred_date = Column(String(50), nullable=True)
            comment = Column(Text, nullable=True)
            status = Column(String(50), default="new")
            created_at = Column(DateTime, server_default=func.now())
        
        class Contact(Base):
            __tablename__ = "contacts"
            id = Column(Integer, primary_key=True, index=True)
            name = Column(String(255), nullable=False)
            email = Column(String(255), nullable=False)
            phone = Column(String(50), nullable=True)
            message = Column(Text, nullable=False)
            status = Column(String(50), default="new")
            created_at = Column(DateTime, server_default=func.now())
        
        # Создаём таблицы
        Base.metadata.create_all(bind=engine)
        
        def save_subscriber_to_db(email: str):
            db = SessionLocal()
            try:
                existing = db.query(Subscriber).filter(Subscriber.email == email).first()
                if existing:
                    return False
                subscriber = Subscriber(email=email)
                db.add(subscriber)
                db.commit()
                return True
            except:
                db.rollback()
                return False
            finally:
                db.close()
        
        def save_order_to_db(data: dict):
            db = SessionLocal()
            try:
                order = Order(
                    name=data.get("name"),
                    email=data.get("email"),
                    phone=data.get("phone"),
                    program=data.get("program"),
                    preferred_date=data.get("preferred_date"),
                    comment=data.get("comment")
                )
                db.add(order)
                db.commit()
                return order.id
            except:
                db.rollback()
                return None
            finally:
                db.close()
        
        def save_contact_to_db(data: dict):
            db = SessionLocal()
            try:
                contact = Contact(
                    name=data.get("name"),
                    email=data.get("email"),
                    phone=data.get("phone"),
                    message=data.get("message")
                )
                db.add(contact)
                db.commit()
                return contact.id
            except:
                db.rollback()
                return None
            finally:
                db.close()
        
        DB_ENABLED = True
        logger.info("✅ База данных подключена")
    else:
        logger.warning("⚠️ DATABASE_URL не задана, работаем с файлами")
        
except Exception as e:
    logger.warning(f"⚠️ База данных не подключена: {e}. Работаем с файлами")

# ==================== Создание приложения ====================

app = FastAPI(
    title="Math Mentor API",
    description="API для сайта репетитора по математике (ЕГЭ/ОГЭ)",
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
    """Главная страница"""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Math Mentor — Репетитор по математике</h1>")


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
        "database": "connected" if DB_ENABLED else "file-based"
    }


# ==================== API Подписка ====================

@app.post("/api/subscribe")
async def subscribe_email(email: str = Form(...)):
    """Подписка на рассылку"""
    logger.info(f"📧 Новая подписка: {email}")
    
    # Сохраняем в файл (всегда)
    subscribers_file = LOG_DIR / "subscribers.txt"
    with open(subscribers_file, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} | {email}\n")
    
    # Сохраняем в БД (если доступна)
    if DB_ENABLED:
        try:
            saved = save_subscriber_to_db(email)
            if saved:
                logger.info(f"✅ Подписка сохранена в БД: {email}")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения в БД: {e}")
    
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
    
    # Сохраняем в файл (всегда)
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
    
    # Сохраняем в БД (если доступна)
    if DB_ENABLED:
        try:
            order_id = save_order_to_db({
                "name": name,
                "email": email,
                "phone": phone,
                "program": program,
                "preferred_date": preferred_date,
                "comment": comment
            })
            if order_id:
                logger.info(f"✅ Заявка №{order_id} сохранена в БД")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения в БД: {e}")
    
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
    
    # Сохраняем в файл (всегда)
    contacts_file = LOG_DIR / "contacts.txt"
    with open(contacts_file, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
        f.write(f"Имя: {name}\n")
        f.write(f"Email: {email}\n")
        f.write(f"Телефон: {phone or 'не указан'}\n")
        f.write(f"Сообщение: {message}\n")
    
    # Сохраняем в БД (если доступна)
    if DB_ENABLED:
        try:
            contact_id = save_contact_to_db({
                "name": name,
                "email": email,
                "phone": phone,
                "message": message
            })
            if contact_id:
                logger.info(f"✅ Сообщение №{contact_id} сохранено в БД")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения в БД: {e}")
    
    return {
        "status": "success",
        "message": f"Спасибо за сообщение, {name}! Я отвечу в ближайшее время."
    }


# ==================== Админ-панель ====================

@app.get("/admin/health")
async def admin_health(password: str = ""):
    """Проверка состояния системы"""
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
    
    if password != admin_password:
        return {"status": "error", "message": "Неверный пароль"}
    
    # Читаем файлы
    subscribers = []
    orders = []
    
    subscribers_file = LOG_DIR / "subscribers.txt"
    if subscribers_file.exists():
        with open(subscribers_file, "r", encoding="utf-8") as f:
            subscribers = f.readlines()[-20:]  # Последние 20
    
    orders_file = LOG_DIR / "orders.txt"
    if orders_file.exists():
        with open(orders_file, "r", encoding="utf-8") as f:
            orders = f.read().split("="*50)[-5:]  # Последние 5 заявок
    
    return {
        "database_enabled": DB_ENABLED,
        "last_subscribers": subscribers,
        "last_orders": orders,
        "logs_exist": {
            "subscribers": subscribers_file.exists(),
            "orders": orders_file.exists(),
            "contacts": (LOG_DIR / "contacts.txt").exists()
        }
    }


# ==================== favicon и robots ====================

@app.get("/favicon.ico")
async def favicon():
    favicon_path = STATIC_DIR / "images" / "favicon.ico"
    if favicon_path.exists():
        return Response(content=favicon_path.read_bytes(), media_type="image/x-icon")
    return Response(status_code=204)


@app.get("/robots.txt")
async def robots():
    return Response(
        content="User-agent: *\nAllow: /\nSitemap: /sitemap.xml",
        media_type="text/plain"
    )


# ==================== Запуск ====================

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"🚀 Запуск Math Mentor API на порту {port}")
    logger.info(f"📊 База данных: {'Подключена' if DB_ENABLED else 'Работа с файлами'}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)