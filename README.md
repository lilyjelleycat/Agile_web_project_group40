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
Cinebuff/
├── app/                    # Application package
│   ├── models/            # Database models
│   ├── routes/            # Route handlers
│   ├── templates/         # HTML templates
│   ├── static/            # Static files (CSS, JS, images)
│   └── __init__.py        # App initialization
├── tests/                 # Test suite
│   ├── test_admin.py      # Admin functionality tests
│   ├── test_routes.py     # Route testing
│   ├── test_selenium.py   # E2E testing
│   └── test.py           # Unit tests
├── instance/              # Instance-specific files
├── requirements.txt       # Project dependencies
└── run.py                # Application entry point
```

## Installation and Setup

1. Clone the repository:
```bash
git clone https://github.com/lilyjelleycat/Cinebuff.git
cd Cinebuff
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
python -m pytest test_routes.py    # Route tests
python -m pytest test_admin.py     # Admin tests
python -m pytest test_selenium.py  # E2E tests
```

3. Generate coverage report:
```bash
coverage run -m pytest
coverage report
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

## License
This project is licensed under the MIT License.