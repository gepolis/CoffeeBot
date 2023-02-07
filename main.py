import asyncio
import time

from aiogram import Dispatcher, Bot, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from config import *
from core import Core
from keyboard import *

bot = Bot(API_TOKEN)

# For example use simple MemoryStorage for Dispatcher.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
core = Core()


# States
class UserOrderComment(StatesGroup):
    comment = State()  # Will be represented in storage as 'Form:name'


class AdminCreateItem(StatesGroup):
    name = State()
    description = State()
    price = State()


class AdminEditItem(StatesGroup):
    name = State()
    description = State()
    price = State()


async def drink(callback, callbackData):
    if not db.exists_order(callbackData[1], callback.from_user.id):
        db.add_item_orders(callback.message.message_id, callbackData[1], callback.from_user.id)
    item_order = db.get_order(callbackData[1], callback.from_user.id, 'wait')
    item = db.get_item(callbackData[1])
    price = core.calc_price(callback.from_user.id)
    await callback.message.edit_text(
        text=f"""<b>{item[1]}</b>
        
{item[1]}: {item[4]}{rub}
{price["size"]["name"]}({price['size']['ml']}мл): <b>{price['size']['price']}{rub}</b>
{price['milk']['name']}: <b>{price['milk']['price']}{rub}</b>

Комментарий: {item_order[3]}

Итог: <b>{price['total']['price']}</b>{rub}""",
        parse_mode="HTML",
        reply_markup=item_settings(callbackData[1])
    )


async def drink_msg(chat_id, message_id, message, callbackData):
    item_order = db.get_order(callbackData[1], message.from_user.id, 'wait')
    item = db.get_item(callbackData[1])
    price = core.calc_price(message.from_user.id)
    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=f"""<b>{item[1]}</b>

{item[1]}: {item[4]}{rub}
{price["size"]["name"]}({price['size']['ml']}мл): <b>{price['size']['price']}{rub}</b>
{price['milk']['name']}: <b>{price['milk']['price']}{rub}</b>
        
Комментарий: {item_order[3]}

Итог: <b>{price['total']['price']}</b>{rub}""",
        parse_mode="HTML",
        reply_markup=item_settings(callbackData[1])
    )


@dp.message_handler()
async def message(message: types.Message):
    if not db.exists_user(message.from_user.id):
        db.add_user(message.from_user.id)
    if message.text == "/start":
        await message.answer(text="Главное меню", reply_markup=main_menu(message.from_user.id))
    if message.text == "☕️Меню":
        await message.answer(text="Меню", reply_markup=menu())
    if message.text == "💻 Админ панель":
        if db.is_admin(message.from_user.id):
            await message.answer(text="Админ панель:", reply_markup=admin_panel())


