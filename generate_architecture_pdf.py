"""Generate a brief System Architecture & Technology Summary PDF."""

from fpdf import FPDF


class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(0, 78, 154)
        self.cell(0, 8, "Plan International Kenya  |  COSME Project", align="R")
        self.ln(4)
        self.set_draw_color(0, 78, 154)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(0, 78, 154)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(0, 78, 154)
        self.line(10, self.get_y(), 80, self.get_y())
        self.ln(3)

    def sub_title(self, title):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(40, 40, 40)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def bullet(self, text, indent=15):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(50, 50, 50)
        x = self.get_x()
        self.set_x(x + indent)
        self.cell(5, 6, "-")
        self.multi_cell(0, 6, text)
        self.ln(1)

    def table_row(self, col1, col2, bold=False):
        style = "B" if bold else ""
        self.set_font("Helvetica", style, 10)
        if bold:
            self.set_fill_color(0, 78, 154)
            self.set_text_color(255, 255, 255)
        else:
            self.set_fill_color(245, 247, 250)
            self.set_text_color(50, 50, 50)
        self.cell(60, 8, col1, border=1, fill=True)
        self.cell(0, 8, col2, border=1, fill=not bold, new_x="LMARGIN", new_y="NEXT")


pdf = PDF()
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=20)
pdf.add_page()

# ── Title ────────────────────────────────────────────────────────────────────
pdf.set_font("Helvetica", "B", 20)
pdf.set_text_color(0, 78, 154)
pdf.cell(0, 12, "Vehicle Request Tracker", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 12)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 8, "System Architecture & Technology Summary", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(8)

# ── 1. System Overview ──────────────────────────────────────────────────────
pdf.section_title("1. System Overview")
pdf.body_text(
    "The Vehicle Request Tracker (VRT) is a web-based application built for "
    "Plan International Kenya's COSME Project. It manages vehicle booking "
    "requests, trip tracking, maintenance scheduling, fuel cost reporting, "
    "and user access control. The system is deployed as a Progressive Web App "
    "(PWA) on PythonAnywhere with a server-side rendered architecture."
)

# ── 2. Architecture ─────────────────────────────────────────────────────────
pdf.section_title("2. Architecture Pattern")
pdf.body_text(
    "The application follows a Monolithic MVC (Model-View-Controller) "
    "architecture pattern:"
)
pdf.bullet("Model Layer  -  SQLAlchemy ORM models (models.py)")
pdf.bullet("View Layer   -  Jinja2 HTML templates (server-side rendering)")
pdf.bullet("Controller   -  Flask route handlers (app.py)")
pdf.bullet("Database     -  SQLite (development) / PostgreSQL (production)")
pdf.ln(2)

pdf.sub_title("High-Level Flow")
pdf.body_text(
    "Browser  -->  Flask (WSGI)  -->  Route Handler  -->  SQLAlchemy ORM  -->  Database\n"
    "                                      |                                         \n"
    "                                Jinja2 Templates  -->  HTML Response  -->  Browser"
)

# ── 3. Languages & Technologies ─────────────────────────────────────────────
pdf.section_title("3. Languages & Technologies")

pdf.sub_title("Back-End")
pdf.table_row("Technology", "Purpose", bold=True)
pdf.table_row("Python 3.13", "Primary programming language")
pdf.table_row("Flask 3.x", "Web framework (routing, sessions, CSRF)")
pdf.table_row("SQLAlchemy / Flask-SQLAlchemy", "ORM & database abstraction")
pdf.table_row("Flask-Login", "User authentication & session management")
pdf.table_row("Flask-Mail", "Email notifications (SMTP)")
pdf.table_row("Flask-WTF", "CSRF protection")
pdf.table_row("Flask-Limiter", "Rate limiting (brute-force prevention)")
pdf.table_row("openpyxl", "Excel (.xlsx) report generation")
pdf.table_row("Gunicorn", "Production WSGI HTTP server")
pdf.ln(4)

