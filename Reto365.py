from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from datetime import datetime, timedelta
import random
import sqlite3

# Configura tu base de datos
def setup_database():
    conn = sqlite3.connect('savings_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS savings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            amount INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Comando /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "¡Hola! Soy tu bot de ahorro.\n"
        "Comandos disponibles:\n"
        "/random - Generar un número aleatorio de ahorro\n"
        "/add <cantidad> - Agregar manualmente una cantidad\n"
        "/total - Ver el acumulado de ahorro\n"
        "/help - Mostrar esta lista de comandos"
    )

# Generar un número aleatorio de ahorro
def random_number(update: Update, context: CallbackContext) -> None:
    number = random.randint(1, 365)
    conn = sqlite3.connect('savings_bot.db')
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute('INSERT INTO savings (date, amount) VALUES (?, ?)', (today, number))
    conn.commit()
    conn.close()
    update.message.reply_text(f"Hoy debes ahorrar: ${number}.")

# Agregar manualmente una cantidad
def add_amount(update: Update, context: CallbackContext) -> None:
    try:
        amount = int(context.args[0])
        today = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect('savings_bot.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO savings (date, amount) VALUES (?, ?)', (today, amount))
        conn.commit()
        conn.close()
        update.message.reply_text(f"Has agregado manualmente: ${amount}.")
    except (IndexError, ValueError):
        update.message.reply_text("Por favor, usa el comando así: /add <cantidad>.")

# Consultar el acumulado
def total_savings(update: Update, context: CallbackContext) -> None:
    conn = sqlite3.connect('savings_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(amount) FROM savings')
    result = cursor.fetchone()
    conn.close()
    total = result[0] if result[0] is not None else 0
    update.message.reply_text(f"Tu ahorro acumulado es: ${total}.")

# Configuración principal del bot
def main():
    # Reemplaza con tu token de Telegram
    TOKEN = "7773547401:AAFbfyH5doKpoQy3W02cjDYKr775uhZmcYg"
    updater = Updater(TOKEN)

    # Configura la base de datos
    setup_database()

    # Agrega manejadores de comandos
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("random", random_number))
    dispatcher.add_handler(CommandHandler("add", add_amount))
    dispatcher.add_handler(CommandHandler("total", total_savings))
    dispatcher.add_handler(CommandHandler("help", start))

    # Configura el recordatorio diario
    job_queue = updater.job_queue
    job_queue.run_daily(send_daily_reminder, time=datetime.now().replace(hour=9, minute=0, second=0))

    # Inicia el bot
    updater.start_polling()
    updater.idle()

# Enviar recordatorio diario
def send_daily_reminder(context: CallbackContext):
    chat_id = context.job.context
    number = random.randint(1, 365)
    context.bot.send_message(chat_id=chat_id, text=f"¡Tu número de ahorro de hoy es: ${number}!")

if __name__ == "__main__":
    main()
