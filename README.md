# Restaurant Table Booking System

A Flask-based restaurant table booking application with:
- Table display
- Customer booking form
- Validation
- Booking confirmation
- Protected admin login
- Admin-only cancellation
- Cancellation phone notice

## Run

1. Install Python 3.10+.
2. Open this folder in VS Code.
3. Open Terminal.
4. Run:

   pip install -r requirements.txt

5. Start the application:

   python application.py

6. Open:

   http://127.0.0.1:5000

## Admin

Open:

   http://127.0.0.1:5000/admin

Default development credentials:

Username: admin
Password: admin123

Change the password and SECRET_KEY before production use.

## Database

A SQLite database named restaurant.db is created automatically on first run.
