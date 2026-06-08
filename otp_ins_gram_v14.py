import telebot
from telebot import types
import cloudscraper
import sqlite3
import time
import threading

# ===================================
# CONFIG
# ===================================

BOT_TOKEN = "8336769257:AAEhw8IQ-PTwDAB3LVqp-YsQYD32DMcu9C0"
API_KEY = "0sJsauUD3Bsr6OnP5ussHhfEpx10nJNA"
ADMIN_USERNAME = "shawon88556677"
ADMIN_CHAT_ID = 6727558565

# ===================================
# SMSBOWER SETTINGS
# ===================================

SERVICE_CODE = "ig"
COUNTRY_ID = "6"
PROVIDER_ID = "3237"
FIX_PRICE = "0.008"


USER_PRICE = 2

MANUAL_PRICE = 0.8


# ===================================
# SMSPOOL CONFIG
# ===================================

SMSPOOL_API_KEY = "1SHdmHGsKkcsU5OGIdmQEdpKjnJr3rOV"

SMSPOOL_COUNTRIES = {

    "1": {
        "name": "Indonesia",
        "country": "9",
        "service": "457",
        "max_price": "0.05",
        "user_price": 6.65
    },

    "2": {
        "name": "United Kingdom",
        "country": "2",
        "service": "457",
        "max_price": "0.05",
        "user_price": 6.65
    }
}

# ===================================
# COUNTRY CONFIG
# ===================================

COUNTRIES = {
    "1": {
        "name": "Indonesia",
        "country_id": "6",
        "provider_id": "3237",
        "fix_price": "0.008",
        "user_price": 1.8
    },

    "2": {
        "name": "Indonesia Best",
        "country_id": "6",
        "provider_id": "2295",
        "fix_price": "0.036",
        "user_price": 5,
        "service_code": "ig"
    },

    "3": {
        "name": "USA",
        "country_id": "12",
        "provider_id": "3209",
        "fix_price": "0.034",
        "user_price": 4.85,
        "service_code": "ig"
    },
    
    "4": {
        "name": "Indonesia",
        "country_id": "6",
        "provider_id": "3109",
        "fix_price": "0.033",
        "user_price": 4.75,
        "service_code": "ig"
    },
    
    "5": {
        "name": "Colombia",
        "country_id": "33",
        "provider_id": "3243",
        "fix_price": "0.012",
        "user_price": 2,
        "service_code": "ig"
    },
    
    "6": {
        "name": "United kingdom",
        "country_id": "16",
        "provider_id": "2738",
        "fix_price": "0.045",
        "user_price": 6.2,
        "service_code": "ig"
    },

    "7": {
        "name": "Yemen",
        "country_id": "73",
        "provider_id": "2377",
        "fix_price": "0.011",
        "user_price": 2,
        "service_code": "ig"
    },

    "8": {
        "name": "BRAZIL",
        "country_id": "73",
        "provider_id": "3160",
        "fix_price": "0.043",
        "user_price": 6,
        "service_code": "ig"
    },

    "9": {
        "name": "United kingdom",
        "country_id": "16",
        "provider_id": "3237",
        "fix_price": "0.018",
        "user_price": 3,
        "service_code": "ig"
    },

    "10": {
        "name": "Colombia 2",
        "country_id": "33",
        "provider_id": "3237",
        "fix_price": "0.01",
        "user_price": 2,
        "service_code": "ig"
    }
}


DEPOSIT_TEXT = """
💳 Deposit System

Bkash/Nagad/Rocket Send Money:
`01701029126`

Comment:
shawon-pay

Minimum:
50 TK

After payment send proof to admin with user id . @insotpgrambotowner
"""

# Updated API URL
BASE_URL = "https://smsbower.app/stubs/handler_api.php"

# ===================================
# BOT START
# ===================================

bot = telebot.TeleBot(BOT_TOKEN)

# Cloudflare bypass scraper
scraper = cloudscraper.create_scraper()

# ===================================
# DATABASE
# ===================================

conn = sqlite3.connect(
    "database.db",
    timeout=30,
    check_same_thread=False
)

conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA synchronous=NORMAL")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    balance REAL DEFAULT 0,
    referred_by INTEGER DEFAULT NULL,
    join_time INTEGER DEFAULT 0
)
""")

try:
    cursor.execute("ALTER TABLE users ADD COLUMN referred_by INTEGER DEFAULT NULL")
    conn.commit()
except:
    pass

try:
    cursor.execute("ALTER TABLE users ADD COLUMN join_time INTEGER DEFAULT 0")
    conn.commit()
except:
    pass

cursor.execute("""
CREATE TABLE IF NOT EXISTS numbers(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    activation_id TEXT,
    phone TEXT,
    status TEXT,
    buy_time INTEGER,
    price REAL DEFAULT 0,
    country TEXT DEFAULT ''
)
""")


# ===================================
# OTP REPORT TABLE
# ===================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS otp_report(
    user_id INTEGER PRIMARY KEY,
    total_otp INTEGER DEFAULT 0
)
""")

conn.commit()

conn.commit()


