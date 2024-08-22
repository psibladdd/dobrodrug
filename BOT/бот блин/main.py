import logging
import sqlite3
import time
import random

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import json

logging.basicConfig(level=logging.INFO)

TOKEN = '7491056485:AAEOEEi60LJCv6lj1meW7Gika0nRmSuh1vM'
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users ( ID INTEGER PRIMARY KEY,name TEXT,balance INTEGER)')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='И зачем все это...)',message_thread_id=4)

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
        if current_balance < 100:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f'Недостаточный баланс для игры. Ваш текущий баланс: {current_balance}',
                                           message_thread_id=4)
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
            return
        time.sleep(2.5)
        if dice.emoji == '🎲':  # Кубик
            if dice.value == 1:
                new_balance = current_balance -50
                mess = f'КРИТИЧЕСКАЯ НЕУДАЧА ❗️😫 \n @{user_name} теряет 50 очков! \n Баланс @{user_name}: {new_balance}'
            elif dice.value == 2:
                new_balance = current_balance + 2
                mess = f'Неплохой бросок. \n @{user_name} получает 2 очка! \n Баланс @{user_name}: {new_balance}'
            elif dice.value == 3:
                new_balance = current_balance + 4
                mess = f'Отличный бросок. \n @{user_name} получает 4 очка! \n Баланс @{user_name}: {new_balance}'
            elif dice.value == 4:
                new_balance = current_balance + 6
                mess = f'Мастерский бросок. \n @{user_name} получает 6 очка! \n Баланс @{user_name}: {new_balance}'
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
                new_balance = current_balance -15
                mess = f'КРИТИЧЕСКАЯ НЕУДАЧА ❗️😫  \n @{user_name} теряет 15 очков! \n Баланс @{user_name}: {new_balance}'
            elif dice.value == 2:
                new_balance = current_balance + 1
                mess = f'И это всё на что ты способен ?🤨 \n @{user_name} получает 1 очков! \n Баланс @{user_name}: {new_balance}'
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
                new_balance = current_balance -15
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
                new_balance = current_balance - 15
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
                new_balance = current_balance - 15
                mess = f'Встань поближе и попробуй ещё раз \n @{user_name} теряет 15 очков! \n Баланс @{user_name}: {new_balance}'
            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()
            await context.bot.send_message(chat_id=update.effective_chat.id, text=mess,
                                           message_thread_id=4)

        elif dice.emoji == '⚽':  # Кубик
            if dice.value > 2:
                new_balance = current_balance +15
                mess = f'Шиииииш. Отличный удар🥳 \n @{user_name} получает 15 очков! \n Баланс @{user_name}: {new_balance}'
            elif dice.value <3:
                new_balance = current_balance - 20
                mess = f'Ты как Дантес! Косишь на оба глаза? \n @{user_name} теряет 20 очков! \n Баланс @{user_name}: {new_balance}'
            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()
            await context.bot.send_message(chat_id=update.effective_chat.id, text=mess,
                                           message_thread_id=4)

        elif dice.emoji == '🎰':  # Кубик
            if dice.value == 1:
                new_balance = current_balance +5
                mess = f'Как вкусно... \n @{user_name} получает 20 очков! \n Баланс @{user_name}: {new_balance}'
            elif dice.value == 22:
                new_balance = current_balance + 10
                mess = f'А теперь уже кисленько... Зато выйграл! \n @{user_name} получает 30 очков! \n Баланс @{user_name}: {new_balance}'
            elif dice.value == 43:
                new_balance = current_balance + 15
                mess = f'ВОУ! Это уже приятно! \n @{user_name} получает 40 очков! \n Баланс @{user_name}: {new_balance}'

            elif dice.value == 16 or dice.value == 32 or dice.value == 48:
                new_balance = current_balance + 20
                mess = f'АААААА ТАК БЛИЗКО \n @{user_name} получает 50 очков! \n Баланс @{user_name}: {new_balance}'
            elif dice.value ==64:
                new_balance = current_balance + 25
                mess = f'Джекпот! Удача на твоей стороне 💸 \n @{user_name} получает 50 очков! \n Баланс @{user_name}: {new_balance}'
            else:
                new_balance = current_balance - 10
                mess = f'Удача покинула тебя 😔 \n @{user_name} теряет 10 очков! \n Баланс @{user_name}: {new_balance}'

            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()
            await context.bot.send_message(chat_id=update.effective_chat.id, text=mess,
                                           message_thread_id=4)


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name

    cursor.execute('SELECT ID FROM users WHERE ID = ?', (user_id,))
    existing_user = cursor.fetchone()

    if existing_user:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Вы уже зарегистрированы.',message_thread_id=4)
    else:
        cursor.execute('INSERT INTO users (ID, name, balance) VALUES (?, ?, ?)', (user_id, first_name, 1000))
        conn.commit()
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Вы успешно зарегистрированы!',message_thread_id=4)

async def admin (update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.message_thread_id == 4:
        user_id = update.message.from_user.id
        chat_id = update.effective_chat.id
        chat_member = await context.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        if chat_member.status not in ['administrator', 'creator']:
            await context.bot.send_message(chat_id=chat_id, text='У вас нет прав администратора.')
            return

            # Логика команды, если пользователь является администратором
        await context.bot.send_message(chat_id=chat_id, text='Команда выполнена.')
def main():
    application = ApplicationBuilder().token(TOKEN).build()
    print()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.Dice.ALL, handle_dice))
    application.add_handler(CommandHandler('register', register))
    application.add_handler(CommandHandler('admin', admin))
    application.run_polling()

if __name__ == '__main__':
    main()
