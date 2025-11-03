# JHALCA Flask + MySQL Project Scaffold

This scaffold creates a Flask web application connected to MySQL using SQLAlchemy and PyMySQL.
It includes a dark sidebar with grouped menus, a top bar with login and user photo, and a reusable 3-tab form layout
(Form / Buscar / Reportes).

## Quick start

1. Create a Python virtualenv and activate it.
2. Install dependencies. Make sure you have `PyMySQL` installed (`pip install PyMySQL`), then install the rest.
   ```
   pip install -r requirements.txt
   ```
3. Update `config.py` with your MySQL connection details.
4. Initialize the database (run the `db_init.sql` script on your MySQL server, or use the included Python script `python init_db.py` to create tables).
5. Run the app:
   ```
   flask run
   ```
   or
   ```
   python app.py
   ```

## Notes
- Authentication uses Flask-Login; role-based checks are demonstrated in `decorators.py`.
- UI uses Bootstrap 5, with a collapsible grouped sidebar.
- Many forms are scaffolded; copy `templates/form_page.html` and adjust fields as needed.
