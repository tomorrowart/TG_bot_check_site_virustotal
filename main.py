import json
import logging
import asyncio
from urls_pars import extract_links
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import base64
import requests
from colorama import Fore
from database import Database, create_table


API_VIRUS = 'API KEY VIRUS TOTAL'
bot = Bot(token='API KEY')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)
is_going = False

DB = Database('data.db')

async def start_command(message: types.Message):
    await DB.insert(message.from_user.id, 0, None)
    await message.reply("Привет! Напиши /go")

# функция, которая будет запускаться при команде /go
async def go_command(message: types.Message):
    is_going = await DB.select_going(message.from_user.id)
    if not bool(is_going):
        await DB.update(1, message.from_user.id)
        await message.reply("Запуск отслеживания попадения домена в бан...")
        await go(message)
    else:
        await go(message)
        await message.reply("Запущена!")

# функция, которая будет запускаться при команде /stop
async def stop_command(message: types.Message):
    is_going = await DB.select_going(message.from_user.id)
    if bool(is_going):
        await DB.update(0, message.from_user.id)
        await message.reply("Остановили отслеживание...")
    else:
        await message.reply("Отслеживание уже остановлено!")
async def get_domen(message: types.Message):
    user_id = message.from_user.id
    urls = await DB.get_domen(user_id)
    if len(urls) == 0:
        await message.answer(f"Не найдено ссылок для отслеживания.\n"
                             f"Для добавления используйте команду /urls после нее укажите ссылку пример\n"
                             f"'/urls https://ya.ru'")
    else:
        await message.delete()
        await message.answer(f"В Отслеживание {urls}")

async def go(message):
    user_id = message.from_user.id
    is_going = await DB.select_going(user_id)
    while bool(is_going):
        urls = await DB.get_domen(user_id)
        if urls == None:
            await message.answer(f'Добавьте ссылки с помощью команды "/urls ваша ссылка с http://"')
            break
        if len(urls) > 0:
            uurl = json.loads(urls)
            key_urls = uurl.keys()
        for i in key_urls:
            domen = uurl[i]
            base = base64.b64encode((domen).encode()).decode().strip("=")
            headers = {
                "accept": "application/json",
                "x-apikey": f"{API_VIRUS}"
            }
            url = f"https://www.virustotal.com/api/v3/urls/{base}/analyse"
            response_analiys = requests.post(url, headers=headers) #Анализ сайте
            await asyncio.sleep(40)
            url = f"https://www.virustotal.com/api/v3/urls/{base}" #Получение результатов анализа
            response = requests.get(url, headers=headers)
            json_data = response.json()
            print(json_data)
            if 'data' in json_data:
                if 'attributes' in json_data['data']:
                    if 'last_analysis_results' in json_data['data']['attributes']:
                        last_data = []
                        for i in json_data['data']['attributes']['last_analysis_results']:
                            if 'unrated' in json_data['data']['attributes']['last_analysis_results'][i]['result']:
                                continue
                            if 'clean' in json_data['data']['attributes']['last_analysis_results'][i]['result']:
                                continue
                            text_res = f"{json_data['data']['attributes']['last_analysis_results'][i]['result']}"
                            last_data.append(text_res)
                            print(Fore.RED + text_res + Fore.RESET)
                        await message.answer(f'{last_data} + {domen}')
        await asyncio.sleep(3600)
        is_going = await DB.select_going(user_id)

async def save_text(message: types.Message):
    text = await extract_links(message.text)
    print(text)
    if len(text) == 0:
        await message.answer("Не найдено ссылки, не забудте указать https://")
    if len(text) > 0:
        user_id = message.from_user.id
        urls = await DB.get_domen(user_id)
        if urls == None:
            urls = {}
        if len(urls) > 0:
            uurl = json.loads(urls)
        else: uurl = {}
        text_link = str(text[0].rstrip().lstrip()).replace(',', '').replace(';', '').replace('"', '').replace('[', '').replace(']', '')
        uurl[len(uurl)+1] = text_link
        db_url = json.dumps(uurl)
        await DB.update_donem(user_id, db_url)
        await message.answer(f"Ссылка сохранена ->'{text[0]}'\n"
                             f"Все ссылки {db_url}\n"
                             f"Что бы добивать еще повторите действие\n"
                             f"Для запуска нажмите /go")

async def delete(message: types.Message):
    user_id = message.from_user.id
    urls = await DB.get_domen(user_id)
    await message.answer(f"Для удаления укажите номер ссылки \n"
                         f"пример для удаления 1 ссылки'/del 1' {urls}")

async def delet(message: types.Message):
    user_id = message.from_user.id
    try:
        i = int(message.text.split('/del')[1].strip().rstrip())
        urls = await DB.get_domen(user_id)
        if urls == None:
            await message.answer(f'Добавьте ссылки с помощью команды "/urls ваша ссылка с http://"')
            return
        if len(urls) > 0:
            uurl = json.loads(urls)
            remov_element = uurl.pop(f'{i}')
            await message.answer(f"Сайт {remov_element} удален")
            db_url = json.dumps(uurl)
            await DB.update_donem(user_id, db_url)
    except:
        return await message.answer("Не число после /del")


async def text(message: types.Message):
    await message.delete()
    await message.answer("Остановить отслеживание /stop\n"
                         "Запустить отслеживание /go\n"
                         "Пришли домен для отслеживания /urls тут ваш домен\n"
                         "Просмотреть отслеживаемые домены /done\n"
                         "Удалить домен /delete \n")
    # await message.answer("Запустить отслеживание /go")
    # await message.answer("Текст сохранен в базе данных")


dp.register_message_handler(start_command, commands=['start'])
dp.register_message_handler(go_command, commands=['go'])
dp.register_message_handler(stop_command, commands=['stop'])
dp.register_message_handler(save_text, commands=['urls'])
dp.register_message_handler(get_domen, commands=['done'])
dp.register_message_handler(delete, commands=['delete'])
dp.register_message_handler(delet, commands=['del'])
dp.register_message_handler(text)
if __name__ == "__main__":
    create_table()
    executor.start_polling(dp, skip_updates=True)
