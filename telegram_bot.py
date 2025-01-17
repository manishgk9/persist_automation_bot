import telebot
from telebot import types
import requests
from credentials import TELEGRAM_BOT_TOKEN
from datetime import datetime, timedelta

API_BASE_URL = "http://localhost:8000"
TELEGRAM_BOT_TOKEN = TELEGRAM_BOT_TOKEN
user_states = {}
waiting_for_feedback = {}
WAITING_FOR_EMAIL = 'waiting_for_email'
WAITING_FOR_PASSWORD = 'waiting_for_password'
LEAVE_TYPES = [
    ('Sick Leave', 'sick'),
    ('Vacation Leave', 'vacation'),
    ('Personal Leave', 'personal')
]
task_name = None
start_date = None
end_date = None
telegram_user_id = None

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 Welcome to persist Bot!\n\n"
                 "🔹 Need assistance? Simply type /help to see all available commands.")


@bot.message_handler(commands=['help'])
def help(message):
    bot.reply_to(message, "👋 Welcome to persist Bot!\n\n"
                 "Here are the available commands:\n"
                 "/start - Displays the start message.\n"
                 "/dailyupdate - Submit your daily update.\n"
                 "/leave - Mark yourself as on leave.\n"
                 "/help - Display this help message.\n"
                 "/hubstaff - To link Telegram with Hubstaff.\n"
                 "/addtask - Add new task on Hubstaff.\n"
                 "/listtask - List all the Hubstaff active tasks.\n"
                 "/stats - Displays the Hubstaff stats.\n"
                 "/feedback - Used to give feedback.")


@bot.message_handler(commands=['leave'])
def handle_leave(message):
    telegram_user_id = message.chat.id
    response = requests.post(
        url=f'{API_BASE_URL}/check-user/', json={'telegram_user_id': str(telegram_user_id)})

    if response.status_code == 200:
        parsed_data = response.json()
        if not parsed_data.get('exists', False):
            bot.send_message(
                telegram_user_id, "Oops! 🚫 The specified user hasn't linked their Telegram with Hubstaff yet. Ask them to use the /hubstaff command.")
            return
    markup = types.InlineKeyboardMarkup(row_width=2)
    for leave_name, leave_value in LEAVE_TYPES:

        markup.add(types.InlineKeyboardButton(
            text=leave_name, callback_data=leave_value))

    bot.send_message(
        chat_id=message.chat.id,
        text="Please choose your leave type:",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data in [leave[1] for leave in LEAVE_TYPES])
def handle_leave_selection(call):
    leave_type = call.data
    telegram_user_id = call.message.chat.id
    print('manish', telegram_user_id, leave_type)
    response = requests.post(url=f'{API_BASE_URL}/leave/', json={
        "telegram_user_id": f'{telegram_user_id}',
        "leave_type": f'{leave_type}',
    })

    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)

    if response.status_code == 201:
        bot.send_message(chat_id=telegram_user_id,
                         text="Leave status marked successfully! ✅")
        return
    else:
        bot.send_message(chat_id=telegram_user_id,
                         text="Failed to mark leave status.")
        return

    bot.answer_callback_query(call.id, text="Processed successfully!")


@bot.message_handler(commands=['dailyupdate'])
def dailyupdate(message):
    telegram_user_id = message.chat.id

    # Check if the user is linked
    response = requests.post(
        url=f'{API_BASE_URL}/check-user/',
        json={'telegram_user_id': str(telegram_user_id)}
    )

    if response.status_code == 200:
        parsed_data = response.json()
        if not parsed_data.get('exists', False):
            bot.send_message(
                chat_id=telegram_user_id,
                text="Oops! 🚫 The specified user hasn't linked their Telegram with Hubstaff yet. "
                     "Ask them to use the /hubstaff command."
            )
            return
    else:
        bot.send_message(
            chat_id=telegram_user_id,
            text="Failed to verify user status. Please try again later."
        )
        return
    bot.send_message(
        chat_id=telegram_user_id,
        text="Please provide your daily update message:"
    )

    bot.register_next_step_handler(message, process_daily_update)

def process_daily_update(message):
    telegram_user_id = message.chat.id
    update_message = message.text.strip()

    if not update_message:
        bot.reply_to(message, "No update message provided. Please try again.")
        return
    response = requests.post(
        url=f'{API_BASE_URL}/dailyupdate/',
        json={
            'telegram_user_id': str(telegram_user_id),
            'update_message': update_message
        }
    )

    if response.status_code == 201:
        bot.reply_to(message, "Daily update submitted successfully! ✅")
    else:
        bot.reply_to(
            message, "Failed to submit daily update. Please try again later.")


