import logging
import sqlite3
import time
import random

from telegram import *
from telegram.ext import *
import json

logging.basicConfig(level=logging.INFO)

SELECT_USER, ENTER_BALANCE, SEND_MESSAGE = range(3)
TOKEN = '7491056485:AAEOEEi60LJCv6lj1meW7Gika0nRmSuh1vM'
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
lood_flag = True
cursor.execute('CREATE TABLE IF NOT EXISTS users ( ID INTEGER PRIMARY KEY, name TEXT, balance INTEGER, username TEXT)')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='И зачем все это...)', message_thread_id=12)

async def handle_dice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global lood_flag
    if not lood_flag:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
        return

    dice = update.message.dice
    user_name = update.message.from_user.username
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

    if (update.message.message_thread_id == 4 and lood_flag == True):
        if current_balance <= 0:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f'Недостаточный баланс для игры. Ваш текущий баланс: {current_balance}',
                                           message_thread_id=12)
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
            return
        time.sleep(2)
        if dice.emoji == '🎲':  # Кубик
            if dice.value == 1:
                new_balance = current_balance - 50
                if (new_balance < 0): new_balance = 0
                mess = f'КРИТИЧЕСКАЯ НЕУДАЧА ❗️😫 \n @{user_name} теряет 50 очков! \n Баланс @{user_name}: {new_balance}'
            elif dice.value == 2:
                new_balance = current_balance + 2
                mess = f'Неплохой бросок. \n @{user_name} получает 2 очка! \n Баланс @{user_name}: {new_balance}'
            elif dice.value == 3:
                new_balance = current_balance + 4
                mess = f'Отличный бросок. \n @{user_name} получает 4 очка! \n Баланс @{user_name}: {new_balance}'
            elif dice.value == 4:
                new_balance = current_balance + 6
                mess = f'Мастерский бросок. \n @{user_name} получает 6 очков! \n Баланс @{user_name}: {new_balance}'
            elif dice.value == 5:
                new_balance = current_balance + 8
                mess = f'Офигенный бросок! \n @{user_name} получает 8 очков! \n Баланс @{user_name}: {new_balance}'
            elif dice.value == 6:
                new_balance = current_balance + 10
                mess = f'ЧТО ОН ТВОРИТ 🤯!!?? \n @{user_name} получает 10 очков! \n Баланс @{user_name}: {new_balance}'
            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()
            await context.bot.send_message(chat_id=update.effective_chat.id,reply_to_message_id=update.message.message_id,
                                           text=mess,
                                           message_thread_id=12)

        elif dice.emoji == '🎳':  # Кубик
            if dice.value == 1:
                new_balance = current_balance - 15
                if (new_balance < 0): new_balance = 0
                mess = f'КРИТИЧЕСКАЯ НЕУДАЧА ❗️😫  \n @{user_name} теряет 15 очков! \n Баланс @{user_name}: {new_balance}'
            elif dice.value == 2:
                new_balance = current_balance + 1
                mess = f'И это всё на что ты способен ?🤨 \n @{user_name} получает 1 очко! \n Баланс @{user_name}: {new_balance}'
            elif dice.value == 3:
                new_balance = current_balance + 3
                mess = f'Для начала не плохо. Продолжаем 👀 \n @{user_name} получает 3 очка! \n Баланс @{user_name}: {new_balance}'
            elif dice.value == 4:
                new_balance = current_balance + 5
                mess = f'Было близко💅  \n @{user_name} получает 5 очков! \n Баланс @{user_name}: {new_balance}'
            elif dice.value == 5:
                new_balance = current_balance + 7
                mess = f'ТАК БЛИЗКО 🥹 \n @{user_name} получает 7 очков! \n Баланс @{user_name}: {new_balance}'
            elif dice.value == 6:
                new_balance = current_balance + 15
                mess = f'СТРАААЙК 👊 \n @{user_name} получает 15 очков! \n Баланс @{user_name}: {new_balance}'

            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()
            await context.bot.send_message(chat_id=update.effective_chat.id, text=mess,reply_to_message_id=update.message.message_id,
                                           message_thread_id=12)
        elif dice.emoji == '🎯':  # Кубик
            if dice.value == 1:
                new_balance = current_balance - 15
                if (new_balance < 0): new_balance = 0
                mess = f'Мдаа... меткость - не твоё \n @{user_name} теряет 15 очков! \n Баланс @{user_name}: {new_balance}'
            elif dice.value == 2:
                new_balance = current_balance + 1
                mess = f'Ну.. Хотя бы попал  \n @{user_name} получает 1 очко! \n Баланс @{user_name}: {new_balance}'
            elif dice.value == 3:
                new_balance = current_balance + 3
                mess = f'Уже лучше! Пробуй еще! \n @{user_name} получает 3 очка! \n Баланс @{user_name}: {new_balance}'
            elif dice.value == 4:
                new_balance = current_balance + 5
                mess = f'Нормально.. Стабильно.. \n @{user_name} получает 5 очков! \n Баланс @{user_name}: {new_balance}'
            elif dice.value == 5:
                new_balance = current_balance + 7
                mess = f'Это было очень близко \n @{user_name} получает 7 очков! \n Баланс @{user_name}: {new_balance}'
            elif dice.value == 6:
                new_balance = current_balance + 15
                mess = f'В яблочко 🍎  \n @{user_name} получает 15 очков! \n Баланс @{user_name}: {new_balance}'

            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()
            await context.bot.send_message(chat_id=update.effective_chat.id,reply_to_message_id=update.message.message_id,
                                           text=mess,
                                           message_thread_id=12)

        elif dice.emoji == '🏀':  # Кубик
            if dice.value > 3:
                new_balance = current_balance + 20
                mess = f'Тебе завидует даже Джордан 😍 \n @{user_name} получает 20 очков! \n Баланс @{user_name}: {new_balance}'
            elif dice.value < 4:
                new_balance = current_balance - 20
                if (new_balance < 0): new_balance = 0
                mess = f'Встань поближе и попробуй ещё раз \n @{user_name} теряет 20 очков! \n Баланс @{user_name}: {new_balance}'

            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()
            await context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.message.message_id,text=mess,
                                           message_thread_id=12)

        elif dice.emoji == '⚽':  # Кубик
            if dice.value > 2:
                new_balance = current_balance + 20
                mess = f'Шиииииш. Отличный удар🥳 \n @{user_name} получает 20 очков! \n Баланс @{user_name}: {new_balance}'
            elif dice.value < 3:
                new_balance = current_balance - 20
                if (new_balance < 0): new_balance = 0
                mess = f'Ты как Дантес! Косишь на оба глаза? \n @{user_name} теряет 20 очков! \n Баланс @{user_name}: {new_balance}'

            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()
            await context.bot.send_message(chat_id=update.effective_chat.id,reply_to_message_id=update.message.message_id, text=mess,
                                           message_thread_id=12)

        elif dice.emoji == '🎰':  # Кубик
            if dice.value == 24 or dice.value == 25 or dice.value == 23 or dice.value == 18 or dice.value == 6 or dice.value == 26 or dice.value == 30 or dice.value == 38 or dice.value == 54:
                new_balance = current_balance + 5
                mess = f'Как вкусно... \n @{user_name} получает 5 очков! \n Баланс @{user_name}: {new_balance}'
            elif dice.value == 21 or dice.value == 35 or dice.value == 44 or dice.value == 27 or dice.value == 11 or dice.value == 47 or dice.value == 39 or dice.value == 42 or dice.value == 59 or dice.value == 41:
                new_balance = current_balance + 7
                mess = f'А теперь уже кисленько... Зато выйграл! \n @{user_name} получает 7 очков! \n Баланс @{user_name}: {new_balance}'
            elif dice.value == 17 or dice.value == 13 or dice.value == 3 or dice.value == 4 or dice.value == 9 or dice.value == 5 or dice.value == 2 or dice.value == 49 or dice.value == 33:
                new_balance = current_balance + 3
                mess = f'ВОУ! Это уже приятно! \n @{user_name} получает 3 очка! \n Баланс @{user_name}: {new_balance}'

            elif dice.value == 16 or dice.value == 63 or dice.value == 56 or dice.value == 52 or dice.value == 48 or dice.value == 61 or dice.value == 62 or dice.value == 60:
                new_balance = current_balance + 10
                mess = f'АААААА ТАК БЛИЗКО \n @{user_name} получает 10 очков! \n Баланс @{user_name}: {new_balance}'
            elif dice.value == 1 or dice.value == 22 or dice.value == 43 or dice.value == 64:
                new_balance = current_balance + 50
                mess = f'Джекпот! Удача на твоей стороне 💸 \n @{user_name} получает 50 очков! \n Баланс @{user_name}: {new_balance}'
            else:
                new_balance = current_balance - 20
                if (new_balance < 0): new_balance = 0
                mess = f'{dice.value}Удача покинула тебя 😔 \n @{user_name} теряет 20 очков! \n Баланс @{user_name}: {new_balance}'

            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()
            await context.bot.send_message(chat_id=update.effective_chat.id,reply_to_message_id=update.message.message_id, text=mess,
                                           message_thread_id=12)
    else:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
        return

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    user_name = '@' + update.message.from_user.username

    cursor.execute('SELECT ID FROM users WHERE ID = ?', (user_id,))
    existing_user = cursor.fetchone()

    if existing_user:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Вы уже зарегистрированы.',
                                       message_thread_id=12)
    else:
        cursor.execute('INSERT INTO users (ID, name, balance, username) VALUES (?, ?, ?, ?)',
                       (user_id, first_name, 1500, user_name))
        conn.commit()
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Вы успешно зарегистрированы!',
                                       message_thread_id=12)

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(update.effective_chat.id)
    if update.effective_chat.type != Chat.PRIVATE:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='Эта команда доступна только в личных сообщениях.', message_thread_id=12)
        return

    user_name = update.message.from_user.username
    if user_name not in ['hlebnastole', 'why_dyrachyo']:
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
    if user_name not in ['hlebnastole', 'why_dyrachyo', 'sdmfy']:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='У вас нет доступа к этой команде')
        return
    args = context.args
    message_text = ' '.join(args)
    target_chat_id = '-2171062047'  # Замените на ID целевого чата

    await context.bot.send_message(chat_id=target_chat_id, text=message_text, message_thread_id=12)
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Сообщение отправлено.')

quiz_word = None
quiz_points = None

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global quiz_word, quiz_points

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

    quiz_word = word.lower()
    quiz_points = points

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Квиз начат с словом '{word}' и {points} баллами.")

async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global quiz_word, quiz_points

    if quiz_word is None or quiz_points is None:
        return

    user_answer = update.message.text.lower()

    if user_answer == quiz_word:
        user_name = update.message.from_user.username
        cursor.execute('UPDATE users SET balance = balance + ? WHERE username = ?', (quiz_points, user_name))
        conn.commit()
        await context.bot.send_message(chat_id="-2171062047", text=f"@{user_name} угадал первый и получает {quiz_points} очков.", reply_to_message_id=update.message.message_id,message_thread_id=12)

        # Сброс состояния квиза
        quiz_word = None
        quiz_points = None

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

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.Dice.ALL, handle_dice))
    application.add_handler(CommandHandler('register', register))
    application.add_handler(CommandHandler('balance', balance))
    application.add_handler(CommandHandler('write', send_message))
    application.add_handler(CommandHandler('quiz', quiz))
    application.add_handler(CommandHandler('lood', lood))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_answer))

    application.run_polling()

if __name__ == '__main__':
    main()
