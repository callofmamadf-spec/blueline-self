  GNU nano 8.7                                                             blue.py
import nest_asyncio
nest_asyncio.apply()
from telethon import TelegramClient, events, Button, functions, types, errors
import asyncio, pytz, os, time, random, re, json
from datetime import datetime

# --- [ تنظیمات اصلی ] ---
API_ID = 31241774
API_HASH = '6ff4a03952a578bd47c72a4c9b52f949'
BOT_TOKEN = '8375534470:AAHYjCjDx4GDPfc4hAvjIcy65S1jP6OosLs'
CHANNEL_ID = "selfBlueLine" # آیدی کانال برای اد اجباری

ADMINS = [8213018015]
ADMIN_ID = 8213018015

bot = TelegramClient('BlueLine_Final', API_ID, API_HASH)

# --- [ دیتابیس ] ---
DB_FILE = "database.json"
FOSH_FOLDER = "fosh_data"
if not os.path.exists(FOSH_FOLDER): os.makedirs(FOSH_FOLDER)
if not os.path.exists('sessions'): os.makedirs('sessions')

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: pass
    return {"diamonds": {str(ADMIN_ID): 999999999}, "gift_codes": {}, "banned_users": []}

def save_db():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

db = load_db()

# --- [ توابع کمکی ] ---
async def is_subscribed(user_id):
    if user_id in ADMINS: return True
    try:
        await bot(functions.channels.GetParticipantRequest(channel=CHANNEL_ID, participant=user_id))
        return True
    except errors.UserNotParticipantError: return False
    except: return True

def get_fosh_list():
    path = f"{FOSH_FOLDER}/list.txt"
    if not os.path.exists(path): return []
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def add_to_fosh(text):
    path = f"{FOSH_FOLDER}/list.txt"
    if len(get_fosh_list()) >= 5000: return False
    with open(path, "a", encoding="utf-8") as f:
        f.write(text + "\n")
    return True

active_clients = {}
user_steps = {}
enemies = {}
tabchi_tasks = {}
self_settings = {}

async def run_mega_self(client, uid):
    iran_tz = pytz.timezone('Asia/Tehran')
    uid_str = str(uid)
    if uid not in enemies: enemies[uid] = []
    if uid not in self_settings:
        me = await client.get_me()
        self_settings[uid] = {'pmlock': False, 'clock': False, 'base_name': me.first_name or "Self"}

    async def clock_worker():
        while uid in active_clients:
            if self_settings[uid]['clock']:
                try:
                    current_time = datetime.now(iran_tz).strftime("%H:%M")
                    new_name = f"{self_settings[uid]['base_name']} | {current_time}"
                    await client(functions.account.UpdateProfileRequest(first_name=new_name))
                except: pass
            await asyncio.sleep(60)

    @client.on(events.NewMessage(incoming=True))
    async def auto_handler(event):
        if event.is_private and self_settings[uid]['pmlock'] and not event.out:
            try: await event.delete()
            except: pass
        if event.sender_id in enemies[uid]:
            f_list = get_fosh_list()
            if f_list: await event.reply(random.choice(f_list))

    client.loop.create_task(clock_worker())

    async def diamond_deductor():
        while uid in active_clients:
            await asyncio.sleep(3600)
            if uid not in ADMINS:
                current_dm = db["diamonds"].get(uid_str, 0)
                if current_dm > 0:
                    db["diamonds"][uid_str] -= 1
                    save_db()
                else:
                    await client.disconnect()
                    active_clients.pop(uid, None)
                    break
    client.loop.create_task(diamond_deductor())
    @client.on(events.NewMessage(outgoing=True, pattern=r'\.(.*)'))
    async def self_cmds(event):
        args = event.pattern_match.group(1).split()
        if not args: return
        cmd = args[0].lower()

        # --- [ پنل راهنما - دقیقاً مطابق سورس اصلی شما ] ---
        if cmd == 'panel':
            help_text = (
                "🛡 پنل مدیریت سلف‌بات BlueLine\n"
                "──────────────────────\n"
                "🚀 تبچی و تبلیغات:\n"
                "  .tab [زمان] | فعالسازی روی بنر (ریپلای)\n"
                "  .untab | خاموش کردن تبچی در این چت\n\n"
                "⏰ تنظیمات پروفایل:\n"
                "  .time on | روشن کردن ساعت در نام\n"
                "  .time off | خاموش کردن ساعت\n\n"
                "🔐 حریم خصوصی و امنیت:\n"
                "  .pmlock on | قفل خودکار پی‌وی\n"
                "  .pmlock off | باز کردن پی‌وی\n"
                "  .save | ذخیره عکس زمان‌دار (ریپلای)\n\n"
                "👊 بخش دشمن و فحش:\n"
                "  .setenemy | ست کردن دشمن (ریپلای)\n"
                "  .unenemy | حذف دشمن (ریپلای)\n"
                "  .addfosh [متن] | افزودن به لیست فحش\n"
                "  .foshlist | آمار لیست فحش (تا 5000)\n\n"
                "🛠 ابزارها:\n"
                "  .ping | تست سرعت و وضعیت\n"
                "  .spam [تعداد] [متن] | ارسال رگباری\n"
                "──────────────────────"
            )
            await event.edit(help_text)

        elif cmd == 'tab' and event.is_reply:
            if len(args) < 2: return await event.edit("❌ زمان را وارد کنید. مثال: .tab 20")
            try:
                sec = int(args[1])
                rep_msg = await event.get_reply_message()
                cid = event.chat_id
                if cid in tabchi_tasks: tabchi_tasks[cid].cancel()
                async def t_run():
                    while True:
                        await client.send_message(cid, rep_msg)
                        await asyncio.sleep(sec)
                tabchi_tasks[cid] = client.loop.create_task(t_run())
                await event.edit(f"🚀 تبچی فعال شد! هر {sec} ثانیه.")
            except: await event.edit("❌ خطا در عدد زمان.")

        elif cmd == 'untab':
            if event.chat_id in tabchi_tasks:
                tabchi_tasks[event.chat_id].cancel()
                del tabchi_tasks[event.chat_id]
                await event.edit("✅ تبچی خاموش شد.")
            else: await event.edit("❌ تبچی اینجا فعال نیست.")

        elif cmd == 'save' and event.is_reply:
            rep = await event.get_reply_message()
            if rep.photo and hasattr(rep.media, 'ttl_seconds'):
                await event.edit("⏳ Downloading...")
                path = await client.download_media(rep)
                await client.send_file("me", path, caption="📸 Photo Saved By Self")
                if os.path.exists(path): os.remove(path)
                await event.edit("✅ در Saved Messages ذخیره شد.")
