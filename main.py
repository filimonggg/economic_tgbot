from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from tgtoken import token
from time import sleep
import pandas as pd
from taskBD import get_task_list, get_task_el
from random import choice

bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
topic = None
level = None
task_id = None
task = None
ans_dict = dict()
c = 0
id_list = list()

b_go_back = [[KeyboardButton('Назад')]]
go_back = ReplyKeyboardMarkup(keyboard=b_go_back, resize_keyboard=True)
b_see_solution_kb = [[KeyboardButton('Посмотреть решение')]]
see_solution_kb = ReplyKeyboardMarkup(keyboard=b_see_solution_kb, resize_keyboard=True,
                                      input_field_placeholder='Чтобы посмотреть ответ решение, нажми на кнопку')
b_go_to_main_menu = [[KeyboardButton('Вернуться на главное меню')]]
go_to_main_menu = ReplyKeyboardMarkup(keyboard=b_go_to_main_menu, resize_keyboard=True,
                                      input_field_placeholder='Вернуться на главное меню')
b_see_solortryagain_kb = [[KeyboardButton('Посмотреть решение'), KeyboardButton('Попробовать еще раз')]]
see_solortryagain_kb = ReplyKeyboardMarkup(keyboard=b_see_solortryagain_kb, resize_keyboard=True,
                                           input_field_placeholder='Попробуй еще раз или посмотри решение')
b_first_option_kb = [[KeyboardButton('Проверить свой уровень'), KeyboardButton('База заданий')]]
first_option_kb = ReplyKeyboardMarkup(keyboard=b_first_option_kb, resize_keyboard=True,
                                      input_field_placeholder='Выбери действие')
b_db_kb = [[KeyboardButton('а'), KeyboardButton('б'), KeyboardButton('в'), KeyboardButton('г'), KeyboardButton('д'),
            KeyboardButton('е'), KeyboardButton('ж'), KeyboardButton('з')]]
db_kb = ReplyKeyboardMarkup(keyboard=b_db_kb, resize_keyboard=True, input_field_placeholder='Выбери тему').add(
    KeyboardButton('Назад'))
b_level_kb = [[KeyboardButton('Обычная сложность'), KeyboardButton('Повышенная сложность')]]
level_kb = ReplyKeyboardMarkup(keyboard=b_level_kb, resize_keyboard=True, input_field_placeholder='Выбери уровень').add(
    KeyboardButton('Назад'))
id_topic = {'а': 'Альтернативные издержки', 'б': 'КПВ', 'в': 'Спрос и предложение', 'г': 'Эластичность',
            'д': 'Производство и издержки', 'е': 'Рыночные структуры', 'ж': 'Рынок труда. Рынок капитала',
            'з': 'Неравенство в распределении доходов, внешние эффекты и общественные блага.'}


class Form(StatesGroup):
    answer = State()
    id = State()
    id_lev = State()
    answer_list = State()
    topic = State()
    level = State()


@dp.message_handler(commands=['start'])
@dp.message_handler(Text('Вернуться на главное меню'))
async def ProcessStartCommand(message: types.Message):
    await message.reply('Приветствую тебя дорогой друг! Здесь ты сможешь подготовиться к олимпиадам по экономике,'
                        'сможешь узнать свой уровень и понять над какими темами тебе стоит поработать, или же просто можешь '
                        'порешать задачи на разные темы чтобы попрактиковаться.\nP.s. Пока задач не очень много, в дальнейшем '
                        'база данных будет пополняться.',
                        reply_markup=first_option_kb
                        )


@dp.message_handler(commands=['answer'])
async def HowToAnswer(message: types.Message):
    await bot.send_message(chat_id=message.chat.id,
                           text='- Если ответ на задачу один, введи просто число. Пример: 123\n'
                                '- Если ответ нецелочисленный, записывай через запятую. Пример: 123,5\n'
                                '- Если ответов на задачу несколько, введи ответы через точку запятую. Пример: 1; 123\n'
                                '- Если в задаче несколько пунктов, сначала введи номер пункта, а за ним ответ. Пункты должны идти по порядку. Пример: а) 1 б) 123\n'
                                '- Если нужно показать убывание или возрастание, например, на сколько изменилась цена, то укажи это знаком перед числом. Пример: если упала, то ответ -5, если выросла, то 5\n'
                                '- В вопросах по типу "как изменилось что-то" нужно указывать ответ в процентах\n'
                                '- Если нужно показать диапазон больше или меньше, используй >, <, >=, <=')