# ===================================
# MANUAL STOCK TABLE
# ===================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS manual_numbers(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT,
    service TEXT,
    status TEXT DEFAULT 'AVAILABLE',
    assigned_user INTEGER DEFAULT 0,
    otp_code TEXT DEFAULT '',
    added_time INTEGER DEFAULT 0,
    buy_time INTEGER DEFAULT 0,
    price REAL DEFAULT 0
)
""")

conn.commit()

try:
    cursor.execute(
        "ALTER TABLE manual_numbers ADD COLUMN service TEXT DEFAULT 'instagram'"
    )
    conn.commit()
except:
    pass

try:
    cursor.execute(
        "ALTER TABLE manual_numbers ADD COLUMN added_time INTEGER DEFAULT 0"
    )
    conn.commit()
except:
    pass

try:
    cursor.execute(
        "ALTER TABLE manual_numbers ADD COLUMN price REAL DEFAULT 0"
    )
    conn.commit()
except:
    pass

try:
    cursor.execute(
        "ALTER TABLE manual_numbers ADD COLUMN buy_time INTEGER DEFAULT 0"
    )
    conn.commit()
except:
    pass

try:
    cursor.execute("ALTER TABLE numbers ADD COLUMN price REAL DEFAULT 0")
    conn.commit()
except:
    pass

try:
    cursor.execute("ALTER TABLE numbers ADD COLUMN country TEXT DEFAULT ''")
    conn.commit()
except:
    pass


# ===================================
# OTP REPORT FUNCTIONS
# ===================================

def add_otp_count(user_id):

    cursor.execute(
        "SELECT total_otp FROM otp_report WHERE user_id=?",
        (user_id,)
    )

    data = cursor.fetchone()

    if data:

        total = int(data[0]) + 1

        cursor.execute(
            "UPDATE otp_report SET total_otp=? WHERE user_id=?",
            (total, user_id)
        )

    else:

        cursor.execute(
            "INSERT INTO otp_report(user_id, total_otp) VALUES(?, ?)",
            (user_id, 1)
        )

    conn.commit()


def reset_daily_otp_report():

    while True:

        try:

            now = time.localtime()

            if now.tm_hour == 0 and now.tm_min == 0:

                cursor.execute("DELETE FROM otp_report")
                conn.commit()

                print("DAILY OTP REPORT RESET DONE")

                time.sleep(60)

            time.sleep(20)

        except Exception as e:

            print("RESET REPORT ERROR:", e)
            time.sleep(20)


# ===================================
# API FUNCTION
# ===================================

def api_get(params):

    try:

        response = scraper.get(
            BASE_URL,
            params=params,
            timeout=30
        )

        print("STATUS CODE:", response.status_code)
        print("FINAL URL:", response.url)

        text = response.text.strip()

        print("RESPONSE:", text[:500])

        if "<html" in text.lower():
            return "CLOUDFLARE OR API BLOCKED"

        return text

    except Exception as e:

        print("API ERROR:", e)

        return None



# ===================================
# DEPOSIT
# ===================================

@bot.message_handler(func=lambda m: m.text == "💳 Deposit")
def deposit(message):

    bot.reply_to(
        message,
        DEPOSIT_TEXT,
        parse_mode="Markdown"
    )

# ===================================
# BALANCE FUNCTIONS
# ===================================

def get_balance(user_id):

    with sqlite3.connect("database.db", timeout=30) as local_conn:

        local_cursor = local_conn.cursor()

        local_cursor.execute(
            "SELECT balance FROM users WHERE user_id=?",
            (user_id,)
        )

        data = local_cursor.fetchone()

        if data:
            return data[0]

        local_cursor.execute(
            "INSERT INTO users(user_id, balance) VALUES(?, ?)",
            (user_id, 0)
        )

        local_conn.commit()

        return 0


def add_balance(user_id, amount):

    with sqlite3.connect("database.db", timeout=30) as local_conn:

        local_cursor = local_conn.cursor()

        bal = float(get_balance(user_id))

        new_bal = bal + float(amount)

        local_cursor.execute(
            "UPDATE users SET balance=? WHERE user_id=?",
            (new_bal, user_id)
        )

        local_conn.commit()


def cut_balance(user_id, amount):

    with sqlite3.connect("database.db", timeout=30) as local_conn:

        local_cursor = local_conn.cursor()

        bal = float(get_balance(user_id))

        if bal < float(amount):
            return False

        new_bal = bal - float(amount)

        local_cursor.execute(
            "UPDATE users SET balance=? WHERE user_id=?",
            (new_bal, user_id)
        )

        local_conn.commit()

        return True

    return False

# ===================================
# START COMMAND
# ===================================

@bot.message_handler(commands=['start'])
def start(message):

    user_id = message.from_user.id

    cursor.execute(
        "SELECT * FROM users WHERE user_id=?",
        (user_id,)
    )

    exists = cursor.fetchone()

    if not exists:

        referred_by = None

        args = message.text.split()

        if len(args) > 1:

            try:

                ref_id = int(args[1])

                if ref_id != user_id:
                    referred_by = ref_id

            except:
                pass

        cursor.execute(
            "INSERT INTO users(user_id, balance, referred_by, join_time) VALUES(?, ?, ?, ?)",
            (user_id, 0, referred_by, int(time.time()))
        )

        conn.commit()

    balance = get_balance(user_id)

    bot_username = bot.get_me().username

    referral_link = f"https://t.me/{bot_username}?start={user_id}"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row("🛒 Buy Instagram Number")
    markup.row("📩 Get OTP")
    markup.row("⭐ Premium Server")
    markup.row("📦 Manual Number")
    markup.row("👥 Referral", "💳 Deposit")
    markup.row("💰 Balance", "🆔 My ID")

    bot.send_message(
        message.chat.id,
        f"""
🤖 INSTAGRAM OTP BOT

👋 Welcome

🆔 User ID: {user_id}

💰 Balance: {balance} টাকা

🎁 Refer & Earn 10%

🔗 Your Referral Link:
{referral_link}
        """,
        reply_markup=markup
    )



# ===================================
# DEPOSIT
# ===================================

@bot.message_handler(func=lambda m: m.text == "💳 Deposit")
def deposit(message):

    bot.reply_to(
        message,
        DEPOSIT_TEXT,
        parse_mode="Markdown"
    )

# ===================================
# BALANCE
# ===================================

@bot.message_handler(func=lambda m: m.text == "💰 Balance")
def balance(message):

    bal = get_balance(message.from_user.id)

    bot.reply_to(
        message,
        f"💰 Balance: {bal} টাকা"
    )

# ===================================
# MY ID
# ===================================

@bot.message_handler(func=lambda m: m.text == "🆔 My ID")
def myid(message):

    bot.reply_to(
        message,
        f"🆔 USER ID:\n\n{message.from_user.id}"
    )



# ===================================
# REFERRAL SYSTEM
# ===================================

@bot.message_handler(func=lambda m: m.text == "👥 Referral")
def referral_panel(message):

    user_id = message.from_user.id

    bot_username = bot.get_me().username

    referral_link = f"https://t.me/{bot_username}?start={user_id}"

    cursor.execute(
        "SELECT COUNT(*) FROM users WHERE referred_by=?",
        (user_id,)
    )

    total_refs = cursor.fetchone()[0]

    bot.reply_to(
        message,
        f"""
👥 Referral System

🔗 Your Referral Link:
{referral_link}

👤 Total Referrals:
{total_refs}

💸 Commission:
10% From Every Deposit
        """
    )


def add_referral_commission(user_id, deposit_amount):

    cursor.execute(
        "SELECT referred_by FROM users WHERE user_id=?",
        (user_id,)
    )

    data = cursor.fetchone()

    if not data:
        return

    referrer_id = data[0]

    if not referrer_id:
        return

    commission = int((deposit_amount * 10) / 100)

    if commission <= 0:
        return

    add_balance(referrer_id, commission)

    try:

        bot.send_message(
            referrer_id,
            f"""
