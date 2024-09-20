import logging
import sqlite3
from datetime import datetime, timedelta
import time
import asyncio
import random
from telegram import *
from telegram.ext import *
import json


# Декоратор для логирования ошибок

SELECT_USER, ENTER_BALANCE, SEND_MESSAGE = range(3)
TOKEN = '7491056485:AAEOEEi60LJCv6lj1meW7Gika0nRmSuh1vM'
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
pending_messages = {}
quizzes = []
duel_info = []
result = []
WAITING_FOR_OPPONENT, ROLLING_DICE = range(2)
message_id_counter = 0
lood_flag = False
emoji_count = {}
cursor.execute('CREATE TABLE IF NOT EXISTS users ( ID INTEGER PRIMARY KEY, name TEXT, balance INTEGER, username TEXT)')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='И зачем все это...)', message_thread_id=12)

async def handle_dice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global lood_flag
    if not lood_flag:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
        return

    dice = update.message.dice

    if update.message.from_user.username is None:
        user_name = update.message.from_user.name
    else:
        user_name = "@" + update.message.from_user.username
    user_id = update.message.from_user.id
    cursor.execute('SELECT balance FROM users WHERE id = ?', (user_id,))
    current_balance = cursor.fetchone()[0]
    cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
    existing_user = cursor.fetchone()
    mess = ''
    if not existing_user:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='Вы не зарегистрированы. Пожалуйста, используйте команду /register.',
                                       message_thread_id=12)
        return

    current_time = time.time()
    user_id = update.effective_user.id
    if user_id in emoji_count:
        last_time, count = emoji_count[user_id]
        if current_time - last_time < 5:
            if count > 10:
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
                return
            else:
                emoji_count[user_id] = (current_time, count + 1)
        else:
            emoji_count[user_id] = (current_time, count - 10)
    else:
        emoji_count[user_id] = (current_time, 1)
    if update.message.message_thread_id == 12 and lood_flag:
        if current_balance <= 0:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f'Недостаточный баланс для игры. Ваш текущий баланс: {current_balance}',
                                           message_thread_id=12)
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
            return
        current = datetime.now().second
        new_current = current + 2
        if (new_current > 59): new_current = new_current % 60
        while (datetime.now().second != new_current):
            pass
        if dice.emoji == '🎲':  # Кубик
            if dice.value == 1:
                new_balance = current_balance - 20
                if new_balance < 0: new_balance = 0
                mess = f'КРИТИЧЕСКАЯ НЕУДАЧА ❗️😫 \n {user_name} теряет 20 очков! \n Баланс {user_name}: {new_balance}'
            elif dice.value == 2:
                new_balance = current_balance + 2
                mess = f'Неплохой бросок. \n {user_name} получает 2 очка! \n Баланс {user_name}: {new_balance}'
            elif dice.value == 3:
                new_balance = current_balance + 4
                mess = f'Отличный бросок. \n {user_name} получает 4 очка! \n Баланс {user_name}: {new_balance}'
            elif dice.value == 4:
                new_balance = current_balance + 6
                mess = f'Мастерский бросок. \n {user_name} получает 6 очков! \n Баланс {user_name}: {new_balance}'
            elif dice.value == 5:
                new_balance = current_balance + 8
                mess = f'Офигенный бросок! \n {user_name} получает 8 очков! \n Баланс {user_name}: {new_balance}'
            elif dice.value == 6:
                new_balance = current_balance + 15
                mess = f'ЧТО ОН ТВОРИТ 🤯!!?? \n {user_name} получает 15 очков! \n Баланс {user_name}: {new_balance}'
            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           reply_to_message_id=update.message.message_id,
                                           text=mess,
                                           message_thread_id=12)

        elif dice.emoji == '🎳':  # Кубик
            if dice.value == 1:
                new_balance = current_balance - 20
                if new_balance < 0: new_balance = 0
                mess = f'КРИТИЧЕСКАЯ НЕУДАЧА ❗️😫  \n {user_name} теряет 20 очков! \n Баланс {user_name}: {new_balance}'
            elif dice.value == 2:
                new_balance = current_balance + 1
                mess = f'И это всё на что ты способен ?🤨 \n {user_name} получает 1 очко! \n Баланс {user_name}: {new_balance}'
            elif dice.value == 3:
                new_balance = current_balance + 3
                mess = f'Для начала не плохо. Продолжаем 👀 \n{user_name} получает 3 очка! \n Баланс {user_name}: {new_balance}'
            elif dice.value == 4:
                new_balance = current_balance + 5
                mess = f'Было близко💅  \n {user_name} получает 5 очков! \n Баланс {user_name}: {new_balance}'
            elif dice.value == 5:
                new_balance = current_balance + 7
                mess = f'ТАК БЛИЗКО 🥹 \n {user_name} получает 7 очков! \n Баланс {user_name}: {new_balance}'
            elif dice.value == 6:
                new_balance = current_balance + 15
                mess = f'СТРАААЙК 👊 \n {user_name} получает 15 очков! \n Баланс {user_name}: {new_balance}'

            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()
            await context.bot.send_message(chat_id=update.effective_chat.id, text=mess,
                                           reply_to_message_id=update.message.message_id,
                                           message_thread_id=12)
        elif dice.emoji == '🎯':  # Кубик
            if dice.value == 1:
                new_balance = current_balance - 15
                if new_balance < 0: new_balance = 0
                mess = f'Мдаа... меткость - не твоё \n {user_name} теряет 15 очков! \n Баланс {user_name}: {new_balance}'
            elif dice.value == 2:
                new_balance = current_balance + 1
                mess = f'Ну.. Хотя бы попал  \n {user_name} получает 1 очко! \n Баланс {user_name}: {new_balance}'
            elif dice.value == 3:
                new_balance = current_balance + 3
                mess = f'Уже лучше! Пробуй еще! \n {user_name} получает 3 очка! \n Баланс {user_name}: {new_balance}'
            elif dice.value == 4:
                new_balance = current_balance + 5
                mess = f'Нормально.. Стабильно.. \n {user_name} получает 5 очков! \n Баланс {user_name}: {new_balance}'
            elif dice.value == 5:
                new_balance = current_balance + 7
                mess = f'Это было очень близко \n {user_name} получает 7 очков! \n Баланс {user_name}: {new_balance}'
            elif dice.value == 6:
                new_balance = current_balance + 15
                mess = f'В яблочко 🍎  \n {user_name} получает 15 очков! \n Баланс {user_name}: {new_balance}'

            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           reply_to_message_id=update.message.message_id,
                                           text=mess,
                                           message_thread_id=12)

        elif dice.emoji == '🏀':  # Кубик
            if dice.value > 3:
                new_balance = current_balance + 15
                mess = f'Тебе завидует даже Джордан 😍 \n {user_name} получает 15 очков! \n Баланс {user_name}: {new_balance}'
            elif dice.value < 4:
                new_balance = current_balance - 20
                if new_balance < 0: new_balance = 0
                mess = f'Встань поближе и попробуй ещё раз \n {user_name} теряет 20 очков! \n Баланс {user_name}: {new_balance}'

            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           reply_to_message_id=update.message.message_id, text=mess,
                                           message_thread_id=12)

        elif dice.emoji == '⚽':  # Кубик
            if dice.value > 2:
                new_balance = current_balance + 15
                mess = f'Шиииииш. Отличный удар🥳 \n {user_name} получает 15 очков! \n Баланс {user_name}: {new_balance}'
            elif dice.value < 3:
                new_balance = current_balance - 20
                if new_balance < 0: new_balance = 0
                mess = f'Ты как Дантес! Косишь на оба глаза? \n {user_name} теряет 20 очков! \n Баланс {user_name}: {new_balance}'

            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           reply_to_message_id=update.message.message_id, text=mess,
                                           message_thread_id=12)

        elif dice.emoji == '🎰':  # Кубик
            if dice.value == 24 or dice.value == 25 or dice.value == 23 or dice.value == 18 or dice.value == 6 or dice.value == 26 or dice.value == 30 or dice.value == 38 or dice.value == 54:
                new_balance = current_balance + 5
                mess = f'Как вкусно... \n {user_name} получает 5 очков! \n Баланс {user_name}: {new_balance}'
            elif dice.value == 21 or dice.value == 35 or dice.value == 44 or dice.value == 27 or dice.value == 11 or dice.value == 47 or dice.value == 39 or dice.value == 42 or dice.value == 59 or dice.value == 41:
                new_balance = current_balance + 7
                mess = f'А теперь уже кисленько... Зато выйграл! \n {user_name} получает 7 очков! \n Баланс {user_name}: {new_balance}'
            elif dice.value == 17 or dice.value == 13 or dice.value == 3 or dice.value == 4 or dice.value == 9 or dice.value == 5 or dice.value == 2 or dice.value == 49 or dice.value == 33:
                new_balance = current_balance + 3
                mess = f'ВОУ! Это уже приятно! \n {user_name} получает 3 очка! \n Баланс {user_name}: {new_balance}'

            elif dice.value == 16 or dice.value == 63 or dice.value == 56 or dice.value == 52 or dice.value == 48 or dice.value == 61 or dice.value == 62 or dice.value == 60:
                new_balance = current_balance + 10
                mess = f'АААААА ТАК БЛИЗКО \n {user_name} получает 10 очков! \n Баланс {user_name}: {new_balance}'
            elif dice.value == 1 or dice.value == 22 or dice.value == 43 or dice.value == 64:
                new_balance = current_balance + 50
                mess = f'Джекпот! Удача на твоей стороне 💸 \n {user_name} получает 50 очков! \n Баланс {user_name}: {new_balance}'
            else:
                new_balance = current_balance - 20
                if new_balance < 0: new_balance = 0
                mess = f'Удача покинула тебя 😔 \n {user_name} теряет 20 очков! \n Баланс {user_name}: {new_balance}'

            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           reply_to_message_id=update.message.message_id, text=mess,
                                           message_thread_id=12)
    else:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
        return

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    user_id = update.message.from_user.id
    first_name = update.message.from_user.name

    cursor.execute('SELECT ID FROM users WHERE ID = ?', (user_id,))
    existing_user = cursor.fetchone()

    if existing_user:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Вы уже зарегистрированы.',
                                       message_thread_id=12)
    else:
        if update.message.from_user.username is None:
            user_name = first_name
            cursor.execute('INSERT INTO users (ID, name, balance, username) VALUES (?, ?, ?, ?)',
                           (user_id, first_name, 1500, user_name))
        else:
            user_name ="@" + update.message.from_user.username
            cursor.execute('INSERT INTO users (ID, name, balance, username) VALUES (?, ?, ?, ?)',
                        (user_id, first_name, 1500, user_name))
        conn.commit()
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Вы успешно зарегистрированы!',
                                       message_thread_id=12)

