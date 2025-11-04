# Movies-Recommendation-System


# Project Setup and Run Instructions

This guide will help you set up the project locally, configure environment variables, apply migrations, create a superuser, and run the development server. Follow each step carefully.

---

## 1️⃣ Clone the Repository

First, clone the project repository from GitHub to your local machine:


## 2️⃣ Create and Activate Virtual Environment

### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows (CMD)

```cmd
python -m venv venv
venv\Scripts\activate
```

> Your terminal prompt should now show `(venv)` indicating the virtual environment is active.


## 3️⃣ Install Dependencies

Install all required Python packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

> Make sure the virtual environment is active before running this command. This installs Django and any other libraries your project needs.

---

## 4️⃣ Configure Environment Variables

Create a `.env` file in the project root:

```env
TMDB_API_KEY= YOUR API KEY HERE
```
* `TMDB_API_KEY` is your TMDB API key for API access.


---

## 5️⃣ Apply Database Migrations

Set up the database schema:

```bash
python manage.py makemigrations
python manage.py migrate
```


---

## 6️⃣ Create a Superuser

Create an admin account to access Django’s admin panel:

```bash
python manage.py createsuperuser
```

---

## 7️⃣ Run the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

---

## 8️⃣ Notes & Tips

* Always **activate the virtual environment** before running any Python commands.
* Keep your `.env` file **private** — do not commit it to GitHub.
* Make sure `__pycache__/` and `migrations/` folders are listed in `.gitignore` to avoid unnecessary files in the repository. Example `.gitignore` entries:

```
__pycache__/
*.pyc
*/migrations/
.env
```

* If `requirements.txt` is updated, run `pip install -r requirements.txt` again.
* For any issues, check if the virtual environment is active and Python version matches the project requirements.

---

**🎉 You're all set! Happy coding!**
