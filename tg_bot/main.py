import telebot
import json
import time
from background import keep_alive
from threading import Thread
import schedule

with open("config.json", 'rb') as file:
  config = json.load(file)

bot = telebot.TeleBot(config.get("API_TOKEN"))


def schedule_checker():
  bot.send_message(
      "993170122",
      f"отсчет времени начался занаво. Время проведенное за таймером равно {(((int(time.strftime('%H')) + 3)%24) * 60 + int(time.strftime('%M'))) - config.get('TIME_HOUR_BUFFER')*60}"
  )
  
  save_json(config)
  bot.send_document("993170122", open(r'config.json', 'r'))
  while True:
    schedule.run_pending()

    t = ((int(time.strftime('%H')) + 3) % 24) * 60 + int(time.strftime('%M'))
    save_json(config)
    if t - config.get('TIME_HOUR_BUFFER') * 60 < 0:
      config['TIME_HOUR_BUFFER'] = -1
      save_json(config)
    if (t - config.get('TIME_HOUR_BUFFER') * 60 >= config['DELTA_SEND']
        and int(time.strftime('%H')) + 4 > 7):
      config['TIME_HOUR_BUFFER'] = (int(time.strftime('%H')) + 3) % 24
      startSending()
      save_json(config)

      print('Y')

    time.sleep(30)


def checAdminUser(message):
  admin_user = 0
  for i in config.get("USERS_ADMIN"):
    if message.from_user.username == i:
      admin_user = 1
      break
  return admin_user


def save_json(config):
  with open('config.json', 'w') as f:
    json.dump(config, f, indent=3)


@bot.message_handler(content_types=['photo'])
def save_id_pict(message):
  admin_users = checAdminUser(message)
  if admin_users:

    file_info = message.photo[0].file_id
    config["PHOTO_ID"].append(file_info)

    save_json(config)
    bot.send_message(message.chat.id, f"Картинка сохранена")
  else:
    bot.send_message(message.chat.id, f"У ТЕБЯ НЕТ ПРАВ")


@bot.message_handler(commands=['test'])
def test(message):
  bot.send_message(message.chat.id, message)


@bot.message_handler(commands=['print_spend_time'])
def print_spend_time(message):
  admin_users = checAdminUser(message)
  if admin_users:
    t = ((int(time.strftime('%H')) + 3) % 24) * 60 + int(time.strftime('%M'))
    bot.send_message(
        message.chat.id,
        f"Время проведенное за таймером равно { t -config.get('TIME_HOUR_BUFFER')*60}"
    )


@bot.message_handler(commands=['draw_mem'])
def draw_n_mem(message):
  admin_users = checAdminUser(message)
  bot.send_message(message.chat.id,
                   f"Введите номер мема или диапазон мемов через запятую")
  if admin_users:
    bot.register_next_step_handler(message, set_n_mem)


@bot.message_handler(commands=['del_mem'])
def erase_N_mem(message):
  admin_users = checAdminUser(message)
  bot.send_message(message.chat.id, f"Введите номер мема")
  if admin_users:
    bot.register_next_step_handler(message, erase_n_mem)


@bot.message_handler(commands=['set_delay_mem'])
def set_minute_spawn_mem(message):
  admin_users = checAdminUser(message)
  if admin_users:
    if (message.from_user.username == 'Denz_ox'):
      bot.send_message(message.chat.id,
                       f"Введите через сколько часов будут появляться мемы")
      bot.register_next_step_handler(message, set_value_minute_spawn_mem)
    else:
      bot.send_message(message.chat.id, f"У ТЕБЯ НЕТ ПРАВ")
  else:
    bot.send_message(message.chat.id, f"У ТЕБЯ НЕТ ПРАВ")


@bot.message_handler(commands=['print_minute_spawn_mem'])
def print_minute_spawn_mem(message):
  admin_users = checAdminUser(message)
  if admin_users:
    if (message.from_user.username == 'Denz_ox'):
      bot.send_message(
          message.chat.id,
          f"каждые {config.get('DELTA_SEND')} минут будут появляться мемы")
    else:
      bot.send_message(message.chat.id, f"У ТЕБЯ НЕТ ПРАВ")
  else:
    bot.send_message(message.chat.id, f"У ТЕБЯ НЕТ ПРАВ")


@bot.message_handler(commands=['print_admins'])
def print_admins(message):
  admin_users = checAdminUser(message)
  if admin_users:
    bot.send_message(message.chat.id, f"всего админов: ")
    for i in config['USERS_ADMIN']:
      bot.send_message(message.chat.id, f"@{i}")
  else:
    bot.send_message(message.chat.id, f"У ТЕБЯ НЕТ ПРАВ")