🎉 Referral Commission Received

👤 User:
{user_id}

💰 Deposit:
{deposit_amount} TK

🎁 Your Commission:
{commission} TK
            """
        )

    except:
        pass


# ===================================
# BUY NUMBER
# ===================================

@bot.message_handler(func=lambda m: m.text == "🛒 Buy Instagram Number")
def buy_number(message):

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "🇲🇨 Indonesia - 2 TK",
            callback_data="buy_1"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "ID Indonesia Best - 5 TK",
            callback_data="buy_2"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "🇺🇸 USA - 4.85 TK",
            callback_data="buy_3"
        )
    )

    # EXTRA EMPTY BUTTONS
    markup.add(
        types.InlineKeyboardButton(
            "🇲🇨 Indonesia - 4.75 TK",
            callback_data="buy_4"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "➕ colombia -2 TK",
            callback_data="buy_5"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "➕ United KINGDOM - 6.2 TK",
            callback_data="buy_6"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            " Yemen - 2 TK",
            callback_data="buy_7"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "BRAZIL - 6 TK",
            callback_data="buy_8"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "United Kingdom - 3 TK",
            callback_data="buy_9"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            " Colombia - 2 TK",
            callback_data="buy_10"
        )
    )

    bot.reply_to(
        message,
        "🌍 Select Country",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def process_buy(call):

    key = call.data.split("_")[1]

    data_cfg = COUNTRIES[key]

    country_id = str(data_cfg["country_id"])
    provider_id = str(data_cfg["provider_id"])
    fix_price = str(data_cfg["fix_price"])
    user_price = float(data_cfg["user_price"])
    service_code = data_cfg.get("service_code", "ig")

    user_id = call.from_user.id

    if not cut_balance(user_id, user_price):

        bot.answer_callback_query(
            call.id,
            "❌ Balance কম আছে"
        )

        return

    # TRY WITH PROVIDER
    params = {
        "api_key": API_KEY,
        "action": "getNumber",
        "service": service_code,
        "country": country_id,
        "providerIds": provider_id,
        "fixPrice": fix_price
    }

    print("BUY PARAMS:", params)

    data = api_get(params)

    print("FIRST RESPONSE:", data)

    # FALLBACK DISABLED
    # Exact fixed rate only
    # If no number available in fixed price then buy fail

    if not data or "NO_NUMBERS" in str(data):

        add_balance(user_id, user_price)

        bot.send_message(
            call.message.chat.id,
            "❌ Number Not Available"
        )

        return

    if data is None:

        add_balance(user_id, user_price)

        bot.send_message(
            call.message.chat.id,
            "❌ API Server Error"
        )

        return

    if "ACCESS_NUMBER" in str(data):

        parts = str(data).split(":")

        activation_id = parts[1]
        phone = parts[2]

        # STRICT FIXED PRICE CHECK
        try:

            check_params = {
                "api_key": API_KEY,
                "action": "getStatus",
                "id": activation_id
            }

            print("STRICT PRICE CHECK ENABLED")

        except Exception as e:

            print("PRICE CHECK ERROR:", e)

        cursor.execute(
            "INSERT INTO numbers(user_id, activation_id, phone, status, buy_time, price, country) VALUES(?, ?, ?, ?, ?, ?, ?)",
            (
                user_id,
                activation_id,
                phone,
                "ACTIVE",
                int(time.time()),
                user_price,
                data_cfg['name']
            )
        )

        conn.commit()

        markup = types.InlineKeyboardMarkup()

        cancel_btn = types.InlineKeyboardButton(
            "❌ Cancel Number",
            callback_data=f"cancel_{activation_id}"
        )

        markup.add(cancel_btn)

        bot.send_message(
            call.message.chat.id,
            f"""
✅ Number Purchased

🌍 Country:
{data_cfg['name']}

📱 Number:
`{phone}`

🆔 Activation ID:
`{activation_id}`

👤 User ID:
`{user_id}`

❌ Cancel available for 2 minutes

💸 Price:
{user_price} টাকা
            """,
            parse_mode="Markdown",
            reply_markup=markup
        )

    else:

        add_balance(user_id, user_price)

        bot.send_message(
            call.message.chat.id,
            f"""
❌ Buy Failed

🌍 Country:
{data_cfg['name']}

📩 API Response:
`{str(data)[:1000]}`
            """,
            parse_mode="Markdown"
        )

# ===================================
# AUTO GET OTP
# ===================================

@bot.message_handler(func=lambda m: m.text == "📩 Get OTP")
def auto_get_otp(message):

    user_id = message.from_user.id

    cursor.execute(
        """
        SELECT activation_id, phone
        FROM numbers
        WHERE user_id=? AND status='ACTIVE'
        ORDER BY id DESC
        LIMIT 1
        """,
        (user_id,)
    )

    row = cursor.fetchone()

    if not row:

        bot.reply_to(
            message,
            "❌ কোনো Active Number পাওয়া যায়নি"
        )

        return

    activation_id = row[0]
    phone = row[1]

    wait_msg = bot.reply_to(
        message,
        f"""
⏳ Waiting For OTP...

📱 Number:
`{phone}`

🆔 Activation ID:
`{activation_id}`

🔄 Auto Checking Started
        """,
        parse_mode="Markdown"
    )

    def check_otp():

        while True:

            try:

                params = {
                    "api_key": API_KEY,
                    "action": "getStatus",
                    "id": activation_id
                }

                data = str(api_get(params))

                print("AUTO OTP CHECK:", data)

                # OTP RECEIVED
                if "STATUS_OK" in data:

                    otp = data.split(":")[1]

                    done_params = {
                        "api_key": API_KEY,
                        "action": "setStatus",
                        "status": "6",
                        "id": activation_id
                    }

                    api_get(done_params)

                    cursor.execute(
                        "UPDATE numbers SET status='USED' WHERE activation_id=?",
                        (activation_id,)
                    )

                    conn.commit()

                    add_otp_count(user_id)

                    bot.edit_message_text(
                        f"""
✅ OTP RECEIVED

📱 Number:
`{phone}`

📩 OTP:
`{otp}`
                        """,
                        wait_msg.chat.id,
                        wait_msg.message_id,
                        parse_mode="Markdown"
                    )

                    break

                elif data in [
                    "STATUS_CANCEL",
                    "STATUS_WAIT_RESEND"
                ]:

                    bot.edit_message_text(
                        f"""
