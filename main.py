from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ContentTypes

from config import API_TOKEN, TOKEN
from plugins import upload_file, create_folder, list_dir
from sql_lite import db_start, create_profile, update_profile, create_project


async def on_startup(_):
    await db_start()

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

class ProfileStatesGroup(StatesGroup):
    name = State()
    surname = State()

class ProjectStatesGroup(StatesGroup):
    street = State()
    numb = State()
    desc = State()
    url = State()

def get_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    reg_kb = KeyboardButton('/reg')
    add_kb = KeyboardButton('/add')
    kb.add(reg_kb, add_kb)
    return kb

def get_cancel_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('/cancel'))
    return kb

@dp.message_handler(commands=['cancel'], state='*')
async def cmd_cancel(message: types.Message, state: FSMContext):
    if state is None:
        return
    
    await state.finish()
    await message.reply('Вы прервали регистрацию!', reply_markup=get_kb())

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message) -> None:
    await message.answer(
        'Добро пожаловать в рабочего бота! Для регистрации нажмите или введите /reg', 
        reply_markup=get_kb())
    await create_profile(user_id=message.from_user.id, nick=message.from_user.username)

@dp.message_handler(commands=['reg'])
async def cmd_reg(message: types.Message) -> None:
    await message.reply("Введите ваше имя", reply_markup=get_cancel_kb())
    await ProfileStatesGroup.name.set()

@dp.message_handler(state=ProfileStatesGroup.name)
async def load_name(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['name'] = message.text
    
    await message.reply("Введите фамилию")
    await ProfileStatesGroup.next()

@dp.message_handler(state=ProfileStatesGroup.surname)
async def load_surname(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['surname'] = message.text
    
    await update_profile(state, user_id=message.from_user.id)
    await message.reply("Профиль успешно заполнен!")
    await state.finish()

@dp.message_handler(commands=['add'])
async def cmd_reg(message: types.Message) -> None:
    await bot.send_message(message.from_user.id,"Введите название улицы", reply_markup=get_cancel_kb())
    await dp.storage.set_state(chat=message.from_user.id, user=message.from_user.id, state=ProjectStatesGroup.street.state)
    await message.delete()
    await ProjectStatesGroup.street.set()
    

@dp.message_handler(state=ProjectStatesGroup.street)
async def load_street(message: types.Message, state: FSMContext) -> None:
    if message.text not in list_dir('Объекты'):
        create_folder(f'Объекты/{message.text}')
    async with state.proxy() as data:
        data['street'] = message.text
    
    await message.reply("Введите номер дома")
    await ProjectStatesGroup.next()


@dp.message_handler(state=ProjectStatesGroup.numb)
async def load_numb(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['numb'] = message.text
    
    await message.reply("Введите краткое описание обьекта")
    await ProjectStatesGroup.next()

@dp.message_handler(state=ProjectStatesGroup.desc)
async def load_desc(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['desc'] = message.text
    
    await message.reply("Загрузите файл")
    await ProjectStatesGroup.next()

@dp.message_handler(state=ProjectStatesGroup.url, content_types=['document'])
async def get_file(message: types.File, state: FSMContext):
    file_id = message.document.file_id    
    name = message.document.file_name
    file_path = f"Uploads/{name}"    
    await bot.download_file_by_id(file_id, file_path)
    

    async with state.proxy() as data:
        street = data['street']
        ya_path = f"Объекты/{street}/{name}"
        data['url'] = ya_path
        upload_file(file_path, ya_path)
    
    await create_project(state, user_id=message.from_user.id)
    await message.reply("Объект успешно добавлен!")
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)