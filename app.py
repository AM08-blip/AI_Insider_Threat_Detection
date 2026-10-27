from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

from models.user import db, User
from models.activity import Activity
import os

from flask import send_from_directory
from werkzeug.utils import secure_filename

from models.document import Document
from ai.predict_threat import predict_user_threat
from datetime import datetime
from io import BytesIO

from flask import send_file

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet
# =========================================================
# FLASK APP SETUP
# =========================================================

app = Flask(__name__)


# =========================================================
# CONFIGURATION
# =========================================================

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "insider-threat-project-secret-key"
# Document Upload Configuration
UPLOAD_FOLDER = "uploads"

ALLOWED_EXTENSIONS = {
    "pdf",
    "doc",
    "docx",
    "txt",
    "jpg",
    "jpeg",
    "png"
}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Maximum upload size = 10 MB
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

# =========================================================
# DATABASE INITIALIZATION
# =========================================================

db.init_app(app)


# =========================================================
# FLASK-LOGIN SETUP
# =========================================================

login_manager = LoginManager()
login_manager.init_app(app)

# If user tries to access protected page without login
login_manager.login_view = "home"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# =========================================================
# ACTIVITY LOGGING FUNCTION
# =========================================================

def log_activity(
    username,
    activity_type,
    details="",
    risk_level="Low",
    user_id=None
):

    activity = Activity(
        user_id=user_id,
        username=username,
        activity_type=activity_type,
        details=details,
        risk_level=risk_level
    )

    db.session.add(activity)
    db.session.commit()

# FILE UPLOAD HELPER FUNCTION
# =========================================================

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =========================================================
# LOGIN PAGE
# =========================================================

@app.route("/")
def home():

    # If already logged in, go directly to dashboard
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    return render_template("login.html")


# =========================================================
# LOGIN PROCESS
# =========================================================

