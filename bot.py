import asyncio
import logging
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from database import (
    init_db, get_or_create_user, update_family_size,
    save_shopping_list, get_user_history, get_family_size,
    update_weekly_budget, get_weekly_budget,
    update_language, get_language, get_user_profile
)
from ai_helper import get_meal_suggestion, get_recipe_by_name, get_weekly_plan, get_budget_weekly_plan
from translations import t
from webserver import start_webserver

load_dotenv()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(storage=MemoryStorage())

WEBAPP_URL = os.getenv("WEBAPP_URL", "")  # ngrok yoki hosting URL


class UserState(StatesGroup):
    waiting_for_preference = State()
    waiting_for_recipe_name = State()
    waiting_for_family_size = State()
    waiting_for_budget = State()


def main_keyboard(lang: str) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text=t(lang, "btn_suggest")), KeyboardButton(text=t(lang, "btn_recipe"))],
        [KeyboardButton(text=t(lang, "btn_budget")), KeyboardButton(text=t(lang, "btn_weekly"))],
        [KeyboardButton(text=t(lang, "btn_family")), KeyboardButton(text=t(lang, "btn_history"))],
        [KeyboardButton(text=t(lang, "btn_help"))],
    ]
    if WEBAPP_URL:
        buttons[-1].append(
            KeyboardButton(text=t(lang, "btn_webapp"), web_app=WebAppInfo(url=WEBAPP_URL))
        )
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def lang_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
        ]
    ])


# /start
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await get_or_create_user(message.from_user.id, message.from_user.full_name)
    await message.answer(
        t("uz", "choose_lang"),
        reply_markup=lang_keyboard()
    )


