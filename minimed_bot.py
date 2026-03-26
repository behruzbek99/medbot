"""
MiniMed - Doctor Rayhona Telegram Bot
Production Version for PythonAnywhere
All-in-one simplified version with unique file names
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from loguru import logger

from minimed_settings import settings
from minimed_ai_service import init_ai_service, get_ai_service
from minimed_diseases_db import get_initial_diseases

# Configure logging
logger.remove()
logger.add("logs/bot.log", rotation="1 day", retention="7 days", level=settings.log_level)
logger.add(sys.stdout, level=settings.log_level, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}")

# Storage
users_db = {}
admins_db = set(settings.admin_usernames_set)
diagnosis_history = []
chat_messages = []
conversation_history = {}
selected_symptoms = {}

SYMPTOMS_LIST = [
    ("1️⃣", "🤒", "Harorat", "symptom_fever"),
    ("2️⃣", "🤧", "Yo'tal", "symptom_cough"),
    ("3️⃣", "🤮", "Qusish", "symptom_vomiting"),
    ("4️⃣", "💩", "Diareya", "symptom_diarrhea"),
    ("5️⃣", "👃", "Burun oqishi", "symptom_runny_nose"),
    ("6️⃣", "😴", "Holsizlik", "symptom_fatigue"),
    ("7️⃣", "🔴", "Teri toshmasi", "symptom_rash"),
    ("8️⃣", "😖", "Qorin og'rig'i", "symptom_abdominal_pain"),
]


class DiagnosisState(StatesGroup):
    waiting_for_age = State()
    waiting_for_symptoms = State()
    waiting_for_duration = State()
    waiting_for_severity = State()


class ChatState(StatesGroup):
    chatting = State()


class SearchState(StatesGroup):
    waiting_for_query = State()


# ============== KEYBOARDS ==============

def get_main_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🩺 Tekshirish"), KeyboardButton(text="💬 Doktor Rayhona")],
        [KeyboardButton(text="📚 Ma'lumotlar"), KeyboardButton(text="🚨 Shoshilinch")],
    ], resize_keyboard=True)


def get_age_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👶 0-1 yosh", callback_data="age_0_1"), InlineKeyboardButton(text="🧒 1-3 yosh", callback_data="age_1_3")],
        [InlineKeyboardButton(text="👦 3-7 yosh", callback_data="age_3_7"), InlineKeyboardButton(text="👨 7+ yosh", callback_data="age_7_plus")],
    ])


def get_symptom_keyboard(selected=None):
    if selected is None:
        selected = []
    keyboard = []
    for num, emoji, name, callback in SYMPTOMS_LIST:
        is_selected = callback in selected
        keyboard.append([InlineKeyboardButton(text=f"✅ {num} {emoji} {name}" if is_selected else f"{num} {emoji} {name}", callback_data=callback)])
    keyboard.append([InlineKeyboardButton(text="✅ TANLASHNI TUGATISH", callback_data="symptoms_done")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_duration_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1️⃣ 1 kundan kam", callback_data="duration_less_1_day"), InlineKeyboardButton(text="2️⃣ 1-3 kun", callback_data="duration_1_3_days")],
        [InlineKeyboardButton(text="3️⃣ 3-7 kun", callback_data="duration_3_7_days"), InlineKeyboardButton(text="4️⃣ 1 haftadan ko'p", callback_data="duration_more_week")],
    ])


def get_severity_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 1️⃣ Yengil", callback_data="severity_mild"), InlineKeyboardButton(text="🟡 2️⃣ O'rtacha", callback_data="severity_moderate")],
        [InlineKeyboardButton(text="🔴 3️⃣ Og'ir", callback_data="severity_severe")],
    ])


def get_main_menu_inline():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu")]])


def get_diagnosis_result_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Doktor bilan suhbat", callback_data="chat_start")],
        [InlineKeyboardButton(text="🩺 Yangi tekshirish", callback_data="diagnosis_start")],
        [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu")],
    ])


def get_chat_actions_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔄 Yangi savol", callback_data="chat_new")], [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu")]])


def get_emergency_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📞 103 ga qo'ng'iroq", url="tel:103")], [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu")]])


def get_disease_search_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔍 Qidirish", callback_data="disease_search")], [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu")]])


def get_subscribe_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Kanalga obuna bo'lish", url=link)] for link in settings.channel_invite_links] + [[InlineKeyboardButton(text="🔄 Obunani tekshirish", callback_data="check_subscription")]])


def get_symptoms_help_text():
    text = "📋 <b>ALOMATLARNI TANLASH:</b>\n\nRaqam yozing yoki tugmani bosing:\n\n"
    for num, emoji, name, _ in SYMPTOMS_LIST:
        text += f"{num} {emoji} <b>{name}</b>\n"
    text += "\n✅ <b>TANLASHNI TUGATISH</b> tugmasini bosing yoki <b>0</b> yozing"
    return text


# ============== SUBSCRIPTION ==============

async def check_subscription(message: types.Message) -> bool:
    if message.from_user.username in admins_db:
        return True
    
    not_subscribed = []
    for link in settings.channel_invite_links:
        try:
            member = await message.bot.get_chat_member(chat_id=link, user_id=message.from_user.id)
            if member.status not in ["member", "administrator", "creator"]:
                not_subscribed.append(link)
        except:
            not_subscribed.append(link)
    
    if not_subscribed:
        await message.answer("⚠️ <b>BOTDAN FOYDALANISH UCHUN OBUNA BO'LING!</b>\n\nQuyidagi kanallarga obuna bo'ling:", reply_markup=get_subscribe_keyboard())
        return False
    return True


# ============== HANDLERS ==============

async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    name = message.from_user.first_name or message.from_user.username or "Foydalanuvchi"
    await message.answer(f"👋 Assalomu alaykum, {name}!\n\n🏥 <b>MiniMed - Doktor Rayhona</b>\n\n📋 Imkoniyatlar:\n🩺 Tekshirish\n💬 Doktor bilan suhbat\n📚 Kasalliklar (1000+)\n🚨 Shoshilinch\n\nTugmani tanlang 👇", reply_markup=get_main_keyboard())


async def handle_diagnosis(message: types.Message, state: FSMContext):
    if not await check_subscription(message):
        return
    await state.clear()
    selected_symptoms[message.from_user.id] = []
    await message.answer("🩺 <b>Yoshni tanlang:</b>", reply_markup=get_age_keyboard())
    await state.set_state(DiagnosisState.waiting_for_age)


async def handle_chat(message: types.Message, state: FSMContext):
    if not await check_subscription(message):
        return
    await state.clear()
    conversation_history[message.from_user.id] = []
    await message.answer("💬 <b>Savolingizni yozing:</b>", reply_markup=get_main_menu_inline())
    await state.set_state(ChatState.chatting)


async def handle_emergency(message: types.Message):
    await message.answer("🚨 <b>SHOSHILINCH!</b>\n\n⚠️ 103 ga qo'ng'iroq qiling agar:\n• Nafas qiyin\n• Hushdan ketish\n• Qattiq qon ketish\n• Zaharlanish\n• Tutilishlar\n\n📞 103 - Tez yordam", reply_markup=get_emergency_keyboard())


async def handle_info(message: types.Message):
    if not await check_subscription(message):
        return
    await message.answer("📚 <b>Kasalliklar (1000+)</b>\n\n🔍 Qidirish uchun kasallik nomini yozing:", reply_markup=get_disease_search_keyboard())


async def process_age(callback: types.CallbackQuery, state: FSMContext):
    age_map = {"age_0_1": "0-1 yosh", "age_1_3": "1-3 yosh", "age_3_7": "3-7 yosh", "age_7_plus": "7+ yosh"}
    age = age_map.get(callback.data, "Noma'lum")
    await state.update_data(child_age=age)
    selected_symptoms[callback.from_user.id] = []
    await callback.message.edit_text(f"✅ Yosh: {age}\n\n{get_symptoms_help_text()}", reply_markup=get_symptom_keyboard([]))
    await state.set_state(DiagnosisState.waiting_for_symptoms)
    await callback.answer()


async def process_symptom_btn(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    if callback.data == "symptoms_done":
        symptoms = selected_symptoms.get(user_id, [])
        if not symptoms:
            await callback.answer("⚠️ Kamida bitta alomat tanlang!", show_alert=True)
            return
        names = {s[3]: s[2] for s in SYMPTOMS_LIST}
        text = ", ".join([names.get(s, s) for s in symptoms])
        await state.update_data(symptoms=text)
        await callback.message.edit_text(f"✅ Alomatlar: {text}\n\n⏱ Davomiyligi?", reply_markup=get_duration_keyboard())
        await state.set_state(DiagnosisState.waiting_for_duration)
        await callback.answer()
        return
    
    current = selected_symptoms.get(user_id, [])
    if callback.data in current:
        current.remove(callback.data)
    else:
        current.append(callback.data)
    selected_symptoms[user_id] = current
    await callback.message.edit_reply_markup(reply_markup=get_symptom_keyboard(current))
    await callback.answer()


async def process_symptom_text(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    txt = msg.text.strip().lower()
    
    if txt in ["0", "tamom", "tayor"]:
        symptoms = selected_symptoms.get(user_id, [])
        if not symptoms:
            await msg.answer("⚠️ Kamida bitta alomat tanlang!")
            return
        names = {s[3]: s[2] for s in SYMPTOMS_LIST}
        text = ", ".join([names.get(s, s) for s in symptoms])
        await state.update_data(symptoms=text)
        await msg.answer(f"✅ Alomatlar: {text}\n\n⏱ Davomiyligi?", reply_markup=get_duration_keyboard())
        await state.set_state(DiagnosisState.waiting_for_duration)
        return
    
    if txt.isdigit() and 1 <= int(txt) <= 8:
        cb = SYMPTOMS_LIST[int(txt) - 1][3]
        current = selected_symptoms.get(user_id, [])
        if cb in current:
            current.remove(cb)
        else:
            current.append(cb)
        selected_symptoms[user_id] = current
        name = SYMPTOMS_LIST[int(txt) - 1][2]
        await msg.answer(f"{'✅' if cb in current else '❌'} {name}", reply_markup=get_symptom_keyboard(current))


async def process_duration(callback: types.CallbackQuery, state: FSMContext):
    dur_map = {"duration_less_1_day": "1 kundan kam", "duration_1_3_days": "1-3 kun", "duration_3_7_days": "3-7 kun", "duration_more_week": "1 haftadan ko'p"}
    dur = dur_map.get(callback.data, "Noma'lum")
    await state.update_data(duration=dur)
    await callback.message.edit_text(f"✅ Davomiyligi: {dur}\n\n🔴 Og'irligi?", reply_markup=get_severity_keyboard())
    await state.set_state(DiagnosisState.waiting_for_severity)
    await callback.answer()


async def process_severity(callback: types.CallbackQuery, state: FSMContext):
    sev_map = {"severity_mild": "Yengil", "severity_moderate": "O'rtacha", "severity_severe": "Og'ir"}
    sev = sev_map.get(callback.data, "Noma'lum")
    await callback.message.edit_text("⏳ Tahlil qilinmoqda...")
    
    try:
        data = await state.get_data()
        ai = get_ai_service()
        result = await ai.get_diagnosis(child_age=data.get("child_age"), symptoms=data.get("symptoms"), duration=data.get("duration"), severity=sev)
        
        diagnosis_history.append({"user_id": str(callback.from_user.id), "symptoms": data.get("symptoms"), "diagnosis": result.get("diagnosis"), "timestamp": datetime.utcnow().isoformat()})
        
        emoji = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}
        text = f"🩺 <b>NATIJA</b>\n\n👶 Yosh: {data.get('child_age')}\n📋 Alomatlar: {data.get('symptoms')}\n⏱ Davomiyligi: {data.get('duration')}\n\n📊 Holat: {result.get('diagnosis')}\n{emoji.get(result.get('risk_level'), '🟡')} Xavf: {result.get('risk_level')}\n\n💡 Tavsiya: {result.get('recommendation')}\n\n⚠️ Bu faqat umumiy maslahat. Shifokorga murojaat qiling."
        
        await callback.message.edit_text(text, reply_markup=get_diagnosis_result_keyboard())
        selected_symptoms.pop(callback.from_user.id, None)
        await state.clear()
    except Exception as e:
        logger.error(f"Error: {e}")
        await callback.message.edit_text("❌ Xatolik. Qayta urinib ko'ring.", reply_markup=get_main_menu_inline())
        await state.clear()
    await callback.answer()


async def process_chat_msg(msg: types.Message, state: FSMContext):
    if not await check_subscription(msg):
        return
    user_id = msg.from_user.id
    hist = conversation_history.get(user_id, [])
    
    try:
        ai = get_ai_service()
        result = await ai.chat(message=msg.text, conversation_history=hist if hist else None)
        resp = result.get("response", "Kechirasiz.")
        hist.append({"role": "user", "content": msg.text})
        hist.append({"role": "assistant", "content": resp})
        conversation_history[user_id] = hist[-10:]
        chat_messages.append({"user_id": str(user_id), "message": msg.text, "response": resp, "timestamp": datetime.utcnow().isoformat()})
        await msg.answer(resp, reply_markup=get_chat_actions_keyboard())
    except Exception as e:
        logger.error(f"Chat error: {e}")
        await msg.answer("❌ Xatolik.", reply_markup=get_chat_actions_keyboard())


async def process_search_query(msg: types.Message, state: FSMContext):
    if not await check_subscription(msg):
        return
    query = msg.text.strip()
    if len(query) < 2:
        await msg.answer("⚠️ Kamida 2 belgi kiriting.")
        return
    
    diseases = get_initial_diseases()
    results = [d for d in diseases if query.lower() in d["name"].lower() or query.lower() in d["name_uz"].lower() or query.lower() in d["symptoms"].lower()][:10]
    
    if not results:
        await msg.answer(f"❌ \"{query}\" topilmadi.", reply_markup=get_disease_search_keyboard())
        await state.clear()
        return
    
    for d in results:
        await msg.answer(f"📋 <b>{d['name_uz']}</b>\n\n🔍 {d['symptoms'][:300]}\n\n📁 {d.get('category', '')}")
    
    await msg.answer(f"✅ {len(results)} ta natija.", reply_markup=get_disease_search_keyboard())
    await state.clear()


async def check_sub_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    ok = True
    for link in settings.channel_invite_links:
        try:
            member = await callback.bot.get_chat_member(chat_id=link, user_id=user_id)
            if member.status not in ["member", "administrator", "creator"]:
                ok = False
                break
        except:
            ok = False
            break
    
    if ok:
        await callback.answer("✅ Tasdiqlandi!", show_alert=True)
        await callback.message.delete()
        await callback.message.answer("✅ Obuna tasdiqlandi!", reply_markup=get_main_keyboard())
    else:
        await callback.answer("❌ Hali obuna bo'lmadingiz!", show_alert=True)


async def handle_callbacks(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data
    
    if data == "main_menu":
        await callback.message.edit_text("🏠 Bosh menyu", reply_markup=get_main_keyboard())
    elif data == "diagnosis_start":
        await handle_diagnosis(callback.message, state)
    elif data == "chat_start":
        await handle_chat(callback.message, state)
    elif data == "chat_new":
        conversation_history[callback.from_user.id] = []
        await state.clear()
        await callback.message.edit_text("✍️ Savolingizni yozing:", reply_markup=get_main_menu_inline())
        await state.set_state(ChatState.chatting)
    elif data == "disease_search":
        await callback.message.edit_text("🔍 Kasallik nomini yozing:", reply_markup=get_main_menu_inline())
        await state.set_state(SearchState.waiting_for_query)
    elif data == "check_subscription":
        await check_sub_callback(callback)
    elif data.startswith("age_"):
        await process_age(callback, state)
    elif data.startswith("symptom_"):
        await process_symptom_btn(callback, state)
    elif data.startswith("duration_"):
        await process_duration(callback, state)
    elif data.startswith("severity_"):
        await process_severity(callback, state)
    
    await callback.answer()


# ============== MAIN ==============

async def main():
    logger.info("🚀 MiniMed Bot ishga tushmoqda...")
    
    init_ai_service(api_key=settings.groq_api_key, model=settings.groq_model, max_tokens=settings.groq_max_tokens, temperature=settings.groq_temperature)
    logger.info("✅ AI service ishga tushdi")
    
    bot = Bot(token=settings.telegram_bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    logger.info(f"👤 Bot: {(await bot.get_me()).username}")
    
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(handle_diagnosis, lambda m: m.text == "🩺 Tekshirish")
    dp.message.register(handle_chat, lambda m: m.text == "💬 Doktor Rayhona")
    dp.message.register(handle_emergency, lambda m: m.text == "🚨 Shoshilinch")
    dp.message.register(handle_info, lambda m: m.text == "📚 Ma'lumotlar")
    dp.message.register(process_symptom_text, DiagnosisState.waiting_for_symptoms)
    dp.message.register(process_chat_msg, ChatState.chatting)
    dp.message.register(process_search_query, SearchState.waiting_for_query)
    dp.callback_query.register(handle_callbacks)
    
    logger.info("✅ Handlerlar ro'yxatdan o'tdi")
    
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("✨ Bot ishlayapti!")
    
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("👋 To'xtatildi")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    (project_root / "logs").mkdir(exist_ok=True)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Goodbye!")
