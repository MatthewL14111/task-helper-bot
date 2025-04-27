
import os
from flask import Flask, request
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")
bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

tasks = {}

def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("➕ 添加任务", callback_data='add_task')],
        [InlineKeyboardButton("📋 查看任务", callback_data='view_tasks')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('欢迎使用任务助手！', reply_markup=reply_markup)

def button(update: Update, context):
    query = update.callback_query
    query.answer()
    if query.data == 'add_task':
        query.message.reply_text('请发送要添加的任务内容。')
        context.user_data['adding_task'] = True
    elif query.data == 'view_tasks':
        user_id = query.from_user.id
        user_tasks = tasks.get(user_id, [])
        if user_tasks:
            text = "\n".join(f"{idx+1}. {task}" for idx, task in enumerate(user_tasks))
        else:
            text = "暂无任务。"
        query.message.reply_text(text)

def message_handler(update: Update, context):
    user_id = update.message.from_user.id
    if context.user_data.get('adding_task'):
        task_content = update.message.text.strip()
        tasks.setdefault(user_id, []).append(task_content)
        update.message.reply_text(f"✅ 已添加任务：{task_content}")
        context.user_data['adding_task'] = False

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

@app.route('/')
def index():
    return 'Task Helper Bot is running.'

if __name__ == "__main__":
    from telegram.ext import ApplicationBuilder
    appbuilder = ApplicationBuilder().token(TOKEN).build()

    dispatcher = Dispatcher(bot, None, workers=4)
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
