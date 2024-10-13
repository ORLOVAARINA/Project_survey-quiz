from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters import Command

BOT_TOKEN = '6807340372:AAG0aXi2JwDkb1ewyxZax98iivmU_8GGHXs'
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Опросные вопросы
survey_questions = [
  "Какой ваш любимый цвет?",
  "Какой ваш любимый сезон?",
  "Какой ваш любимый спорт?"
]

# Викторина 1
quizzes_1 = [
  {"question": "Какое животное самое быстрое?", "options": ["Гепард", "Лев", "Тигр"], "correct_otvet": 0},
  {"question": "Какая самая большая планета в Солнечной системе?", "options": ["Юпитер", "Сатурн", "Нептун"], "correct_otvet": 0},
  {"question": "Какое дерево самое высокое?", "options": ["Секвойя", "Дуб", "Ель"], "correct_otvet": 0}
]

# Викторина 2
quizzes_2 = [
  {"question": "Какая самая высокая гора в мире?", "options": ["Эверест", "Канченджанга", "Лхоцзе"], "correct_otvet": 0},
  {"question": "Какая самая длинная река в мире?", "options": ["Амазонка", "Нил", "Янцзы"], "correct_otvet": 1},
  {"question": "Какое государство самое большое по площади?", "options": ["Россия", "Канада", "Китай"], "correct_otvet": 1}
]

kb_builder = ReplyKeyboardBuilder()
kb_builder.row(KeyboardButton(text='Пройти опрос'), KeyboardButton(text='Пройти викторину 1'), KeyboardButton(text='Пройти викторину 2'), width=3)
keyboard = kb_builder.as_markup(resize_keyboard=True)

user_progress = {}

@dp.message(Command(commands='start'))
async def process_start_command(message: Message):
  await message.answer('Привет! Выбери действие:', reply_markup=keyboard)

async def ask_survey_question(message: Message):
  user_id = message.from_user.id
  step = user_progress[user_id]["survey_step"]
  question = survey_questions[step]
  await message.answer(question, reply_markup=types.ReplyKeyboardRemove()) # Убираем клавиатуру для ввода текста

async def quiz_question(message: Message, step: int, quiz_list):
  quiz = quiz_list[step]
  kb = ReplyKeyboardBuilder().row(*(KeyboardButton(text=opt) for opt in quiz["options"])).as_markup(resize_keyboard=True)
  await message.answer(quiz["question"], reply_markup=kb)

@dp.message(lambda message: message.text == 'Пройти опрос')
async def start_survey(message: Message):
  user_progress[message.from_user.id] = {"survey_step": 0, "survey_answers": []}
  await ask_survey_question(message)

@dp.message(lambda message: message.text == 'Пройти викторину 1')
async def start_quiz_1(message: Message):
    user_progress[message.from_user.id] = {"quiz_step": 0, "correct_answers": 0, "quiz_number": 1}
    await quiz_question(message, 0, quizzes_1)

@dp.message(lambda message: message.text == 'Пройти викторину 2')
async def start_quiz_2(message: Message):
    user_progress[message.from_user.id] = {"quiz_step": 0, "correct_answers": 0, "quiz_number": 2}
    await quiz_question(message, 0, quizzes_2)

@dp.message(lambda message: message.from_user.id in user_progress and "survey_step" in user_progress[message.from_user.id])
async def handle_survey_answer(message: Message):
    user_id = message.from_user.id
    step = user_progress[user_id]["survey_step"]
    user_progress[user_id]["survey_answers"].append(message.text)

    if step + 1 < len(survey_questions):
        user_progress[user_id]["survey_step"] += 1
        await ask_survey_question(message)
    else:
        results = "\n".join(f"{q}: {a}" for q, a in zip(survey_questions, user_progress[user_id]["survey_answers"]))
        await message.answer(f"Спасибо за участие в опросе!\nВаши ответы:\n{results}", reply_markup=keyboard)
        del user_progress[user_id]  # Очищаем данные пользователя после завершения опроса

@dp.message(lambda message: message.from_user.id in user_progress and "quiz_step" in user_progress[message.from_user.id])
async def handle_quiz_answer(message: Message):
    user_id = message.from_user.id
    step = user_progress[user_id]["quiz_step"]
    user_progress[user_id].setdefault("quiz_answers", []).append(message.text)
    quiz_list = quizzes_1 if user_progress[user_id]["quiz_number"] == 1 else quizzes_2

    if step + 1 < len(quiz_list):
        user_progress[user_id]["quiz_step"] += 1
        await quiz_question(message, user_progress[user_id]["quiz_step"], quiz_list)
    else:
        correct_answers = sum(
            1 for i, answer in enumerate(user_progress[user_id]["quiz_answers"])
            if i < len(quiz_list) and answer == quiz_list[i]["options"][quiz_list[i]["correct_otvet"]]
        )
        total_questions = len(quiz_list)
        await message.answer(f"Спасибо за участие! Правильных ответов: {correct_answers} из {total_questions}", reply_markup=keyboard)

if __name__ == '__main__':
    dp.run_polling(bot)