def get_top_users():
    cursor.execute('SELECT username, balance FROM users ORDER BY balance DESC LIMIT 10')
    top_users = cursor.fetchall()
    return top_users

def boll(result: []):
    seen = set()

    for element in result:
        if element in seen:
            return "true"
        seen.add(element)

    return "false"
def get_combo_text(dice_value: int):
    values = ["BAR", "виноград", "лимон", "семь"]
    dice_value -= 1
    result = []
    for _ in range(3):
        result.append(values[dice_value % 4])
        dice_value //= 4
    return result

async def send_top_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top_users = get_top_users()
    message = "Топ 10 пользователей по очкам:\n"
    for i, (username, balance) in enumerate(top_users, start=1):
        message += f"{i}. {username}: {balance}\n"
    await context.bot.send_message(chat_id="-1002171062047", text=message, message_thread_id=12)

async def daily_reward(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if (update.message.from_user.username == None):
        user_name = update.message.from_user.name
    else:
        user_name = "@" + update.message.from_user.username


    cursor.execute('SELECT ID, last_reward_time,balance FROM users WHERE ID = ?', (user_id,))
    user_data = cursor.fetchone()
    user_bal = user_data[2]

    if not user_data:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Вы не зарегистрированы. Пожалуйста, используйте команду /register.', message_thread_id=12)
        return

    last_reward_time_str = user_data[1]
    last_reward_time = datetime.strptime(last_reward_time_str, '%Y-%m-%d %H:%M:%S') if last_reward_time_str else None


    if last_reward_time and datetime.now() - last_reward_time < timedelta(days=1):
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Вы уже получили буст сегодня. Попробуйте завтра.', message_thread_id=12)
        return
    if(user_bal>3000):
        reward_amount = random.randint(1,200)
    elif(user_bal>2000): reward_amount = random.randint(250,300)
    else: reward_amount = random.randint(390,500)
    cursor.execute('UPDATE users SET balance = balance + ?, last_reward_time = ? WHERE ID = ?', (reward_amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user_id))
    conn.commit()

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Буст для {user_name} на сегодня {reward_amount} очков', message_thread_id=12)

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type != Chat.PRIVATE:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='Эта команда доступна только в личных сообщениях.', message_thread_id=12)
        return

    user_name = update.message.from_user.username
    if user_name not in ['hlebnastole', 'why_dyrachyo', 'sdmfy']:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='У вас нет доступа к этой программе')
        return

    args = context.args
    if len(args) != 2:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='Используйте команду в формате: /balance "username" "число"')
        return

    target_username = args[0]
    try:
        amount = int(args[1])
    except ValueError:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Пожалуйста, введите корректное число.')
        return

    cursor.execute('SELECT username FROM users WHERE username = ?', (target_username,))
    existing_user = cursor.fetchone()

    if not existing_user:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f'Пользователь {target_username} не найден в базе данных.')
        return

    # Обновление баланса в базе данных
    cursor.execute('UPDATE users SET balance = balance + ? WHERE username = ?', (amount, target_username))
    conn.commit()
    cursor.execute('SELECT balance FROM users WHERE username = ?', (target_username,))
    conn.commit()
    bal = cursor.fetchone()[0]
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f'Баланс пользователя {target_username} теперь {bal}.')

