import logging
import sqlite3
from datetime import datetime, timedelta
import time
import asyncio
import random
from telegram import *
from telegram.ext import *

# Константы
SELECT_USER, ENTER_BALANCE, SEND_MESSAGE = range(3)
TOKEN = '7491056485:AAEOEEi60LJCv6lj1meW7Gika0nRmSuh1vM'
WAITING_FOR_OPPONENT, ROLLING_DICE = range(2)
message_id_counter = 0
lood_flag = False
emoji_count = {}

# Подключение к базе данных
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (ID INTEGER PRIMARY KEY, name TEXT, balance INTEGER, username TEXT, last_reward_time TEXT, morning INTEGER)')

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальные переменные
pending_messages = {}
quizzes = []
duel_info = []
result = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text='И зачем все это...)', message_thread_id=12)

async def handle_dice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global lood_flag
    if not lood_flag:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
        return

    dice = update.message.dice
    user_id = update.message.from_user.id
    user_name = update.message.from_user.username or update.message.from_user.name

    cursor.execute('SELECT balance FROM users WHERE id = ?', (user_id,))
    current_balance = cursor.fetchone()[0]

    if current_balance <= 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Недостаточный баланс для игры. Ваш текущий баланс: {current_balance}', message_thread_id=12)
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
        return

    current_time = time.time()
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
        current = datetime.now().second
        new_current = (current + 2) % 60
        while datetime.now().second != new_current:
            pass
        if dice.emoji == '🎲':
            new_balance = current_balance + [20, 2, 4, 6, 8, 15][dice.value - 1]
            mess = f'{"КРИТИЧЕСКАЯ НЕУДАЧА ❗️😫" if dice.value == 1 else f"Неплохой бросок. \n {user_name} получает 2 очка!" if dice.value == 2 else f"Отличный бросок. \n {user_name} получает 4 очка!" if dice.value == 3 else f"Мастерский бросок. \n {user_name} получает 6 очков!" if dice.value == 4 else f"Офигенный бросок! \n {user_name} получает 8 очков!" if dice.value == 5 else f"ЧТО ОН ТВОРИТ 🤯!!?? \n {user_name} получает 15 очков!"} \n Баланс {user_name}: {new_balance}'
            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           reply_to_message_id=update.message.message_id,
                                           text=mess, message_thread_id=12)

        elif dice.emoji == '🎳':
            new_balance = current_balance + [20, 1, 3, 5, 7, 15][dice.value - 1]
            mess = f'{"КРИТИЧЕСКАЯ НЕУДАЧА ❗️😫" if dice.value == 1 else f"И это всё на что ты способен ?🤨 \n {user_name} получает 1 очко!" if dice.value == 2 else f"Для начала не плохо. Продолжаем 👀 \n{user_name} получает 3 очка!" if dice.value == 3 else f"Было близко💅  \n {user_name} получает 5 очков!" if dice.value == 4 else f"ТАК БЛИЗКО 🥹 \n {user_name} получает 7 очков!" if dice.value == 5 else f"СТРАААЙК 👊 \n {user_name} получает 15 очков!"} \n Баланс {user_name}: {new_balance}'
            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()
            await context.bot.send_message(chat_id=update.effective_chat.id, text=mess,
                                           reply_to_message_id=update.message.message_id, message_thread_id=12)

        elif dice.emoji == '🎯':
            new_balance = current_balance + [15, 1, 3, 5, 7, 15][dice.value - 1]
            mess = f'{"Мдаа... меткость - не твоё \n {user_name} теряет 15 очков!" if dice.value == 1 else f"Ну.. Хотя бы попал  \n {user_name} получает 1 очко!" if dice.value == 2 else f"Уже лучше! Пробуй еще! \n {user_name} получает 3 очка!" if dice.value == 3 else f"Нормально.. Стабильно.. \n {user_name} получает 5 очков!" if dice.value == 4 else f"Это было очень близко \n {user_name} получает 7 очков!" if dice.value == 5 else f"В яблочко 🍎  \n {user_name} получает 15 очков!"} \n Баланс {user_name}: {new_balance}'
            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           reply_to_message_id=update.message.message_id,
                                           text=mess, message_thread_id=12)

        elif dice.emoji == '🏀':
            new_balance = current_balance + (15 if dice.value > 3 else -20)
            mess = f'{"Тебе завидует даже Джордан 😍 \n {user_name} получает 15 очков!" if dice.value > 3 else f"Встань поближе и попробуй ещё раз \n {user_name} теряет 20 очков!"}'
            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           reply_to_message_id=update.message.message_id,
                                           text=mess, message_thread_id=12)

        elif dice.emoji == '⚽':
            new_balance = current_balance + (15 if dice.value > 2 else -20)
            mess = f'{"Шиииииш. Отличный удар🥳 \n {user_name} получает 15 очков!" if dice.value > 2 else f"Ты как Дантес! Косишь на оба глаза? \n {user_name} теряет 20 очков!"}'
            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           reply_to_message_id=update.message.message_id,
                                           text=mess, message_thread_id=12)

        elif dice.emoji == '🎰':
            new_balance = current_balance + (
                5 if dice.value in [24, 25, 23, 18, 6, 26, 30, 38, 54] else 7 if dice.value in [21, 35, 44, 27, 11, 47,
                                                                                                39,
                                                                                                42, 59,
                                                                                                41] else 3 if dice.value in [
                    17, 13, 3, 4, 9, 5, 2, 49, 33] else 10 if dice.value in [16, 63, 56, 52, 48, 61, 62,
                                                                             60] else 50 if dice.value in [1, 22, 43,
                                                                                                           64] else -20)
            mess = f'{"Как вкусно..." if dice.value in [24, 25, 23, 18, 6, 26, 30, 38, 54] else "А теперь уже кисленько... Зато выйграл!" if dice.value in [21, 35, 44, 27, 11, 47, 39, 42, 59, 41] else "ВОУ! Это уже приятно!" if dice.value in [17, 13, 3, 4, 9, 5, 2, 49, 33] else "АААААА ТАК БЛИЗКО" if dice.value in [16, 63, 56, 52, 48, 61, 62, 60] else "Джекпот! Удача на твоей стороне 💸" if dice.value in [1, 22, 43, 64] else "Удача покинула тебя 😔"} \n {user_name} получает {new_balance - current_balance} очков! \n Баланс {user_name}: {new_balance}'
            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           reply_to_message_id=update.message.message_id,
                                           text=mess, message_thread_id=12)




