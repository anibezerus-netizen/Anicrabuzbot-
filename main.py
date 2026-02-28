import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ====== TOKEN VA VIP ID ======
BOT_TOKEN = "8612161126:AAGvLSt9PS6LKBGS2-XaNn-JadLd3YezK1Q"  # Yangi token
VIP_ID = 7991544389  # Bot egasi

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ====== MA'LUMOTLAR ======
users = set()
admins = set()
special_admins = set()
media_files = {}  # {'nom': file_id}
apk_files = {}    # {'nom': (file_id, tavsif)}

settings = {
    "bot_name": "Anicrabuzbot",
    "start_text": "Salom! Botimizga xush kelibsiz!",
    "maintenance": False
}

# ====== Rollar ======
def get_role(user_id):
    if user_id == VIP_ID:
        return "vip"
    elif user_id in special_admins:
        return "special"
    elif user_id in admins:
        return "admin"
    else:
        return "user"

# ====== START ======
@dp.message(CommandStart())
async def start(message: types.Message):
    user_id = message.from_user.id
    users.add(user_id)

    if settings["maintenance"] and user_id != VIP_ID:
        await message.answer("🛠 Bot texnik rejimda.")
        return

    kb = InlineKeyboardBuilder()
    kb.button(text="📱 APK", callback_data="apk_menu")
    kb.button(text="📂 Media", callback_data="media_menu")
    kb.button(text="📊 Statistika", callback_data="stats")
    
    await message.answer(settings["start_text"], reply_markup=kb.as_markup())

# ====== STATISTIKA ======
@dp.callback_query(lambda c: c.data=="stats")
async def stats(call: types.CallbackQuery):
    role = get_role(call.from_user.id)
    if role in ["admin","special","vip"]:
        await call.message.answer(f"👥 Foydalanuvchilar soni: {len(users)}")
    await call.answer()

# ====== APK MENU ======
@dp.callback_query(lambda c: c.data=="apk_menu")
async def apk_menu(call: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    for name in apk_files:
        kb.button(text=name, callback_data=f"apk_{name}")
    await call.message.answer("📱 APK ro'yxati:", reply_markup=kb.as_markup())
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("apk_"))
async def send_apk(call: types.CallbackQuery):
    name = call.data.replace("apk_","")
    if name in apk_files:
        file_id, desc = apk_files[name]
        await call.message.answer_document(file_id, caption=desc)
    await call.answer()

# ====== MEDIA MENU ======
@dp.callback_query(lambda c: c.data=="media_menu")
async def media_menu(call: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    for name in media_files:
        kb.button(text=name, callback_data=f"media_{name}")
    await call.message.answer("📂 Media ro'yxati:", reply_markup=kb.as_markup())
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("media_"))
async def send_media(call: types.CallbackQuery):
    name = call.data.replace("media_","")
    if name in media_files:
        file_id = media_files[name]
        await call.message.answer_document(file_id)
    await call.answer()

# ====== SOZLAMALAR ======
@dp.callback_query(lambda c: c.data=="settings")
async def settings_menu(call: types.CallbackQuery):
    role = get_role(call.from_user.id)
    if role not in ["special","vip"]:
        return
    kb = InlineKeyboardBuilder()
    kb.button(text="🛠 Texnik rejim", callback_data="toggle_maintenance")
    await call.message.answer("⚙️ Sozlamalar:", reply_markup=kb.as_markup())
    await call.answer()

@dp.callback_query(lambda c: c.data=="toggle_maintenance")
async def toggle_maintenance(call: types.CallbackQuery):
    if call.from_user.id != VIP_ID:
        return
    settings["maintenance"] = not settings["maintenance"]
    status = "yoqildi" if settings["maintenance"] else "o‘chirildi"
    await call.message.answer(f"🛠 Texnik rejim {status}.")
    await call.answer()

# ====== FILE QO‘SHISH (Admin) ======
@dp.message(lambda m: m.document is not None)
async def add_file(message: types.Message):
    role = get_role(message.from_user.id)
    if role not in ["admin","special","vip"]:
        return

    file_name = message.document.file_name
    file_id = message.document.file_id

    if file_name.endswith(".apk"):
        apk_files[file_name] = (file_id,"📱 APK tavsifi")
        await message.answer("APK qo‘shildi.")
    else:
        media_files[file_name] = file_id
        await message.answer("Media qo‘shildi.")

# ====== RUN ======
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