async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.effective_chat.type != Chat.PRIVATE:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='Эта команда доступна только в личных сообщениях.', message_thread_id=12)
        return

    user_name = update.message.from_user.username
    if user_name not in ['hlebnastole', 'sdmfy', 'why_dyrachyo']:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='У вас нет доступа к этой команде')
        return

    target_chat_id = '-1002171062047'  # Замените на ID целевого чата
    # Проверяем, есть ли в сообщении изображение
    if update.message.photo:
        # Получаем последнее изображение из списка фотографий
        photo = update.message.photo[-1]
        photo_file = await photo.get_file()

        # Отправляем изображение в целевой чат
        await context.bot.send_photo(chat_id=target_chat_id, photo=photo_file.file_id, caption=update.message.caption, message_thread_id=12)
    else:
        # Отправляем текстовое сообщение в целевой чат
        message_text = ' '.join(context.args)
        await context.bot.send_message(chat_id=target_chat_id, text=message_text, message_thread_id=12)

    await context.bot.send_message(chat_id=update.effective_chat.id, text='Сообщение отправлено.')


quiz_word = None
quiz_points = None

quizzes = []

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global quizzes

    if update.effective_chat.type != Chat.PRIVATE:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='Эта команда доступна только в личных сообщениях.', message_thread_id=12)
        return

    user_name = update.message.from_user.username
    if user_name not in ['hlebnastole', 'why_dyrachyo', 'sdmfy']:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='У вас нет доступа к этой команде')
        return

    args = context.args
    if len(args) != 2:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='Используйте команду в формате: /quiz "слово" "число"')
        return

    word = args[0]
    points = args[1]

    quiz_id = len(quizzes) + 1  # Генерация уникального идентификатора квиза
    quizzes.append({'id': quiz_id, 'word': word.lower(), 'points': points})

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"Квиз начат с словом '{word}' и {points} баллами. Идентификатор квиза: {quiz_id}")