async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    first_name = update.message.from_user.name
    user_name = update.message.from_user.username or first_name

    cursor.execute('SELECT ID FROM users WHERE ID = ?', (user_id,))
    existing_user = cursor.fetchone()

    if existing_user:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Вы уже зарегистрированы.', message_thread_id=12)
    else:
        cursor.execute('INSERT INTO users (ID, name, balance, username) VALUES (?, ?, ?, ?)', (user_id, first_name, 1500, user_name))
        conn.commit()
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Вы успешно зарегистрированы!', message_thread_id=12)

def get_top_users():
    cursor.execute('SELECT username, balance FROM users ORDER BY balance DESC LIMIT 10')
    top_users = cursor.fetchall()
    return top_users

async def send_top_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top_users = get_top_users()
    message = "Топ 10 пользователей по очкам:\n"
    for i, (username, balance) in enumerate(top_users, start=1):
        message += f"{i}. {username}: {balance}\n"
    await context.bot.send_message(chat_id="-1002171062047", text=message, message_thread_id=12)

async def daily_reward(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_name = update.message.from_user.username or update.message.from_user.name

    cursor.execute('SELECT ID, last_reward_time, balance FROM users WHERE ID = ?', (user_id,))
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

    reward_amount = random.randint(1, 200) if user_bal > 3000 else random.randint(250, 300) if user_bal > 2000 else random.randint(390, 500)
    cursor.execute('UPDATE users SET balance = balance + ?, last_reward_time = ? WHERE ID = ?', (reward_amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user_id))
    conn.commit()

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Буст для {user_name} на сегодня {reward_amount} очков', message_thread_id=12)

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type != Chat.PRIVATE:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Эта команда доступна только в личных сообщениях.', message_thread_id=12)
        return

    user_name = update.message.from_user.username
    if user_name not in ['hlebnastole', 'why_dyrachyo', 'sdmfy']:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='У вас нет доступа к этой программе')
        return

    args = context.args
    if len(args) != 2:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Используйте команду в формате: /balance "username" "число"')
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
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Пользователь {target_username} не найден в базе данных.')
        return

    cursor.execute('UPDATE users SET balance = balance + ? WHERE username = ?', (amount, target_username))
    conn.commit()
    cursor.execute('SELECT balance FROM users WHERE username = ?', (target_username,))
    bal = cursor.fetchone()[0]
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Баланс пользователя {target_username} теперь {bal}.')