❌ OTP Failed

📩 Status:
`{data}`
                        """,
                        wait_msg.chat.id,
                        wait_msg.message_id,
                        parse_mode="Markdown"
                    )

                    break

                time.sleep(5)

            except Exception as e:

                print("AUTO OTP ERROR:", e)

                time.sleep(5)

    threading.Thread(target=check_otp).start()


# ===================================
# CANCEL SYSTEM
# ===================================

@bot.callback_query_handler(func=lambda call: call.data.startswith("cancel_"))
def cancel_number(call):

    activation_id = call.data.split("_")[1]

    cursor.execute(
        "SELECT user_id, buy_time, status, price FROM numbers WHERE activation_id=?",
        (activation_id,)
    )

    data = cursor.fetchone()

    if not data:
        return

    user_id, buy_time, status, price = data

    if status != "ACTIVE":

        bot.answer_callback_query(
            call.id,
            "❌ OTP Already Received"
        )

        return

    now = int(time.time())

    if now - buy_time < 120:

        remaining = 120 - (now - buy_time)

        bot.answer_callback_query(
            call.id,
            f"⏳ Wait {remaining} sec before cancel"
        )

        return

    # API cancel request
    params = {
        "api_key": API_KEY,
        "action": "setStatus",
        "status": "8",
        "id": activation_id
    }

    api_get(params)

    add_balance(user_id, price)

    cursor.execute(
        "UPDATE numbers SET status='CANCELLED' WHERE activation_id=?",
        (activation_id,)
    )

    conn.commit()

    bot.edit_message_text(
        f"✅ Number Cancelled From API\n\n💰 {price} টাকা refunded",
        call.message.chat.id,
        call.message.message_id
    )

# ===================================
# AUTO REFUND
# ===================================

def auto_refund_checker():

    while True:

        try:

            now = int(time.time())

            cursor.execute(
                "SELECT activation_id, user_id, buy_time, price FROM numbers WHERE status='ACTIVE'"
            )

            rows = cursor.fetchall()

            for row in rows:

                activation_id = row[0]
                user_id = row[1]
                buy_time = row[2]
                price = row[3]

                if now - buy_time >= 1200:

                    params = {
                        "api_key": API_KEY,
                        "action": "getStatus",
                        "id": activation_id
                    }

                    data = str(api_get(params))

                    print("AUTO CHECK:", activation_id, data)

                    # OTP RECEIVED
                    if "STATUS_OK" in data:

                        cursor.execute(
                            "UPDATE numbers SET status='USED' WHERE activation_id=?",
                            (activation_id,)
                        )

                        conn.commit()

                        continue

                    # REFUND ONLY IF NO OTP
                    if data in [
                        "STATUS_WAIT_CODE",
                        "STATUS_WAIT_RESEND",
                        "STATUS_CANCEL"
                    ]:

                        cancel_params = {
                            "api_key": API_KEY,
                            "action": "setStatus",
                            "status": "8",
                            "id": activation_id
                        }

                        api_get(cancel_params)

                        add_balance(user_id, price)

                        cursor.execute(
                            "UPDATE numbers SET status='REFUNDED' WHERE activation_id=?",
                            (activation_id,)
                        )

                        conn.commit()

                        bot.send_message(
                            user_id,
                            f"""
💰 Auto Refund Done

🆔 Activation ID:
`{activation_id}`

💸 Refund:
{price} TK
                            """,
                            parse_mode="Markdown"
                        )

            time.sleep(30)

        except Exception as e:

            print("AUTO REFUND ERROR:", e)

            time.sleep(30)





# ===================================
# PREMIUM SERVER
# ===================================

@bot.message_handler(func=lambda m: m.text == "⭐ Premium Server")
def premium_server(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row("🛒 Premium Buy")
    markup.row("📩 Premium OTP")
    markup.row("🔙 Back")

    bot.send_message(
        message.chat.id,
        "⭐ PREMIUM SERVER",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text == "🔙 Back")
def premium_back(message):
    start(message)


@bot.message_handler(func=lambda m: m.text == "🛒 Premium Buy")
def premium_buy(message):

    markup = types.InlineKeyboardMarkup()

    for key, cfg in SMSPOOL_COUNTRIES.items():

        markup.add(
            types.InlineKeyboardButton(
                f"{cfg['name']} - {cfg['user_price']} TK",
                callback_data=f"spbuy_{key}"
            )
        )

    bot.send_message(
        message.chat.id,
        "🌍 Select Country",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("spbuy_"))
def smspool_buy(call):

    key = call.data.split("_")[1]

    cfg = SMSPOOL_COUNTRIES[key]

    user_price = float(cfg['user_price'])

    user_id = call.from_user.id

    if not cut_balance(user_id, user_price):

        bot.answer_callback_query(
            call.id,
            "❌ Balance কম আছে"
        )

        return

    try:

        headers = {
            "Authorization": f"Bearer {SMSPOOL_API_KEY}"
        }

        payload = {
            "country": cfg.get('country', '1'),
            "service": cfg.get('service', '457'),
            "max_price": cfg.get('max_price', '0.35'),
            "quantity": 1
        }

        print("BUY PAYLOAD:", payload)

        response = scraper.post(
            "https://api.smspool.net/purchase/sms",
            headers=headers,
            data=payload,
            timeout=30
        )

        data = response.json()

        print("SERVER BUY:", data)

        if not data.get("success"):

            add_balance(user_id, user_price)

            bot.send_message(
                call.message.chat.id,
                "❌ Number Not Available"
            )

            return

        order_id = str(data['order_id'])
        phone = str(data['number'])

        cursor.execute(
            "INSERT INTO numbers(user_id, activation_id, phone, status, buy_time, price, country) VALUES(?, ?, ?, ?, ?, ?, ?)",
            (
                user_id,
                order_id,
                phone,
                "ACTIVE",
                int(time.time()),
                user_price,
                "PREMIUM " + cfg['name']
            )
        )

        conn.commit()

        markup = types.InlineKeyboardMarkup()

        markup.add(
            types.InlineKeyboardButton(
                "❌ Cancel Number",
                callback_data=f"spcancel_{order_id}"
            )
        )

        bot.send_message(
            call.message.chat.id,
            f"""
✅ NUMBER PURCHASED

🌍 Country:
{cfg['name']}

📱 Number:
`{phone}`

🆔 Order ID:
`{order_id}`

💸 Price:
{user_price} TK