async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global quizzes
    global message_id_counter
    if update.effective_chat.type == Chat.PRIVATE:
        user_id = update.message.from_user.id
        message_text = update.message.text
        # Генерация уникального идентификатора сообщения
        message_id_counter += 1
        message_id = message_id_counter

        # Сохранение сообщения в очереди
        pending_messages[message_id] = {'user_id': user_id, 'text': message_text}

        # Отправка сообщения администратору для подтверждения
        admin_chat_id = '1432989775'  # Замените на ID администратора
        keyboard = [
            [InlineKeyboardButton("Отправить", callback_data=f"approve_{message_id}")],
            [InlineKeyboardButton("Отклонить", callback_data=f"reject_{message_id}")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=admin_chat_id,
                                       text=f"Пользователь анонимно отправил сообщение:\n{message_text}",
                                       reply_markup=reply_markup)
        return
    if not quizzes:
        return

    user_answer = update.message.text.lower()

    # Проверка текущего квиза
    current_quiz = quizzes[0]
    if user_answer == current_quiz['word']:
        user_id = update.message.from_user.id
        if update.message.from_user.username is None:
            user_name = update.message.from_user.name
        else:
            user_name = "@" + update.message.from_user.username

        cursor.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (current_quiz['points'], user_id))
        conn.commit()

        await context.bot.send_message(chat_id="-1002171062047",
                                       text=f"{user_name} угадал слово и получает {current_quiz['points']} очков.",
                                       reply_to_message_id=update.message.message_id, message_thread_id=12)

        # Удаление текущего квиза из очереди
        quizzes.pop(0)

