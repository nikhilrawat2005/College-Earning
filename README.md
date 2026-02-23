# SwapSavvy Pro

A comprehensive professional networking and skill-sharing platform that connects learners with teachers, enabling knowledge exchange, portfolio showcasing, and professional growth.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Database Models](#database-models)
- [Security Features](#security-features)
- [Deployment](#deployment)
- [Contributing](#contributing)

## 🎯 Overview

SwapSavvy Pro is a full-featured social networking platform designed for professionals, educators, and learners. It combines the best aspects of professional networking (like LinkedIn) with skill-sharing capabilities, allowing users to:

- **Learn**: Find teachers and courses to acquire new skills
- **Teach**: Offer services and share knowledge with learners
- **Network**: Connect with professionals, build relationships, and grow your network
- **Showcase**: Display portfolios, experiences, and achievements

The platform supports both authenticated users and guest browsing, making it accessible to everyone while encouraging account creation for full functionality.

## ✨ Features

### 🔐 Authentication & User Management
- **Email Verification**: Secure signup with 6-digit verification codes
- **Password Security**: Hashed passwords using Werkzeug
- **Guest Mode**: Browse the platform without registration (24-hour session)
- **Profile Modes**: Choose between Learner, Teacher, or Both
- **User Profiles**: Comprehensive profiles with avatar, cover photo, headline, summary, and location

### 👤 Profile Management
- **Professional Profiles**: 
  - Headline and summary
  - Location and website
  - Open to work/freelance indicators
  - Profile mode selection (Learner/Teacher/Both)
- **Portfolio Management**: Add, edit, and delete portfolio items with media
- **Experience Tracking**: Manage work experience with dates, companies, and descriptions
- **Education History**: Track educational background
- **Skills System**: Add skills with proficiency levels and years of experience
- **Rating & Reviews**: Rate and review users based on service types

### 📱 Social Features
- **Posts**: Create text and media posts
- **Interactions**: Like and comment on posts
- **Follow System**: Follow/unfollow users
- **Connections**: Send and manage professional connection requests
- **Messaging**: Direct messaging between users with read receipts
- **Notifications**: Real-time notifications for interactions
- **Feed**: Personalized dashboard showing posts from followed users

### 🔍 Discovery & Search
- **Explore Page**: Discover users, posts, and trending skills
- **Search Functionality**: Search users by username, name, or headline
- **Trending Skills**: View most popular skills on the platform
- **Filter Options**: Filter search results by type (all, people, posts)

### 💼 Professional Features
- **Services**: Teachers can list services with pricing (Fixed, Hourly, Project, Free)
- **Learning Goals**: Learners can set goals with budget and timeline
- **Response Time**: Teachers can set expected response times
- **Hourly Rates**: Set and display hourly rates for services

### 🎨 User Interface
- **Modern Design**: Neon Pro Edge theme with gradient effects
- **Responsive Layout**: Works on desktop, tablet, and mobile devices
- **Dark/Light Mode**: Theme switching capability (via theme.js)
- **Glass Morphism**: Modern UI effects with glass-like components
- **Smooth Animations**: CSS transitions and hover effects

### 🔒 Security & Performance
- **CSRF Protection**: Flask-WTF CSRF tokens
- **Rate Limiting**: Flask-Limiter for API protection
- **Security Headers**: Flask-Talisman for additional security
- **File Upload Validation**: Secure file handling with size limits
- **Session Management**: Secure session handling with expiry
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection

## 🛠 Technologies Used

### Backend
- **Flask 2.3.3**: Python web framework
- **SQLAlchemy 3.0.5**: ORM for database operations
- **Flask-Migrate 4.0.5**: Database migrations
- **Flask-Mail 0.9.1**: Email sending functionality
- **Flask-WTF 1.1.1**: CSRF protection and form handling
- **Flask-Limiter 3.3.0**: Rate limiting
- **Flask-Talisman 1.0.0**: Security headers
- **Werkzeug 2.3.7**: Password hashing and utilities
- **python-dotenv 1.0.0**: Environment variable management

### Database
- **SQLite**: Default database (can be configured for PostgreSQL/MySQL)
- **Alembic 1.12.1**: Database migration tool

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with custom properties and gradients
- **JavaScript**: Interactive features and AJAX requests
- **Jinja2**: Template engine

### Deployment
- **Gunicorn 20.1.0**: WSGI HTTP server for production
- **Heroku**: Deployment platform (Procfile included)

## 📁 Project Structure

```
Mini Project ( )
├── app/
│   ├── __init__.py              # Application factory and configuration
│   ├── models.py                # Database models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication routes (signup, login, verify)
│   │   ├── main.py              # Main routes (dashboard, explore, search)
│   │   ├── profile.py            # Profile management routes
│   │   └── social.py             # Social features (posts, messages, connections)
│   └── services/
│       ├── __init__.py
│       ├── email_service.py      # Email sending service
│       └── user_service.py       # User-related business logic
├── templates/                    # Jinja2 templates
│   ├── base.html                # Base template
│   ├── landing.html             # Landing page
│   ├── dashboard.html           # User dashboard
│   ├── profile.html             # User profile view
│   ├── edit_profile.html        # Profile editing
│   ├── explore.html             # Discovery page
│   ├── search.html              # Search results
│   ├── messages.html             # Messages list
│   ├── conversation.html         # Individual conversation
│   ├── connections.html          # Connection requests
│   ├── notifications.html        # Notifications
│   ├── manage_portfolio.html    # Portfolio management
│   ├── manage_experience.html   # Experience management
│   ├── manage_education.html     # Education management
│   └── includes/                # Template partials
├── static/
│   ├── css/
│   │   └── style.css            # Main stylesheet (Neon Pro Edge theme)
│   ├── js/
│   │   ├── theme.js             # Theme switching
│   │   ├── post-actions.js      # Post interactions
│   │   └── guest.js             # Guest mode functionality
│   ├── img/                     # Images and assets
│   └── uploads/                 # User-uploaded files
│       ├── avatars/             # User avatars
│       ├── covers/             # Cover photos
│       ├── posts/               # Post media
│       ├── portfolio/           # Portfolio items
│       └── documents/           # Documents
├── instance/
│   └── swapsavvy.db            # SQLite database
├── app.py                      # Main application entry point (legacy)
├── requirements.txt            # Python dependencies
├── Procfile                    # Heroku deployment config
├── runtime.txt                 # Python version for Heroku
└── README.md                   # This file
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.11.4 or higher
- pip (Python package manager)
- Git (optional, for cloning)

### Step 1: Clone or Download the Project
```bash
# If using Git
git clone <repository-url>
cd "Mini Project ( )"
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration
Create a `.env` file in the root directory:

```env
# Secret Key (generate a random string)
SECRET_KEY=your-secret-key-here-change-in-production

# Database URL (SQLite by default)
DATABASE_URL=sqlite:///swapsavvy.db

# Email Configuration (for email verification)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Flask Configuration
FLASK_CONFIG=development
FLASK_APP=app.py
```

**Note**: For Gmail, you'll need to:
1. Enable 2-factor authentication
2. Generate an "App Password" in your Google Account settings
3. Use the app password in `MAIL_PASSWORD`

### Step 5: Initialize Database
```bash
# Run the application once to create the database
python app.py
```

Or if using Flask CLI:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Step 6: Run the Application
```bash
# Development mode
python app.py

# Or using Flask CLI
flask run
```

The application will be available at `http://localhost:5000`

## ⚙️ Configuration

### Database Configuration
The application uses SQLite by default. To use PostgreSQL or MySQL:

1. Update `DATABASE_URL` in `.env`:
   ```env
   DATABASE_URL=postgresql://user:password@localhost/swapsavvy
   ```

2. Install the appropriate database driver:
   ```bash
   pip install psycopg2-binary  # For PostgreSQL
   pip install pymysql          # For MySQL
   ```

### File Upload Configuration
- **Max File Size**: 16 MB (configurable in `app.py`)
- **Allowed Extensions**: png, jpg, jpeg, gif, mp4, mov, webp, pdf, ppt, pptx
- **Upload Folders**: Automatically created in `static/uploads/`

### Rate Limiting
Default limits (configurable in `app.py`):
- **General**: 200 requests per day, 50 per hour
- **Signup/Login**: 5 requests per minute
- **Resend Code**: 3 requests per hour

## 📖 Usage

### For Users

#### Signing Up
1. Navigate to the landing page
2. Click "Sign Up"
3. Fill in username, email, password, name, and gender
4. Check your email for verification code
5. Enter the 6-digit code to verify your account
6. Log in with your credentials

#### Guest Mode
1. Click "Browse as Guest" on the landing page
2. Explore users, posts, and content (read-only)
3. Create an account to unlock full features

#### Creating a Profile
1. Go to "Edit Profile" after logging in
2. Fill in your professional information:
   - Headline and summary
   - Location and website
   - Profile mode (Learner/Teacher/Both)
   - Skills with proficiency levels
3. Upload avatar and cover photo
4. Add experience, education, and portfolio items

#### Social Features
- **Create Posts**: Share text or media posts from the dashboard
- **Follow Users**: Click "Follow" on user profiles
- **Send Messages**: Start conversations from user profiles
- **Connect**: Send professional connection requests
- **Like & Comment**: Interact with posts in your feed

### For Developers

#### Running in Development
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

#### Database Migrations
```bash
# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback last migration
flask db downgrade
```

#### Testing Email Functionality
In development, verification codes are printed to console. Check the terminal output for the code.

## 🔌 API Endpoints

### Public Endpoints
- `GET /` - Landing page
- `GET /landing` - Landing page
- `GET /explore` - Explore page (guest accessible)
- `GET /search?q=<query>` - Search users
- `GET /profile/<username>` - View user profile (guest accessible)
- `GET /api/user/<username>` - Get user data (JSON)
- `GET /api/posts?page=<page>&per_page=<per_page>` - Get posts (JSON)

### Authentication Endpoints
- `GET/POST /signup` - User registration
- `GET/POST /verify` - Email verification
- `POST /resend-code` - Resend verification code
- `GET/POST /login` - User login
- `GET /logout` - User logout
- `GET /browse-as-guest` - Start guest session
- `GET /end-guest-session` - End guest session

### Protected Endpoints (Require Login)
- `GET /dashboard` - User dashboard
- `GET /edit-profile` - Edit profile page
- `POST /update_profile` - Update profile
- `GET /manage-portfolio` - Portfolio management
- `POST /portfolio/add` - Add portfolio item
- `POST /portfolio/<id>/edit` - Edit portfolio item
- `POST /portfolio/<id>/delete` - Delete portfolio item
- `GET /manage-experience` - Experience management
- `POST /experience/add` - Add experience
- `GET /manage-education` - Education management
- `POST /education/add` - Add education

### Social Endpoints
- `POST /user/<id>/follow` - Follow/unfollow user
- `POST /user/<id>/connect` - Send connection request
- `GET /connections` - View connections
- `POST /connection/<id>/accept` - Accept connection
- `POST /connection/<id>/reject` - Reject connection
- `GET /messages` - Messages list
- `GET /messages/<user_id>` - View conversation
- `POST /messages/send` - Send message
- `GET /notifications` - Notifications list
- `POST /notifications/read-all` - Mark all as read
- `POST /post/<id>/like` - Like/unlike post
- `POST /post/<id>/comment` - Comment on post
- `POST /create-post` - Create new post
- `POST /post/<id>/delete` - Delete post
- `POST /user/<id>/review` - Add review

## 🗄️ Database Models

### Core Models
- **User**: User accounts with profile information
- **PendingUser**: Temporary users awaiting email verification
- **EmailVerification**: Verification codes and attempts

### Profile Models
- **Experience**: Work experience entries
- **Education**: Educational background
- **Skill**: Available skills
- **UserSkill**: User-skill associations with proficiency
- **PortfolioItem**: Portfolio projects and work samples

### Social Models
- **Post**: User posts (text and media)
- **Like**: Post likes
- **Comment**: Post comments
- **Follow**: User follow relationships
- **Connection**: Professional connections (pending/accepted)
- **Message**: Direct messages between users
- **Notification**: User notifications
- **Review**: User reviews and ratings

### Service Models
- **Service**: Services offered by teachers
- **LearningGoal**: Learning goals set by learners

## 🔐 Security Features

### Authentication Security
- Password hashing with Werkzeug (PBKDF2)
- Email verification required for account activation
- Rate limiting on authentication endpoints
- Session-based authentication with secure cookies

### Application Security
- CSRF protection on all forms
- SQL injection prevention via SQLAlchemy ORM
- File upload validation (type and size)
- Secure filename handling
- Security headers via Flask-Talisman

### Data Protection
- Input validation and sanitization
- XSS prevention in templates
- Secure session management
- Guest mode restrictions for write operations

## 🚢 Deployment

### Heroku Deployment

1. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

2. **Set Environment Variables**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DATABASE_URL=postgresql://...
   heroku config:set MAIL_SERVER=smtp.gmail.com
   heroku config:set MAIL_PORT=587
   heroku config:set MAIL_USE_TLS=True
   heroku config:set MAIL_USERNAME=your-email@gmail.com
   heroku config:set MAIL_PASSWORD=your-app-password
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

4. **Run Migrations**
   ```bash
   heroku run flask db upgrade
   ```

### Other Platforms
The application can be deployed on any platform supporting Python/Flask:
- **AWS Elastic Beanstalk**
- **Google App Engine**
- **DigitalOcean App Platform**
- **Railway**
- **Render**

### Production Considerations
1. **Use PostgreSQL** instead of SQLite
2. **Set strong SECRET_KEY** (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)
3. **Enable HTTPS** (required for secure cookies)
4. **Configure proper CORS** if using API
5. **Set up logging** and monitoring
6. **Use environment variables** for all sensitive data
7. **Configure backup** for database
8. **Set up email service** (SendGrid, Mailgun, etc.)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Write docstrings for functions and classes

## 📝 License

This project is part of a Mini Project assignment. Please refer to your institution's guidelines for usage and distribution.

## 🐛 Troubleshooting

### Common Issues

**Email not sending:**
- Check SMTP credentials in `.env`
- For Gmail, ensure "Less secure app access" is enabled or use App Password
- Check firewall/network settings

**Database errors:**
- Ensure database file has write permissions
- Run migrations: `flask db upgrade`
- Check database URL in `.env`

**File upload issues:**
- Check file size (max 16MB)
- Verify file extension is allowed
- Ensure `static/uploads/` directories exist

**Import errors:**
- Activate virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version (3.11.4+)

## 📞 Support

For issues, questions, or suggestions, please:
1. Check existing issues in the repository
2. Create a new issue with detailed description
3. Include error messages and steps to reproduce

## 🎉 Acknowledgments

- Built with Flask and modern web technologies
- Inspired by professional networking platforms
- Designed for educational and professional use

---

**SwapSavvy Pro** - Connect, Learn, Teach, Grow! 🚀