⏳ Cancel After 2 Minutes
            """,
            parse_mode="Markdown",
            reply_markup=markup
        )

    except Exception as e:

        add_balance(user_id, user_price)

        bot.send_message(
            call.message.chat.id,
            f"❌ SERVER ERROR\n\n{e}"
        )


@bot.message_handler(func=lambda m: m.text == "📩 Premium OTP")
def premium_otp(message):

    user_id = message.from_user.id

    cursor.execute(
        """
        SELECT activation_id, phone
        FROM numbers
        WHERE user_id=? AND status='ACTIVE'
        AND country LIKE 'PREMIUM%'
        ORDER BY id DESC
        LIMIT 1
        """,
        (user_id,)
    )

    row = cursor.fetchone()

    if not row:

        bot.reply_to(
            message,
            "❌ No Active Number"
        )

        return

    order_id = row[0]
    phone = row[1]

    wait_msg = bot.reply_to(
        message,
        f"⏳ Waiting OTP...\n\n📱 {phone}"
    )

    def checker():

        while True:

            try:

                # FIRST CHECK DATABASE STATUS
                cursor.execute(
                    "SELECT status FROM numbers WHERE activation_id=?",
                    (order_id,)
                )

                status_row = cursor.fetchone()

                if not status_row:
                    break

                current_status = status_row[0]

                # STOP LOOP IF CANCELLED / REFUNDED / USED
                if current_status in ["CANCELLED", "REFUNDED", "USED"]:

                    print(f"CHECKER STOPPED: {current_status}")

                    try:
                        bot.edit_message_text(
                            "❌ OTP Checking Stopped",
                            wait_msg.chat.id,
                            wait_msg.message_id
                        )
                    except:
                        pass

                    break

                headers = {
                    "Authorization": f"Bearer {SMSPOOL_API_KEY}"
                }

                response = scraper.get(
                    f"https://api.smspool.net/request/check/{order_id}",
                    headers=headers,
                    timeout=30
                )

                data = response.json()

                print("SERVER OTP:", data)

                sms_code = str(data.get("sms", ""))

                if sms_code and sms_code != "":

                    cursor.execute(
                        "UPDATE numbers SET status='USED' WHERE activation_id=?",
                        (order_id,)
                    )

                    conn.commit()

                    add_otp_count(user_id)

                    resend_markup = types.InlineKeyboardMarkup()

                    resend_markup.add(
                        types.InlineKeyboardButton(
                            "♻️ Resend OTP",
                            callback_data=f"resend_{order_id}"
                        )
                    )

                    bot.edit_message_text(
                        f"✅ OTP RECEIVED\n\n📩 OTP:\n`{sms_code}`\n\n♻️ You Can Request Another OTP",
                        wait_msg.chat.id,
                        wait_msg.message_id,
                        parse_mode="Markdown",
                        reply_markup=resend_markup
                    )

                    break

                time.sleep(5)

            except Exception as e:

                print("SERVER OTP ERROR:", e)
                time.sleep(5)

    threading.Thread(target=checker).start()


@bot.callback_query_handler(func=lambda call: call.data.startswith("spcancel_"))
def smspool_cancel(call):

    order_id = call.data.split("_")[1]

    cursor.execute(
        "SELECT user_id, buy_time, status, price FROM numbers WHERE activation_id=?",
        (order_id,)
    )

    row = cursor.fetchone()

    if not row:
        return

    user_id, buy_time, status, price = row

    if status != "ACTIVE":

        bot.answer_callback_query(
            call.id,
            "❌ Already Used"
        )

        return

    now = int(time.time())

    if now - buy_time < 120:

        left = 120 - (now - buy_time)

        bot.answer_callback_query(
            call.id,
            f"⏳ Wait {left} sec"
        )

        return

    try:

        headers = {
            "Authorization": f"Bearer {SMSPOOL_API_KEY}"
        }

        # OTP already received কিনা check
        check_response = scraper.get(
            f"https://api.smspool.net/request/check/{order_id}",
            headers=headers,
            timeout=30
        )

        check_text = check_response.text.lower()

        # OTP আসলে refund off
        if "full_sms" in check_text or "code" in check_text:

            cursor.execute(
                "UPDATE numbers SET status='USED' WHERE activation_id=?",
                (order_id,)
            )

            conn.commit()

            bot.answer_callback_query(
                call.id,
                "❌ OTP Already Received"
            )

            return

        # SMSPOOL cancel request
        cancel_response = scraper.post(
            "https://api.smspool.net/sms/cancel",
            headers={
                "Authorization": f"Bearer {SMSPOOL_API_KEY}"
            },
            data={
                "orderid": order_id
            },
            timeout=30
        )

        print("SMSPOOL CANCEL:", cancel_response.text)

        cancel_text = cancel_response.text.lower()

        if "success" not in cancel_text:

            bot.answer_callback_query(
                call.id,
                "❌ Website Refund Failed"
            )

            return

    except Exception as e:

        print("SERVER CANCEL ERROR:", e)

        bot.answer_callback_query(
            call.id,
            "❌ Cancel API Error"
        )

        return

    add_balance(user_id, price)

    cursor.execute(
        "UPDATE numbers SET status='CANCELLED' WHERE activation_id=?",
        (order_id,)
    )

    conn.commit()

    bot.edit_message_text(
        f"✅ NUMBER CANCELLED\n\n💰 {price} TK Refunded",
        call.message.chat.id,
        call.message.message_id
    )


def smspool_auto_refund():

    local_conn = sqlite3.connect(
        "database.db",
        timeout=30,
        check_same_thread=False
    )

    local_conn.execute("PRAGMA journal_mode=WAL")
    local_cursor = local_conn.cursor()

    while True:

        try:

            now = int(time.time())

            local_cursor.execute(
                """
                SELECT activation_id, user_id, buy_time, price
                FROM numbers
                WHERE status='ACTIVE'
                AND country LIKE 'PREMIUM%'
                """
            )

            rows = local_cursor.fetchall()

            for row in rows:

                order_id = row[0]
                user_id = row[1]
                buy_time = row[2]
                price = row[3]

                if now - buy_time >= 1200:

                    headers = {
                        "Authorization": f"Bearer {SMSPOOL_API_KEY}"
                    }

                    try:

                        # OTP এসেছে কিনা check
                        check_response = scraper.get(
                            f"https://api.smspool.net/request/check/{order_id}",
                            headers=headers,
                            timeout=30
                        )

                        check_text = check_response.text.lower()

                        # OTP already received
                        if "full_sms" in check_text or "code" in check_text:

                            local_cursor.execute(
                                "UPDATE numbers SET status='USED' WHERE activation_id=?",
                                (order_id,)
                            )

                            local_conn.commit()

                            continue

                        cancel_response = scraper.post(
                            "https://api.smspool.net/sms/cancel",
                            headers={
                                "Authorization": f"Bearer {SMSPOOL_API_KEY}",
                                "Content-Type": "application/json"
                            },
                            json={
                                "orderid": order_id
                            },
                            timeout=30
                        )

                        print("AUTO CANCEL:", cancel_response.text)

                        if "success" not in cancel_response.text.lower():
                            continue

                    except Exception as e:
                        print("AUTO CANCEL ERROR:", e)
                        continue

                    add_balance(user_id, price)

                    local_cursor.execute(
                        "UPDATE numbers SET status='REFUNDED' WHERE activation_id=?",
                        (order_id,)
                    )

                    local_conn.commit()

                    bot.send_message(
                        user_id,
                        f"💰 AUTO REFUND DONE\n\n🆔 Order ID:\n`{order_id}`",
                        parse_mode="Markdown"
                    )

            time.sleep(30)

        except Exception as e:

            print("AUTO REFUND ERROR:", e)
            time.sleep(30)




# ===================================
# MANUAL STOCK SYSTEM
# ===================================

@bot.message_handler(func=lambda m: m.text == "📦 Manual Number")
def manual_number_panel(message):

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "📲 Buy Manual Instagram Number",
            callback_data="manual_buy_ig"
        )
    )

    bot.send_message(
        message.chat.id,
        "📦 Manual Stock Number System",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data == "manual_buy_ig")
def manual_buy_ig(call):

    user_id = call.from_user.id
    global MANUAL_PRICE

    PRICE = float(MANUAL_PRICE)

    if not cut_balance(user_id, PRICE):

        bot.answer_callback_query(
            call.id,
            "❌ Balance কম আছে"
        )

        return

    cursor.execute(
        """
        SELECT id, phone
        FROM manual_numbers
        WHERE status='AVAILABLE'
        ORDER BY RANDOM()
        LIMIT 1
        """
    )

    row = cursor.fetchone()

    if not row:

        add_balance(user_id, PRICE)

        bot.send_message(
            call.message.chat.id,
            "❌ Manual Number Stock Empty"
        )

        return

    number_id = row[0]
    phone = row[1]

    cursor.execute(
        """
        UPDATE manual_numbers
        SET status='ASSIGNED',
        assigned_user=?,
        added_time=?,
        buy_time=?
        WHERE id=?
        """,
        (
            user_id,
            int(time.time()),
            int(time.time()),
            number_id
        )
    )

    conn.commit()

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "❌ Cancel Manual Number",
            callback_data=f"manualcancel_{number_id}"
        )
    )

    bot.send_message(
        call.message.chat.id,
        f"""