async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.effective_chat.type != Chat.PRIVATE:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Эта команда доступна только в личных сообщениях.', message_thread_id=12)
        return

    user_name = update.message.from_user.username
    if user_name not in ['hlebnastole', 'sdmfy', 'why_dyrachyo']:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='У вас нет доступа к этой команде')
        return

    target_chat_id = '-1002171062047'
    if update.message.photo:
        photo = update.message.photo[-1]
        photo_file = await photo.get_file()
        await context.bot.send_photo(chat_id=target_chat_id, photo=photo_file.file_id, caption=update.message.caption, message_thread_id=12)
    else:
        message_text = ' '.join(context.args)
        await context.bot.send_message(chat_id=target_chat_id, text=message_text, message_thread_id=12)

    await context.bot.send_message(chat_id=update.effective_chat.id, text='Сообщение отправлено.')

async def send_anonymous_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global message_id_counter
    if update.effective_chat.type == Chat.PRIVATE:
        user_id = update.message.from_user.id
        message_text = update.message.text
        photo = None

        if update.message.photo:
            photo = update.message.photo[-1]
            photo_file = await photo.get_file()
            photo_file_id = photo_file.file_id

        message_id_counter += 1
        message_id = message_id_counter

        pending_messages[message_id] = {'user_id': user_id, 'text': message_text, 'photo_file_id': photo_file_id if photo else None}

        admin_chat_id = '1432989775'
        keyboard = [
            [InlineKeyboardButton("Отправить", callback_data=f"approve_{message_id}")],
            [InlineKeyboardButton("Отклонить", callback_data=f"reject_{message_id}")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=admin_chat_id, text=f"Пользователь анонимно отправил сообщение:\n{message_text}", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    query.answer()

    action, message_id = query.data.split('_')
    message_id = int(message_id)

    if message_id not in pending_messages:
        await context.bot.send_message(chat_id=query.message.chat_id, text="Сообщение не найдено.")
        return

    if action == 'approve':
        message_info = pending_messages[message_id]
        target_chat_id = "-1002171062047"
        if message_info['photo_file_id']:
            await context.bot.send_photo(chat_id=target_chat_id, photo=message_info['photo_file_id'], caption=f"Новое сообщение от анонимного пользователя:\n{message_info['text']}", message_thread_id=16)
        else:
            await context.bot.send_message(chat_id=target_chat_id, text=f"Новое сообщение от анонимного пользователя:\n{message_info['text']}", message_thread_id=16)
        await context.bot.send_message(chat_id=query.message.chat_id, text=f"Отправлено в чат.")
    elif action == 'reject':
        await context.bot.send_message(chat_id=query.message.chat_id, text=f"Отклонено.")

    pending_messages.pop(message_id, None)

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global quizzes

    if update.effective_chat.type != Chat.PRIVATE:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Эта команда доступна только в личных сообщениях.', message_thread_id=12)
        return

    user_name = update.message.from_user.username
    if user_name not in ['hlebnastole', 'why_dyrachyo', 'sdmfy']:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='У вас нет доступа к этой команде')
        return

    args = context.args
    if len(args) != 2:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Используйте команду в формате: /quiz "слово" "число"')
        return

    word = args[0]
    points = args[1]

    quiz_id = len(quizzes) + 1
    quizzes.append({'id': quiz_id, 'word': word.lower(), 'points': points})

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Квиз начат с словом '{word}' и {points} баллами. Идентификатор квиза: {quiz_id}")

async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global quizzes
    global message_id_counter
    if update.effective_chat.type == Chat.PRIVATE:
        user_id = update.message.from_user.id
        message_text = update.message.text
        message_id_counter += 1
        message_id = message_id_counter

        pending_messages[message_id] = {'user_id': user_id, 'text': message_text}

        admin_chat_id = '1432989775'
        keyboard = [
            [InlineKeyboardButton("Отправить", callback_data=f"approve_{message_id}")],
            [InlineKeyboardButton("Отклонить", callback_data=f"reject_{message_id}")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=admin_chat_id, text=f"Пользователь анонимно отправил сообщение:\n{message_text}", reply_markup=reply_markup)
        return

    if not quizzes:
        return

    user_answer = update.message.text.lower()

    current_quiz = quizzes[0]
    if user_answer == current_quiz['word']:
        user_id = update.message.from_user.id
        user_name = update.message.from_user.username or update.message.from_user.name

        cursor.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (current_quiz['points'], user_id))
        conn.commit()

        await context.bot.send_message(chat_id="-1002171062047", text=f"{user_name} угадал слово и получает {current_quiz['points']} очков.", reply_to_message_id=update.message.message_id, message_thread_id=12)

        quizzes.pop(0)

async def lood(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global lood_flag
    if update.effective_chat.type != Chat.PRIVATE:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Эта команда доступна только в личных сообщениях.', message_thread_id=12)
        return

    user_name = update.message.from_user.username
    if user_name not in ['hlebnastole', 'why_dyrachyo', 'sdmfy']:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='У вас нет доступа к этой команде')
        return

    if context.args[0] == 'Y':
        lood_flag = True
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Лудка разрешена')
    elif context.args[0] == 'N':
        lood_flag = False
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Лудка запрещена')
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Возможные параметры команды Y/N')

async def good_morning(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_name = update.message.from_user.username or update.message.from_user.name

    cursor.execute('SELECT ID, morning FROM users WHERE ID = ?', (user_id,))
    existing_user = cursor.fetchone()

    if not existing_user:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Вы не зарегистрированы. Пожалуйста, используйте команду /register.', message_thread_id=12)
        return

    if update.message.message_thread_id == 2:
        day = existing_user[1]
        current = datetime.now().day
        current_time = datetime.now().time().hour
        if current_time > 12 or current_time < 6:
            await context.bot.send_message(chat_id=update.effective_chat.id, text='Слишком поздно для доброго утра!', message_thread_id=12)
            return
        if current != day:
            reward_amount = 100
            cursor.execute('UPDATE users SET balance = balance + ? WHERE ID = ?', (reward_amount, user_id))
            conn.commit()
            cursor.execute('UPDATE users SET morning = ? WHERE ID = ?', (current, user_id))
            conn.commit()

            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'За пожелание доброго утра {user_name} получает +100 очков.', message_thread_id=12)

async def duels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    global duel_info

    if not duel_info:
        cursor.execute('SELECT balance, username, ID FROM users WHERE ID = ?', (user_id,))
        first_user = cursor.fetchone()

        if not first_user:
            await context.bot.send_message(chat_id=update.effective_chat.id, text='Вы не зарегистрированы. Пожалуйста, используйте команду /register.', message_thread_id=12)
            return ConversationHandler.END

        if first_user[0] < 25:
            await context.bot.send_message(chat_id=update.effective_chat.id, text='К сожалению вашего баланса не хватает для игры!', message_thread_id=12)
            return ConversationHandler.END

        duel_info.append(first_user)
        username = first_user[1]
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'{username} пришёл на дуэль. Ожидает соперника. Чтобы выйти на дуэль отправь ⚔️', message_thread_id=12)
    elif user_id != duel_info[0][2]:
        cursor.execute('SELECT balance, username, ID FROM users WHERE ID = ?', (user_id,))
        second_user = cursor.fetchone()

        if not second_user:
            await context.bot.send_message(chat_id=update.effective_chat.id, text='Вы не зарегистрированы. Пожалуйста, используйте команду /register.', message_thread_id=12)
            return ConversationHandler.END

        if second_user[0] < 25:
            await context.bot.send_message(chat_id=update.effective_chat.id, text='К сожалению вашего баланса не хватает для игры!', message_thread_id=12)
            return ConversationHandler.END

        duel_info.append(second_user)
        username_2 = second_user[1]
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'{username_2} и {duel_info[0][1]} дуэляться. У кого больше выпадет на кубике получает +25 очков. У кого меньше -25 очков', message_thread_id=12)

        await context.bot.send_message(chat_id=update.effective_chat.id, text='Бросок ' + duel_info[0][1] + ':', message_thread_id=12)
        dice_message = await context.bot.send_dice(chat_id=update.effective_chat.id, emoji=Dice.DICE, message_thread_id=12)
        result = [dice_message.dice.value]
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Бросок ' + duel_info[1][1] + ':', message_thread_id=12)
        dice_message = await context.bot.send_dice(chat_id=update.effective_chat.id, emoji=Dice.DICE, message_thread_id=12)
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

