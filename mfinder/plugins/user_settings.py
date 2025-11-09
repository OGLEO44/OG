from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from mfinder.db.settings_sql import get_search_settings, change_search_settings
from mfinder.utils.constants import SET_MSG


@Client.on_message(filters.command("settings"))
async def user_settings(bot, message):
    user_id = message.from_user.id
    set_kb = await find_search_settings(user_id)
    await bot.send_message(
        chat_id=message.from_user.id,  # safer than message.chat.id
        text=SET_MSG,
        reply_markup=set_kb,
    )


@Client.on_callback_query(filters.regex(r"^prec (.+)$"))
async def set_precise_mode(bot, query):
    user_id = query.from_user.id
    prsc_mode = query.data.split()[1]

    if prsc_mode == "on":
        await change_search_settings(user_id, precise_mode=True)
    elif prsc_mode == "off":
        await change_search_settings(user_id, precise_mode=False)
    elif prsc_mode == "md":
        await query.answer("Toggle Precise Search ON/OFF", show_alert=False)
        return

    set_kb = await find_search_settings(user_id)
    await query.message.edit(text=SET_MSG, reply_markup=set_kb)


@Client.on_callback_query(filters.regex(r"^res (.+)$"))
async def set_list_mode(bot, query):
    user_id = query.from_user.id
    result_mode = query.data.split()[1]

    if result_mode == "btnn":
        await change_search_settings(user_id, button_mode=True, link_mode=False, list_mode=False)
    elif result_mode == "link":
        await change_search_settings(user_id, button_mode=False, link_mode=True, list_mode=False)
    elif result_mode == "list":
        await change_search_settings(user_id, button_mode=False, link_mode=False, list_mode=True)
    elif result_mode == "mode":
        await query.answer("Toggle Button/Link/List Mode", show_alert=False)
        return

    set_kb = await find_search_settings(user_id)
    await query.message.edit(text=SET_MSG, reply_markup=set_kb)


async def find_search_settings(user_id):
    search_settings = await get_search_settings(user_id)
    if not search_settings:
        search_settings = {}
        await change_search_settings(user_id)

    kb = [InlineKeyboardButton("[Precise Mode]:", callback_data="prec md")]
    on_kb = InlineKeyboardButton("✅ Enable", callback_data="prec on")
    off_kb = InlineKeyboardButton("❌ Disable", callback_data="prec off")

    if search_settings.get("precise_mode", False):
        kb.append(off_kb)
    else:
        kb.append(on_kb)

    bkb = [InlineKeyboardButton("[Result Mode]:", callback_data="res mode")]
    btn_kb = InlineKeyboardButton("🔳 Button", callback_data="res btnn")
    link_kb = InlineKeyboardButton("🔗 HyperLink", callback_data="res link")
    list_kb = InlineKeyboardButton("📃 List", callback_data="res list")

    button_mode = search_settings.get("button_mode", False)
    link_mode = search_settings.get("link_mode", True)
    list_mode = search_settings.get("list_mode", False)

    if button_mode:
        bkb.append(link_kb)
    elif link_mode:
        bkb.append(list_kb)
    elif list_mode:
        bkb.append(btn_kb)
    else:
        bkb.append(list_kb)

    return InlineKeyboardMarkup([kb, bkb])