async def lood(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global lood_flag
    if update.effective_chat.type != Chat.PRIVATE:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='Эта команда доступна только в личных сообщениях.', message_thread_id=12)
        return

    user_name = update.message.from_user.username
    if user_name not in ['hlebnastole', 'why_dyrachyo', 'sdmfy']:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='У вас нет доступа к этой команде')
        return

    if (context.args[0] == 'Y'):
        lood_flag = True
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Лудка разрешена')
    elif (context.args[0] == 'N'):
        lood_flag = False
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Лудка запрещена')
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Возможные параметры команды Y/N')


async def good_morning(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if (update.message.from_user.username == None):
        user_name = update.message.from_user.name
    else:
        user_name = "@" + update.message.from_user.username
    # Проверка, зарегистрирован ли пользователь
    cursor.execute('SELECT ID,morning FROM users WHERE ID = ?', (user_id,))
    existing_user = cursor.fetchone()

    if not existing_user:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Вы не зарегистрированы. Пожалуйста, используйте команду /register.', message_thread_id=12)
        return


    if(update.message.message_thread_id==2):
        day = existing_user[1]
        current = datetime.now().day
        # Проверка времени
        current_time = datetime.now().time().hour
        if (current_time > 12 or current_time < 6):
            await context.bot.send_message(chat_id=update.effective_chat.id, text='Слишком поздно для доброго утра!',
                                           message_thread_id=12)
            return
        if (current != day):
            # Обновление баланса
            reward_amount = 100  # Количество баллов, которое пользователь получает
            cursor.execute('UPDATE users SET balance = balance + ? WHERE ID = ?', (reward_amount, user_id))
            conn.commit()
            cursor.execute('UPDATE users SET morning = ? WHERE ID = ?', (current, user_id))
            conn.commit()

            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f'За пожелание доброго утра {user_name} получает +100 очков.',
                                           message_thread_id=12)

            return