table_users = set()
players = {}
finished_players = set()

# Функция для создания клавиатуры
async def create_keyboard():
    keyboard = [[InlineKeyboardButton(text="Присоединиться", callback_data="join_game")]]
    return InlineKeyboardMarkup(keyboard)

# Функция для создания клавиатуры для игры
async def create_game_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="Ещё...", callback_data="take_card")],
        [InlineKeyboardButton(text="Хватит", callback_data="enough_card")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Функция для начала набора игроков
async def start_damn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat.id
    await context.bot.send_message(chat_id, "Набор на игру в 21. Присоединиться?", reply_markup=await create_keyboard())
    context.job_queue.run_once(deal_cards, 30, data=chat_id)

# Функция для обработки присоединения игрока
async def join_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username
    chat_id = query.message.chat.id

    if user_id in table_users:
        await query.answer("Ты уже за столом")
    else:
        table_users.add(user_id)
        usernames = []
        for user_id in table_users:
            chat_member = await context.bot.get_chat_member(chat_id, user_id)
            usernames.append(chat_member.user.username)
        await query.edit_message_text(f"Участники стола: {', '.join(usernames)}", reply_markup=await create_keyboard())

# Функция для раздачи карт
async def deal_cards(context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = context.job.data
    await context.bot.send_message(chat_id=chat_id, text="Игра началась!")
    suits = ['♠', '♣', '♥', '♦']
    values = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]
    deck = [(value, suit) for value in values for suit in suits]
    random.shuffle(deck)

    for user_id in table_users:
        hand = [deck.pop(), deck.pop()]
        players[user_id] = {
            'hand': hand,
            'score': 0,
            'username': (await context.bot.get_chat_member(chat_id, user_id)).user.username
        }
        await context.bot.send_message(user_id, "Твои карты: {}".format(', '.join(f"{card[0]}{card[1]}" for card in hand)), reply_markup=await create_game_keyboard())

# Функция для раздачи карты
def deal_card():
    suits = ['♠', '♣', '♥', '♦']
    values = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]
    deck = [(value, suit) for value in values for suit in suits]
    random.shuffle(deck)
    return deck.pop()

