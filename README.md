# 🤖 Persist Automation Bot – Django DRF Backend

A Django REST Framework-based API backend built to automate task and productivity tracking for platforms like Hubstaff. Designed to integrate with bots (e.g., Telegram) or clients that require real-time interaction with user workflows like login, daily updates, task management, and more.

---
# Demo Videos
---

https://github.com/user-attachments/assets/cc786b4e-aa99-49e8-9e8c-7bae3d3204d9


---

## 🚀 Features

- 🔐 **Login**: Automate login to platforms like Hubstaff.
- ✅ **User Verification**: Check if a Telegram user is authorized.
- 📆 **Daily Update**: Submit daily progress or work summaries.
- 📋 **Task Management**: Add, list, and track assigned tasks.
- 📝 **Feedback**: Submit structured feedback via API.
- 📊 **Stats**: View performance or work-related statistics.
- 🌴 **Leave Status**: Record leave or unavailability.

---

## 📂 API Endpoints

| Endpoint             | Method | Description                         |
|----------------------|--------|-------------------------------------|
| `/check-user/`       | POST   | Verify if a Telegram user exists    |
| `/hubstaff/login/`   | POST   | Perform login to Hubstaff           |
| `/dailyupdate/`      | POST   | Submit daily work update            |
| `/leave/`            | POST   | Notify leave status                 |
| `/feedback/`         | POST   | Submit feedback                     |
| `/listtask/`         | GET    | Retrieve task list                  |
| `/addtask/`          | POST   | Add a new task                      |
| `/stats/`            | GET    | View user stats or analytics        |

---

## 🧠 Tech Stack

- **Python 3.10+**
- **Django 4.x**
- **Django REST Framework**
- **PostgreSQL / SQLite** (configurable)
- **Telegram Bot** (expected frontend client)

---

## ⚙️ Setup Instructions

1. **Clone the Repository**

```bash
git clone https://github.com/manishgk9/persist_automation_bot.git
cd persist_automation_bot
````

2. **Create Virtual Environment**

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

4. **Set Environment Variables**

Create a `.env` file:

```env
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=*
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

5. **Apply Migrations**

```bash
python manage.py migrate
```

6. **Run the Server**

```bash
python manage.py runserver
```

---

## 📦 Example Request (POST /dailyupdate/)

```http
POST /dailyupdate/
Content-Type: application/json

{
  "telegram_id": 123456789,
  "update": "Completed UI module and wrote test cases."
}
```

---

## 🔐 Authentication

* Most endpoints are **open** for bot access using `telegram_id` as identity.
* Can be extended with `TokenAuthentication` or OAuth if required.

---

## 🧪 Future Enhancements

* [ ] JWT Authentication
* [ ] Admin dashboard with task analytics
* [ ] Email or Telegram alerts on task status
* [ ] Support for multiple platforms (e.g., Asana, Trello)

---

## 🙋‍♂️ Author

**Manish Yadav**
[GitHub](https://github.com/manishgk9)

---

## 🛡️ License

This project is licensed under the MIT License.

```
