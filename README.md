# 🎓🚀 College Earning  
### Turn Your Skills Into Opportunities.

A full-stack Flask web application built to connect college students through a verified, skill-based ecosystem.

College Earning allows students to create profiles, verify their identity via email, offer their skills, and explore other student profiles in a clean, animated, notebook-themed interface.

---

## 🌟 Live Concept

> Built for students.  
> Powered by skills.  
> Designed with creativity.

---

## ✨ Core Features

### 🔐 Secure Authentication
- Email verification system (OTP-based)
- Login / Logout functionality
- Secure password hashing (Werkzeug)
- Change password feature
- CSRF protection enabled

---

### 👤 Smart Profile System
- Edit profile functionality
- Year, Class, Section structure
- College name and bio
- Worker toggle (Offer skills option)
- Skill-based profile tagging

---

### 🛠 Skill-Based Community
- “Offers Skills” badge display
- Skills shown dynamically
- Structured dashboard listing verified users
- Clean profile viewing interface

---

### 📊 Dashboard
- View all verified student profiles
- Total users count
- Total workers count
- Worker skill visibility
- Responsive card-based layout

---

### 🎨 Unique UI Experience
- Notebook-style grid background
- Cartoon-inspired rounded font theme
- Marker-outline buttons & cards
- Animated background lines (Vanilla JS)
- Responsive design
- Subtle hover animations

---

## 🧰 Tech Stack

### Backend
- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-Mail
- Flask-WTF
- Flask-Limiter
- SQLite

### Frontend
- HTML5
- CSS3
- Vanilla JavaScript
- Custom animation system

---

## 📂 Project Structure
college_earning/
│
├── app.py
├── config.py
├── requirements.txt
│
├── app/
│ ├── init.py
│ ├── models.py
│ ├── forms.py
│ ├── user_service.py
│ ├── email_service.py
│ ├── extensions.py
│ │
│ ├── auth/
│ │ └── routes.py
│ │
│ └── main/
│ └── routes.py
│
├── templates/
├── static/
│ ├── style.css
│ └── js/animation.js
│
└── README.md


---

## ⚙️ Installation Guide

1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/college-earning.git
cd college-earning

2️⃣ Create Virtual Environment

python -m venv venv
venv\Scripts\activate   # Windows

3️⃣ Install Dependencies

pip install -r requirements.txt

4️⃣ Create Environment File

Create a .env file in root directory:
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///college_earning.db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

5️⃣ Run Application

python app.py

Open in browser:

http://127.0.0.1:5000
>>>>>>> 25f7e4d (feat: Update user registration and profile forms with new fields and validation)