@dp.callback_query_handler()
async def callback_handler(callback: types.CallbackQuery):
    await callback.answer(callback.data)
    callback_data = callback.data.split("_")
    if callback_data[0] == "drink":
        print(callback_data[1])
        await drink(callback, callback_data)
    if callback_data[0] == "item":
        if callback_data[2] == "milk":
            await callback.message.edit_text("Выберите тип молока:", reply_markup=item_milks(callback_data[1]))
        if callback_data[2] == "size":
            await callback.message.edit_text("Выберите размер:", reply_markup=item_sizes(callback_data[1]))
        if callback_data[2] == "comment":
            await UserOrderComment.comment.set()
            await callback.message.edit_text("Введите коментарий к заказу:")
        if callback_data[2] == "buy":
            order = db.get_order(int(callback_data[1]),callback.from_user.id,'wait')
            item = db.get_item(int(callback_data[1]))
            order = core.calc_price_order(order)
            desc=f"Размер: {order['size']['name']}({order['size']['ml']}): {order['size']['price']}{rub}\nРазмер: {order['milk']['name']}: {order['milk']['price']}{rub}"
            await bot.send_invoice(
                callback.message.chat.id,
                title=item[1],
                description=desc,
                provider_token="381764678:TEST:50100",
                currency='rub',
                is_flexible=False,  # True если конечная цена зависит от способа доставки
                prices=[types.LabeledPrice(label=item[1], amount=order['total']['price']*100)],
                start_parameter='time-machine-example',
                payload='some-invoice-payload-for-our-internal-use'
            )
    if callback_data[0] == "setting":
        if callback_data[2] == "milk":
            db.set_order_milk(callback.from_user.id, callback_data[1], callback_data[3])
            await drink(callback, callback_data)
        if callback_data[2] == "size":
            db.set_order_size(callback.from_user.id, callback_data[1], callback_data[3])
            await drink(callback, callback_data)
    if callback_data[0] == "back":
        if callback_data[1] == "menu":
            db.delete_order(callback.from_user.id)
            await callback.message.edit_text("Меню:", reply_markup=menu())
    if callback_data[0] == "admin":
        if db.is_admin(callback.from_user.id):
            if callback_data[1] == "items":
                if len(callback_data) == 3:
                    await callback.message.edit_text("Товары", reply_markup=admin_items(int(callback_data[2])))
                if len(callback_data) == 4:
                    if callback_data[3] == "delete":
                        db.delete_item(callback_data[2])
                        await callback.message.edit_text("✅ Вы успешно удалили товар!")
                        await asyncio.sleep(1)
                        await callback.message.edit_text("Товары:", reply_markup=admin_items(1))
                    if callback_data[3] == "create":
                        await callback.message.edit_text("Введите название:")
                        await AdminCreateItem().name.set()
                    else:
                        await callback.message.edit_text(f"{db.get_item(callback_data[3])[3]}",
                                                         reply_markup=admin_item(callback_data[3]))
            if callback_data[1] == "panel":
                await callback.message.edit_text("Админ панель:", reply_markup=admin_panel())
            if callback_data[1] == "user":
                if len(callback_data) == 3:
                    await callback.message.edit_text(text=f"{callback_data[2]}",
                                                     reply_markup=admin_user(callback_data[2]))
                elif len(callback_data) == 4:
                    if callback_data[3] == "delete":
                        if int(callback_data[2]) == callback.from_user.id:
                            return False
                        await callback.message.edit_text("Подтвердить удаление:",
                                                         reply_markup=admin_user_delete(callback_data[2]))
                else:
                    if callback_data[4] == "confirm":
                        db.delete_user(callback_data[2], 1)
                        await callback.message.edit_text("✅ Успешное удаление!")
                        await asyncio.sleep(1)
                        await callback.message.edit_text("Пользователи",
                                                         reply_markup=admin_users())
                    if callback_data[3] == "adm":
                        if int(callback_data[2]) == callback.from_user.id and callback_data[4] == "0":
                            return False
                        db.user_set_admin(callback_data[2], callback_data[4])
                        await callback.message.edit_text("✅ Успех!")
                        await asyncio.sleep(1)
                        await callback.message.edit_text("Пользователь",
                                                         reply_markup=admin_user(callback_data[2]))
            if callback_data[1] == "users":
                if len(callback_data) == 2:
                    await callback.message.edit_text(text="Пользователи", reply_markup=admin_users())
                else:

                    if callback_data[2] == "admin":
                        if int(callback_data[3]) >> math.ceil(len(db.get_admins()) / 10) or int(callback_data[3]) <= 0:
                            return
                        await bot.edit_message_text(chat_id=callback.message.chat.id,
                                                    message_id=callback.message.message_id,
                                                    text=f"Администрация({callback_data[3]}/{math.ceil(len(db.get_admins()) / 10)})",
                                                    reply_markup=admin_users_admin(int(callback_data[3])))
                    if callback_data[2] == "users":
                        if int(callback_data[3]) >> math.ceil(len(db.get_users()) / 10) or int(
                                callback_data[3]) <= 0:
                            return
                        await bot.edit_message_text(chat_id=callback.message.chat.id,
                                                    message_id=callback.message.message_id,
                                                    text=f"Пользователи({callback_data[3]}/{math.ceil(len(db.get_users()) / 10)})",
                                                    reply_markup=admin_users_users(int(callback_data[3])))
@dp.pre_checkout_query_handler(lambda query: True)
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    print('successful_payment:')
    pmnt = message.successful_payment.to_python()
    for key, val in pmnt.items():
        print(f'{key} = {val}')

    await bot.send_message(
        message.chat.id,
        "Успешная оплата."
    )
    db.set_order_status(message.from_user.id,"wait","payed",round(time.time()))
    order = db.get_order_payed(message.from_user.id)
    await bot.send_message(
        -1001686676348,
        f"<b>Новый заказ</b>\n\n{db.get_size(order[5])[1]} {db.get_milk(order[6])[1]} {db.get_item(order[4])[1]}",
        parse_mode="HTML"
    )

@dp.message_handler(state=UserOrderComment.comment)
async def process_comment(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['comm'] = message.text
    db.set_comment(message.from_user.id, message.text)
    await state.finish()
    order = db.get_order_user(message.from_user.id, 'wait')

    await drink_msg(message.chat.id, order[7], message, ["drink", str(order[4])])
    await message.delete()


@dp.message_handler(state=AdminCreateItem.name)
async def process_name(message: types.Message, state: FSMContext):
    db.create_item(message.text)
    db.set_itemname(message.text, message.from_user.id)
    await message.answer(text="Введите описание товара:")
    await AdminCreateItem.next()


@dp.message_handler(state=AdminCreateItem.description)
async def process_desc(message: types.Message, state: FSMContext):
    db.set_description(message.text, db.get_user(message.from_user.id)[3])
    await message.answer(text="Введите цену товара:")

    await AdminCreateItem.next()


@dp.message_handler(state=AdminCreateItem.price)
async def process_price(message: types.Message, state: FSMContext):
    try:
        num = int(message.text)
    except Exception as e:
        await message.answer(text="Ошибка, введите число:")
        await AdminCreateItem.price.set()
        return False
    db.set_price(int(message.text), db.get_user(message.from_user.id)[3])
    db.set_show(db.get_user(message.from_user.id)[3])
    msg = await message.answer(text="Вы успешно создали товар!")
    await asyncio.sleep(1)
    await msg.edit_text(text="Товары", reply_markup=admin_items(1))
    await state.finish()


executor.start_polling(dp)