@dp.message_handler(Text('Проверить свой уровень'))
async def CheckLevel(message: types.Message):
    await message.reply('Итак, сейчас тебе будет предложено решить ' + str(len(
        id_topic) * 2) + ' задач по различным темам из курса микроэкономики '
                         'за 10 класс. Как решишь задачу, сначала напиши ее номер, после чего ответ. В конце будут '
                         'подведены итоги, и ты сможешь узнать свой результат.')
    sleep(10)
    if message.text == 'Назад':
        await bot.send_message(chat_id=message.chat.id, text='Ты вернулся на главное меню. Можешь либо пойти и сразу '
                                                             'начать решать задачи, либо же сначала проверить свой '
                                                             'уровень', reply_markup=first_option_kb)
    else:
        for topic in id_topic.values():
            for i in range(1, 3):
                tasks = get_task_list(topic, i)
                while True:
                    t_id = choice(list(tasks['id']))
                    if int(get_task_el(t_id, 'answer_type')) == 1:
                        break
                global id_list
                id_list.append(t_id)
                task = get_task_el(t_id, 'task')
                if 'C:' in task:
                    p = open('tasks/' + str(t_id + 1) + '.png', 'rb')
                    await bot.send_message(chat_id=message.chat.id, text=str(t_id))
                    await bot.send_photo(chat_id=message.chat.id, photo=p)
                else:
                    await message.reply('Задача номер ' + str(t_id) + '\n' + get_task_el(t_id, 'task'))
                sleep(2)

        await bot.send_message(chat_id=message.chat.id, text='Выбери номер задачи, на которую хочешь отправить ответ',
                               reply_markup=go_back)
        await Form.id_lev.set()


