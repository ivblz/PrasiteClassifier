from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
import torch
import os
import model_func


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

model = torch.load(f'models/model_view_cestodes.pth', map_location=device)
model_view_cestodes = model.eval()
model_view_cestodes.load_state_dict(torch.load(f'models_state_dicts//model_view_cestodes.pth', map_location=device))

model = torch.load(f'models/model_view_trematodes.pth', map_location=device)
model_view_trematodes = model.eval()
model_view_trematodes.load_state_dict(torch.load(f'models_state_dicts//model_view_trematodes.pth', map_location=device))

model = torch.load(f'models/model_view_protista.pth', map_location=device)
model_view_protista = model.eval()
model_view_protista.load_state_dict(torch.load(f'models_state_dicts//model_view_protista.pth', map_location=device))

model = torch.load(f'models/model_class.pth', map_location=device)
model_class = model.eval()
model_class.load_state_dict(torch.load(f'models_state_dicts//model_class.pth', map_location=device))

model = torch.load(f'models/model_view_nematoda.pth', map_location=device)
model_view_nematoda = model.eval()
model_view_nematoda.load_state_dict(torch.load(f'models_state_dicts//model_view_nematoda.pth', map_location=device))

def model_return(photo):
    class_names = [name for name in os.listdir('parasites_data/view') if name != '.DS_Store']
    predicted_parasite = model_func.predict_parasite(photo, model_class, class_names)

    if (predicted_parasite == 'strongleaders') or (predicted_parasite == 'something') or (predicted_parasite == 'special_human_parasites'):
        return predicted_parasite
    else:
        if (predicted_parasite == 'cestodes'): model_view = model_view_cestodes
        elif (predicted_parasite == 'nematoda'): model_view = model_view_nematoda
        elif (predicted_parasite == 'protista'): model_view = model_view_protista
        elif (predicted_parasite == 'trematodes'): model_view = model_view_trematodes
        view_names = [name for name in os.listdir(f'parasites_data/view/{predicted_parasite}') if name != '.DS_Store']
        predicted_parasite = model_func.predict_parasite(photo, model_view, view_names)
        return predicted_parasite

def photo_save(path, name):
    new_path = f"{path.rsplit('.', 1)[0]}_{name}.png"
    os.rename(path, new_path)



API_TOKEN = '7773206389:AAGKW8oNFiYCsCjxoa_mN8xVIT_Khu66wSU'

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# Команда /start
@dp.message(Command('start'))
async def send_welcome(message: types.Message):
    await message.reply("Классификатор яиц паразитов у млекопитающих:\n    - cestodes\n    - nematoda\n    - nprotista    \n    - trematodes\n    - special_human_parasites\n    - strongleaders\n    - something\n\n набор команд - /help")

# Команда /help
@dp.message(Command('help'))
async def send_help(message: types.Message):
    await message.reply("/start - старт\n/help - список команд\n/class - классификация паразита\n/message - предложить улучшения")

picture_none = 1
# Команда /class
@dp.message(Command('class'))
async def class_command(message: types.Message):
    global picture_none
    picture_none = 0
    await message.reply("Пожалуйста, отправьте изображение")


path, solve = '', ''
# Обработка изображений
@dp.message(lambda message: message.content_type == types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    global picture_none, path, solve
    if picture_none == 0:
        wait_message = await message.reply("Подождите пару секунд...")

        path = f'parasites/{message.photo[-1].file_id}.png'
        await message.bot.download(file=message.photo[-1].file_id, destination=path)

        solve = model_return(path)

        # Создаем inline кнопки
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text="Определено верно", callback_data="correct"))
        builder.add(types.InlineKeyboardButton(text="Не верно", callback_data="incorrect"))

        await wait_message.delete()
        await message.answer(f"Это {solve}", reply_markup=builder.as_markup())
        picture_none = 1
    else: await message.answer("Неопознанная команда")

# Обработка нажатия inline кнопок
@dp.callback_query(lambda c: c.data in ["correct", "incorrect"])
async def handle_buttons(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup()  # Удаляем только inline кнопки
    if callback.data == "incorrect":
        
        # Создаем inline кнопки
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text="cestodes", callback_data="option_1"))
        builder.row(types.InlineKeyboardButton(text="nematoda", callback_data="option_2"))
        builder.row(types.InlineKeyboardButton(text="protista", callback_data="option_3"))
        builder.row(types.InlineKeyboardButton(text="trematodes", callback_data="option_4"))
        builder.row(types.InlineKeyboardButton(text="special_human_parasites", callback_data="option_5"))
        builder.row(types.InlineKeyboardButton(text="strongleaders", callback_data="option_6"))
        builder.row(types.InlineKeyboardButton(text="something", callback_data="option_7"))
        builder.row(types.InlineKeyboardButton(text="не знаю", callback_data="option_8"))

        await callback.message.answer("Пожалуйста, выберите класс:", reply_markup=builder.as_markup())

    else:
        await callback.message.answer("Ваш ответ очень важен для нас,\nСпасибо!")
        photo_save(path, solve)
    await callback.answer()