@dp.callback_query(F.data.in_({"lang_uz", "lang_ru"}))
async def set_language(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    await update_language(callback.from_user.id, lang)
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer(
        t(lang, "welcome", name=callback.from_user.first_name),
        parse_mode="Markdown",
        reply_markup=main_keyboard(lang)
    )


async def get_lang(user_id: int) -> str:
    return await get_language(user_id)


# Ovqat tavsiya qil
@dp.message(F.text.in_({t("uz", "btn_suggest"), t("ru", "btn_suggest")}))
async def ask_preference(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    await state.set_state(UserState.waiting_for_preference)
    await message.answer(t(lang, "ask_preference"), parse_mode="Markdown")


@dp.message(UserState.waiting_for_preference)
async def process_preference(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_lang(message.from_user.id)
    thinking_msg = await message.answer(t(lang, "thinking"))

    family_size = await get_family_size(message.from_user.id)
    result = await get_meal_suggestion(message.text, family_size, lang)

    await save_shopping_list(
        message.from_user.id,
        result["meal_name"],
        result["full_response"],
        result["full_response"]
    )

    await thinking_msg.delete()
    await message.answer(result["full_response"])

    inline_buttons = [
        [InlineKeyboardButton(text=t(lang, "btn_new_suggest"), callback_data="new_suggestion")],
    ]
    if WEBAPP_URL:
        inline_buttons.append([
            InlineKeyboardButton(
                text="🛒 Bozorlik ro'yxatini ko'rish" if lang == "uz" else "🛒 Открыть список покупок",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ])

    await message.answer(
        t(lang, "suggest_again"),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_buttons)
    )


# Retsept izla
@dp.message(F.text.in_({t("uz", "btn_recipe"), t("ru", "btn_recipe")}))
async def ask_recipe_name(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    await state.set_state(UserState.waiting_for_recipe_name)
    await message.answer(t(lang, "ask_recipe"), parse_mode="Markdown")


@dp.message(UserState.waiting_for_recipe_name)
async def process_recipe_name(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_lang(message.from_user.id)
    thinking_msg = await message.answer(t(lang, "recipe_thinking", name=message.text), parse_mode="Markdown")

    family_size = await get_family_size(message.from_user.id)
    recipe = await get_recipe_by_name(message.text, family_size, lang)

    await thinking_msg.delete()
    await message.answer(recipe)


# Byudjet bo'yicha reja
@dp.message(F.text.in_({t("uz", "btn_budget"), t("ru", "btn_budget")}))
async def ask_budget(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    current_budget = await get_weekly_budget(message.from_user.id)
    family_size = await get_family_size(message.from_user.id)

    if current_budget > 0:
        await message.answer(
            t(lang, "current_budget", budget=current_budget, family_size=family_size),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=t(lang, "btn_use_budget"), callback_data="use_saved_budget")],
                [InlineKeyboardButton(text=t(lang, "btn_change_budget"), callback_data="change_budget")],
            ])
        )
    else:
        await state.set_state(UserState.waiting_for_budget)
        await message.answer(t(lang, "ask_budget"), parse_mode="Markdown")


@dp.message(UserState.waiting_for_budget)
async def process_budget(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    try:
        budget_text = message.text.strip().replace(" ", "").replace(",", "")
        budget = float(budget_text)

        if budget < 10000:
            await message.answer(t(lang, "budget_too_low"))
            return
        if budget > 100_000_000:
            await message.answer(t(lang, "budget_too_high"))
            return

        await update_weekly_budget(message.from_user.id, budget)
        await state.clear()

        family_size = await get_family_size(message.from_user.id)
        thinking_msg = await message.answer(
            t(lang, "budget_saved", budget=budget, family_size=family_size),
            parse_mode="Markdown"
        )

        plan = await get_budget_weekly_plan(budget, family_size, lang)
        await thinking_msg.delete()
        await _send_long_message(message, plan)

    except ValueError:
        await message.answer(t(lang, "budget_invalid"), parse_mode="Markdown")


@dp.callback_query(F.data == "use_saved_budget")
async def use_saved_budget(callback: CallbackQuery):
    lang = await get_lang(callback.from_user.id)
    budget = await get_weekly_budget(callback.from_user.id)
    family_size = await get_family_size(callback.from_user.id)
    await callback.answer()

    thinking_msg = await callback.message.answer(
        t(lang, "budget_thinking", budget=budget),
        parse_mode="Markdown"
    )
    plan = await get_budget_weekly_plan(budget, family_size, lang)
    await thinking_msg.delete()
    await _send_long_message(callback.message, plan)


@dp.callback_query(F.data == "change_budget")
async def change_budget(callback: CallbackQuery, state: FSMContext):
    lang = await get_lang(callback.from_user.id)
    await callback.answer()
    await state.set_state(UserState.waiting_for_budget)
    await callback.message.answer(t(lang, "change_budget_ask"))


# Haftalik reja
@dp.message(F.text.in_({t("uz", "btn_weekly"), t("ru", "btn_weekly")}))
async def weekly_plan(message: Message):
    lang = await get_lang(message.from_user.id)
    thinking_msg = await message.answer(t(lang, "weekly_thinking"))
    family_size = await get_family_size(message.from_user.id)
    plan = await get_weekly_plan(family_size, lang)
    await thinking_msg.delete()
    await _send_long_message(message, plan)


# Tarix
@dp.message(F.text.in_({t("uz", "btn_history"), t("ru", "btn_history")}))
async def show_history(message: Message):
    lang = await get_lang(message.from_user.id)
    profile = await get_user_profile(message.from_user.id)
    history = await get_user_history(message.from_user.id)

    text = t(lang, "history_title")
    text += t(lang, "family_count", size=profile["family_size"])
    if profile["weekly_budget"] > 0:
        text += t(lang, "budget_line", budget=profile["weekly_budget"])
    else:
        text += t(lang, "no_budget")

    if history:
        text += t(lang, "history_list")
        for i, (meal_name, created_at) in enumerate(history, 1):
            date = created_at[:10] if created_at else ""
            text += f"{i}. {meal_name} — {date}\n"
    else:
        text += t(lang, "no_history")

    await message.answer(text, parse_mode="Markdown")


# Oila soni
@dp.message(F.text.in_({t("uz", "btn_family"), t("ru", "btn_family")}))
async def ask_family_size(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    current = await get_family_size(message.from_user.id)
    await state.set_state(UserState.waiting_for_family_size)
    await message.answer(t(lang, "ask_family_size", size=current), parse_mode="Markdown")


@dp.message(UserState.waiting_for_family_size)
async def process_family_size(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    try:
        size = int(message.text.strip())
        if 1 <= size <= 20:
            await update_family_size(message.from_user.id, size)
            await state.clear()
            await message.answer(t(lang, "family_updated", size=size), parse_mode="Markdown")
        else:
            await message.answer(t(lang, "family_invalid"))
    except ValueError:
        await message.answer(t(lang, "family_not_number"))


# Yordam
@dp.message(F.text.in_({t("uz", "btn_help"), t("ru", "btn_help")}))
async def help_cmd(message: Message):
    lang = await get_lang(message.from_user.id)
    await message.answer(t(lang, "help_text"), parse_mode="Markdown")


# Callbacks
@dp.callback_query(F.data == "new_suggestion")
async def new_suggestion(callback: CallbackQuery, state: FSMContext):
    lang = await get_lang(callback.from_user.id)
    await callback.answer()
    await state.set_state(UserState.waiting_for_preference)
    await callback.message.answer(t(lang, "ask_new_suggest"))


@dp.callback_query(F.data == "save_list")
async def save_list_confirm(callback: CallbackQuery):
    lang = await get_lang(callback.from_user.id)
    await callback.answer(t(lang, "list_saved"), show_alert=True)


async def _send_long_message(message: Message, text: str):
    if len(text) > 4000:
        parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for part in parts:
            await message.answer(part)
    else:
        await message.answer(text)


async def main():
    await init_db()
    await start_webserver(port=8090, bot=bot)
    print("🤖 Bozorlik bot ishga tushdi!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