else: await event.edit("❌ این پیام یک عکس زمان‌دار نیست.")

        elif cmd == 'setenemy' and event.is_reply:
            rep = await event.get_reply_message()
            if rep.sender_id not in enemies[uid]:
                enemies[uid].append(rep.sender_id)
                await event.edit("👤 دشمن تنظیم شد.")

        elif cmd == 'unenemy' and event.is_reply:
            rep = await event.get_reply_message()
            if rep.sender_id in enemies[uid]:
                enemies[uid].remove(rep.sender_id)
                await event.edit("✅ دشمن حذف شد.")

        elif cmd == 'addfosh' and len(args) > 1:
            txt = " ".join(args[1:])
            if add_to_fosh(txt): await event.edit(f"✅ اضافه شد. (کل: {len(get_fosh_list())})")
            else: await event.edit("❌ ظرفیت 5000 فحش تکمیل است.")

        elif cmd == 'foshlist':
            await event.edit(f"📜 تعداد فحش‌های ذخیره شده: {len(get_fosh_list())}")

        elif cmd == 'ping':
            s = time.time()
            await event.edit("Checking...")
            ms = round((time.time() - s) * 1000, 2)
            await event.edit(f"🚀 Ping: {ms}ms")

        elif cmd == 'time' and len(args) > 1:
            val = args[1].lower()
            self_settings[uid]['clock'] = (val == 'on')
            if val == 'off': await client(functions.account.UpdateProfileRequest(first_name=self_settings[uid]['base_name']))
            await event.edit(f"⏰ ساعت پروفایل: {val}")

        elif cmd == 'pmlock' and len(args) > 1:
            val = args[1].lower()
            self_settings[uid]['pmlock'] = (val == 'on')
            await event.edit(f"🔒 قفل پی‌وی: {val}")

        elif cmd == 'spam' and len(args) >= 3:
            try:
                c, t = int(args[1]), " ".join(args[2:])
                await event.delete()
                for _ in range(c): await client.send_message(event.chat_id, t); await asyncio.sleep(0.3)
            except: pass

# --- [ بخش ربات مدیریت ] ---
@bot.on(events.NewMessage(pattern='/start'))
async def bot_start(event):
    uid = event.sender_id
    if uid in db.get("banned_users", []): return await event.reply("❌ دسترسی شما مسدود است.")

    # اد اجباری
    if not await is_subscribed(uid):
        buttons = [[Button.url("📢 عضویت در کانال", f"https://t.me/{CHANNEL_ID}")], [Button.inline("✅ جوین شدم", data="verify_sub")]]
        return await event.reply("⚠️ ابتدا عضو کانال شوید:", buttons=buttons)

    dm = "♾" if uid in ADMINS else db["diamonds"].get(str(uid), 0)
    buttons = [
        [Button.inline("🚀 ران کردن سلف", data="run_direct")],
        [Button.inline("💸 انتقال الماس", data="transfer"), Button.inline("🎁 کد هدیه", data="use_gift")],
        [Button.url("🛒 خرید الماس", "https://t.me/RICHMAHDIYI")]
    ]
    if uid in ADMINS:
        buttons.append([Button.inline("🚫 بن / آن‌بن کاربر", data="ban_user")])
        buttons.append([Button.inline("⚙️ مدیریت الماس", data="admin_panel")])
    await event.reply(f"🛡 پنل مدیریت سلف‌بات BlueLine\n💎 موجودی: {dm} الماس", buttons=buttons)

