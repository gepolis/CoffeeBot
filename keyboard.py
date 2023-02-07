import math

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

import database
from config import rub

db = database.Database("db.db")


def main_menu(user):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add(KeyboardButton("☕️Меню"))
    if db.is_admin(user):
        kb.add(KeyboardButton("💻 Админ панель"))
    return kb


def menu():
    kb = InlineKeyboardMarkup()
    for drink in db.get_items():
        if drink[2] == 1:
            kb.add(InlineKeyboardButton(f"{drink[1]} - {drink[4]}{rub}", callback_data=f"drink_{drink[0]}"))
    return kb


def item_settings(item):
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("🥛", callback_data=f"item_{item}_milk"),
           InlineKeyboardButton("🗨", callback_data=f"item_{item}_comment"),
           InlineKeyboardButton("🆙", callback_data=f"item_{item}_size"))
    kb.add(InlineKeyboardButton("💳 Оплатить",callback_data=f"item_{item}_buy"))
    kb.add(InlineKeyboardButton("⬅ Назад", callback_data="back_menu"))
    return kb


def item_milks(item):
    kb = InlineKeyboardMarkup()
    milks = db.get_milks()
    for milk in milks:
        kb.add(InlineKeyboardButton(f"{milk[1]} - {str(milk[3])}{rub}", callback_data=f"setting_{item}_milk_{milk[0]}"))
    return kb


def item_sizes(item):
    kb = InlineKeyboardMarkup()
    sizes = db.get_sizes()
    for size in sizes:
        kb.add(InlineKeyboardButton(f"{size[1]}({size[2]}мл) - {str(size[3])}{rub}",
                                    callback_data=f"setting_{item}_size_{size[0]}"))
    return kb


def admin_panel():
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("🙍 Пользователи", callback_data="admin_users"),
           InlineKeyboardButton("📦 Товары", callback_data="admin_items_1"))
    kb.row(InlineKeyboardButton("📦 Заказы", callback_data="admin_orders"),
           InlineKeyboardButton("📈 Статистика", callback_data="admin_stats"))
    return kb

def admin_item_edit_back(item):
    return InlineKeyboardMarkup().add(InlineKeyboardButton("Назад",callback_data=f"admin_items_item_{item}"))

def admin_users():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("💻 Администрация", callback_data="admin_users_admin_1"))
    kb.add(InlineKeyboardButton("🙍 Пользователи", callback_data="admin_users_users_1"))
    kb.add(InlineKeyboardButton("⬅ Назад", callback_data="admin_panel"))
    return kb


def admin_users_admin(page: int = 1):
    kb = InlineKeyboardMarkup()
    max_page = math.ceil(len(db.get_admins()) / 10)
    print(page)
    for admin in db.get_admins_limit(page):
        kb.add(InlineKeyboardButton(f"{admin[1]}", callback_data=f"admin_user_{admin[1]}"))
    kb.row(InlineKeyboardButton(f"⏪", callback_data="admin_users_admin_1"),
           InlineKeyboardButton("⬅", callback_data=f"admin_users_admin_{page - 1}"),
           InlineKeyboardButton(f"{page}", callback_data=f"admin_users_admin_{page}"),
           InlineKeyboardButton("➡", callback_data=f"admin_users_admin_{page + 1}"),
           InlineKeyboardButton("⏩", callback_data=f"admin_users_admin_{max_page}")
           )
    kb.add(InlineKeyboardButton("⬅ Назад", callback_data="admin_users"))
    return kb


def admin_users_users(page: int = 1):
    kb = InlineKeyboardMarkup()
    max_page = math.ceil(len(db.get_users_limit(page)) / 10)
    print(page)
    for user in db.get_users_limit(page):
        kb.add(InlineKeyboardButton(f"{user[1]}", callback_data=f"admin_user_{user[1]}"))
    kb.row(InlineKeyboardButton(f"⏪", callback_data="admin_users_users_1"),
           InlineKeyboardButton("⬅", callback_data=f"admin_users_users_{page - 1}"),
           InlineKeyboardButton(f"{page}", callback_data=f"admin_users_users_{page}"),
           InlineKeyboardButton("➡", callback_data=f"admin_users_users_{page + 1}"),
           InlineKeyboardButton("⏩", callback_data=f"admin_users_users_{max_page}")
           )
    kb.add(InlineKeyboardButton("⬅ Назад", callback_data="admin_users"))
    return kb


def admin_items(page):
    kb = InlineKeyboardMarkup()
    max_page = math.ceil(len(db.get_admins()) / 10)
    print(page)
    for item in db.get_items_limit(page):
        kb.add(InlineKeyboardButton(f"{item[1]}", callback_data=f"admin_items_item_{item[0]}"))
    kb.row(InlineKeyboardButton(f"⏪", callback_data="admin_items_1"),
           InlineKeyboardButton("⬅", callback_data=f"admin_items_{page - 1}"),
           InlineKeyboardButton(f"{page}", callback_data=f"admin_items_{page}"),
           InlineKeyboardButton("➡", callback_data=f"admin_items_{page + 1}"),
           InlineKeyboardButton("⏩", callback_data=f"admin_items_{max_page}")
           )
    kb.add(InlineKeyboardButton("➕ Создать", callback_data=f"admin_items_item_create"))
    kb.add(InlineKeyboardButton("⬅ Назад", callback_data="admin_panel"))
    return kb


def admin_orders():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("💳 Оплачены", callback_data="admin_orders_pay"))
    kb.add(InlineKeyboardButton("✅ Получены", callback_data="admin_orders_gave"))
    kb.add(InlineKeyboardButton("🔎 Поиск", callback_data="admin_orders_search"))
    return kb


def admin_user(user):
    kb = InlineKeyboardMarkup()
    print(db.is_admin(user))
    if not db.is_admin(user):
        admin = {"text": "➕ Выдать права администратора", "callback": "1"}
    else:
        admin = {"text": "➖ Забрать права администратора", "callback": "0"}
    kb.add(InlineKeyboardButton(text=admin['text'], callback_data=f"admin_user_{user}_adm_{admin['callback']}"))
    kb.add(InlineKeyboardButton(text="❌ Удалить", callback_data=f"admin_user_{user}_delete"))
    kb.add(InlineKeyboardButton(text="⬅ Назад", callback_data="admin_users"))
    return kb


def admin_user_delete(user):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Подтвердить", callback_data=f"admin_user_{user}_delete_confirm"))
    kb.add(InlineKeyboardButton("❌ Отменить", callback_data=f"admin_user_{user}"))
    return kb


def admin_item(item):
    item_i = db.get_item(item)
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("❌ Удалить", callback_data=f"admin_items_{item}_delete"))
    kb.add(InlineKeyboardButton("⬅ Назад", callback_data="admin_items_1"))
    return kb