@dp.message_handler(state=Form.id_lev)
async def ChooseCheckTask(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['id'] = message.text
    await state.finish()
    global id_list
    if data['id'] == 'Назад':
        await bot.send_message(chat_id=message.chat.id, text='Ты вернулся на главное меню. Можешь либо пойти и сразу '
                                                             'начать решать задачи, либо же сначала проверить свой '
                                                             'уровень', reply_markup=first_option_kb)
        global id_list
        id_list = list()
        global ans_dict
        ans_dict = dict()
        global c
        c = 0
    elif data['id'] not in map(str, id_list):
        await bot.send_message(chat_id=message.chat.id, text='Такой задачи нет, введи корректный номер')
        await Form.id_lev.set()
    else:
        global task_id
        task_id = int(data['id'])
        await bot.send_message(chat_id=message.chat.id, text='Вы выбрали задачу ' + data['id'] +
                                                             '. Введите ответ на задачу. Чтобы понять, как правильно вводить ответ, используй команду /answer.')
        await Form.answer_list.set()


@dp.message_handler(state=Form.answer_list)
async def MakeAnsDict(message: types.Message, state: FSMContext):
    await state.finish()
    async with state.proxy() as data:
        data['answer'] = message.text
    if data['answer'] == '/answer':
        await bot.send_message(chat_id=message.chat.id,
                               text='- Если ответ на задачу один, введи просто число. Пример: 123\n'
                                    '- Если ответ нецелочисленный, записывай через запятую. Пример: 123,5\n'
                                    '- Если ответов на задачу несколько, введи ответы через точку запятую. Пример: 1; 123\n'
                                    '- Если в задаче несколько пунктов, сначала введи номер пункта, а за ним ответ. Пункты должны идти по порядку. Пример: а) 1 б) 123\n'
                                    '- Если нужно показать убывание или возрастание, например, на сколько изменилась цена, то укажи это знаком перед числом. Пример: если упала, то ответ -5, если выросла, то 5\n'
                                    '- В вопросах по типу "как изменилось что-то" нужно указывать ответ в процентах\n'
                                    '- Если нужно показать диапазон больше или меньше, используй >, <, >=, <=')
        await bot.send_message(chat_id=message.chat.id, text='А теперь введи ответ на задачу')
        await Form.answer_list.set()
    else:
        global ans_dict
        ans_dict[task_id] = data['answer']
        print(ans_dict)
        global c
        c += 1
        if c == len(id_topic) * 2:
            correct = 0
            id_incorrect = list()
            topics = set()
            for id, ans in ans_dict.items():
                cor_ans = str(get_task_el(id, 'answer'))
                if cor_ans == ans:
                    correct += 1
                else:
                    id_incorrect.append(id)
                    topics.add(get_task_el(id, 'topic'))
            await bot.send_message(chat_id=message.chat.id,
                                   text='Вы ответили правильно на ' + str(correct) + ' вопросов из ' + str(
                                       len(id_topic) * 2))
            await bot.send_message(chat_id=message.chat.id,
                                   text='Неправильно решенные задачи: ' + ',\n'.join([str(i) + ' Верный ответ: ' +
                                                                                      str(get_task_el(i, 'answer')) for i
                                                                                      in
                                                                                      id_incorrect]))
            await bot.send_message(chat_id=message.chat.id, text='Темы для проработки: ' + ', '.join(topics))
            await bot.send_message(chat_id=message.chat.id, text='Отлично! Теперь ты можешь вернуться на главное меню',
                                   reply_markup=go_to_main_menu)
        else:
            await bot.send_message(chat_id=message.chat.id,
                                   text='Ответ на задачу ' + str(task_id) + ' записан. Введи номер '
                                                                            'следующей задачи, на которую хочешь отправить ответ')
            await Form.id_lev.set()


@dp.message_handler(Text('База заданий'))
async def DbChooseTopic(message: types.Message):
    await message.reply('Добро пожаловать в сборник заданий и их решений. Выбираешь задачу, решаешь, вводишь ответ и '
                        'система проверяет его, в случае неправильного ответа у тебя будут еще попытки, или же ты сразу'
                        ' можешь посмотреть решение. Из списка темы выбери нужную: \nа) Альтернативные издержки\nб) КПВ'
                        '\nв) Спрос и предложение\nг) Эластичность\nд) Производство и издержки\nе) Рыночные структуры\n'
                        'ж) Рынок труда. Рынок капитала\nз) Неравенство в распределении доходов, внешние эффекты и'
                        ' общественные блага',
                        reply_markup=db_kb)
    await Form.topic.set()


@dp.message_handler(state=Form.topic)
async def DbChoseLevel(message: types.Message, state: FSMContext):
    await state.finish()
    if message.text == 'Назад':
        await bot.send_message(chat_id=message.chat.id, text='Ты вернулся на главное меню. Можешь либо пойти и сразу '
                                                             'начать решать задачи, либо же сначала проверить свой '
                                                             'уровень', reply_markup=first_option_kb)
    else:
        global topic
        topic = id_topic[message.text]
        await message.reply('Теперь выбери уровень задач: обычный или повышенный',
                            reply_markup=level_kb)
        await Form.level.set()


@dp.message_handler(state=Form.level)
async def DbWork(message: types.Message, state: FSMContext):
    await state.finish()
    if message.text == 'Назад':
        await bot.send_message(chat_id=message.chat.id, text='Ты вернулся к выбору темы. Из списка выбери нужную: '
                                                             'Из списка темы выбери нужную: \nа) Альтернативные издержки\nб) КПВ'
                                                             '\nв) Спрос и предложение\nг) Эластичность\nд) Производство и издержки\nе) Рыночные структуры\n'
                                                             'ж) Рынок труда. Рынок капитала\nз) Неравенство в распределении доходов, внешние эффекты и'
                                                             ' общественные блага', reply_markup=db_kb)
        await Form.topic.set()
    else:
        global level
        if message.text == 'Обычная сложность':
            level = 1
        elif message.text == 'Повышенная сложность':
            level = 2
        global task
        task = get_task_list(topic, level)
        s = task[['id', 'task']]
        pd.set_option('display.max_colwidth', None)
        for i in s['id']:
            global id_list
            id_list.append(i)
            if 'C:' in str(get_task_el(i, 'task')):
                p = open('tasks/' + str(i + 1) + '.png', 'rb')
                await bot.send_message(chat_id=message.chat.id, text=str(i))
                await bot.send_photo(chat_id=message.chat.id, photo=p)
            else:
                await message.reply('Задача номер ' + str(i) + '\n' + get_task_el(i, 'task'))
        await message.reply('Напиши номер задачи, которую хочешь решить')
        await Form.id.set()


@dp.message_handler(state=Form.id)
async def DbChooseCheckTask(message: types.Message, state: FSMContext):
    await state.finish()
    global id_list
    if message.text == 'Назад':
        await bot.send_message(chat_id=message.chat.id,
                               text='Ты вернулся к выбору уровня задач, выбери сложность: '
                                    'обычную или повышенную',
                               reply_markup=level_kb)
        await Form.level.set()
        global id_list
        id_list = list()
    elif message.text not in map(str, id_list):
        await bot.send_message(chat_id=message.chat.id, text='Такой задачи нет, введи корректный номер')
        await Form.id.set()
    else:
        async with state.proxy() as data:
            data['id'] = message.text
        global task_id
        task_id = int(data['id'])
        sol_type = get_task_el(task_id, 'answer_type')
        if sol_type == 1:
            await bot.send_message(chat_id=message.chat.id, text='Вы выбрали задачу ' + data['id'] +
                                                                 '. Введите ответ на задачу. Чтобы понять, как правильно вводить ответ, используй команду /answer')
            await Form.answer.set()
        else:
            await bot.send_message(chat_id=message.chat.id,
                                   text='У данной задачи нет четкого ответа, который можно '
                                        'проверить в нашей тестирующей системе. Вы можете решить '
                                        'задачу, после чего сравнить с правильным ответом и '
                                        'посмотреть решение.', reply_markup=see_solution_kb)


@dp.message_handler(state=Form.answer)
async def CheckAnswer(message: types.Message, state: FSMContext):
    await state.finish()
    async with state.proxy() as data:
        data['answer'] = message.text
    if data['answer'] == '/answer':
        await bot.send_message(chat_id=message.chat.id,
                               text='- Если ответ на задачу один, введи просто число. Пример: 123\n'
                                    '- Если ответ нецелочисленный, записывай через запятую. Пример: 123,5\n'
                                    '- Если ответов на задачу несколько, введи ответы через точку запятую. Пример: 1; 123\n'
                                    '- Если в задаче несколько пунктов, сначала введи номер пункта, а за ним ответ. Пункты должны идти по порядку. Пример: а) 1 б) 123\n'
                                    '- Если нужно показать убывание или возрастание, например, на сколько изменилась цена, то укажи это знаком перед числом. Пример: если упала, то ответ -5, если выросла, то 5\n'
                                    '- В вопросах по типу "как изменилось что-то" нужно указывать ответ в процентах\n'
                                    '- Если нужно показать диапазон больше или меньше, используй >, <, >=, <=')
        await bot.send_message(chat_id=message.chat.id, text='А теперь введи ответ на задачу')
        await Form.answer.set()
    if data['answer'] == 'Назад':
        await bot.send_message(chat_id=message.chat.id,
                               text='Введи номер задачи, которую хочешь решить')
        await Form.id.set()

    else:
        await bot.send_message(chat_id=message.chat.id, text='Ваш ответ: ' + data['answer'])
        answer = str(get_task_el(task_id, 'answer'))
        if answer == data['answer']:
            await bot.send_message(chat_id=message.chat.id,
                                   text='Верно! Можешь выбрать следующую задачу для решения или же вернуться назад.',
                                   reply_markup=go_back)
            await Form.id.set()
        else:
            await bot.send_message(chat_id=message.chat.id,
                                   text='Неверно, попробуй еще раз или посмотри решение задачи',
                                   reply_markup=see_solortryagain_kb)


@dp.message_handler(Text('Попробовать еще раз'))
async def AnswerAgain(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text='Введите ответ на задачу')
    await Form.answer.set()


@dp.message_handler(Text('Посмотреть решение'))
async def ShowSolution(message: types.Message):
    solution = str(get_task_el(task_id, 'solution'))
    answer = str(get_task_el(task_id, 'answer'))
    await bot.send_message(chat_id=message.chat.id, text='Ответ: ' + answer)
    if 'C:' in solution:
        p = p = open('solutions/' + str(task_id + 1) + '.png', 'rb')
        await bot.send_photo(chat_id=message.chat.id, photo=p)
    else:
        await bot.send_message(chat_id=message.chat.id, text=solution)
    await bot.send_message(chat_id=message.chat.id,
                           text='Можешь выбрать следующую задачу для решения или же вернуться назад.',
                           reply_markup=go_back)
    await Form.id.set()


@dp.message_handler(Text('Вернуться назад'), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await Form.previous()


if __name__ == '__main__':
    executor.start_polling(dp)
