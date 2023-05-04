import threading
import logging
import sqlite3
import telegram
from telegram.ext import Updater, CommandHandler, Filters
from datetime import datetime
import re
import requests
import base64
from configurator import *

request_sequence = 0

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("logs\debug_{0}.log".format(str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S")))),
        logging.StreamHandler()
    ]
)

logging.info('Starting...')

url = "http://" + apiIP + ":7860/sdapi/v1/txt2img"

headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

conn = sqlite3.connect('userConf.db', check_same_thread=False)

logging.info('Connected to sqlite db.')

cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        hr INTEGER,
        scale INTEGER,
        seed INTEGER,
        width INTEGER,
        height INTEGER,
        strength INTEGER,
        steps INTEGER,
        tokens INTEGER,
        upscaler TEXT
    )
''')

# Обработчик команды /start
def start(update, context):
    logging.info(str(update.message.from_user.username) + ' - Start message requested.')
    context.bot.send_message(chat_id=update.effective_chat.id, text=start_msg)

# Обработчик команды /help
def help(update, context):
    logging.info(str(update.message.from_user.username) + ' - Help message requested.')
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_msg, parse_mode=telegram.ParseMode.HTML)

def make_request(update, context):
    global request_sequence
    request_sequence += 1
    user_id = update.message.from_user.id
    cursor.execute('SELECT hr, scale, seed, width, height, strength, steps, tokens, upscaler FROM users WHERE user_id = ?', (user_id,))
    dbResult = cursor.fetchone()

    if dbResult is not None:
        high_resolution, hr_scale, seed, width, height, prompt_strength, steps, tokens, upscaler = dbResult
    else:
        new_user = (
            user_id,
            high_resolutionD,
            hr_scaleD,
            seedD,
            widthD,
            heightD,
            prompt_strengthD,
            stepsD,
            tokensD,
            upscalerD
        )
        cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', new_user)
        conn.commit()
        high_resolution = high_resolutionD
        hr_scale = hr_scaleD
        seed = seedD
        width = widthD
        height = heightD
        prompt_strength = prompt_strengthD
        steps = stepsD
        tokens = tokensD
        upscaler = upscalerD

    if tokens <= 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text=tokensne_msg)
        logging.info("(Thread " + str(threading.current_thread().ident) + ") " + str(update.message.from_user.username) + ' - Prompt ignored (Not Enough Tokens).')
        cursor.execute('UPDATE users SET tokens=? WHERE user_id=?', (100, user_id))
        conn.commit()
        request_sequence -= 1
        return

    # Получаем текст сообщения после команды /generate
    temp_prompt = ' '.join(context.args)

    logging.info("(Thread " + str(threading.current_thread().ident) + ") " + str(update.message.from_user.username) + ' - Prompt achieved. Trying to send...')
    
    context.bot.send_message(chat_id=update.effective_chat.id, text="Генерирую изображение по описанию " + temp_prompt +
                                ".\n\nТекущая позиция в очереди - " + str(request_sequence) + "\n\n" + aftergen_msg)
    
    data = {
        "enable_hr": high_resolution,
        "denoising_strength": 0.4,
        "hr_scale": hr_scale,
        "hr_upscaler": upscaler,
        "prompt": ("(masterpiece), (best quality), " + temp_prompt),
        "negative_prompt": "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name, bad eyes",
        "seed": seed,
        "subseed": -1,
        "subseed_strength": 0,
        "seed_resize_from_h": -1,
        "seed_resize_from_w": -1,
        "width": width,
        "height": height,
        "sampler_name": "UniPC",
        "cfg_scale": prompt_strength,
        "steps": steps,
        "batch_size": 1,
        "restore_faces": False,
        "index_of_first_image": 0,
        "save_images": True,
        "clip_skip": 2,
        "is_using_inpainting_conditioning": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
    except requests.exceptions.ConnectTimeout:
        logging.warning("(Thread " + str(threading.current_thread().ident) + ") " + str(update.message.from_user.username) + ' - ExceptionHandler: API Connect Timeout.')
        context.bot.send_message(chat_id=update.effective_chat.id, text=generr_msg)
        request_sequence -= 1
        return
    except requests.exceptions.ConnectionError:
        logging.warning("(Thread " + str(threading.current_thread().ident) + ") " + str(update.message.from_user.username) + ' - ExceptionHandler: API Connection Error.')
        context.bot.send_message(chat_id=update.effective_chat.id, text=gentimeout_msg)
        request_sequence -= 1
        return

    json_data = response.json()

    if 'images' in json_data:
        image = json_data['images']

    with open("imgBuffer", "wb") as fh:
        fh.write(base64.decodebytes(image[0].encode()))
        
    with open('imgBuffer', 'rb') as f:
        # Отправляем изображение
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=f)

    tokens -= 1

    cursor.execute('UPDATE users SET tokens=? WHERE user_id=?', (tokens, user_id))
    conn.commit()

    logging.info("(Thread " + str(threading.current_thread().ident) + ") " + str(update.message.from_user.username) + ' - Image sent succesfully.')

    request_sequence -= 1

    
def generate_prompt(update, context):
    thread = threading.Thread(target=make_request, args=[update, context])
    thread.start()

def config(update, context):
    user_id = update.message.from_user.id
    cursor.execute('SELECT hr, scale, seed, width, height, strength, steps, tokens, upscaler FROM users WHERE user_id = ?', (user_id,))
    dbResult = cursor.fetchone()

    if dbResult is not None:
        high_resolution, hr_scale, seed, width, height, prompt_strength, steps, tokens, upscaler = dbResult
    else:
        new_user = (
            user_id,
            high_resolutionD,
            hr_scaleD,
            seedD,
            widthD,
            heightD,
            prompt_strengthD,
            stepsD,
            tokensD,
            upscalerD
        )
        cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', new_user)
        conn.commit()
        high_resolution = high_resolutionD
        hr_scale = hr_scaleD
        seed = seedD
        width = widthD
        height = heightD
        prompt_strength = prompt_strengthD
        steps = stepsD
        tokens = tokensD
        upscaler = upscalerD

    conf_cmnd = update.message.text

    # Ищем совпадения с регулярным выражением
    match1 = re.search(r'/config (\w+) (\S+)', conf_cmnd)
    cfg_arg = ' '.join(context.args)

    conf_decline = "Некорректный формат команды"

    if match1:

        option = match1.group(1)
        opt_var = match1.group(2)

        conf_accept = "Настройка " + option + " сохранена со значением " + opt_var

        match option:

            case "hr":
                if opt_var == "enable":
                    high_resolution = True
                    context.bot.send_message(chat_id=update.message.chat_id, text=conf_accept)
                    logging.info(str(update.message.from_user.username) + ' - Config change request.')
                elif opt_var == "disable":
                    high_resolution = False
                    context.bot.send_message(chat_id=update.message.chat_id, text=conf_accept)
                    logging.info(str(update.message.from_user.username) + ' - Config change request.')
                else:
                    context.bot.send_message(chat_id=update.message.chat_id, text=conf_decline)
                    logging.info(str(update.message.from_user.username) + ' - Wrong config syntax.')
                    return
            
            case "upscaler":
                if opt_var == "Latent" or opt_var == "ESRGAN_4x":
                    upscaler = opt_var
                    context.bot.send_message(chat_id=update.message.chat_id, text=conf_accept)
                    logging.info(str(update.message.from_user.username) + ' - Config change request.')
                else:
                    context.bot.send_message(chat_id=update.message.chat_id, text=conf_decline)
                    logging.info(str(update.message.from_user.username) + ' - Wrong config syntax.')
                    return

            case "hr_scale":
                if float(opt_var) <= 2.00 and float(opt_var) >= 1.00:
                    hr_scale = float(opt_var)
                    context.bot.send_message(chat_id=update.message.chat_id, text=conf_accept)
                    logging.info(str(update.message.from_user.username) + ' - Config change request.')
                else:
                    context.bot.send_message(chat_id=update.message.chat_id, text=conf_decline)
                    logging.info(str(update.message.from_user.username) + ' - Wrong config syntax.')
                    return

            case "seed":
                if opt_var == "random":
                    seed = -1
                    context.bot.send_message(chat_id=update.message.chat_id, text=conf_accept)
                    logging.info(str(update.message.from_user.username) + ' - Config change request.')
                elif int(opt_var) > 0:
                    seed = int(opt_var)
                    context.bot.send_message(chat_id=update.message.chat_id, text=conf_accept)
                    logging.info(str(update.message.from_user.username) + ' - Config change request.')
                else:
                    context.bot.send_message(chat_id=update.message.chat_id, text=conf_decline)
                    logging.info(str(update.message.from_user.username) + ' - Wrong config syntax.')
                    return
                
            case "width":
                if int(opt_var) >= 128 and int(opt_var) <= 512:
                    width = int(opt_var)
                    context.bot.send_message(chat_id=update.message.chat_id, text=conf_accept)
                    logging.info(str(update.message.from_user.username) + ' - Config change request.')
                else:
                    context.bot.send_message(chat_id=update.message.chat_id, text=conf_decline)
                    logging.info(str(update.message.from_user.username) + ' - Wrong config syntax.')
                    return

            case "height":
                if int(opt_var) >= 128 and int(opt_var) <= 512:
                    height = int(opt_var)
                    context.bot.send_message(chat_id=update.message.chat_id, text=conf_accept)
                    logging.info(str(update.message.from_user.username) + ' - Config change request.')
                else:
                    context.bot.send_message(chat_id=update.message.chat_id, text=conf_decline)
                    logging.info(str(update.message.from_user.username) + ' - Wrong config syntax.')
                    return

            case "strength":
                if int(opt_var) >= 0 and int(opt_var) <= 20:
                    prompt_strength = int(opt_var)
                    context.bot.send_message(chat_id=update.message.chat_id, text=conf_accept)
                    logging.info(str(update.message.from_user.username) + ' - Config change request.')
                else:
                    context.bot.send_message(chat_id=update.message.chat_id, text=conf_decline)
                    logging.info(str(update.message.from_user.username) + ' - Wrong config syntax.')
                    return

            case "steps":
                if int(opt_var) >= 1 and int(opt_var) <= 50:
                    steps = int(opt_var)
                    context.bot.send_message(chat_id=update.message.chat_id, text=conf_accept)
                    logging.info(str(update.message.from_user.username) + ' - Config change request.')
                else:
                    context.bot.send_message(chat_id=update.message.chat_id, text=conf_decline)
                    logging.info(str(update.message.from_user.username) + ' - Wrong config syntax.')
                    return
            case _:
                context.bot.send_message(chat_id=update.message.chat_id, text=conf_decline)
                logging.info(str(update.message.from_user.username) + ' - Wrong config syntax.')

        new_config = (
            high_resolution,
            hr_scale,
            seed,
            width,
            height,
            prompt_strength,
            steps,
            upscaler
        )
        cursor.execute('UPDATE users SET hr=?, scale=?, seed=?, width=?, height=?, strength=?, steps=?, upscaler=? WHERE user_id=?', (*new_config, user_id))
        conn.commit()

    elif cfg_arg == "current":
        logging.info(str(update.message.from_user.username) + ' - Current config request.')
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=(
                "High Resolution is " + ("<b>enabled</b>\n" if high_resolution else "<b>disabled</b>\n") +
                "Upscaler is <b>" + upscaler + "</b>\n" +
                "HR Scale is <b>" + str(hr_scale) + "</b>\n" +
                "Seed is <b>" + ("random</b>\n" if seed == -1 else (str(seed) + "</b>\n")) +
                "Width is <b>" + str(width) + "</b>\n" +
                "Height is <b>" + str(height) + "</b>\n" +
                "Prompt strength is <b>" + str(prompt_strength) + "</b>\n" +
                "Generation steps is <b>" + str(steps) + "</b>\n" + 
                "\nТокенов осталось - <b>" + str(tokens) + "</b>"
            ), parse_mode=telegram.ParseMode.HTML)
    elif cfg_arg == "default":
        logging.info(str(update.message.from_user.username) + ' - Default config request.')
        high_resolution = high_resolutionD
        hr_scale = hr_scaleD
        seed = seedD
        width = widthD
        height = heightD
        prompt_strength = prompt_strengthD
        steps = stepsD
        upscaler = upscalerD
        new_config = (
            high_resolution,
            hr_scale,
            seed,
            width,
            height,
            prompt_strength,
            steps,
            upscaler
        )
        cursor.execute('UPDATE users SET hr=?, scale=?, seed=?, width=?, height=?, strength=?, steps=?, upscaler=? WHERE user_id=?', (*new_config, user_id))
        conn.commit()

        context.bot.send_message(chat_id=update.message.chat_id, text="Конфиг сброшен к настройкам по умолчанию")
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text=conf_decline)
        logging.info(str(update.message.from_user.username) + ' - Wrong config syntax.')

# Создаем экземпляр Updater и передаем ему токен бота
updater = Updater(bot_token, use_context=True)

logging.info('Bot updater is ready.')

# Получаем экземпляр Dispatcher для регистрации обработчиков команд
dispatcher = updater.dispatcher

logging.info('Dispatcher is created, handlers initialization...')

# Регистрируем обработчики команд
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

generate_handler = CommandHandler('generate', generate_prompt)
dispatcher.add_handler(generate_handler)

config_handler = CommandHandler('config', config) #Filters.chat(chat_id=chatID)
dispatcher.add_handler(config_handler)

logging.info('Handlers ready.')

# Запускаем бота
updater.start_polling()

logging.info('Polling started.')