import firebase_admin
from firebase_admin import credentials, firestore
import random
import string
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- Firebase Inbuilt Setup ---
firebase_json = {
  "type": "service_account",
  "project_id": "demon999-344cd",
  "private_key_id": "34d2b3c60c47c1d37c42a62bcaedc4f40e78cbfb",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCau3O9B5nN+kxG\nbn9iRAjOsLIPnpp4gfwWu8OeIxrVqydcTcs4CDsekIYXJP0zSv1y6xh1ax9iv6t8\nYAm6RqG7I89frigv7eLULG+oM9snG1Hm1AS2BOk48Gx4/Re3DVz6Cdb2JQ52sa0g\nVbZP2dfSSeujCOBdhhIBUrGWVLQ7skJQ4/Xozc3SJxLhRqbPmK0baJPHI9Zss71i\nBGXjN8umjDuDG6QLB7iEWxM13ZCKQvj8jqAPkvBhVq2u0DDcUdhVOjVNV0eSOM0o\npFEvZIAUO6SJWAM5NZzpeLxrGl+HzgRstZ+NA6yCE/rHeubPK0o/0osHXRnPujlK\nBbbcXNd3AgMBAAECggEAKqZtzhZ4wipyeN1/VkY7iUFyK1UD7iCiLGAAGShC/s9p\nD4vP7rdyGEgs9dc3xbovZ0w/Fyp6Yb1EVwmf1M0gSlWiFRULtb5kDijbdCkrCLoC\nltYtIED1SkEXHThiH45a6P7qVjm7pWLvPiDyGkuJLkk63tsVASJx9xRkp/PcJDHe\nSeb/+/NpVCFw99X1stol5vx9COg419wpa5xO91L5pBgyZvbs8BnJyK/vVujkSBQT\n7SDghaysSnb1f/1ZmCtDpn5v/ULFkziderpjtMZeCbjmQ6lj4aZid67S70X2HEGe\nIjVIf0o1wDezF1Jk0VVxj1oD1Kck/zOk4zkZif9HyQKBgQDNCLQEQKWijQhVPI8U\ncjEhSLl6W2lYW3uPUlim//8fignCbvaDdC6+pirvkjPfDjkAROSXvtoibUVFOHpJ\nQFd5/4oXoPjf13vNsCM6uHLAFePUm0CLX5r6uOw+SJi2/5A965HW6JO2Cwc40Pqi\njw2vr2nZre8Xeo71CHGlluzmbwKBgQDBMc510gclRl7Uabq+4xmbUxts7XFxNJzQ\nf1wfULX0lxhM8lAq14enpUPt46TF6b/Is6DMMwerR/ApkCMFXnnX2eYv8c/th3o7\nwhzRky4NVwkuow08W5SqbBtz2h7HW+yKB8FnF5lAK/aRYgUdY55U4QIKEwiPi9OF\n247w1qljeQKBgH0ieKu3wN9qb9GFulViNDX6KqlQrQSuIMUiHtUdnFllZ/twuacU\n+4qD4+R/OIVEKunNIi6y3nLwebx7cbbPPBRLL76oEfybiQXKIFYwSGiPc5NIhaYK\nXY3z2stQh1P4udHwufuNysjqBihY8v7PjCzTRCkEjM2pkSJfWu0TJdalAoGBAKpy\nItDYB+3e8/M7hMK84e6jl+K2aguSe3eHpeMK9j1gwNPCRPBHTyudJx1OZiUmYUnV\nENyXeQCoaz6AKCWogJ7rY6aRFP1fNXxbecl8rHigfT1kJV1G/xaMYnwHyHfipgHx\nbbRioZZ4MwV5EUIojZwdGAuDV14t4uSKHMZm3PMhAoGAfa1oAZyEMTiH8/u0lHNv\no2vrA+wj5p1Te0T5QCHhd+p25ggalcfp4TU1kZA8vRlkK2OMsjSRlxRNX4fSCgoj\nXfDy+qCF4Xp5b+J2DQOYkZJQwpSTpEDNIyCjFkkUO7JD1E8GTymlvn7RjlKWMuFr\n93svBjOgvnkenXs+vVVC27A=\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-ov1lf@demon999-344cd.iam.gserviceaccount.com",
  "client_id": "105774785977737880157",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-ov1lf%40demon999-344cd.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

cred = credentials.Certificate(firebase_json)
firebase_admin.initialize_app(cred)
db = firestore.client()

# --- Bot Setup ---
TOKEN = '7376937034:AAHYiIu6c_TO-axtbxhIMy9DVB258g8ZYF4'  # Your NEW bot token
ADMIN_ID = 6291465341  # Your Telegram ID (TheLucifer_000)

# --- Utility Functions ---
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def generate_bonus_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# --- Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_ref = db.collection('users').document(str(user.id))
    user_doc = user_ref.get()

    if user_doc.exists:
        await update.message.reply_text(f"Welcome back, {user.first_name}!")
    else:
        user_ref.set({
            'user_id': user.id,
            'username': user.username or '',
            'first_name': user.first_name or '',
            'balance': 0,
            'bonus_claimed': False,
            'otp': None,
            'upi': '',
            'mobile': ''
        })
        await update.message.reply_text(f"Hello {user.first_name}! Welcome to Demon999 Casino!")

async def otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    otp_code = generate_otp()
    db.collection('users').document(str(user.id)).update({'otp': otp_code})
    await update.message.reply_text(f"Your OTP is:\n`{otp_code}`", parse_mode="Markdown")

async def signupbonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_ref = db.collection('users').document(str(user.id))
    user_doc = user_ref.get()

    if user_doc.exists:
        if user_doc.to_dict().get('bonus_claimed'):
            await update.message.reply_text("You already claimed the signup bonus!")
        else:
            bonus_code = generate_bonus_code()
            user_ref.update({
                'bonus_code': bonus_code,
                'bonus_claimed': True
            })
            await update.message.reply_text(
                f"Your Bonus Code:\n`{bonus_code}`\n\nPaste this in the website to claim ₹100 bonus!",
                parse_mode="Markdown"
            )
    else:
        await update.message.reply_text("Please /start first!")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_doc = db.collection('users').document(str(user.id)).get()
    if user_doc.exists:
        balance = user_doc.to_dict().get('balance', 0)
        await update.message.reply_text(f"Your Balance: ₹{balance}")
    else:
        await update.message.reply_text("Please /start first!")

async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("₹100", callback_data='deposit_100')],
        [InlineKeyboardButton("₹200", callback_data='deposit_200')],
        [InlineKeyboardButton("₹500", callback_data='deposit_500')],
        [InlineKeyboardButton("₹1000", callback_data='deposit_1000')],
    ]
    await update.message.reply_text("Choose deposit amount:", reply_markup=InlineKeyboardMarkup(keyboard))

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("₹100", callback_data='withdraw_100')],
        [InlineKeyboardButton("₹200", callback_data='withdraw_200')],
        [InlineKeyboardButton("₹500", callback_data='withdraw_500')],
        [InlineKeyboardButton("₹1000", callback_data='withdraw_1000')],
    ]
    await update.message.reply_text("Choose withdraw amount:", reply_markup=InlineKeyboardMarkup(keyboard))

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_doc = db.collection('users').document(str(user.id)).get()

    if user_doc.exists:
        data = user_doc.to_dict()
        await update.message.reply_text(
            f"👤 Profile:\n"
            f"Username: @{data.get('username')}\n"
            f"First Name: {data.get('first_name')}\n"
            f"Balance: ₹{data.get('balance')}\n"
            f"UPI ID: {data.get('upi') or 'Not set'}"
        )
    else:
        await update.message.reply_text("Please /start first!")

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Support Options:\n"
        "- Deposit Issue\n"
        "- Withdraw Issue\n"
        "- Change Credentials\n"
        "- Bonus Issue\n"
        "Please contact Admin @TheLucifer_000."
    )

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id == ADMIN_ID:
        await update.message.reply_text("Admin Panel: Upload QR Codes using /amountqr.")
    else:
        await update.message.reply_text("Unauthorized!")

async def amountqr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id == ADMIN_ID:
        await update.message.reply_text("Send QR codes now (filenames should be 100.png, 200.png, etc).")
    else:
        await update.message.reply_text("Unauthorized!")

# --- Callback Query Handler ---
async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user = query.from_user

    if data.startswith('deposit_'):
        amount = data.split('_')[1]
        await query.edit_message_text(
            f"Please deposit ₹{amount} using the QR code.\nContact Admin after deposit."
        )
    elif data.startswith('withdraw_'):
        amount = data.split('_')[1]
        await query.edit_message_text(
            f"Withdraw request for ₹{amount} has been submitted.\nAdmin will contact you soon."
        )

# --- Main Application ---
app = Application.builder().token(TOKEN).build()

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

print("Bot is running...")
app.run_polling()