import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from dotenv import load_dotenv

load_dotenv()

# Подключение к БД
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# Для Render (замена postgres:// на postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# ==================== Модели ====================

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


# Создание таблиц
Base.metadata.create_all(bind=engine)


# ==================== Функции для работы с БД ====================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_subscriber(email: str):
    """Сохраняет подписчика в БД"""
    db = SessionLocal()
    try:
        # Проверяем, нет ли уже такого email
        existing = db.query(Subscriber).filter(Subscriber.email == email).first()
        if existing:
            return False  # Уже подписан
        
        subscriber = Subscriber(email=email)
        db.add(subscriber)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def save_order(data: dict):
    """Сохраняет заявку на урок в БД"""
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
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def save_contact(data: dict):
    """Сохраняет сообщение обратной связи в БД"""
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
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_all_subscribers():
    """Получает всех подписчиков"""
    db = SessionLocal()
    try:
        return db.query(Subscriber).order_by(Subscriber.created_at.desc()).all()
    finally:
        db.close()


def get_all_orders():
    """Получает все заявки"""
    db = SessionLocal()
    try:
        return db.query(Order).order_by(Order.created_at.desc()).all()
    finally:
        db.close()