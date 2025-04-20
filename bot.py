import firebase_admin
from firebase_admin import credentials, firestore
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- Firebase Setup ---
firebaseConfig = {
    "apiKey": "AIzaSyA0uNQFLMPtbFMw3zfuglqC0RtL56w1LZo",
    "authDomain": "demon999-344cd.firebaseapp.com",
    "projectId": "demon999-344cd",
    "storageBucket": "demon999-344cd.appspot.com",
    "messagingSenderId": "271946918255",
    "appId": "1:271946918255:web:0070a434be461ca724a09a",
    "measurementId": "G-99801YY47E"
}

cred = credentials.Certificate("demon999-344cd-firebase-adminsdk.json")  # <--- Your correct path here
firebase_admin.initialize_app(cred)
db = firestore.client()

# --- Bot Setup ---
TOKEN = '7376937034:AAG-YNUmU4HqSVfhTbQiXCtAVwZzFW-hv7c'  # <--- Your bot token here
ADMIN_ID = 6291465341  # @TheLucifer_000 Telegram ID

# --- Functions ---
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def generate_bonus_code():
    return ''.join(random.choices(string.digits, k=6))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_ref = db.collection('users').document(str(user.id))
    user_doc = user_ref.get()

    if user_doc.exists:
        await update.message.reply_text(f"Welcome back, {user.first_name}!")
    else:
        user_ref.set({
            'username': user.username,
            'user_id': user.id,
            'first_name': user.first_name,
            'bonus_claimed': False,
            'otp': None,
            'balance': 0
        })
        await update.message.reply_text(f"Welcome {user.first_name}! Thanks for joining us.")

async def otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    otp_code = generate_otp()
    db.collection('users').document(str(user.id)).update({'otp': otp_code})
    await update.message.reply_text(f"Your OTP code is: `{otp_code}`", parse_mode="Markdown")

async def signupbonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_ref = db.collection('users').document(str(user.id))
    user_doc = user_ref.get()

    if user_doc.exists and user_doc.to_dict().get('bonus_claimed'):
        await update.message.reply_text("Bonus already claimed or code already generated!")
    else:
        bonus_code = generate_bonus_code()
        user_ref.update({'bonus_code': bonus_code, 'bonus_claimed': True})
        await update.message.reply_text(f"Your Signup Bonus Code is: `{bonus_code}`\nPaste this code on website to claim your 100₹ Bonus!", parse_mode="Markdown")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_doc = db.collection('users').document(str(user.id)).get()
    balance = user_doc.to_dict().get('balance', 0) if user_doc.exists else 0
    await update.message.reply_text(f"Your Balance is: ₹{balance}")

async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("100", callback_data='deposit_100')],
        [InlineKeyboardButton("200", callback_data='deposit_200')],
        [InlineKeyboardButton("500", callback_data='deposit_500')],
        [InlineKeyboardButton("1000", callback_data='deposit_1000')],
        [InlineKeyboardButton("2000", callback_data='deposit_2000')],
        [InlineKeyboardButton("5000", callback_data='deposit_5000')],
    ]
    await update.message.reply_text("Select Amount to Deposit:", reply_markup=InlineKeyboardMarkup(keyboard))

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("100", callback_data='withdraw_100')],
        [InlineKeyboardButton("200", callback_data='withdraw_200')],
        [InlineKeyboardButton("500", callback_data='withdraw_500')],
        [InlineKeyboardButton("1000", callback_data='withdraw_1000')],
        [InlineKeyboardButton("2000", callback_data='withdraw_2000')],
        [InlineKeyboardButton("5000", callback_data='withdraw_5000')],
    ]
    await update.message.reply_text("Select Amount to Withdraw:", reply_markup=InlineKeyboardMarkup(keyboard))

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_doc = db.collection('users').document(str(user.id)).get()

    if user_doc.exists:
        data = user_doc.to_dict()
        await update.message.reply_text(
            f"👤 Profile:\nUsername: @{data.get('username')}\nBalance: ₹{data.get('balance')}\nFirst Name: {data.get('first_name')}"
        )
    else:
        await update.message.reply_text("Profile not found! Please use /start first.")

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Deposit Problem", callback_data='support_deposit')],
        [InlineKeyboardButton("Withdraw Problem", callback_data='support_withdraw')],
        [InlineKeyboardButton("Change Credentials", callback_data='support_credentials')],
        [InlineKeyboardButton("Bonus Problem", callback_data='support_bonus')],
    ]
    await update.message.reply_text("Select Support Option:", reply_markup=InlineKeyboardMarkup(keyboard))

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to access Admin Panel!")
        return
    
    await update.message.reply_text("✅ Welcome to Admin Panel!\nUse /amountqr to upload QR images.")

async def amountqr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id != ADMIN_ID:
        await update.message.reply_text("❌ Not authorized to upload QR!")
        return
    
    await update.message.reply_text("Send me the QR Image you want to upload with filename like '100.png', '200.png', etc.")

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith('deposit_'):
        amount = data.split('_')[1]
        await query.edit_message_text(f"Deposit ₹{amount}\n\nDownload Scanner: [{amount}-scanner.png]\n\nSubmit Ref/UTR after deposit.", parse_mode="Markdown")
    
    elif data.startswith('withdraw_'):
        amount = data.split('_')[1]
        user = query.from_user
        user_doc = db.collection('users').document(str(user.id)).get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            await context.bot.send_message(
                ADMIN_ID,
                f"⚡ Withdraw Request:\nUsername: @{user_data.get('username')}\nMobile: {user_data.get('mobile', 'Not Available')}\nAmount: ₹{amount}\nUPI ID: {user_data.get('upi', 'Not Available')}"
            )
            await query.edit_message_text("Withdraw request submitted! Admin will verify soon.")
        else:
            await query.edit_message_text("User not registered!")

    elif data.startswith('support_'):
        option = data.split('_')[1]
        if option == "deposit":
            await query.edit_message_text("Deposit Problem:\nPlease make sure you sent correct amount & submitted correct Ref/UTR number.")
        elif option == "withdraw":
            await query.edit_message_text("Withdraw Problem:\nFirst deposit minimum once to withdraw.\nTurnover must be completed.")
        elif option == "credentials":
            await query.edit_message_text("Credentials Change:\nYou cannot manually change credentials. Contact Admin.")
        elif option == "bonus":
            await query.edit_message_text("Bonus Problem:\nSignup Bonus can only be claimed ONCE per user.")

# --- Main ---
app = Application.builder().token(TOKEN).build()

# --- Commands ---
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("otp", otp))
app.add_handler(CommandHandler("signupbonus", signupbonus))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("deposit", deposit))
app.add_handler(CommandHandler("withdraw", withdraw))
app.add_handler(CommandHandler("profile", profile))
app.add_handler(CommandHandler("support", support))
app.add_handler(CommandHandler("admin", admin))
app.add_handler(CommandHandler("amountqr", amountqr))
app.add_handler(CallbackQueryHandler(callback_query_handler))

print("Bot Running...")
app.run_polling()