@bot.message_handler(commands=['feedback'])
def feedback(message):
    telegram_user_id = message.chat.id
    isLoginRequired = True
    response = requests.post(url=f'{API_BASE_URL}/check-user/', json={
        'telegram_user_id': f'{telegram_user_id}'
    })

    if response.status_code == 200:
        parsed_data = response.json()
        isLoginRequired = parsed_data['exists']

    if not isLoginRequired:
        bot.send_message(chat_id=telegram_user_id,
                         text="Oops! 🚫 The specified user hasn't linked their Telegram with Hubstaff yet. Ask them to use the / hubstaff command.")
        return
    else:
        waiting_for_feedback[telegram_user_id] = True
        bot.send_message(chat_id=telegram_user_id,
                         text="Please provide your feedback:")


@bot.message_handler(func=lambda message: message.chat.id in waiting_for_feedback and waiting_for_feedback[message.chat.id])
def receive_feedback(message):
    telegram_user_id = message.chat.id
    feedback_message = message.text.strip()

    if not feedback_message:
        bot.reply_to(message, "Please provide your feedback.")
        return

    print(feedback_message)
    response = requests.post(
        f'{API_BASE_URL}/feedback/',
        data={'telegram_user_id': telegram_user_id,
              'message': feedback_message}
    )

    if response.status_code == 201:
        bot.reply_to(message, "Feedback submitted successfully!")
        return
    else:
        bot.reply_to(message, "Failed to submit feedback.")
        return
    waiting_for_feedback.pop(telegram_user_id, None)

# start addtask


@bot.message_handler(commands=['addtask'])
def addtask(message):
    global telegram_user_id, task_name, start_date, end_date
    telegram_user_id = message.chat.id
    response = requests.post(
        url=f'{API_BASE_URL}/check-user/', json={'telegram_user_id': str(telegram_user_id)})

    if response.status_code == 200:
        parsed_data = response.json()
        if not parsed_data.get('exists', False):
            bot.send_message(
                telegram_user_id, "Oops! 🚫 The specified user hasn't linked their Telegram with Hubstaff yet. Ask them to use the /hubstaff command.")
            return
    bot.send_message(telegram_user_id, "Please provide the task name.")
    bot.register_next_step_handler(message, ask_start_date)