async def send_anonymous_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global message_id_counter
    if update.effective_chat.type == Chat.PRIVATE:
        user_id = update.message.from_user.id
        message_text = update.message.text
        photo = None

        # Проверяем, есть ли в сообщении изображение
        if update.message.photo:
            photo = update.message.photo[-1]
            photo_file = await photo.get_file()
            photo_file_id = photo_file.file_id

        # Генерация уникального идентификатора сообщения
        message_id_counter += 1
        message_id = message_id_counter

        # Сохранение сообщения в очереди
        pending_messages[message_id] = {'user_id': user_id, 'text': message_text, 'photo_file_id': photo_file_id if photo else None}

        # Отправка сообщения администратору для подтверждения
        admin_chat_id = '1432989775'  # Замените на ID администратора
        keyboard = [
            [InlineKeyboardButton("Отправить", callback_data=f"approve_{message_id}")],
            [InlineKeyboardButton("Отклонить", callback_data=f"reject_{message_id}")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        print("dfs")
        await context.bot.send_message(chat_id=admin_chat_id, text=f"Пользователь анонимно отправил сообщение:\n{message_text}", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    query.answer()
    print("xfd")
    action, message_id = query.data.split('_')
    message_id = int(message_id)

    if message_id not in pending_messages:
        await context.bot.send_message(chat_id=query.message.chat_id, text="Сообщение не найдено.")
        return

    if action == 'approve':
        # Отправка сообщения в чат
        message_info = pending_messages[message_id]
        target_chat_id = "-1002171062047"  # Замените на ID целевого чата
        if message_info['photo_file_id']:
            await context.bot.send_photo(chat_id=target_chat_id, photo=message_info['photo_file_id'], caption=f"Новое сообщение от анонимного пользователя:\n{message_info['text']}", message_thread_id=16)
        else:
            await context.bot.send_message(chat_id=target_chat_id, text=f"Новое сообщение от анонимного пользователя:\n{message_info['text']}", message_thread_id=16)
        await context.bot.send_message(chat_id=query.message.chat_id, text=f"Отправлено в чат.")
    elif action == 'reject':
        # Отклонение сообщения
        await context.bot.send_message(chat_id=query.message.chat_id, text=f"Отклонено.")

    # Удаление сообщения из очереди
    pending_messages.pop(message_id, None)


async def duels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    global duel_info

    if not duel_info:
        cursor.execute('SELECT balance, username, ID FROM users WHERE ID = ?', (user_id,))
        first_user = cursor.fetchone()

        if not first_user:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text='Вы не зарегистрированы. Пожалуйста, используйте команду /register.',
                                           message_thread_id=12)
            return ConversationHandler.END

        if first_user[0] < 25:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text='К сожалению вашего баланса не хватает для игры!',
                                           message_thread_id=12)
            return ConversationHandler.END

        duel_info.append(first_user)
        username = first_user[1]
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f'{username} пришёл на дуэль. Ожидает соперника. Чтобы выйти на дуэль отправь ⚔️',
                                       message_thread_id=12)
    elif user_id != duel_info[0][2]:
        cursor.execute('SELECT balance, username, ID FROM users WHERE ID = ?', (user_id,))
        second_user = cursor.fetchone()

        if not second_user:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text='Вы не зарегистрированы. Пожалуйста, используйте команду /register.',
                                           message_thread_id=12)
            return ConversationHandler.END

        if second_user[0] < 25:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text='К сожалению вашего баланса не хватает для игры!',
                                           message_thread_id=12)
            return ConversationHandler.END

        duel_info.append(second_user)
        username_2 = second_user[1]
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f'{username_2} и {duel_info[0][1]} дуэляться. У кого больше выпадет на кубике получает +25 очков. У кого меньше -25 очков',
                                       message_thread_id=12)

        # Бросок кубика для первого игрока
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Бросок ' + duel_info[0][1] + ':',
                                       message_thread_id=12)
        dice_message = await context.bot.send_dice(chat_id=update.effective_chat.id, emoji=Dice.DICE,
                                                   message_thread_id=12)
        result = [dice_message.dice.value]
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='Бросок ' + duel_info[1][1] + ':', message_thread_id=12)
        # Бросок кубика для второго игрока
        dice_message = await context.bot.send_dice(chat_id=update.effective_chat.id, emoji=Dice.DICE,
                                                   message_thread_id=12)
        result.append(dice_message.dice.value)

        winner = None
        loser = None
        if result[0] > result[1]:
            winner = duel_info[0]
            loser = duel_info[1]
        elif result[0] < result[1]:
            winner = duel_info[1]
            loser = duel_info[0]
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Ничья!', message_thread_id=12)
            duel_info.clear()
            return
        time.sleep(3)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Победу одержал {winner[1]}!', message_thread_id=12)

        cursor.execute('UPDATE users SET balance = balance + ? WHERE ID = ?', (25, winner[2]))
        conn.commit()
        cursor.execute('UPDATE users SET balance = balance - ? WHERE ID = ?', (25, loser[2]))
        conn.commit()

        duel_info.clear()

players = {}

# Колода карт
deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4
random.shuffle(deck)

# Функция для раздачи карт
def deal_card():
    return deck.pop()

# Функция для подсчета очков
def calculate_score(hand):
    score = sum(hand)
    if score > 21 and 11 in hand:
        hand.remove(11)
        hand.append(1)
        score = sum(hand)
    return score

# Обработчик команды /start


# Обработчик сообщения для присоединения к игре
async def join_game(update: Update, context: CallbackContext) -> None:
    print("join")
    user_id = update.message.from_user.id
    if user_id not in players:
        players[user_id] = {
            'hand': [deal_card(), deal_card()],
            'score': 0,
            'username': '@' + update.message.from_user.username
        }
        await update.message.reply_text(f"{update.message.from_user.username} присоединился к столу игры в 21.")
        await context.bot.send_message(update.message.chat.id, "20 секунд до начала игры. Чтобы присоединиться к столу, отправьте '🔖'.")

        # Запускаем асинхронную задачу для приема новых игроков
        asyncio.create_task(accept_players(update, context))