@bot.message_handler(commands=['print_chanel'])
def print_chanels(message):
  admin_users = checAdminUser(message)
  if admin_users:
    bot.send_message(message.chat.id, f"рассылка мемов в канале: ")
    bot.send_message(message.chat.id, f"{config['CHANEL_LOGIN']}")
  else:
    bot.send_message(message.chat.id, f"У ТЕБЯ НЕТ ПРАВ")


@bot.message_handler(commands=['set_chanel'])
def set_chanel(message):
  if (message.from_user.username == 'Denz_ox'):
    bot.send_message(message.chat.id, f"Введите название канала")
    bot.register_next_step_handler(message, set_name_chanel)
  else:
    bot.send_message(message.chat.id, f"У ТЕБЯ НЕТ ПРАВ")


@bot.message_handler(commands=['set_admin'])
def set_admin(message):
  if (message.from_user.username == 'Denz_ox'):
    bot.send_message(message.chat.id, f"Введите имя админа")
    bot.register_next_step_handler(message, set_name_admin)
  else:
    bot.send_message(message.chat.id, f"У ТЕБЯ НЕТ ПРАВ")


@bot.message_handler(commands=['erase_admin'])
def erase_admin(message):
  if (message.from_user.username == 'Denz_ox'):
    bot.send_message(message.chat.id, f"Введите имя админа")
    bot.register_next_step_handler(message, erase_name_admin)
  else:
    bot.send_message(message.chat.id, f"У ТЕБЯ НЕТ ПРАВ")


@bot.message_handler(commands=['print_value_mems'])
def print_value_mems(message):
  admin_users = checAdminUser(message)
  if admin_users:
    bot.send_message(
        message.chat.id,
        f"количество сохраненных мемов равно { len(config.get('PHOTO_ID')) }")


@bot.message_handler(commands=['print_steps'])
def print_steps(message):
  admin_users = checAdminUser(message)
  if admin_users:
    bot.send_message(
        message.chat.id,
        f"размер пачки отправляемых мемов равен { config.get('STEP') }")
  else:
    bot.send_message(message.chat.id, f"У ТЕБЯ НЕТ ПРАВ")


@bot.message_handler(commands=['set_steps'])
def set_steps(message):

  admin_users = checAdminUser(message)

  if admin_users:
    bot.send_message(message.chat.id,
                     f"введите размер пачки отправляемых мемов")

    bot.register_next_step_handler(message, set_value_steps)
  else:
    bot.send_message(message.chat.id, f"У ТЕБЯ НЕТ ПРАВ")


@bot.message_handler(commands=['send_mem'])
def send_mem(message):

  admin_users = checAdminUser(message)
  if admin_users:
    length_list_id_mems = len(config.get('PHOTO_ID'))

    if (length_list_id_mems != 0
        and length_list_id_mems - config.get('STEP') >= 0):
      while len(
          config.get('PHOTO_ID')) != length_list_id_mems - config.get('STEP'):
        try:
          bot.send_photo(config.get('CHANEL_LOGIN'),
                         config.get('PHOTO_ID').pop(0))
          bot.send_message(message.chat.id,
                           f"мем оправлен в {config.get('CHANEL_LOGIN')} ")
          save_json(config)
        except:
          time.sleep(1)

      bot.send_message(
          message.chat.id,
          f"отправка {config.get('STEP')} мемов в {config.get('CHANEL_LOGIN')} завершена"
      )
    elif (length_list_id_mems - config.get('STEP') <= 0):
      bot.send_message(
          message.chat.id,
          f"запрос на отправку {config.get('STEP')} мемов не осуществлен, т.к. хранится {length_list_id_mems} мема"
      )
    else:
      bot.send_message(message.chat.id, f"мемов нет :(")

  else:
    bot.send_message(message.chat.id, f"У ТЕБЯ НЕТ ПРАВ")


@bot.message_handler()
def no_correct_input(message):
  if message.text[0] == "/":
    bot.send_message(message.chat.id, f"что ты высрал")


@bot.message_handler()
def set_name_chanel(message):
  print("L")
  if config['CHANEL_LOGIN'][1:] != message.text:
    print("YESS")
    config['CHANEL_LOGIN'] = '@' + message.text
    save_json(config)
    bot.send_message(message.chat.id,
                     f"@{message.text} теперь рассылаемый канал")
  else:
    bot.send_message(message.chat.id,
                     f"@{message.text} уже в рассылаемый канал")