def ask_start_date(message):
    global task_name
    task_name = message.text.strip()

    if not task_name:
        bot.send_message(telegram_user_id,
                         "Task name is required. Please provide a task name.")
        bot.register_next_step_handler(message, ask_start_date)
        return
    today = datetime.today()
    markup = types.InlineKeyboardMarkup()

    row = []
    for i in range(7):
        date = today + timedelta(days=i)
        button_text = date.strftime('%Y-%m-%d')
        reverse_text = date.strftime('%d-%m-%Y')
        button = types.InlineKeyboardButton(
            text=reverse_text, callback_data=f'start_{button_text}')
        row.append(button)
        if len(row) == 3 or i == 6:
            markup.add(*row)
            row = []

    bot.send_message(telegram_user_id,
                     "Please choose a start date:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('start_'))
def handle_start_date(call):
    global start_date
    start_date = call.data.split('_')[1]
    today = datetime.today()
    markup = types.InlineKeyboardMarkup()

    row = []
    for i in range(7):
        date = today + timedelta(days=i)
        button_text = date.strftime('%Y-%m-%d')
        reverse_text = date.strftime('%d-%m-%Y')
        button = types.InlineKeyboardButton(
            text=reverse_text, callback_data=f'end_{button_text}')
        row.append(button)
        if len(row) == 3 or i == 6:
            markup.add(*row)
            row = []

    bot.send_message(call.message.chat.id,
                     "Please choose an end date:", reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('end_'))
def handle_end_date(call):
    global end_date
    end_date = call.data.split('_')[1]
    if not task_name or not start_date or not end_date:
        bot.send_message(call.message.chat.id,
                         "Failed to complete task data. Try again.")
        return

    response = requests.post(
        url=f'{API_BASE_URL}/addtask/',
        json={
            'telegram_user_id': telegram_user_id,
            'task_name': task_name,
            'start_time': start_date,
            'end_time': end_date
        }
    )

    if response.status_code == 201:
        bot.send_message(
            call.message.chat.id, f"Task '{task_name}' added successfully with start date {start_date} and end date {end_date}.")
        return
    else:
        bot.send_message(call.message.chat.id,
                         "Failed to add task. Please try again.")

    reset_task_data()
    return


def reset_task_data():
    global task_name, start_date, end_date, telegram_user_id
    task_name = None
    start_date = None
    end_date = None
    telegram_user_id = None
# end addtask


@bot.message_handler(commands=['listtask'])
def listtask(message):
    telegram_user_id = message.chat.id

    # Check if the user is linked
    response = requests.post(
        url=f'{API_BASE_URL}/check-user/',
        json={'telegram_user_id': str(telegram_user_id)}
    )

    if response.status_code == 200:
        parsed_data = response.json()
        if not parsed_data.get('exists', False):
            bot.send_message(
                chat_id=telegram_user_id,
                text="Oops! 🚫 The specified user hasn't linked their Telegram with Hubstaff yet. "
                     "Ask them to use the /hubstaff command."
            )
            return
    else:
        bot.send_message(
            chat_id=telegram_user_id,
            text="Failed to verify user status. Please try again later."
        )
        return
    bot.send_message(
        chat_id=telegram_user_id,
        text="Fetching your active tasks..."
    )

    response = requests.post(
        url=f'{API_BASE_URL}/listtask/',
        json={'telegram_user_id': telegram_user_id}
    )

    if response.status_code == 200:
        tasks = response.json().get('tasks', [])
        if tasks:
            task_list = "\n".join(
                [f"Task {i+1}: {task['task_name']} (Start: {task['start_time']}, End: {task['end_time']})"
                 for i, task in enumerate(tasks)]
            )
            bot.reply_to(message, f"Active tasks:\n{task_list}")
            return
        else:
            bot.reply_to(message, "No active tasks found.")
            return
    else:
        bot.reply_to(
            message, "Failed to fetch active tasks. Please try again later.")
        return


@bot.message_handler(commands=['stats'])
def stats(message):
    telegram_user_id = message.chat.id
    isLoginRequired = True
    response = requests.post(url=f'{API_BASE_URL}/check-user/', json={
        'telegram_user_id': str(telegram_user_id)
    })

    if response.status_code == 200:
        parsed_data = response.json()
        isLoginRequired = parsed_data['exists']
        if not isLoginRequired:
            bot.send_message(chat_id=telegram_user_id,
                            text="Oops! 🚫 The specified user hasn't linked their Telegram with Hubstaff yet. Ask them to use the /hubstaff command.")
            return
    
    bot.reply_to(
        message, "Please wait the stats are ... ")
    response = requests.post(
        url=f'{API_BASE_URL}/stats/',
        json={'telegram_user_id': str(
            telegram_user_id)}
    )

    if response.status_code == 200:
        stats_data = response.json()
        task_names = "\n".join(stats_data.get('task_names', []))
        stats_message = (
            f"Tasks Completed: {stats_data['tasks_completed']}\n"
            f"Total Time Spent: {stats_data['total_time_spent']} hours\n"
            f"Last Updated: {stats_data['last_updated']}\n"
            f"Task Names:\n{task_names}"
        )

        bot.reply_to(message, stats_message)
        return
    else:
        bot.reply_to(message, "Failed to fetch stats.")
        return


@bot.message_handler(commands=['hubstaff'])
def hubstaff(message):
    """Handle /hubstaff command to start the login process."""
    user_states[message.chat.id] = WAITING_FOR_EMAIL
    bot.reply_to(message, "Please enter your Hubstaff email:")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Handle user responses based on their state."""
    user_id = message.chat.id

    # Check if the user is in a valid state
    if user_id not in user_states:
        return

    state = user_states[user_id]

    if state == WAITING_FOR_EMAIL:
        handle_email_input(message, user_id)

    elif state == WAITING_FOR_PASSWORD:
        handle_password_input(message, user_id)


def handle_email_input(message, user_id):
    """Handle email input from the user."""
    email = message.text.strip()

    if not email:
        bot.reply_to(
            message, "Email is required! Please enter your Hubstaff email:")
        return

    # Save email and transition to next state
    user_states[user_id] = WAITING_FOR_PASSWORD
    user_states[f'{user_id}_email'] = email
    bot.reply_to(message, "Please enter your Hubstaff password:")


def handle_password_input(message, user_id):
    """Handle password input from the user and process the login."""
    password = message.text.strip()
    email = user_states.get(f'{user_id}_email')

    if not email:
        bot.reply_to(
            message, "Error: Email was not received. Restart the process with /hubstaff.")
        cleanup_state(user_id)
        return

    # Attempt to authenticate with the API
    try:
        print(email, password, user_id)
        response = requests.post(
            f'{API_BASE_URL}/hubstaff/login/',
            data={'email': email, 'password': password,
                  'telegram_user_id': user_id}
        )
        if response.status_code == 200:
            bot.reply_to(message, "Hubstaff linked successfully!")
            return
        else:
            bot.reply_to(
                message, "Failed to link Hubstaff account. Please check your credentials.")
            return
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")
    finally:
        cleanup_state(user_id)


def cleanup_state(user_id):
    """Clean up the user state."""
    user_states.pop(user_id, None)
    user_states.pop(f'{user_id}_email', None)


if __name__ == '__main__':
    bot.polling(none_stop=True)
