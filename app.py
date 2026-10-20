import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-change-this-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///rocky_lake_clubs.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="founder")
    club_id = db.Column(db.Integer, db.ForeignKey("club.id"), nullable=True)
    club = db.relationship("Club", backref="founders", foreign_keys=[club_id])

class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    short_description = db.Column(db.String(300), default="")
    description = db.Column(db.Text, default="")
    meeting_day = db.Column(db.String(80), default="")
    meeting_time = db.Column(db.String(80), default="")
    location = db.Column(db.String(120), default="")
    contact = db.Column(db.String(200), default="")
    logo_url = db.Column(db.String(500), default="")
    banner_url = db.Column(db.String(500), default="")
    accent = db.Column(db.String(20), default="#4f46e5")
    published = db.Column(db.Boolean, default=True)
    custom_css = db.Column(db.Text, default="")
    custom_html = db.Column(db.Text, default="")

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login", next=request.path))
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            abort(403)
        return fn(*args, **kwargs)
    return wrapper

@app.context_processor
def inject_user():
    return {"current_user": session.get("username"), "role": session.get("role")}

@app.route("/")
def index():
    clubs = Club.query.filter_by(published=True).order_by(Club.name.asc()).all()
    return render_template("index.html", clubs=clubs)

@app.route("/club/<slug>")
def club_page(slug):
    club = Club.query.filter_by(slug=slug, published=True).first_or_404()
    return render_template("club.html", club=club)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role
            session["club_id"] = user.club_id
            return redirect(request.args.get("next") or url_for("dashboard"))
        flash("Incorrect username or password.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    if session["role"] == "admin":
        return redirect(url_for("admin"))
    club = Club.query.get(session.get("club_id"))
    return render_template("dashboard.html", club=club)

@app.route("/dashboard/club", methods=["GET", "POST"])
@login_required
def edit_club():
    if session["role"] == "admin":
        club_id = request.args.get("club_id", type=int)
        club = Club.query.get_or_404(club_id)
    else:
        club = Club.query.get_or_404(session.get("club_id"))
    if request.method == "POST":
        club.name = request.form["name"].strip()
        club.slug = request.form["slug"].strip().lower().replace(" ", "-")
        club.short_description = request.form.get("short_description", "")
        club.description = request.form.get("description", "")
        club.meeting_day = request.form.get("meeting_day", "")
        club.meeting_time = request.form.get("meeting_time", "")
        club.location = request.form.get("location", "")
        club.contact = request.form.get("contact", "")
        club.logo_url = request.form.get("logo_url", "")
        club.banner_url = request.form.get("banner_url", "")
        club.accent = request.form.get("accent", "#4f46e5")
        club.custom_css = request.form.get("custom_css", "")
        club.custom_html = request.form.get("custom_html", "")
        if session["role"] == "admin":
            club.published = "published" in request.form
        db.session.commit()
        flash("Club page saved.", "success")
        return redirect(url_for("dashboard") if session["role"] != "admin" else url_for("admin"))
    return render_template("edit_club.html", club=club)

@app.route("/admin")
@login_required
@admin_required
def admin():
    clubs = Club.query.order_by(Club.name.asc()).all()
    users = User.query.order_by(User.username.asc()).all()
    return render_template("admin.html", clubs=clubs, users=users)

@app.route("/admin/club/new", methods=["GET", "POST"])
@login_required
@admin_required
def new_club():
    if request.method == "POST":
        name = request.form["name"].strip()
        slug = request.form["slug"].strip().lower().replace(" ", "-")
        if Club.query.filter_by(slug=slug).first():
            flash("That URL slug is already used.", "error")
            return render_template("new_club.html")
        club = Club(name=name, slug=slug, short_description=request.form.get("short_description",""))
        db.session.add(club)
        db.session.commit()
        flash("Club created. You can now create a founder account for it.", "success")
        return redirect(url_for("admin"))
    return render_template("new_club.html")

@app.route("/admin/club/<int:club_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_club(club_id):
    club = Club.query.get_or_404(club_id)
    for user in User.query.filter_by(club_id=club.id).all():
        db.session.delete(user)
    db.session.delete(club)
    db.session.commit()
    flash("Club deleted.", "success")
    return redirect(url_for("admin"))

@app.route("/admin/user/new", methods=["GET", "POST"])
@login_required
@admin_required
def new_user():
    clubs = Club.query.order_by(Club.name.asc()).all()
    if request.method == "POST":
        username = request.form["username"].strip()
        if User.query.filter_by(username=username).first():
            flash("That username already exists.", "error")
            return render_template("new_user.html", clubs=clubs)
        role = request.form["role"]
        club_id = request.form.get("club_id", type=int) if role == "founder" else None
        user = User(username=username, password_hash=generate_password_hash(request.form["password"]),
                    role=role, club_id=club_id)
        db.session.add(user)
        db.session.commit()
        flash("User account created.", "success")
        return redirect(url_for("admin"))
    return render_template("new_user.html", clubs=clubs)

@app.route("/admin/user/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == session["user_id"]:
        flash("You cannot delete the account you are currently using.", "error")
    else:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted.", "success")
    return redirect(url_for("admin"))

def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username="admin").first():
            password = os.environ.get("ADMIN_PASSWORD", "ChangeMe123!")
            admin = User(username="admin", password_hash=generate_password_hash(password), role="admin")
            db.session.add(admin)
            db.session.commit()
        if Club.query.count() == 0:
            examples = [
                Club(name="Robotics Club", slug="robotics", short_description="Build, code, experiment, and compete."),
                Club(name="Art Club", slug="art", short_description="Create, share ideas, and explore different art styles."),
                Club(name="Game Club", slug="game-club", short_description="Board games, strategy games, and friendly challenges.")
            ]
            db.session.add_all(examples)
            db.session.commit()

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
