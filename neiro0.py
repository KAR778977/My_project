import telebot
from g4f.client import Client
from telebot import types
import re
from FusionBrain import GenerateModel
import base64
API_TOKEN=''
bot = telebot.TeleBot(API_TOKEN)
api_key=''
secret_key=''
url='https://api-key.fusionbrain.ai/'
works_model=['gpt-3','gpt-3.5-turbo','gpt-4o','gpt-4o-mini','gpt-4','gpt-4-turbo',
             'llama-2-13b','llama-3-8b','llama-3-70b','llama-3.1-8b','llama-3.1-70b',
             'llama-3.1-405b','mistral-7b','mixtral-8x7b','mixtral-8x22b','mixtral-8x7b-dpo','yi-34b',
             'gemini', 'gemini-pro', 'gemini-flash','gemma-2b','gemma-2b-9b', 'gemma-2b-27b','claude-2.1',
             'claude-3-opus','claude-3-sonnet', 'claude-3-haiku','claude-3-5-sonnet','blackbox', 'qwen-1.5-14b',
             'command-r+','dbrx-instruct','sparkdesk-v1.1','qwen-2-72b', 'glm-3-6b', 'glm-4-9b','glm-4',
             'yi-1.5-9b','solar-10-7b','deepseek','llava-13b',]
image_model=['sdxl', 'sd-3','playground-v2.5','flux', 'flux-realism','flux-anime','flux-3d','flux-disney', 'flux-pixel',
             'flux-schnell', 'dalle', 'dalle-2','dalle-mini', 'emi', 'any-dark','kandinsky']

text_kb=types.ReplyKeyboardMarkup()
for x in works_model:
    text_kb.add(types.KeyboardButton(x))
image_kb=types.ReplyKeyboardMarkup()
for x in image_model:
    image_kb.add(types.KeyboardButton(x))

@bot.message_handler(commands=['start'])
def welcome(message):
    kb=types.ReplyKeyboardMarkup()
    kb.add(types.KeyboardButton('image'),types.KeyboardButton('text'))
    with open('kandinsky-download-1727201968288.png', 'rb') as f:
        bot.send_photo(message.chat.id, f)
    bot.send_message(message.chat.id, 'Hi, I am a chat-neiro-bot, I can help you with your work, generate s photo or even write a text or a code',reply_markup=kb)
@bot.message_handler(func=lambda message:message.text in ['text','image'])
def choiceMode(message):
    mode=message.text
    if message.text=='text':
        bot.send_message(message.chat.id, 'You choosed text generation, choose model',reply_markup=text_kb)
    if message.text =='image':
        bot.send_message(message.chat.id, 'You choosed image generation, choose model',reply_markup=image_kb)
    bot.register_next_step_handler(message,model_func,mode)

def model_func(message,mode):
    model=message.text
    bot.send_message(message.chat.id,'Alright, send me promt')
    if mode=='text':
        bot.register_next_step_handler(message, get_responce,model)
    if mode=='image':
        bot.register_next_step_handler(message, get_responce_image,model)


def get_responce(message,model):
    client = Client()
    ask=message.text
    response = client.chat.completions.create(model=model,
        messages=[{'role':'user','content':ask}])
    result= response.choices[0].message.content
    if result:
        bot.send_message(message.chat.id,result)
    else:
        bot.send_message(message.chat.id, 'не удалось найти ответ')

def get_responce_image(message,model):
    client = Client()
    ask = message.text
    if model=='kandinsky':
        bot.send_message(message.chat.id,'пока не написали')
    response = client.chat.completions.create(model=model,
                                              messages=[{'role': 'user', 'content': ask}])
    result = response.choices[0].message.content
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern,result)[0]
    urls=urls[:urls.index(')')]
    if result:
        bot.send_message(message.chat.id, urls)
    else:
        bot.send_message(message.chat.id, 'не удалось найти ответ')
# @bot.message_handler(func=lambda message: message.text in works_model or message.text in image_model)
# def promt_choose(message):


def choose_style(message):
    style = {
        'KANDINSKY': 'KANDINSKY',
        'Детальное фото': 'UHD',
        'ANIME': 'ANIME',
        'No style': 'DEFAULT',
    }
    kb_style = types.ReplyKeyboardMarkup()
    for x in style:
        kb_style.add(x)
    bot.send_message(message.chat.id, f'Choose style', reply_markup=kb_style)
    bot.register_next_step_handler(message, kandinsky_style)


def kandinsky_style(message):
    style = message.text
    bot.send_message(message.chat.id, 'Alright, send me promt')
    bot.register_next_step_handler(message, kandinsky_main, style)


def kandinsky_main(message, style):
    promt = message.text
    api = GenerateModel(url=url, api_key=api_key, secret_key=secret_key)
    model_id = api.get_model()
    uuid = api.generate(promt, model_id, style)
    images = api.check_generation(uuid)
    if images != None:
        image_base64 = images[0]
        print(image_base64)
        image_data = base64.b64decode(image_base64)
        with open('image.jpg', 'wb') as f:
            f.write(image_data)
        with open('image.jpg', 'rb') as f:
            bot.send_photo(message.chat.id, f, caption=promt)
        print(' Готово!')
    else:
        bot.send_message(message.chat.id, 'Произошла ошибка во время генерации')


bot.infinity_polling()