✅ Manual Number Purchased

📱 Number:
`{phone}`

💸 Price:
{PRICE} TK

⏳ OTP Wait Time: 5 Minutes
❌ Cancel Available After 2 Minutes
        """,
        parse_mode="Markdown",
        reply_markup=markup
    )

    try:

        if ADMIN_CHAT_ID != 123456789:

            bot.send_message(
                ADMIN_CHAT_ID,
            f"""
🚨 NEW MANUAL ORDER

👤 USER ID:
`{user_id}`

📱 NUMBER:
`{phone}`

💰 PRICE:
{PRICE} TK
            """,
                parse_mode="Markdown"
            )

    except Exception as e:
        print("ADMIN NOTIFY ERROR:", e)


@bot.message_handler(commands=['addnumber'])
def add_manual_number(message):

    if message.from_user.id != ADMIN_CHAT_ID:
        return

    try:

        lines = message.text.splitlines()

        if len(lines) <= 1:

            bot.reply_to(
                message,
                "/addnumber\n017xxxx\n017xxxx"
            )

            return

        added = 0

        for phone in lines[1:]:

            phone = phone.strip()

            if not phone:
                continue

            cursor.execute(
                """
                INSERT INTO manual_numbers(
                    phone,
                    service,
                    status,
                    added_time,
                    price
                )
                VALUES(?, ?, ?, ?, ?)
                """,
                (
                    phone,
                    "instagram",
                    "AVAILABLE",
                    int(time.time()),
                    MANUAL_PRICE
                )
            )

            added += 1

        conn.commit()

        bot.reply_to(
            message,
            f"✅ {added} Numbers Added"
        )

        try:

            cursor.execute(
                "SELECT user_id FROM users"
            )

            all_users = cursor.fetchall()

            for usr in all_users:

                try:

                    bot.send_message(
                        usr[0],
                        f"📦 New Manual Stock Added\n\n🔥 {added} New Numbers Added"
                    )

                except:
                    pass

        except Exception as e:

            print("MANUAL STOCK NOTIFY ERROR:", e)

    except Exception as e:

        bot.reply_to(
            message,
            f"❌ Error\n\n{e}"
        )


@bot.message_handler(commands=['setprice'])
def set_manual_price(message):

    global MANUAL_PRICE

    if message.from_user.id != ADMIN_CHAT_ID:
        return

    try:

        cmd = message.text.split()

        MANUAL_PRICE = float(cmd[1])

        bot.reply_to(
            message,
            f"✅ Manual Price Set To {MANUAL_PRICE} TK"
        )

    except:

        bot.reply_to(
            message,
            "/setprice 0.8"
        )


@bot.message_handler(func=lambda m: m.text and not m.text.startswith('/'))
def quick_send_otp(message):

    if message.from_user.id != ADMIN_CHAT_ID:
        return

    try:

        parts = message.text.strip().split()

        if len(parts) != 2:
            return

        phone = parts[0]
        otp = parts[1]

        if not otp.isdigit():
            return

        cursor.execute(
            """
            SELECT assigned_user
            FROM manual_numbers
            WHERE phone=?
            AND status='ASSIGNED'
            """,
            (phone,)
        )

        row = cursor.fetchone()

        if not row:
            return

        user_id = row[0]

        bot.send_message(
            user_id,
            f"""
✅ OTP RECEIVED

📱 Number:
`{phone}`