async def accept_players(update: Update, context: CallbackContext) -> None:
    end_time = datetime.now() + timedelta(seconds=20)

    while datetime.now() < end_time:
        await asyncio.sleep(1)  # Ждем 1 секунду перед проверкой новых сообщений

    usernames = [player['username'] for player in players.values()]
    players_str = ', '.join(usernames)
    print(players_str)
    if len(usernames) == 1:
        await context.bot.send_message(update.message.chat.id, "К сожалению, игроки не набраны!")
    else:
        await start_game(update.message.chat.id, context)

async def handle_message(update: Update, context: CallbackContext) -> None:
    if update.message.text == '21':
        user_id = update.message.from_user.id
        if user_id not in players:
            players[user_id] = {
                'hand': [deal_card(), deal_card()],
                'score': 0,
                'username': '@' + update.message.from_user.username
            }
            usernames = [player['username'] for player in players.values()]
            players_str = ', '.join(usernames)
            await update.message.reply_text(
                f"{update.message.from_user.username} присоединился к столу игры в 21.\n За столом: {players_str}")

# Функция для начала игры
async def start_game(chat_id, context: CallbackContext):
    print("start game")
    if players:
        await context.bot.send_message(chat_id, "Игра в 21 началась.")
        for user_id, player in players.items():
            await context.bot.send_message(user_id, f"Твои карты: {player['hand']}")
            await context.bot.send_message(user_id, "Ещё?", reply_markup=generate_markup())
            print("else")
    else:
        await context.bot.send_message(chat_id, "Никто не присоединился к столу игры в 21. Сорянчик.")

# Функция для генерации клавиатуры
async def generate_markup():
    print("gen knopok")
    keyboard = [
        [InlineKeyboardButton("Взять ещё", callback_data='hit')],
        [InlineKeyboardButton("Оставить как есть", callback_data='stand')]
    ]
    return InlineKeyboardMarkup(keyboard)

# Обработчик сообщения для взятия ещё одной карты или остановки
async def handle_game_action(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    if user_id in players:
        if query.data == 'hit':
            players[user_id]['hand'].append(deal_card())
            await query.edit_message_text(f"Твои карты: {players[user_id]['hand']}")
            if calculate_score(players[user_id]['hand']) > 21:
                await query.edit_message_text("Ты проиграл.")
                del players[user_id]
            else:
                await query.edit_message_text("Ещё?", reply_markup=generate_markup())
        elif query.data == 'stand':
            players[user_id]['score'] = calculate_score(players[user_id]['hand'])
            await query.edit_message_text(f"Ты остановился с {players[user_id]['score']} очками.")
            await check_game_over(context)

# Функция для проверки окончания игры
async def check_game_over(context: CallbackContext):
    if all(player['score'] != 0 for player in players.values()):
        winner = max(players.values(), key=lambda x: x['score'])
        for user_id, player in players.items():
            await context.bot.send_message(user_id, f"Игра в 21 закончилась.\nПобедитель: @{winner['username']} с {winner['score']} очками.")
        players.clear()
def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex('^⚔️$'), duels))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex('^🚀$'), daily_reward))
    #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex('^21$'), join_game))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(
        '^(доброе утро|Доброе утро|Доброго утра|доброго утра|Доброе|доброе)$'), good_morning))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_anonymous_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_answer))
    application.add_handler(MessageHandler(filters.PHOTO & ~filters.COMMAND, send_message))
    application.add_handler(MessageHandler(filters.PHOTO & ~filters.COMMAND, send_anonymous_message))
    application.add_handler(MessageHandler(filters.Dice.ALL, handle_dice))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(CallbackQueryHandler(handle_game_action))
    application.add_handler(CommandHandler('balance', balance))
    application.add_handler(CommandHandler('write', send_message))
    application.add_handler(CommandHandler('quiz', quiz))
    application.add_handler(CommandHandler('lood', lood))
    application.add_handler(CommandHandler('top', send_top_users))
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('register', register))

    application.run_polling()
if __name__ == '__main__':
    main()
Упрости код