@app.route("/login", methods=["POST"])
def login():

    username = request.form.get("username")
    password = request.form.get("password")

    # Find user
    user = User.query.filter_by(username=username).first()


    # -----------------------------------------------------
    # Successful Login
    # -----------------------------------------------------

    if user and check_password_hash(user.password, password):
        login_user(user)

        log_activity(
            username=user.username,
            user_id=user.id,
            activity_type="Login",
            details="User logged in successfully",
            risk_level="Low"
        )

        if user.role == "admin":
            return redirect(url_for("dashboard"))

        return redirect(url_for("employee_dashboard"))
    # -----------------------------------------------------
    # Failed Login
    # -----------------------------------------------------

    log_activity(
        username=username if username else "Unknown",
        activity_type="Failed Login",
        details="Invalid username or password",
        risk_level="Medium"
    )

    flash("Invalid username or password")

    return redirect(url_for("home"))


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/dashboard")
@login_required
def dashboard():

    if current_user.role != "admin":
        return redirect(
            url_for("employee_dashboard")
        )

    # -----------------------------------------
    # Recent activities
    # -----------------------------------------

    recent_activities = (
        Activity.query
        .order_by(Activity.timestamp.desc())
        .limit(10)
        .all()
    )

    # -----------------------------------------
    # Total users
    # -----------------------------------------

    total_users = User.query.count()


    # -----------------------------------------
    # AI Threat Analysis
    # -----------------------------------------

    employees = (
        User.query
        .filter_by(role="user")
        .all()
    )

    high_risk_count = 0
    suspicious_count = 0

    high_risk_users = []


    for employee in employees:

        result = predict_user_threat(
            employee.username
        )

        if result["risk_level"] in [
            "Medium",
            "High"
        ]:
            suspicious_count += 1

        if result["risk_level"] == "High":

            high_risk_count += 1

            high_risk_users.append(
                result
            )


    return render_template(
        "dashboard.html",

        recent_activities=recent_activities,

        total_users=total_users,

        suspicious_count=suspicious_count,

        high_risk_count=high_risk_count,

        high_risk_users=high_risk_users
    )

    # ----------------------------------------
    # Load Dashboard
    # ----------------------------------------

    return render_template(
        "dashboard.html",
        recent_activities=recent_activities,
        total_users=total_users,
        suspicious_count=suspicious_count,
        high_risk_count=high_risk_count
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
@login_required
def logout():

    # Save logout activity before logging user out
    log_activity(
        username=current_user.username,
        user_id=current_user.id,
        activity_type="Logout",
        details="User logged out successfully",
        risk_level="Low"
    )

    logout_user()

    return redirect(url_for("home"))

@app.route("/users")
@login_required
def users():

    # Only admins can access User Management
    if current_user.role != "admin":
        flash("Access denied.")
        return redirect(url_for("dashboard"))

    all_users = User.query.order_by(User.id.asc()).all()

    return render_template(
        "users.html",
        users=all_users
    )


@app.route("/users/add", methods=["POST"])
@login_required
def add_user():

    # Only admins can create accounts
    if current_user.role != "admin":
        flash("Access denied.")
        return redirect(url_for("dashboard"))

    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    role = request.form.get("role", "user")

    # Basic validation
    if not username or not email or not password:

        flash("Please fill in all fields.")

        return redirect(url_for("users"))

    # Only allow valid roles
    if role not in ["user", "admin"]:
        role = "user"

    # Check username
    existing_username = User.query.filter_by(
        username=username
    ).first()

    if existing_username:

        flash("Username already exists.")

        return redirect(url_for("users"))

    # Check email
    existing_email = User.query.filter_by(
        email=email
    ).first()

    if existing_email:

        flash("Email already exists.")

        return redirect(url_for("users"))

    # Create user
    new_user = User(
        username=username,
        email=email,
        password=generate_password_hash(password),
        role=role
    )

    db.session.add(new_user)
    db.session.commit()

    # Record admin action
    log_activity(
        username=current_user.username,
        user_id=current_user.id,
        activity_type="User Created",
        details=f"Created account: {username}",
        risk_level="Low"
    )

    flash("User created successfully.")

    return redirect(url_for("users"))

@app.route("/employee")
@login_required
def employee_dashboard():

    # Prevent admins from using employee portal
    if current_user.role != "user":
        return redirect(url_for("dashboard"))

    my_activities = (
        Activity.query
        .filter_by(user_id=current_user.id)
        .order_by(Activity.timestamp.desc())
        .limit(10)
        .all()
    )

    return render_template(
        "employee_dashboard.html",
        my_activities=my_activities
    )

@app.route("/documents")
@login_required
def documents():

    if current_user.role != "user":
        return redirect(url_for("dashboard"))

    all_documents = (
        Document.query
        .order_by(Document.uploaded_at.desc())
        .all()
    )

    return render_template(
        "documents.html",
        documents=all_documents
    )

@app.route("/documents/upload", methods=["POST"])
@login_required
def upload_document():

    if current_user.role != "user":
        return redirect(url_for("dashboard"))

    file = request.files.get("document")

    if not file or file.filename == "":
        flash("Please select a file.")
        return redirect(url_for("documents"))

    if not allowed_file(file.filename):
        flash("File type not allowed.")
        return redirect(url_for("documents"))

    original_name = file.filename

    safe_name = secure_filename(file.filename)

    unique_name = (
        f"{current_user.id}_"
        f"{int(__import__('time').time())}_"
        f"{safe_name}"
    )

    os.makedirs(
        app.config["UPLOAD_FOLDER"],
        exist_ok=True
    )

    file.save(
        os.path.join(
            app.config["UPLOAD_FOLDER"],
            unique_name
        )
    )

    new_document = Document(
        filename=unique_name,
        original_name=original_name,
        uploaded_by=current_user.id,
        uploader_username=current_user.username
    )

    db.session.add(new_document)
    db.session.commit()

    log_activity(
        username=current_user.username,
        user_id=current_user.id,
        activity_type="Document Upload",
        details=f"Uploaded: {original_name}",
        risk_level="Low"
    )

    flash("Document uploaded successfully.")

    return redirect(url_for("documents"))

@app.route("/documents/view/<int:document_id>")
@login_required
def view_document(document_id):

    if current_user.role != "user":
        return redirect(url_for("dashboard"))

    document = db.session.get(
        Document,
        document_id
    )

    if not document:
        flash("Document not found.")
        return redirect(url_for("documents"))

    log_activity(
        username=current_user.username,
        user_id=current_user.id,
        activity_type="Document View",
        details=f"Viewed: {document.original_name}",
        risk_level="Low"
    )

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        document.filename
    )
@app.route("/documents/download/<int:document_id>")
@login_required
def download_document(document_id):

    if current_user.role != "user":
        return redirect(url_for("dashboard"))

    document = db.session.get(
        Document,
        document_id
    )

    if not document:
        flash("Document not found.")
        return redirect(url_for("documents"))

    log_activity(
        username=current_user.username,
        user_id=current_user.id,
        activity_type="Document Download",
        details=f"Downloaded: {document.original_name}",
        risk_level="Low"
    )

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        document.filename,
        as_attachment=True,
        download_name=document.original_name
    )