📩 OTP:
`{otp}`
            """,
            parse_mode="Markdown"
        )

        cursor.execute(
            """
            UPDATE manual_numbers
            SET status='USED', otp_code=?
            WHERE phone=?
            """,
            (otp, phone)
        )

        conn.commit()

        add_otp_count(user_id)

        bot.reply_to(
            message,
            "✅ OTP Delivered"
        )

    except Exception as e:
        print("QUICK OTP ERROR:", e)


@bot.message_handler(commands=['sendotp'])
def send_manual_otp(message):

    if message.from_user.id != ADMIN_CHAT_ID:
        return

    try:

        cmd = message.text.split(maxsplit=2)

        phone = cmd[1]
        otp = cmd[2]

        cursor.execute(
            """
            SELECT assigned_user
            FROM manual_numbers
            WHERE phone=?
            AND status='ASSIGNED'
            """,
            (phone,)
        )

        row = cursor.fetchone()

        if not row:

            bot.reply_to(
                message,
                "❌ Number Not Found"
            )

            return

        user_id = row[0]

        bot.send_message(
            user_id,
            f"""
✅ OTP RECEIVED

📱 Number:
`{phone}`

📩 OTP:
`{otp}`
            """,
            parse_mode="Markdown"
        )

        cursor.execute(
            """
            UPDATE manual_numbers
            SET status='USED', otp_code=?
            WHERE phone=?
            """,
            (otp, phone)
        )

        conn.commit()

        add_otp_count(user_id)

        bot.reply_to(
            message,
            "✅ OTP Sent Successfully"
        )

    except Exception as e:

        bot.reply_to(
            message,
            f"❌ Error\n\n{e}"
        )


@bot.message_handler(commands=['manualstock'])
def manual_stock(message):

    if message.from_user.id != ADMIN_CHAT_ID:
        return

    cursor.execute(
        "SELECT COUNT(*) FROM manual_numbers WHERE status='AVAILABLE'"
    )

    available = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM manual_numbers WHERE status='USED'"
    )

    used = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM manual_numbers WHERE status='ASSIGNED'"
    )

    assigned = cursor.fetchone()[0]

    bot.send_message(
        message.chat.id,
        f"""
📦 MANUAL STOCK REPORT

✅ AVAILABLE : {available}
📩 ASSIGNED : {assigned}
☑️ USED : {used}
        """
    )




# ===================================
# MANUAL CANCEL SYSTEM
# ===================================

@bot.callback_query_handler(func=lambda call: call.data.startswith("manualcancel_"))
def manual_cancel(call):

    number_id = call.data.split("_")[1]

    cursor.execute("""
    SELECT assigned_user, added_time, status, price
    FROM manual_numbers
    WHERE id=?
    """, (number_id,))

    row = cursor.fetchone()

    if not row:
        return

    assigned_user, added_time, status, price = row

    if assigned_user != call.from_user.id:
        return

    if status != "ASSIGNED":

        bot.answer_callback_query(
            call.id,
            "❌ Already Closed"
        )

        return

    now = int(time.time())

    if now - added_time < 120:

        left = 120 - (now - added_time)

        bot.answer_callback_query(
            call.id,
            f"⏳ Wait {left} sec"
        )

        return

    add_balance(assigned_user, price)

    cursor.execute("""
    UPDATE manual_numbers
    SET status='CANCELLED'
    WHERE id=?
    """, (number_id,))

    conn.commit()

    bot.edit_message_text(
        f"✅ Manual Number Cancelled\n\n💰 {price} TK Refunded",
        call.message.chat.id,
        call.message.message_id
    )


# ===================================
# MANUAL AUTO CLEANER
# ===================================

def manual_auto_cleaner():

    local_conn = sqlite3.connect(
        "database.db",
        timeout=30,
        check_same_thread=False
    )

    local_conn.execute("PRAGMA journal_mode=WAL")

    local_cursor = local_conn.cursor()

    while True:

        try:

            now = int(time.time())

            # AUTO CANCEL AFTER 5 MINUTES
            local_cursor.execute("""
            SELECT id, assigned_user, price, buy_time
            FROM manual_numbers
            WHERE status='ASSIGNED'
            AND buy_time > 0
            AND (? - buy_time) >= 300
            """, (now,))

            assigned_rows = local_cursor.fetchall()

            for row in assigned_rows:

                number_id = row[0]
                user_id = row[1]
                price = row[2]

                add_balance(user_id, price)

                local_cursor.execute("""
                UPDATE manual_numbers
                SET status='AUTO_CANCELLED'
                WHERE id=?
                """, (number_id,))

                local_conn.commit()

                try:

                    bot.send_message(
                        user_id,
                        f"""
❌ Manual Number Auto Cancelled

💰 Refund:
{price} TK
                        """
                    )

                except:
                    pass

            # REMOVE AVAILABLE STOCK AFTER 15 MINUTES
            local_cursor.execute("""
            DELETE FROM manual_numbers
            WHERE status='AVAILABLE'
            AND (? - added_time) >= 900
            """, (now,))

            local_conn.commit()

            time.sleep(30)

        except Exception as e:

            print("MANUAL AUTO CLEAN ERROR:", e)

            time.sleep(30)



# ===================================
# ADMIN USER REPORT
# ===================================

import os

@bot.message_handler(commands=['allusers'])
def all_users_report(message):

    if message.from_user.id != ADMIN_CHAT_ID:
        return

    try:

        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]

        cursor.execute("SELECT user_id, balance FROM users ORDER BY user_id ASC")
        users = cursor.fetchall()

        now = time.localtime()

        today_start = int(time.mktime((
            now.tm_year,
            now.tm_mon,
            now.tm_mday,
            0, 0, 0,
            0, 0, -1
        )))

        cursor.execute(
            "SELECT COUNT(*) FROM users WHERE join_time>=?",
            (today_start,)
        )

        daily_new_users = cursor.fetchone()[0]

        report_text = f"""📊 ALL USERS REPORT

👥 Total Users : {total_users}
📅 Daily New Users : {daily_new_users}

"""

        serial = 1

        for user in users:

            user_id = user[0]
            balance = user[1]

            try:
                chat = bot.get_chat(user_id)

                username = chat.first_name

                if chat.username:
                    username += f" (@{chat.username})"

            except:
                username = "Unknown"

            cursor.execute(
                "SELECT COUNT(*) FROM numbers WHERE user_id=?",
                (user_id,)
            )

            total_number = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM numbers WHERE user_id=? AND status='USED'",
                (user_id,)
            )

            otp_recv = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM numbers WHERE user_id=? AND status='REFUNDED'",
                (user_id,)
            )

            refund = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM users WHERE referred_by=?",
                (user_id,)
            )

            refer_list = cursor.fetchone()[0]

            report_text += f"""
{serial}.
user name : {username}
user id : {user_id}
blance : {balance}
total number : {total_number}
otp recv : {otp_recv}
refund : {refund}
reger list : {refer_list}

