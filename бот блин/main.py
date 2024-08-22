import logging
import sqlite3
import time
import random

from telegram import *
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import json

logging.basicConfig(level=logging.INFO)

SELECT_USER, ENTER_BALANCE = range(2)
TOKEN = '7491056485:AAEOEEi60LJCv6lj1meW7Gika0nRmSuh1vM'
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users ( ID INTEGER PRIMARY KEY, name TEXT, balance INTEGER, username TEXT)')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='И зачем все это...)', message_thread_id=4)

async def handle_dice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
                                        message_thread_id=4)
        return

    if update.message.message_thread_id == 4:
        if current_balance < 0:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f'Недостаточный баланс для игры. Ваш текущий баланс: {current_balance}',
                                           message_thread_id=4)
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
            return
        time.sleep(2.5)
        if dice.emoji == '🎲':  # Кубик
            if dice.value == 1:
                new_balance = current_balance - 50
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
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=mess,
                                           message_thread_id=4)

        elif dice.emoji == '🎳':  # Кубик
            if dice.value == 1:
                new_balance = current_balance - 15
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
            await context.bot.send_message(chat_id=update.effective_chat.id, text=mess,
                                           message_thread_id=4)
        elif dice.emoji == '🎯':  # Кубик
            if dice.value == 1:
                new_balance = current_balance - 15
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
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=mess,
                                           message_thread_id=4)

        elif dice.emoji == '🏀':  # Кубик
            if dice.value > 3:
                new_balance = current_balance + 20
                mess = f'Тебе завидует даже Джордан 😍 \n @{user_name} получает 20 очков! \n Баланс @{user_name}: {new_balance}'
            elif dice.value < 4:
                new_balance = current_balance - 20
                mess = f'Встань поближе и попробуй ещё раз \n @{user_name} теряет 20 очков! \n Баланс @{user_name}: {new_balance}'
            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()
            await context.bot.send_message(chat_id=update.effective_chat.id, text=mess,
                                           message_thread_id=4)

        elif dice.emoji == '⚽':  # Кубик
            if dice.value > 2:
                new_balance = current_balance + 20
                mess = f'Шиииииш. Отличный удар🥳 \n @{user_name} получает 20 очков! \n Баланс @{user_name}: {new_balance}'
            elif dice.value < 3:
                new_balance = current_balance - 20
                mess = f'Ты как Дантес! Косишь на оба глаза? \n @{user_name} теряет 20 очков! \n Баланс @{user_name}: {new_balance}'
            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()
            await context.bot.send_message(chat_id=update.effective_chat.id, text=mess,
                                           message_thread_id=4)

        elif dice.emoji == '🎰':  # Кубик
            if dice.value == 24 or dice.value == 25 or dice.value == 26 or dice.value == 18 or dice.value == 30 or dice.value == 38  or dice.value == 54:
                new_balance = current_balance + 5
                mess = f'Как вкусно... \n @{user_name} получает 5 очков! \n Баланс @{user_name}: {new_balance}'
            elif dice.value == 21 or dice.value == 35 or dice.value == 27 or dice.value == 11 or dice.value == 47 or dice.value == 39 or dice.value == 42 or dice.value == 59 or dice.value == 41:
                new_balance = current_balance + 7
                mess = f'А теперь уже кисленько... Зато выйграл! \n @{user_name} получает 7 очков! \n Баланс @{user_name}: {new_balance}'
            elif dice.value == 17 or dice.value == 13 or dice.value == 3 or dice.value == 4 or dice.value == 9 or dice.value == 5 or dice.value == 2 or dice.value == 49 or dice.value == 33 or dice.value == 18:
                new_balance = current_balance + 3
                mess = f'ВОУ! Это уже приятно! \n @{user_name} получает 3 очка! \n Баланс @{user_name}: {new_balance}'

            elif dice.value == 16 or dice.value == 63  or dice.value == 56 or dice.value == 52 or dice.value == 48 or dice.value == 61 or dice.value == 62 or dice.value == 60:
                new_balance = current_balance + 10
                mess = f'АААААА ТАК БЛИЗКО \n @{user_name} получает 10 очков! \n Баланс @{user_name}: {new_balance}'
            elif dice.value == 1 or dice.value == 22 or dice.value == 43 or dice.value == 64:
                new_balance = current_balance + 50
                mess = f'Джекпот! Удача на твоей стороне 💸 \n @{user_name} получает 50 очков! \n Баланс @{user_name}: {new_balance}'
            else:
                new_balance = current_balance - 30
                mess = f'{dice.value} Удача покинула тебя 😔 \n @{user_name} теряет 30 очков! \n Баланс @{user_name}: {new_balance}'

            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()
            await context.bot.send_message(chat_id=update.effective_chat.id, text=mess,
                                           message_thread_id=4)

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    user_name = update.message.from_user.username

    cursor.execute('SELECT ID FROM users WHERE ID = ?', (user_id,))
    existing_user = cursor.fetchone()

    if existing_user:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Вы уже зарегистрированы.', message_thread_id=4)
    else:
        cursor.execute('INSERT INTO users (ID, name, balance, username) VALUES (?, ?, ?, ?)', (user_id, first_name, 1000, user_name))
        conn.commit()
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Вы успешно зарегистрированы!', message_thread_id=4)

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type != Chat.PRIVATE:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Эта команда доступна только в личных сообщениях.', message_thread_id=4)
        return

    user_name = update.message.from_user.username
    if user_name == 'hlebnastole' or user_name == 'why_dyrachyo':
        keyboard = [
            [KeyboardButton("Изменить баланс пользователя")],
            [KeyboardButton("Скрытно кого-то послать")],
            [KeyboardButton("Создать квизз")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Привет, {user_name}! Чем могу быть полезен?', reply_markup=reply_markup)
        return
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='ебать ты лох')



async def button1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Введите username пользователя, которому хотите изменить баланс:')
    return SELECT_USER

async def select_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_name = update.message.text
    cursor.execute('SELECT username FROM users WHERE username = ?', (user_name,))
    existing_user = cursor.fetchone()

    if not existing_user:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Пользователь {user_name} не найден в базе данных.')
        return ConversationHandler.END

    context.user_data['selected_user'] = user_name
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Введите новый баланс для пользователя {user_name}:')
    return ENTER_BALANCE

async def enter_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        new_balance = int(update.message.text)
    except ValueError:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Пожалуйста, введите корректное число.')
        return ENTER_BALANCE

    selected_user = context.user_data['selected_user']

    # Обновление баланса в базе данных
    cursor.execute('UPDATE users SET balance = ? WHERE username = ?', (new_balance, selected_user))
    conn.commit()

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Баланс пользователя {selected_user} обновлен на {new_balance}.')
    return ConversationHandler.END





async def button2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Вы нажали Кнопку 2")

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('admin', admin)],
        states={
            SELECT_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_user)],
            ENTER_BALANCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_balance)],
        },
        fallbacks=[],
    )

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.Dice.ALL, handle_dice))
    application.add_handler(CommandHandler('register', register))
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^Изменить баланс пользователя$'), button1))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^Скрытно кого-то послать$'), button2))

    application.run_polling()

if __name__ == '__main__':
    main()


if __name__ == '__main__':
    main()