pdf.sub_title("Front-End")
pdf.table_row("Technology", "Purpose", bold=True)
pdf.table_row("HTML5 / Jinja2", "Server-side rendered templates")
pdf.table_row("CSS3", "Custom styles (style.css)")
pdf.table_row("JavaScript (ES5)", "Client-side validation & interactivity")
pdf.table_row("Bootstrap 5.3", "Responsive UI framework (CDN)")
pdf.table_row("Bootstrap Icons", "Icon library (CDN)")
pdf.table_row("FullCalendar.js", "Interactive booking calendar view")
pdf.table_row("Service Worker", "Offline support & PWA caching")
pdf.ln(4)

pdf.sub_title("Database")
pdf.table_row("Technology", "Purpose", bold=True)
pdf.table_row("SQLite", "Development & lightweight deployment")
pdf.table_row("PostgreSQL", "Production database (PythonAnywhere)")
pdf.ln(4)

pdf.sub_title("Infrastructure & Deployment")
pdf.table_row("Technology", "Purpose", bold=True)
pdf.table_row("PythonAnywhere", "Cloud hosting platform")
pdf.table_row("Git / GitHub", "Version control & code repository")
pdf.table_row("PWA (manifest + SW)", "Installable app, offline access")
pdf.table_row("WSGI (wsgi.py)", "Production entry point")

# ── 4. Key Modules ──────────────────────────────────────────────────────────
pdf.add_page()
pdf.section_title("4. Application Modules")

modules = [
    ("Authentication & Users", "Login, registration, password reset, role-based access (admin/driver/requester)"),
    ("Vehicle Management", "Add, edit, archive vehicles with status tracking (available/in_use/maintenance)"),
    ("Booking Management", "Create, approve, cancel booking requests with conflict detection"),
    ("Trip Tracking", "Record actual trip start/end, odometer readings, fuel usage"),
    ("Maintenance Scheduling", "Schedule, track, and complete vehicle maintenance records"),
    ("Reports & Analytics", "Vehicle trip reports, budget reports by project code, Excel export"),
    ("Calendar View", "Interactive calendar showing pending/approved bookings (FullCalendar.js)"),
    ("Audit Logging", "Tracks all create/edit/delete/approve actions with user and timestamp"),
    ("Page Analytics", "Records page views, response times, device types, and browser info"),
]

for title, desc in modules:
    pdf.sub_title(title)
    pdf.body_text(desc)

# ── 5. Security Features ────────────────────────────────────────────────────
pdf.section_title("5. Security Features")
pdf.bullet("CSRF protection on all POST forms (Flask-WTF)")
pdf.bullet("Password hashing with Werkzeug (PBKDF2-SHA256)")
pdf.bullet("Rate limiting on login & registration endpoints")
pdf.bullet("Session timeout with automatic logout warning")
pdf.bullet("Role-based access control (admin, driver, requester)")
pdf.bullet("Soft-delete protection (records archived, not permanently removed)")
pdf.bullet("Secure cookie settings (HttpOnly, SameSite=Lax)")

# ── 6. Data Model ───────────────────────────────────────────────────────────
pdf.ln(4)
pdf.section_title("6. Data Models")
pdf.body_text("The system uses 7 database tables:")
models_list = [
    ("Users", "Authentication, roles, profile info"),
    ("Vehicles", "Registration, make/model, status"),
    ("Bookings", "Requests with planned dates, routes, purpose, status"),
    ("Trips", "Actual start/end times, odometer, fuel data"),
    ("MaintenanceRecords", "Scheduled/completed maintenance with cost"),
    ("AuditLogs", "Action history for accountability"),
    ("PageViews", "Usage analytics and performance metrics"),
]
pdf.table_row("Table", "Description", bold=True)
for name, desc in models_list:
    pdf.table_row(name, desc)

# ── Save ─────────────────────────────────────────────────────────────────────
output_path = r"c:\Users\Bmuiruri.PLANKE-KILIFI\Desktop\Benard\My Project\My work\trackers\VRT_System_Architecture.pdf"
pdf.output(output_path)
print(f"PDF saved to: {output_path}")