@bot.message_handler()
def set_name_admin(message):
  if config['USERS_ADMIN'].count(message.text) == 0:
    config['USERS_ADMIN'].append(message.text)
    save_json(config)
    bot.send_message(message.chat.id, f"@{message.text} в списке админов")
  else:
    bot.send_message(message.chat.id, f"@{message.text} уже в списке админов")


@bot.message_handler()
def erase_name_admin(message):
  try:
    config['USERS_ADMIN'].pop(config['USERS_ADMIN'].index(message.text))
    save_json(config)
    bot.send_message(message.chat.id,
                     f"@{message.text} удален из списка админов")
  except:
    bot.send_message(message.chat.id, f'В списке нет @{message.text}')


@bot.message_handler()
def set_value_steps(message):
  admin_users = checAdminUser(message)
  if admin_users:
    try:
      if (int(message.text) > 0):
        config["STEP"] = int(message.text)
        bot.send_message(
            message.chat.id,
            f"размер пачки отправляемых мемов равен {config.get('STEP') }")
        save_json(config)
      else:
        bot.send_message(message.chat.id, f"введено число меньше 1")
    except:
      bot.send_message(message.chat.id, f"введено не число")
  else:
    bot.send_message(message.chat.id, f"У ТЕБЯ НЕТ ПРАВ")


@bot.message_handler()
def set_value_minute_spawn_mem(message):
  admin_users = checAdminUser(message)
  if admin_users:
    try:
      if (int(message.text) > 0):
        config["DELTA_SEND"] = int(message.text) * 60
        bot.send_message(
            message.chat.id,
            f"мемы будут появляться каждые {config.get('DELTA_SEND') } минут")
        save_json(config)

      else:
        bot.send_message(message.chat.id, f"введено число меньше 1")
    except:
      bot.send_message(message.chat.id, f"введено не число")
  else:
    bot.send_message(message.chat.id, f"У ТЕБЯ НЕТ ПРАВ")


@bot.message_handler()
def set_n_mem(message):
  admin_users = checAdminUser(message)
  if admin_users:
    if (message.text.count(',') == 1):
      a, b = message.text.split(',')
      if (int(a) >= 0 and int(b) >= 0):
        i = int(a)
        while i < int(b):
          try:
            bot.send_message(message.chat.id, f"{i} мем:")
            bot.send_photo(message.chat.id, config.get('PHOTO_ID')[i])
            i += 1
          except:
            time.sleep(1)
      else:
        bot.send_message(message.chat.id, f"введено число меньше 0")
    else:
      try:
        if (int(message.text) >= 0):
          bot.send_photo(message.chat.id,
                         config.get('PHOTO_ID')[int(message.text)])

        else:
          bot.send_message(message.chat.id, f"введено число меньше 0")
      except:
        bot.send_message(message.chat.id, f"введено не число")
  else:
    bot.send_message(message.chat.id, f"У ТЕБЯ НЕТ ПРАВ")


def erase_n_mem(message):
  admin_users = checAdminUser(message)
  if admin_users:
    try:
      if (int(message.text) >= 0):
        bot.send_photo(message.chat.id,
                       config.get('PHOTO_ID').pop(int(message.text)))
        bot.send_message(message.chat.id, f"мем удален")
      else:
        bot.send_message(message.chat.id, f"введено число меньше 0")
    except:
      bot.send_message(message.chat.id, f"введено не число")
  else:
    bot.send_message(message.chat.id, f"У ТЕБЯ НЕТ ПРАВ")


@bot.message_handler()
def startSending():
  length_list_id_mems = len(config.get('PHOTO_ID'))
  if (length_list_id_mems != 0
      and length_list_id_mems - config.get('STEP') >= 0):
    while len(
        config.get('PHOTO_ID')) != length_list_id_mems - config.get('STEP'):
      try:
        bot.send_photo(config.get('CHANEL_LOGIN'),
                       config.get('PHOTO_ID').pop(0))
        save_json(config)
        bot.send_message(config.get('GROUP_ID'),
                         f"мем оправлен в {config.get('CHANEL_LOGIN')} ")

      except:
        time.sleep(1)
    bot.send_message(
        config.get('GROUP_ID'),
        f"отправка {config.get('STEP')} мемов в {config.get('CHANEL_LOGIN')} завершена"
    )
  elif (length_list_id_mems - config.get('STEP') <= 0):
    bot.send_message(
        config.get('GROUP_ID'),
        f"запрос на отправку {config.get('STEP')} мемов не осуществлен, т.к. хранится {length_list_id_mems} мема"
    )
  else:
    bot.send_message(config.get('GROUP_ID'), f"мемов нет :(")


Thread(target=schedule_checker).start()

keep_alive()

bot.polling(non_stop=True, interval=0)