# Функция для подсчета очков
def calculate_score(hand):
    score = sum(card[0] for card in hand)
    if score > 21 and 11 in [card[0] for card in hand]:
        hand.remove((11, hand[hand.index((11, card[1]))][1]))
        hand.append((1, hand[hand.index((11, card[1]))][1]))
        score = sum(card[0] for card in hand)
    return score

# Функция для обработки действий игрока
async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat.id

    if user_id in players:
        if query.data == 'take_card':
            players[user_id]['hand'].append(deal_card())
            score = calculate_score(players[user_id]['hand'])
            if score == 21:
                await query.edit_message_text(f"Твои карты: {', '.join(f'{card[0]}{card[1]}' for card in players[user_id]['hand'])}")
            elif score > 21:
                await query.edit_message_text(f"Твои карты: {', '.join(f'{card[0]}{card[1]}' for card in players[user_id]['hand'])}")
                del players[user_id]
            else:
                await query.edit_message_text(f"Твои карты: {', '.join(f'{card[0]}{card[1]}' for card in players[user_id]['hand'])}\nЕщё?", reply_markup=await create_game_keyboard())
        elif query.data == 'enough_card':
            players[user_id]['score'] = calculate_score(players[user_id]['hand'])
            finished_players.add(user_id)
            await query.edit_message_text(f"Твои карты: {', '.join(f'{card[0]}{card[1]}' for card in players[user_id]['hand'])}\nТы остановился с {players[user_id]['score']} очками.")

            # Проверка, все ли игроки завершили игру
            if len(finished_players) == len(table_users):
                await announce_winners(context, chat_id)

# Функция для объявления победителей
async def announce_winners(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> None:
    winners = []
    max_score = 0

    for user_id, player in players.items():
        score = player['score']
        if score > max_score and score <= 21:
            max_score = score
            winners = [player['username']]
        elif score == max_score:
            winners.append(player['username'])

    if winners:
        winners_text = ', '.join(winners)
        await context.bot.send_message(chat_id="1002171062047", text=f"Победители: {winners_text} с {max_score} очками.")
    else:
        await context.bot.send_message(chat_id="1002171062047", text="Никто не выиграл.")

    # Очистка данных для новой игры
    table_users.clear()
    players.clear()
    finished_players.clear()

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler('damn', start_damn))
    application.add_handler(CallbackQueryHandler(join_game, pattern='^join_game$'))
    application.add_handler(CallbackQueryHandler(handle_action, pattern='^(take_card|enough_card)$'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex('^⚔️$'), duels))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex('^🚀$'), daily_reward))
    #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex('^21$'), start_game))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(
        '^(доброе утро|Доброе утро|Доброго утра|доброго утра|Доброе|доброе)$'), good_morning))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_anonymous_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_answer))
    application.add_handler(MessageHandler(filters.PHOTO & ~filters.COMMAND, send_message))
    application.add_handler(MessageHandler(filters.PHOTO & ~filters.COMMAND, send_anonymous_message))
    application.add_handler(MessageHandler(filters.Dice.ALL, handle_dice))
    application.add_handler(CallbackQueryHandler(button_callback))
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
