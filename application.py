from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from models import db, Admin, RestaurantTable, Booking

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///restaurant.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "admin_login"
login_manager.login_message = "Please log in as an administrator."
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

with app.app_context():
    db.create_all()

    if not Admin.query.first():
        db.session.add(Admin(
            username="admin",
            password=generate_password_hash("admin123")
        ))

    if not RestaurantTable.query.first():
        tables = [
            RestaurantTable(table_number=1, capacity=2),
            RestaurantTable(table_number=2, capacity=2),
            RestaurantTable(table_number=3, capacity=4),
            RestaurantTable(table_number=4, capacity=4),
            RestaurantTable(table_number=5, capacity=4),
            RestaurantTable(table_number=6, capacity=6),
            RestaurantTable(table_number=7, capacity=6),
            RestaurantTable(table_number=8, capacity=8),
        ]
        db.session.add_all(tables)
    db.session.commit()

@app.route("/")
def index():
    tables = RestaurantTable.query.order_by(RestaurantTable.table_number).all()
    return render_template("index.html", tables=tables)

@app.route("/booking/<int:table_id>", methods=["GET", "POST"])
def booking(table_id):
    table = RestaurantTable.query.get_or_404(table_id)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        booking_date = request.form.get("booking_date", "")
        booking_time = request.form.get("booking_time", "")
        guests_raw = request.form.get("guests", "")

        if not all([name, phone, email, booking_date, booking_time, guests_raw]):
            flash("Please fill in all required fields.", "error")
            return redirect(request.url)

        if not phone.isdigit() or len(phone) != 10:
            flash("Please enter a valid 10-digit phone number.", "error")
            return redirect(request.url)

        if "@" not in email or "." not in email.split("@")[-1]:
            flash("Please enter a valid email address.", "error")
            return redirect(request.url)

        try:
            guests = int(guests_raw)
        except ValueError:
            flash("Invalid number of guests.", "error")
            return redirect(request.url)

        if guests <= 0:
            flash("Number of guests must be greater than 0.", "error")
            return redirect(request.url)

        if guests > table.capacity:
            flash(f"Table {table.table_number} can accommodate only {table.capacity} guests.", "error")
            return redirect(request.url)

        try:
            selected_date = datetime.strptime(booking_date, "%Y-%m-%d").date()
            selected_time = datetime.strptime(booking_time, "%H:%M").time()
        except ValueError:
            flash("Invalid date or time.", "error")
            return redirect(request.url)

        if selected_date < date.today():
            flash("Booking date cannot be in the past.", "error")
            return redirect(request.url)

        existing = Booking.query.filter_by(
            table_id=table.id,
            booking_date=selected_date,
            booking_time=selected_time,
            status="Confirmed"
        ).first()

        if existing:
            flash("This table is already booked for the selected date and time.", "error")
            return redirect(request.url)

        new_booking = Booking(
            customer_name=name,
            phone=phone,
            email=email,
            booking_date=selected_date,
            booking_time=selected_time,
            guests=guests,
            table_id=table.id,
            status="Confirmed"
        )
        db.session.add(new_booking)
        db.session.commit()

        return redirect(url_for("confirmation", booking_id=new_booking.id))

    return render_template("booking.html", table=table, today=date.today().isoformat())

@app.route("/confirmation/<int:booking_id>")
def confirmation(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return render_template("confirmation.html", booking=booking)

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        admin = Admin.query.filter_by(username=username).first()

        if admin and check_password_hash(admin.password, password):
            login_user(admin)
            return redirect(url_for("admin_dashboard"))

        flash("Invalid username or password.", "error")

    return render_template("admin_login.html")

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    bookings = Booking.query.order_by(
        Booking.booking_date.desc(),
        Booking.booking_time.desc()
    ).all()
    tables = RestaurantTable.query.order_by(RestaurantTable.table_number).all()
    return render_template("admin_dashboard.html", bookings=bookings, tables=tables)

@app.route("/admin/cancel/<int:booking_id>", methods=["POST"])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.status == "Confirmed":
        booking.status = "Cancelled"
        db.session.commit()
        flash("Booking cancelled successfully.", "success")
    else:
        flash("This booking is already cancelled.", "error")

    return redirect(url_for("admin_dashboard"))

@app.route("/admin/logout")
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for("admin_login"))

if __name__ == "__main__":
    app.run(debug=True)
