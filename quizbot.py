import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import logging

import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Состояния разговора
QUESTION, RETRY = range(2)



# Ваш квиз
quiz = [
    {
        "question": "1. Как называется меч, который носил Фродо?",
        "options": ["Оркрист", "Гламдринг", "Жало", "Нарсил"],
        "correct_answer": 2
    },
    # Добавьте остальные вопросы
    {
        "question": "2. Кто уничтожил Кольцо Всевластья?",
        "options": ["Фродо", "Сэм", "Саурон", "Голлум"],
        "correct_answer": 3
    },

    {
        "question": "3. Как называется крепость Сарумана?",
        "options": ["Гондор", "Хельмова Падь", "Изенгард", "Минас-Тирит"],
        "correct_answer": 2
    },

    {
        "question": "4. Кто убил Балрога в шахтах Мории?",
        "options": ["Арагорн", "Фродо", "Леголас", "Гэндальф"],
        "correct_answer": 3
    },

    {
        "question": "5. Какому виду хоббита принадлежит Фродо?",
        "options": ["Горный хоббит", "Степной хоббит", "Мизинцы", "Бэггинсы"],
        "correct_answer": 3
    },

    {
        "question": "6. Как зовут отца Леголаса?",
        "options": ["Эльронд", "Глорфиндел", "Трандуил", "Галадриэль"],
        "correct_answer": 2
    },

    {
        "question": "7. Как назывался последний король Гондора?",
        "options": ["Теоден", "Эарнур", "Денетор", "Арагорн"],
        "correct_answer": 1
    },

    {
        "question": "8. Сколько членов было в Братстве Кольца?",
        "options": ["7", "8", "9", "10"],
        "correct_answer": 2
    },

    {
        "question": "9. Кто был первым носителем Единого Кольца?",
        "options": ["Саурон", "Исилдур", "Бильбо", "Фродо"],
        "correct_answer": 0
    },

    {
        "question": "10. Кто подарил Фродо мифриловую кольчугу?",
        "options": ["Арагорн", "Гэндальф", "Бильбо", "Леголас"],
        "correct_answer": 2
    }

]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Отправляем изображение с подписью
    await update.message.reply_photo(
        photo=open('welcome_image.jpg', 'rb'),
        caption=(
            "Чтобы получить заветное сокровище, испытание знаниями должны вы пройти. "
            "Для этого надо ответить на 10 вопросов, касающихся мира Средиземья. "
            "Силу свою проверить сможете, если хоббитов, эльфов и темных лордов мудрости постичь вы сумеете. "
            "Внимательно слушать, думать глубоко должны вы. Ошибетесь — путь к сокровищу тернист станет. "
            "Но, правильные ответы найдя, достойны великого приза окажетесь. "
            "Пусть знания и сила всегда с вами будут, искатели приключений."
        )
    )

    # Инициализируем данные пользователя
    context.user_data['score'] = 0
    context.user_data['current_question'] = 0

    # Переходим к первому вопросу
    return await ask_question(update, context)

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q_num = context.user_data['current_question']
    if q_num < len(quiz):
        question = quiz[q_num]
        reply_keyboard = [question['options']]
        await update.message.reply_text(
            question['question'],
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return QUESTION
    else:
        return await show_result(update, context)

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q_num = context.user_data['current_question']
    answer = update.message.text
    correct_option = quiz[q_num]['options'][quiz[q_num]['correct_answer']]
    if answer == correct_option:
        context.user_data['score'] += 1
    context.user_data['current_question'] += 1
    return await ask_question(update, context)

async def show_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    score = context.user_data['score']
    await update.message.reply_text(f"Вы набрали {score} из {len(quiz)} правильных ответов.")
    if 7 <= score <= 10:
        # Отправляем видео и код
        await update.message.reply_text("Поздравляем! Испытание Средиземья прошли вы успешно, храбрыми и мудрыми оказались.")
        await update.message.reply_video(video=open('congratulations.mp4', 'rb'))
        await update.message.reply_text("Теперь отправьте секретный код M1THRAND1R, чтобы к заветному призу приблизиться - t.me/secrethelperman")
        return ConversationHandler.END
    else:
        # Предлагаем попробовать еще раз
        reply_keyboard = [['Попробовать еще раз']]
        await update.message.reply_text(
            "К сожалению, вы не набрали достаточное количество правильных ответов.",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return RETRY

async def retry_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    if user_input == 'Попробовать еще раз':
        # Сбрасываем данные пользователя и начинаем сначала
        context.user_data['score'] = 0
        context.user_data['current_question'] = 0
        return await ask_question(update, context)
    else:
        await update.message.reply_text(
            "Если хотите попробовать еще раз, нажмите кнопку ниже.",
            reply_markup=ReplyKeyboardMarkup([['Попробовать еще раз']], one_time_keyboard=True)
        )
        return RETRY

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Квиз прерван.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
            RETRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, retry_quiz)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
