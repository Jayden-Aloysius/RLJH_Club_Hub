# Rocky Lake Junior High — Club Hub

A Python/Flask club-hub website for Rocky Lake Junior High.

## Features

- Public home page listing all published clubs
- Individual club pages
- Founder login accounts
- Founders can customize:
  - name and description
  - meeting information
  - logo/banner image URLs
  - accent colour
  - custom CSS
  - custom HTML section
- Admin dashboard
- Admin can create/delete clubs
- Admin can create/delete founder and admin accounts
- Admin can edit any club
- SQLite database, so no separate database server is needed for the starter project

## Run it locally

1. Install Python 3.11+.
2. Open a terminal in this folder.
3. Run:

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

macOS/Linux/Chromebook Linux:
```bash
source .venv/bin/activate
```

4. Install packages:

```bash
pip install -r requirements.txt
```

5. Start the site:

```bash
python app.py
```

6. Open http://127.0.0.1:5000

### First admin login

Username: `admin`

Default development password: `ChangeMe123!`

**Change this immediately for a real deployment.** You can set `ADMIN_PASSWORD` before first startup to choose the initial admin password.

Example:

```bash
ADMIN_PASSWORD="your-long-random-password" python app.py
```

Also set a strong `SECRET_KEY` in production.

## Important production notes

This is a starter implementation. Before using it for an actual school community:

- Put it behind HTTPS.
- Use a strong secret key.
- Replace the development admin password.
- Add CSRF protection.
- Add school-approved authentication if the school requires it.
- Add moderation/reporting controls.
- Avoid publishing students' personal contact information.
- Consider storing uploaded images on a proper object-storage service instead of accepting arbitrary image URLs.
- Disable Flask debug mode in production.
- Have a school administrator review the privacy and moderation design.

## Suggested next upgrades

- Google/Microsoft school login
- Club membership/join buttons
- announcements and events
- calendar integration
- image uploads
- drag-and-drop page builder
- admin moderation queue
- searchable clubs
- club categories
- school announcements
- audit log
- email notifications
