# 🎓 Math Mentor — Сайт репетитора по математике

![Math Mentor](static/images/main-logo.png)

**Math Mentor** — это современный лендинг для репетитора по математике, специализирующегося на подготовке к **ЕГЭ** и **ОГЭ**. Сайт включает в себя блог с полезными статьями, формы обратной связи и записи на пробный урок.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED)

---

## 📸 Скриншоты

### Главный экран
![Главный экран](screenshots/homepage.png)

### Форма записи на пробный урок
![Запись на урок](screenshots/order-form.png)

### Обо мне
![Обо мне](screenshots/about.png)

---

## 🚀 Что мы сделали

### Фронтенд (Frontend)
- **Адаптировали готовый HTML-шаблон** `Urban - T-Shirt Store` под тематику репетитора по математике.
- **Заменили весь контент**: тексты, изображения, цветовую схему.
- **Создали дополнительные страницы**:
  - `/blog` — список всех статей.
  - `/blog/article-1`, `/blog/article-2`, `/blog/article-3` — полноценные статьи с полезным контентом.
- **Добавили формы**:
  - Подписка на рассылку (в футере).
  - Запись на пробный урок (модальное окно).
- **Интегрировали социальные сети**: Telegram, ВКонтакте, YouTube, WhatsApp.

### Бэкенд (Backend)
- **Написали сервер на FastAPI** (Python):
  - Раздача статических файлов (HTML, CSS, JS, изображения).
  - API-эндпоинты для обработки форм.
  - Логирование заявок в файлы.
  - CORS для безопасного взаимодействия с фронтендом.
- **Настроили маршрутизацию** для SPA-подобного поведения.

### Деплой
- **Упаковали проект в Docker**:
  - `Dockerfile` для сборки образа.
  - `docker-compose.yml` для удобного локального запуска.
- **Подготовили к хостингу** на Render, Railway или VPS.

---

## 🛠️ Технологии

| Категория | Технологии | Для чего использовали |
|:---|:---|:---|
| **Бэкенд** | ![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688?logo=fastapi) ![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python) | Обработка запросов, API, раздача статики |
| **Фронтенд** | ![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript) | Структура, стили, интерактивность |
| **Библиотеки** | ![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?logo=bootstrap) ![Swiper](https://img.shields.io/badge/Swiper-9-6332F6?logo=swiper) ![jQuery](https://img.shields.io/badge/jQuery-1.11.0-0769AD?logo=jquery) | Сетка, слайдеры, анимации |
| **Контейнеризация** | ![Docker](https://img.shields.io/badge/Docker-27.0-2496ED?logo=docker) | Упаковка приложения для деплоя |
| **Шрифты** | Google Fonts (Inter, Montserrat) | Типографика |

---