@app.route("/activity-logs")
@login_required
def activity_logs():

    if current_user.role != "admin":
        return redirect(url_for("employee_dashboard"))

    activities = (
        Activity.query
        .order_by(Activity.timestamp.desc())
        .all()
    )

    return render_template(
        "activity_logs.html",
        activities=activities
    )


@app.route("/my-activity")
@login_required
def my_activity():

    if current_user.role != "user":
        return redirect(url_for("dashboard"))

    activities = (
        Activity.query
        .filter_by(user_id=current_user.id)
        .order_by(Activity.timestamp.desc())
        .all()
    )

    return render_template(
        "my_activity.html",
        activities=activities
    )

@app.route("/threats")
@login_required
def threats():

    if current_user.role != "admin":
        return redirect(
            url_for("employee_dashboard")
        )

    employees = (
        User.query
        .filter_by(role="user")
        .all()
    )

    threat_results = []

    for employee in employees:

        result = predict_user_threat(
            employee.username
        )

        threat_results.append(result)

    threat_results.sort(
        key=lambda item: item["risk_score"],
        reverse=True
    )

    return render_template(
        "threats.html",
        threat_results=threat_results
    )

@app.route("/reports")
@login_required
def reports():

    if current_user.role != "admin":
        return redirect(
            url_for("employee_dashboard")
        )

    employees = (
        User.query
        .filter_by(role="user")
        .all()
    )

    report_results = []

    for employee in employees:

        result = predict_user_threat(
            employee.username
        )

        recent_activity_count = (
            Activity.query
            .filter_by(user_id=employee.id)
            .count()
        )

        result["activity_count"] = (
            recent_activity_count
        )

        report_results.append(result)

    report_results.sort(
        key=lambda x: x["risk_score"],
        reverse=True
    )

    return render_template(
        "reports.html",
        report_results=report_results
    )

@app.route("/reports/download")
@login_required
def download_report():

    if current_user.role != "admin":
        return redirect(
            url_for("employee_dashboard")
        )

    employees = (
        User.query
        .filter_by(role="user")
        .all()
    )

    buffer = BytesIO()

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    elements = []

    title = Paragraph(
        "AI-Based Insider Threat Detection System",
        styles["Title"]
    )

    subtitle = Paragraph(
        "Security Analysis Report",
        styles["Heading2"]
    )

    generated_time = Paragraph(
        "Generated on: "
        + datetime.now().strftime(
            "%d-%m-%Y %I:%M %p"
        ),
        styles["Normal"]
    )

    elements.append(title)
    elements.append(Spacer(1, 10))
    elements.append(subtitle)
    elements.append(generated_time)
    elements.append(Spacer(1, 20))

    data = [
        [
            "Employee",
            "Risk Score",
            "Risk Level",
            "AI Result",
            "Reason"
        ]
    ]

    for employee in employees:

        result = predict_user_threat(
            employee.username
        )

        ai_result = (
            "Suspicious"
            if result["prediction"] == 1
            else "Normal"
        )

        reasons = ", ".join(
            result["reasons"]
        )

        data.append([
            employee.username,
            f'{result["risk_score"]}%',
            result["risk_level"],
            ai_result,
            reasons
        ])

    table = Table(
        data,
        colWidths=[
            80,
            65,
            65,
            70,
            190
        ]
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.black
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                6
            )
        ])
    )

    elements.append(table)

    pdf.build(elements)

    buffer.seek(0)

    log_activity(
        username=current_user.username,
        user_id=current_user.id,
        activity_type="Report Download",
        details="Downloaded AI threat analysis report",
        risk_level="Low"
    )

    filename = (
        "insider_threat_report_"
        + datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
        + ".pdf"
    )

    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf"
    )


# =========================================================
# APPLICATION START
# =========================================================

if __name__ == "__main__":

    with app.app_context():

        # Create database tables if they don't already exist
        db.create_all()

        # -----------------------------------------------
        # Create Default Admin Account
        # -----------------------------------------------

        admin = User.query.filter_by(
            username="admin"
        ).first()

        if not admin:

            admin = User(
                username="admin",
                email="admin@company.com",
                password=generate_password_hash(
                    "Admin@123"
                ),
                role="admin"
            )

            db.session.add(admin)
            db.session.commit()

            print(
                "Default admin created successfully."
            )

    

    # -----------------------------------------------
    # Start Flask Server
    # -----------------------------------------------

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )