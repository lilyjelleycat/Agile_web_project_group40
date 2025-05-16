# Cinebuff

## Overview
Cinebuff is a comprehensive web application that enables users to track, review, and share their movie-watching experiences. Built with Flask and modern web technologies, it provides a user-friendly interface for movie enthusiasts to manage their personal movie collections and interact with other users' reviews.

## Features
- **User Authentication**
  - Secure sign-up and login system
  - User profile management
  - Admin dashboard for site management

- **Movie Management**
  - Add and track watched movies
  - Write and edit movie reviews
  - Rate movies on various criteria
  - Upload movie posters and information

- **Social Features**
  - Share movie reviews with other users
  - View and interact with community reviews
  - Follow other users' movie activities

- **Analytics**
  - Visualize movie watching statistics
  - Genre distribution analysis
  - Personal watching trends
  - Rating distributions

## Technology Stack
- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Bootstrap, JavaScript, AJAX
- **Testing**: Unittest, Selenium, Flask-Testing
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF, WTForms

## Project Structure
```
Agile_web_project_group40/
├── run.py                      # Main application entry point
├── requirements.txt            # Python dependencies for the project
├── README.md                   # Project documentation
├── movies.db                   # SQLite database file (copy of the instance one)
├── instance/                   # Instance folder
│   └── movies.db              # Main SQLite database for the application
├── app/                        # Main application package
│   ├── __init__.py            # App initialization, DB and login setup
│   ├── models.py              # Database models (Movie, Member, Review, etc.)
│   ├── static/                # Static assets
│   │   └── styles.css         # Application styles
│   ├── templates/             # HTML templates
│   │   ├── base.html          # Base template with common layout
│   │   ├── index.html         # Home page template
│   │   ├── login.html         # Login page
│   │   ├── register.html      # Registration page
│   │   ├── profile.html       # User profile page
│   │   ├── movie_detail.html  # Movie details page
│   │   ├── search.html        # Search page
│   │   └── ... other templates
│   ├── admin/                 # Admin blueprint package
│   │   ├── __init__.py
│   │   ├── forms.py           # Admin-related forms
│   │   ├── routes.py          # Admin routes for uploading/editing movies
│   │   └── utils.py           # Admin utility functions
│   ├── errors/                # Error handling blueprint
│   │   ├── __init__.py
│   │   └── handlers.py        # Error handlers (404, 500, etc.)
│   ├── main/                  # Main blueprint package
│   │   ├── __init__.py
│   │   └── routes.py          # Main routes (home page, etc.)
│   ├── movies/                # Movies blueprint package
│   │   ├── __init__.py
│   │   ├── forms.py           # Movie-related forms
│   │   ├── routes.py          # Movie routes (search, details, reviews)
│   │   └── utils.py           # Movie utility functions
│   └── users/                 # Users blueprint package
│       ├── __init__.py
│       ├── forms.py           # User-related forms
│       └── routes.py          # User routes (login, register, profile)
├── tests/                      # Test directory
│   ├── __init__.py
│   ├── seleniumTestRegisterLogin.py  # Selenium tests for registration/login
│   ├── unitTestRegisterLogin.py      # Unit tests for registration/login
│   └── testConf.py                   # Test configuration
```

## Installation and Setup

1. Clone the repository and go into the root path:
```bash
git clone https://github.com/lilyjelleycat/Agile_web_project_group40.git
```

2. Create and activate a virtual environment:
```bash
python -m venv app-venv
# On Windows
app-venv\Scripts\activate
# On macOS/Linux
source app-venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
flask db upgrade
```

5. Run the application:
```bash
python run.py
```

The application will be available at `http://localhost:5000`

## Testing

The project includes a comprehensive test suite covering different aspects of the application:

1. Run all tests:
```bash
python -m pytest
```

2. Run specific test categories:
```bash
python3 -m tests.unitTestRegisterLogin     # unit tests
python3 -m tests.seleniumTestRegisterLogin  # selenium tests
```


## Group Members

| UWA ID | Name | GitHub Username |
|:------:|:----:|:---------------:|
| 23979227 | Rodney Paul |turbomilllenium |
| 24554031 | Shashank Sreeram |shashanksreeram13  |
| 24103209 | Hongfei Peng | fei817 |
| 24056458 | Xin Li | lilyjelleycat |

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## References

### Official Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Flask-Login Documentation](https://flask-login.readthedocs.io/)
- [Flask-WTF Documentation](https://flask-wtf.readthedocs.io/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)
- [Selenium with Python](https://selenium-python.readthedocs.io/)

### Learning Resources
- [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
- [Real Python Flask Tutorials](https://realpython.com/tutorials/flask/)
- [TestDriven.io Flask Testing Guide](https://testdriven.io/blog/flask-pytest-testing/)
- [Mozilla MDN Web Docs](https://developer.mozilla.org/en-US/)

### Tools and Services
- [GitHub](https://github.com/)
- [Python Package Index (PyPI)](https://pypi.org/)
- [pytest Documentation](https://docs.pytest.org/)

### AI Development Tools
- [GitHub Copilot](https://github.com/features/copilot) - AI pair programming tool used for code suggestions and completion
- [ChatGPT](https://chat.openai.com/) - OpenAI's language model used for code review, debugging, and documentation assistance

