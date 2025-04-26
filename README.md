# LSMS (Learning & School Management System)

A full-featured web-based school and learning management platform built with **Django**, featuring real-time notifications, subscription billing, multi-role dashboards, assignment handling, and secure authentication with email verification.

---

## 🚀 Features

- ✅ Student, Teacher, Parent, and Client Admin roles
- ✅ Email-based registration and activation (via Brevo SMTP)
- ✅ Real-time notifications with WebSockets (Django Channels)
- ✅ Push notification bell for role-based updates
- ✅ Assignment creation, submission, and evaluation
- ✅ Subscription management with Flutterwave
- ✅ Plan-based user limits (students/teachers)
- ✅ Background tasks using Celery + Redis
- ✅ Attractive, responsive UI (Bootstrap 5)

---

## ⚙️ Technologies

- **Backend**: Django 5.2, Django REST Framework, Channels, Celery
- **Frontend**: HTML, Bootstrap 5, WebSockets (JS)
- **Email**: Brevo SMTP
- **Payments**: Flutterwave
- **Asynchronous Tasks**: Celery + Redis
- **Deployment**: Render (Gunicorn + WhiteNoise)

---

## 🔧 Local Setup

```bash
git clone https://github.com/yourusername/prolsms.git
cd prolsms
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```ini
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-brevo-login
EMAIL_HOST_PASSWORD=your-brevo-smtp-key
DEFAULT_FROM_EMAIL=your@email.com

CELERY_BROKER_URL=redis://localhost:6379
```

Then run:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Start Celery (in a separate terminal):
```bash
celery -A PROLSMS worker --loglevel=info
```

---

## 🌐 Deployment on Render

1. Set up a **Web Service** and push this repo.
2. Add a **Background Worker**:
   ```
   celery -A PROLSMS worker --loglevel=info
   ```
3. Add a **Key Value (Redis)** service, and copy the Redis URL.
4. Add **Environment Variables**:
   - Django + Brevo + Redis + Flutterwave config
5. Add a `Procfile`:
   ```
   web: gunicorn PROLSMS.wsgi --log-file -
   worker: celery -A PROLSMS worker --loglevel=info
   ```
6. Add `runtime.txt` and `requirements.txt`
7. In `settings.py`, ensure:
   ```python
   STATIC_ROOT = BASE_DIR / 'staticfiles'
   MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
   ```

---

## 📬 Contact & Contributions

Contributions welcome! Fork the repo and submit a PR.

Maintained by **[YUSUF BABATUNDE MUFTAUDEEN (DEV. PROGRESS)]**  
📧 djangproj@gmail.com 
🌐 [https://pimconcepts.com.ng](https://pimconcepts.com.ng)

---

> Built with ❤️ to simplify and scale school operations across the world.