"""

            serial += 1

        file_name = "all_users_report.txt"

        with open(file_name, "w", encoding="utf-8") as f:
            f.write(report_text)

        with open(file_name, "rb") as f:

            bot.send_document(
                message.chat.id,
                f,
                caption="📄 All Users Report"
            )

        try:
            os.remove(file_name)
        except:
            pass

    except Exception as e:

        bot.reply_to(
            message,
            f"❌ Error:\n{e}"
        )




# ===================================
# ADMIN BROADCAST
# ===================================

@bot.message_handler(commands=['broadcast'])
def broadcast(message):

    if message.from_user.id != ADMIN_CHAT_ID:
        return

    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()

    success = 0
    failed = 0

    if message.reply_to_message:

        broadcast_msg = message.reply_to_message

        for user in users:

            user_id = user[0]

            try:

                bot.copy_message(
                    user_id,
                    message.chat.id,
                    broadcast_msg.message_id
                )

                success += 1
                time.sleep(0.2)

            except:

                failed += 1

    else:

        msg = message.text.replace('/broadcast', '').strip()

        if not msg:

            bot.reply_to(
                message,
                "❌ Reply to photo/video/text and send /broadcast"
            )

            return

        for user in users:

            user_id = user[0]

            try:

                bot.send_message(user_id, msg)

                success += 1
                time.sleep(0.2)

            except:

                failed += 1

    bot.reply_to(
        message,
        f"""
✅ Broadcast Completed

📩 Success: {success}
❌ Failed: {failed}
"""
    )

@bot.message_handler(commands=['otpreport'])
def otp_report_command(message):

    if message.from_user.id != ADMIN_CHAT_ID:
        return

    cursor.execute("""
    SELECT user_id, total_otp
    FROM otp_report
    ORDER BY total_otp DESC
    """)

    rows = cursor.fetchall()

    if not rows:

        bot.reply_to(message, "❌ No OTP Report Found")
        return

    text_report = "📊 DAILY OTP REPORT\n\n"

    total_all = 0
    serial = 1

    for row in rows:

        user_id = row[0]
        total_otp = row[1]

        total_all += total_otp

        now = time.localtime()

        today_start = int(time.mktime((
            now.tm_year,
            now.tm_mon,
            now.tm_mday,
            0, 0, 0,
            0, 0, -1
        )))

        cursor.execute("""
        SELECT country, COUNT(*)
        FROM numbers
        WHERE user_id=?
        AND status='USED'
        AND buy_time>=?
        GROUP BY country
        """, (user_id, today_start))

        countries = cursor.fetchall()

        country_text = ""

        for c in countries:

            country_name = c[0] if c[0] else "Unknown"

            country_text += f"{country_name} = {c[1]}\n"

        text_report += f"""
{serial}.
USER ID : {user_id}
TOTAL OTP : {total_otp}

COUNTRY REPORT:
{country_text}

"""

        serial += 1

    text_report += f"\n🔥 TOTAL OTP TODAY : {total_all}"

    bot.send_message(message.chat.id, text_report)


@bot.message_handler(commands=['countryreport'])
def country_report(message):

    now = time.localtime()

    today_start = int(time.mktime((
        now.tm_year,
        now.tm_mon,
        now.tm_mday,
        0, 0, 0,
        0, 0, -1
    )))

    cursor.execute("""
    SELECT country, COUNT(*)
    FROM numbers
    WHERE status='USED'
    AND buy_time>=?
    GROUP BY country
    ORDER BY COUNT(*) DESC
    """, (today_start,))

    rows = cursor.fetchall()

    if not rows:

        bot.reply_to(message, "❌ No Country OTP Report")
        return

    text = "🌍 COUNTRY OTP REPORT\n\n"

    total = 0

    for row in rows:

        country = row[0] if row[0] else "Unknown"
        count = row[1]

        total += count

        text += f"""
🌍 {country}
📩 OTP : {count}

"""

    text += f"\n🔥 TOTAL OTP : {total}"

    bot.send_message(message.chat.id, text)


# ===================================
# ADMIN BALANCE
# ===================================

@bot.message_handler(commands=['addbalance'])
def addbal(message):

    if message.from_user.id != ADMIN_CHAT_ID:
        return

    try:

        cmd = message.text.split()

        user_id = int(cmd[1])
        amount = float(cmd[2])

        add_balance(user_id, amount)
        add_referral_commission(user_id, amount)

        bot.reply_to(
            message,
            "✅ Balance Added"
        )

    except:

        bot.reply_to(
            message,
            "/addbalance USER_ID AMOUNT"
        )




@bot.message_handler(commands=['removebalance'])
def removebal(message):

    if message.from_user.id != ADMIN_CHAT_ID:
        return

    try:

        cmd = message.text.split()

        user_id = int(cmd[1])
        amount = float(cmd[2])

        bal = float(get_balance(user_id))

        new_bal = max(0, round(bal - amount, 2))

        cursor.execute(
            "UPDATE users SET balance=? WHERE user_id=?",
            (new_bal, user_id)
        )

        conn.commit()

        bot.reply_to(
            message,
            f"✅ {amount} TK Removed From {user_id}"
        )

    except:

        bot.reply_to(
            message,
            "/removebalance USER_ID AMOUNT"
        )


# ===================================
# MANUAL STOCK AUTO FIX
# ===================================

try:

    cursor.execute("""
    UPDATE manual_numbers
    SET status='AVAILABLE'
    WHERE status IS NULL OR status=''
    """)

    conn.commit()

except Exception as e:

    print("MANUAL STOCK FIX ERROR:", e)


# ===================================
# RUN BOT
# ===================================

threading.Thread(target=auto_refund_checker, daemon=True).start()
threading.Thread(target=smspool_auto_refund, daemon=True).start()
threading.Thread(target=reset_daily_otp_report, daemon=True).start()
threading.Thread(target=manual_auto_cleaner, daemon=True).start()

print("BOT RUNNING...")

while True:

    try:

        bot.infinity_polling(
            timeout=60,
            long_polling_timeout=60
        )

    except Exception as e:

        print("POLLING ERROR:", e)

        time.sleep(5)
        continue
