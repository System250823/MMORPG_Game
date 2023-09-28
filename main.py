import random 
from random import choice
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram import os
from aiogram.types import InputFile
API_TOKEN = '6665407722:AAGkQHHYsNikQJRjTRoNvBwWJfwKLB50YQ8'


bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

monsters = [
    {"name": "Гоблин", "level": 5, "HP": 30, "damage": 10, "reward_gold": 30, 'img' : 'goblin',},
    {"name": "Орк", "level": 35, "HP": 200, "damage": 40, "reward_gold": 50, 'img' : 'ork',},
    {"name": "Велетень", "level": 70, "HP": 1000, "damage": 50, "reward_gold": 100, 'img' : 'giant',},
    {"name": "Маленький слизь", "level": 20, "HP": 100, "damage": 20, "reward_gold": 40, 'img' : 'small slime',},
    {"name": "Велика слизь", "level": 250, "HP": 2000, "damage": 80, "reward_gold": 500, 'img' : 'big slime',},
    {"name": "Хімера", "level": 500, "HP": 4000, "damage": 150, "reward_gold": 1000, 'img' : 'chimera',},
    {"name": "Дракон", "level": 700, "HP": 6500, "damage": 250, "reward_gold": 5000, 'img' : 'dragon',},
    {"name": "Великий Дракон", "level": 1000, "HP": 10000, "damage": 1000, "reward_gold": 10000, 'img' : 'big dragon'}
]

players = {}
main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(types.KeyboardButton('Пошук монстра'))
main_menu.add(types.KeyboardButton('Атакувати'))
main_menu.add(types.KeyboardButton('Магазин'))

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    players[user_id] = {"level": 1, "HP": 100, "damage": 10, "gold": 0}
    await message.answer("Ласкаво просимо до гри! Ви створили свого персонажа.", reply_markup=main_menu)

@dp.message_handler(text=("Пошук монстра"))
async def start_battle(message: types.Message):
    user_id = message.from_user.id
    if user_id not in players:
        await message.answer("Для початку гри скористайтеся /start.")
        return
    monster = random.choice(monsters)
    players[user_id]["current_monster"] = monster
    players[user_id]["monster_HP"] = monster["HP"]
    monster_image_path = f'{monster["img"]}.jpg'
    markup = types.ReplyKeyboardRemove()
    await message.answer_photo(photo=InputFile(monster_image_path),
                        caption=f"Ви почали битву з монстром: \n{monster['name']}\nРівень ({monster['level']})\nЗдоров\'я : {monster['HP']}\nШкода : {monster['damage']}\n"
                        f"Ваше поточне здоров'я: {players[user_id]['HP']}\n "
                        "Використовуйте 'Атакувати', щоб атакувати монстра.", )

@dp.message_handler(text=("Атакувати"))
async def attack_monster(message: types.Message):
    user_id = message.from_user.id
    if user_id not in players:
        await message.answer("Для початку гри скористайтеся /start.")
        return
    if "current_monster" not in players[user_id]:
        await message.answer("Для початку битви скористайтесь Battle.")
        return
    monster = players[user_id]["current_monster"]
    player_damage = players[user_id]["damage"]
    player_damage_done = random.randint(player_damage - 5, player_damage + 5)
    monster_damage_done = random.randint(monster["damage"] - 5, monster["damage"] + 5)
    players[user_id]["monster_HP"] -= player_damage_done
    players[user_id]["HP"] -= monster_damage_done
    if players[user_id]["monster_HP"] <= 0:
        gold_reward = monster["reward_gold"]
        players[user_id]["gold"] += gold_reward
        players[user_id].pop("current_monster", None)
        await message.answer(f"Вітаємо! Ви перемогли монстра та здобули {gold_reward} золотих.\n "
                             f"Ваше поточне здоров'я: {players[user_id]['HP']}.")
        await message.answer("Використовуйте /battle щоб почати нову битву.")
    elif players[user_id]["HP"] <= 0:
        players.pop(user_id, None)
        await message.answer("Ви програли. Ваш персонаж помер. Для початку нової гри скористайтеся /start.")
    else:
        await message.answer(f"Ви завдали {player_damage_done} урона монстру\n "
                             f"Ваше поточне здоров'я: {players[user_id]['HP']}\n "
                             f"Здоров'я монстра: {players[user_id]['monster_HP']}")

@dp.message_handler(text=("Магазин"))
async def visit_shop(message: types.Message):
    user_id = message.from_user.id
    if user_id not in players:
        await message.answer("Для початку гри скористайтеся /start.")
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("/upgrade_damage", "/upgrade_hp")
    await message.answer("Ласкаво просимо до магазину!\nЩо б ви хотіли покращити?\nНапишіть якщо хочете покращити урон /upgrade_damage\nАбо якщо хочете покращити здоров\'я /upgrade_hp ",)

@dp.message_handler(commands=("upgrade_damage"))
async def upgrade_damage(message: types.Message):
    user_id = message.from_user.id
    if user_id not in players:
        await message.answer("Для початку гри скористайтеся /start.")
        return
    if players[user_id]["gold"] < 20:
        await message.answer("У вас недостатньо золота для покращення.")
        return
    players[user_id]["gold"] -= 20
    players[user_id]["damage"] += 10
    await message.answer(f"Стата покращена! Поточна шкода: {players[user_id]['damage']}.\n Залишок золота: {players[user_id]['gold']}.")

@dp.message_handler(commands=("upgrade_hp"))
async def upgrade_health(message: types.Message):
    user_id = message.from_user.id
    if user_id not in players:
        await message.answer("Для початку гри скористайтеся /start.")
        return
    if players[user_id]["gold"] < 20:
        await message.answer("У вас недостатньо золота для покращення.")
        return
    players[user_id]["gold"] -= 20
    players[user_id]["HP"] += 50
    await message.answer(f"Стата покращена! Поточне здоров\'я: {players[user_id]['HP']}.\n Залишок золота: {players[user_id]['gold']}.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