# Обработка нажатия inline кнопок
@dp.callback_query(lambda c: c.data in ["option_1", "option_2", "option_3","option_4","option_5","option_6","option_7","option_8"])
async def second_handle_buttons(callback: types.CallbackQuery):
    # Обработка нажатия каждой кнопки
    if callback.data == "option_1":
        await callback.message.edit_reply_markup()  # Удаляем предыдущие кнопки

        new_builder = InlineKeyboardBuilder()
        new_builder.add(types.InlineKeyboardButton(text="cestodes_Diphyllobothriosis", callback_data="cestodes_Diphyllobothriosis"))
        new_builder.row(types.InlineKeyboardButton(text="cestodes_Dipylidiosis", callback_data="cestodes_Dipylidiosis"))
        new_builder.row(types.InlineKeyboardButton(text="cestodes_Spirometrosis", callback_data="cestodes_Spirometrosis"))
        new_builder.row(types.InlineKeyboardButton(text="cestodes_Taeniosis", callback_data="cestodes_Taeniosis"))
        await callback.message.answer("Теперь выберите вид:", reply_markup=new_builder.as_markup())

    elif callback.data == "option_2":
        await callback.message.edit_reply_markup()  # Удаляем предыдущие кнопки

        new_builder = InlineKeyboardBuilder()
        new_builder.add(types.InlineKeyboardButton(text="nematoda_Gnathostom", callback_data="nematoda_Gnathostom"))
        new_builder.row(types.InlineKeyboardButton(text="nematoda_ollulanus", callback_data="nematoda_ollulanus"))
        new_builder.row(types.InlineKeyboardButton(text="nematoda_spicocerca", callback_data="nematoda_spicocerca"))
        new_builder.row(types.InlineKeyboardButton(text="nematoda_toxascris", callback_data="nematoda_toxascris"))
        await callback.message.answer("Теперь выберите вид:", reply_markup=new_builder.as_markup())

    elif callback.data == "option_3":
        await callback.message.edit_reply_markup()  # Удаляем предыдущие кнопки

        new_builder = InlineKeyboardBuilder()
        new_builder.add(types.InlineKeyboardButton(text="protista_coccidia", callback_data="protista_coccidia"))
        new_builder.row(types.InlineKeyboardButton(text="protista_giardia", callback_data="protista_giardia"))
        new_builder.row(types.InlineKeyboardButton(text="protista_isosporosis", callback_data="protista_isosporosis"))
        new_builder.row(types.InlineKeyboardButton(text="protista_toxoplasmosis", callback_data="protista_toxoplasmosis"))
        await callback.message.answer("Теперь выберите вид:", reply_markup=new_builder.as_markup())

    elif callback.data == "option_4":
        await callback.message.edit_reply_markup()  # Удаляем предыдущие кнопки

        new_builder = InlineKeyboardBuilder()
        new_builder.add(types.InlineKeyboardButton(text="trematodes_Fasciolosis", callback_data="trematodes_Fasciolosis"))
        new_builder.row(types.InlineKeyboardButton(text="trematodes_Metagonimosis", callback_data="trematodes_Metagonimosis"))
        new_builder.row(types.InlineKeyboardButton(text="trematodes_Opistorchiosis", callback_data="trematodes_Opistorchiosis"))
        new_builder.row(types.InlineKeyboardButton(text="trematodes_Paragonimosis", callback_data="trematodes_Paragonimosis"))
        await callback.message.answer("Теперь выберите вид:", reply_markup=new_builder.as_markup())
    
    elif callback.data in ["option_5", "option_6", "option_7", "option_8"]:
        await callback.message.edit_reply_markup()  # Удаляем предыдущие кнопки
        solve = 'special_human_parasites' if callback.data == "option_5" else 'strongleaders' if callback.data == "option_6" else 'something' if callback.data == "option_7" else 'noname'  # Устанавливаем значение solve в зависимости от callback.data
        photo_save(path, solve)
        await callback.message.answer("Ваш ответ очень важен для нас,\nСпасибо!")

@dp.callback_query(lambda c: c.data in ["cestodes_Diphyllobothriosis", "cestodes_Dipylidiosis", "cestodes_Spirometrosis", "cestodes_Taeniosis", 
                                          "nematoda_Gnathostom", "nematoda_ollulanus", "nematoda_spicocerca", "nematoda_toxascris", 
                                          "protista_coccidia", "protista_giardia", "protista_isosporosis", "protista_toxoplasmosis", 
                                          "trematodes_Fasciolosis", "trematodes_Metagonimosis", "trematodes_Opistorchiosis", "trematodes_Paragonimosis"])
async def handle_new_option(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup()  # Удаляем предыдущие кнопки
    solve = callback.data  # Название кнопки, на которую нажал пользователь
    photo_save(path, solve)  # Передаем в функцию
    await callback.message.answer("Ваш ответ очень важен для нас,\nСпасибо!")


message_none = 1
@dp.message(Command('message'))
async def send_message(message: types.Message):
    global message_none
    # Запрашиваем у пользователя текст сообщения
    await message.answer("Пожалуйста, напишите ваше предложение по улучшению:")
    message_none = 0

@dp.message()
async def process_improvement(message: types.Message):
    global message_none
    # Получаем текст предложения
    improvement_text = message.text
    if message_none == 0:
        # Отправляем сообщение в чат
        await message.answer("Спасибо за ваше предложение!")
        message_none = 1
          # Замените на нужный ID чата
        await bot.send_message(chat_id='7263418923', text=f'{message.from_user.full_name} ({message.from_user.username}): {improvement_text}')

        with open("add.txt", "a", encoding="utf-8") as file:
            file.write(f"{message.from_user.full_name} ({message.from_user.username}): {improvement_text}\n")
    else:
        await message.answer("Неопознанная команда")


if __name__ == '__main__':
    dp.run_polling(bot)