@bot.on(events.CallbackQuery())
async def cb_handler(event):
    uid, data = event.sender_id, event.data.decode()
    if data == "verify_sub":
        if await is_subscribed(uid): await event.delete(); await bot_start(event)
        else: await event.answer("❌ هنوز عضو نشدید!", alert=True)
        return
    if uid in db.get("banned_users", []): return
    if data == "run_direct":
        if uid not in ADMINS and db["diamonds"].get(str(uid), 0) < 60: return await event.answer("❌ الماس کافی ندارید.", alert=True)
        user_steps[uid] = {'step': 'phone'}
        await event.edit("📱 شماره خود را وارد کنید:")
    elif data == "transfer": user_steps[uid] = {'step': 'trans_id'}; await event.edit("👤 آیدی مقصد:")
    elif data == "use_gift": user_steps[uid] = {'step': 'enter_gift'}; await event.edit("📩 کد هدیه:")
    elif data == "admin_panel" and uid in ADMINS: user_steps[uid] = {'step': 'gift_val'}; await event.edit("💎 مقدار الماس کد:")
    elif data == "ban_user" and uid in ADMINS: user_steps[uid] = {'step': 'ban_step'}; await event.edit("🚫 آیدی جهت بن/آن‌بن:")

@bot.on(events.NewMessage())
async def manager_steps(event):
    uid = event.sender_id
    if uid not in user_steps or event.text.startswith('/'): return
    step = user_steps[uid]['step']
    if step == 'phone':
        phone = event.text.strip()
        c = TelegramClient(f'sessions/u_{uid}', API_ID, API_HASH)
        await c.connect()
        try:
            res = await c.send_code_request(phone)
            user_steps[uid].update({'c': c, 'phone': phone, 'hash': res.phone_code_hash, 'step': 'code'})
            await event.reply("📩 کد را بفرستید:")
        except Exception as e: await event.reply(f"❌ خطا: {e}"); user_steps.pop(uid)
    elif step == 'code':
        data = user_steps[uid]
        try:
            await data['c'].sign_in(data['phone'], event.text.strip(), phone_code_hash=data['hash'])
            active_clients[uid] = data['c']
            await event.reply("✅ سلف فعال شد!")
            bot.loop.create_task(run_mega_self(data['c'], uid))
            user_steps.pop(uid)
        except Exception as e: await event.reply(f"❌ خطا: {e}")
    elif step == 'ban_step' and uid in ADMINS:
        try:
            u = await bot.get_entity(event.text.replace("@","").strip())
            if u.id in db["banned_users"]: db["banned_users"].remove(u.id); msg = "آن‌بن شد."
            else: db["banned_users"].append(u.id); msg = "بن شد."
            save_db(); await event.reply(msg)
        except: await event.reply("خطا.")
        user_steps.pop(uid)
    elif step == 'trans_id': user_steps[uid].update({'target': event.text.strip(), 'step': 'trans_amount'}); await event.reply("مقدار:")
    elif step == 'trans_amount':
        try:
            amt, target = int(event.text), str(user_steps[uid]['target'])
            if uid in ADMINS or db["diamonds"].get(str(uid), 0) >= amt:
                if uid not in ADMINS: db["diamonds"][str(uid)] -= amt
                db["diamonds"][target] = db["diamonds"].get(target, 0) + amt
                save_db(); await event.reply("✅ انجام شد.")
        except: pass
        user_steps.pop(uid)
    elif step == 'gift_val' and uid in ADMINS:
        try:
            v, code = int(event.text), f"GIFT-{random.randint(100, 999)}"
            db["gift_codes"][code] = v; save_db(); await event.reply(f"🎁 کد: {code}")
        except: pass
        user_steps.pop(uid)
    elif step == 'enter_gift':
        code = event.text.strip()
        if code in db["gift_codes"]:
            v = db["gift_codes"].pop(code)
            db["diamonds"][str(uid)] = db["diamonds"].get(str(uid), 0) + v
            save_db(); await event.reply(f"✅ {v} الماس اضافه شد.")
        user_steps.pop(uid)

async def start_all():
    await bot.start(bot_token=BOT_TOKEN)
    await bot.run_until_disconnected()

if __name__ == '__main__':
    bot.loop.run_until_complete(start_all())
