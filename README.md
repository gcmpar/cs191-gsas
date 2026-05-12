# UP DCS: Graduate Student Admission System (Continuation)

**By Group WIP**
- Jerwyn Angchua
- Lara Carrillo
- Glenn Paragas

**Client:** Dr. Richelle Ann Juayong

📖 [Project Blog](https://sites.google.com/up.edu.ph/cs191-blog/home?authuser=1)

---

*Software Engineering I — CS 192 TBC/HQR1*
*Instructor: Dr. Ligaya Leah Figueroa*

---

## Overview / Summary

The **Graduate Student Admission System (GSAS)** is a Django-based web application built for the UP Department of Computer Science (DCS) to streamline the processing and management of graduate student applications. It supports three DCS graduate programs: **PhD CS**, **MS CS**, and **MS Bioinfo**.

The system provides tools to:
- Manage applicant profiles and their application records
- Track application status (Processing / Accepted / Rejected)
- Record and review transcript entries (per course, per semester, with grades)
- Scan and import Transcript of Records (TOR) PDFs using OCR
- Perform bulk import of applications from Excel spreadsheets
- Manage the course catalog, programs, prerequisite rules, and equivalence mappings
- Create reusable prerequisite mappings that can be applied across multiple applications

This is a **continuation** project built on top of lessons learned from a previous version, with a fully restructured Django app architecture for maintainability.

---

## Prerequisites

Before installing, make sure the following are available on your system:

### System Requirements
- **Python 3.11+** — [python.org](https://www.python.org/downloads/)
- **MySQL 8.0+** — [dev.mysql.com](https://dev.mysql.com/downloads/mysql/)
- **Tesseract OCR** — Required for the TOR PDF scanning feature
  - Windows: Download installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
  - After installing, add Tesseract to your system `PATH`, or set the path in `pytesseract.pytesseract.tesseract_cmd` inside your environment
- **Poppler** — Required by `pdf2image` to convert PDFs to images
  - Windows: Download from [poppler releases](https://github.com/oschwartz10612/poppler-windows/releases/) and add the `bin/` folder to your `PATH`

### Python Package Dependencies

All Python packages are listed in `requirements.txt`. Key dependencies include:

| Package | Purpose |
|---|---|
| `Django==5.2.7` | Web framework |
| `mysqlclient` | MySQL database connector |
| `django-bootstrap5` | Bootstrap 5 UI components |
| `django-select2` | Searchable dropdowns |
| `openpyxl` | Excel file parsing (batch import) |
| `pdf2image` | Convert PDF pages to images (OCR) |
| `pytesseract` | OCR engine wrapper (TOR scanning) |
| `pillow` | Image processing for OCR |
| `numpy` | Numerical operations |
| `scikit-learn` | ML utilities (OCR pipeline) |

---

## Installation Guide

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd CS191-192
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up the MySQL Database

Open your MySQL client (e.g., MySQL Workbench or the `mysql` CLI) and create the database:

```sql
CREATE DATABASE gsas_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

The default database configuration in `gsas/settings.py` is:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gsas_demo',
        'USER': 'root',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

> **Note:** Update `USER` and `PASSWORD` to match your local MySQL credentials.

### 5. Apply Database Migrations

```bash
python manage.py migrate
```

### 6. Create a Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

Follow the prompts to set a username and password.

### 7. Run the Development Server

```bash
python manage.py runserver
```

The app will be available at **http://127.0.0.1:8000/**.

> Navigate to `http://127.0.0.1:8000/accounts/login/` to log in.

---

## Tutorial

### Navigating the System

After logging in, the navigation bar gives access to the main modules:

| Section | URL Prefix | Description |
|---|---|---|
| Applicants | `/applicants/` | View and manage applicant profiles |
| Applications | `/applications/` | View, add, and edit application records |
| Schools | `/schools/` | Manage schools in the course catalog |
| Programs | `/programs/` | Manage graduate programs |
| Courses | `/courses/` | Manage the course catalog, prerequisites, and equivalences |
| Admin Panel | `/admin/` | Django admin for power users |

---

### Managing Applicants

- **Search applicants** at `/applicants/` — filter by name or status (Applying, Enrolled, Rejected, Deferred).
- **Add an applicant** at `/applicants/add/` — fill in name, email, contact number, and status.
- **Edit/view** an applicant by clicking their entry in the list.

---

### Managing Applications

#### Searching Applications

Go to `/applications/` to search all application records. You can:
- Search by application number, program, study load, or notes
- Filter by application status (Processing, Accepted, Rejected)
- Results are paginated (15 per page)

#### Adding an Application

Go to `/applications/add/` and fill in:
- The applicant (select from existing applicants)
- Application number, degree program (PhD CS / MS CS / MS Bioinfo), study load, date applied, status, folder link, and optional notes

#### Editing an Application

On the application edit page (`/applications/<id>/edit/`), you can:
- Update all application fields
- Manage the **transcript** — add/edit/remove course entries with academic year, semester, and grade
- Use the **OCR scanner** to auto-import courses from a TOR PDF
- Manage **prerequisite mappings** for the application

#### Viewing an Application

The view page (`/applications/<id>/`) shows a read-only summary of:
- Applicant information
- Application details (program, status, study load, folder link, notes)
- Full transcript with course codes, grades, and any equivalences detected
- Applied prerequisite mappings

---

### Batch Import (Excel)

The batch import feature allows you to upload an Excel spreadsheet of applicants and create multiple application records at once.

#### Supported Excel Columns

The spreadsheet must contain these column headers (case-insensitive):

| Column | Description |
|---|---|
| `Application No.` | Application reference number |
| `Last Name` | Applicant last name |
| `First Name` | Applicant first name |
| `Middle Name` | Applicant middle name |
| `Email Address` | Contact email |
| `Contact Number` | Phone number |
| `Program` | Degree program (auto-detected: PhD, MS, Bioinfo) |
| `Applying as Full-Time or Part-Time` | Study load |
| `Application Status` | Status (Accepted / Rejected / else → Processing) |
| `Link to Applicant Main Folder` | Google Drive or folder link |
| `NGSE Remarks` | Notes / remarks field |

#### Batch Import Workflow

1. Navigate to **Applications → Batch Import** (`/applications/batch-imports/upload/`)
2. Upload your Excel (`.xlsx`) file
3. On the confirmation page, review each row and assign each applicant to an existing applicant record (or skip rows)
4. Click **Confirm Import** — all matched rows are saved under a single `BatchImport` record
5. View past imports at `/applications/batch-imports/`

---

### OCR TOR Scanning

This feature scans a student's Transcript of Records (TOR) PDF and extracts course data automatically.

#### Requirements
- Tesseract OCR must be installed and accessible in `PATH`
- Poppler must be installed and accessible in `PATH`

#### Workflow

1. Open an application's edit page
2. In the **Scan TOR** section, upload a PDF of the student's TOR
3. The system converts each PDF page to an image, runs OCR, and extracts course lines
4. You are redirected to the **OCR Preview page** (`/applications/<id>/ocr-preview/`):
   - Each extracted row shows: course code (as read), description, grade, units
   - The system attempts to **auto-match** the scanned course code to an existing course in the database
   - You can manually select a different course from the dropdown for each row
   - Check/uncheck rows to include or exclude them from import
5. Click **Save Selected** — checked rows are saved as `ApplicationTranscript` entries
   - Duplicate entries (same application + course) are automatically skipped

---

### Managing the Course Catalog

#### Courses

- **List:** `/courses/` — view all courses with their associated programs
- **Add:** `/courses/add/` — enter course code, name, units, description, and assign to programs
- **Edit:** `/courses/<id>/edit/`
- **View:** `/courses/<id>/` — shows course details, its prerequisite structure, and equivalence groups it belongs to

#### Equivalence Mappings

An **Equivalence Map** defines that a group of "source" courses together satisfies one "target" course. These are managed from the **Course View page**.

To create an equivalence mapping:
1. Go to the target course's view page (`/courses/<id>/`)
2. In the Equivalence Mapping section, select the source courses that map to this course
3. Click **Save Mapping**
4. Duplicate mappings (same source set + same target) are blocked automatically

#### Prerequisite Mappings (per Application)

A **Prerequisite Mapping** is a reusable template that declares: *"these source courses from the transcript satisfy this prerequisite course."* It is linked to a specific application but shared globally — saving the same logical mapping twice is prevented.

To create a prerequisite mapping on an application:
1. Go to the application's edit page
2. In the **Prerequisite Mappings** section:
   - Select one or more **source courses** from the application's transcript
   - Select one **target prerequisite course**
   - Click **Save New Mapping** — the mapping is created (or an existing identical one is linked)
3. To load a previously saved mapping, use the **Load Existing Mapping** dropdown and click **Load**
4. To remove a mapping from this application, click **Remove** next to it (the mapping template itself is preserved)

---

### Managing Schools and Programs

- **Schools** (`/schools/`): Add/edit/delete schools that offer programs. Each course belongs to programs at schools.
- **Programs** (`/programs/`): Add/edit/delete programs under a school. Programs group courses and are referenced by applications.

---

## Troubleshooting

### `mysqlclient` installation fails on Windows

Install the Microsoft C++ Build Tools first, or use the pre-compiled wheel:
```bash
pip install mysqlclient
```
If that fails, download the appropriate `.whl` from [Christoph Gohlke's site](https://www.lfd.uci.edu/~gohlke/pythonlibs/) and install with `pip install <filename>.whl`.

---

### `pdf2image` / Poppler errors

**Error:** `Unable to get page count. Is poppler installed and in PATH?`

**Fix:** Download Poppler for Windows and add the `bin/` directory to your system `PATH` environment variable. Restart your terminal after doing so.

---

### `pytesseract` / Tesseract errors

**Error:** `tesseract is not installed or it's not in your PATH`

**Fix:**
1. Install Tesseract from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
2. Add the Tesseract install directory (e.g., `C:\Program Files\Tesseract-OCR\`) to your `PATH`
3. Alternatively, set it explicitly in code or in `settings.py`:
   ```python
   import pytesseract
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

---

### Migration errors or `Table already exists`

If you get migration errors from a previous database state:
```bash
python manage.py migrate --fake-initial
```
Or drop and recreate the database and re-run `python manage.py migrate`.

---

### `django_select2` widget not loading

Make sure your `urlpatterns` in `gsas/urls.py` includes:
```python
path("select2/", include("django_select2.urls")),
```
This is already present by default. If autocomplete dropdowns appear blank, check that the dev server is running and that `django_select2` is in `INSTALLED_APPS`.

---

### Login redirect loop

By default, `LoginRequiredMiddleware` is active. Make sure the `accounts` URLs are registered and that `LOGIN_URL` in `settings.py` points to the correct login view. The login page is at `/accounts/login/`.

---

### OCR produces garbage or empty results

- Ensure the TOR PDF is high-quality (scan at ≥ 300 DPI recommended)
- Heavily handwritten or non-standard formatted TORs may not parse well
- Check the server logs — the OCR module logs per-page errors at `ERROR` level
- You can still manually add transcript courses on the edit page without using OCR
