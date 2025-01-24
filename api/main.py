import os
import json
import telegram
import telegram.ext
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import db, credentials, initialize_app
import datetime
from mistralai import Mistral


class AutoGrader:
    def run_test_cases(self, test_cases, student_function):
        """
        Run all test cases on the student function, accommodating flat dictionaries.
        """
        score = 0
        total = len(test_cases)

        print(test_cases)

        result_feedback = ""

        # Create a namespace to safely execute the student's function
        namespace = {}
        try:
            exec(student_function, namespace)
            # Extract the function from the namespace
            student_function = namespace["factorial"]
        except Exception as e:
            return f"Error in student code: {e}"

        for i, test in enumerate(test_cases, start=1):
            input_data = int(test["input"])  # Convert input to integer
            expected = int(test["expected_output"])  # Convert expected output to integer

            try:
                result = student_function(input_data)
                
                if result == expected:
                    result_feedback += f"- Test {i}: Passed ✅ (Input: {input_data}, Expected: {expected}, Got: {result})\n"
                    score += 1
                else:
                    result_feedback += f"- Test {i}: Failed ❌ (Input: {input_data}, Expected: {expected}, Got: {result})\n"
            except Exception as e:
                result_feedback += f"- Test {i}: Error ❌ (Input: {input_data}, Expected: {expected}, Got: {e})\n"

        result_feedback += f"\nFinal Score: {score}/{total}"

        return result_feedback


# Flask app for Vercel
app = Flask(__name__)

# Telegram bot token and webhook URL
telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
webhook_url = os.getenv('WEBHOOK_URL')  # Example: https://your-vercel-deployment-url.com/webhook

bot = telegram.Bot(token=telegram_bot_token)

# Firebase initialization
fb_credentials = json.loads(os.getenv('FIREBASE_DB_CONVERSATIONS'))
fb_credentials2 = json.loads(os.getenv('FIREBASE_DB_ASSIGNMENTS'))

if "conversations" not in firebase_admin._apps:
    credentials_object_conversations = credentials.Certificate(fb_credentials)
    initialize_app(credentials_object_conversations, {
        'databaseURL': 'https://urop-telegram-chatbot-default-rtdb.asia-southeast1.firebasedatabase.app/'
    }, name='conversations')

if "assignments" not in firebase_admin._apps:
    credentials_object_assignments = credentials.Certificate(fb_credentials2)
    initialize_app(credentials_object_assignments, {
        'databaseURL': 'https://urop-chatbot-assignments-default-rtdb.asia-southeast1.firebasedatabase.app/'
    }, name='assignments')

reference_to_database_conversations = db.reference('/', app=firebase_admin.get_app('conversations'))
reference_to_database_assignments = db.reference('/', app=firebase_admin.get_app('assignments'))

# States for conversation handler
ASK_STUDENTID, ASK_ASSIGNMENT, ASK_CODE_SUBMISSION = range(3)
CONVERSATION_INFORMATION = {}

# Handlers
def handle_start_command(update: Update, context: CallbackContext):
    username = update.message.from_user.username or update.message.from_user.first_name
    CONVERSATION_INFORMATION.clear()
    update.message.reply_text(f"Hello {username}, please enter your student ID.")
    return ASK_STUDENTID

def handle_ask_studentid(update: Update, context: CallbackContext):
    student_id = update.message.text
    CONVERSATION_INFORMATION['student_id'] = student_id
    assignments = reference_to_database_assignments.get()
    keyboard = [[telegram.KeyboardButton(assignment['assignment_name'])] for assignment in assignments.values()]
    update.message.reply_text("Which assignment would you like to submit?", reply_markup=telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return ASK_ASSIGNMENT

def handle_ask_assignment(update: Update, context: CallbackContext):
    assignment = update.message.text
    CONVERSATION_INFORMATION['assignment'] = assignment
    assignment_notes = next((a['assignment_notes'] for a in reference_to_database_assignments.get().values() if a['assignment_name'] == assignment), "No notes found.")
    update.message.reply_text(f"Assignment details: {assignment_notes}\nPlease submit your code.")
    return ASK_CODE_SUBMISSION

def handle_ask_code_submission(update: Update, context: CallbackContext):
    code = update.message.text
    CONVERSATION_INFORMATION['code_submitted'] = code
    update.message.reply_text(f"Code received. Student ID: {CONVERSATION_INFORMATION['student_id']}, Assignment: {CONVERSATION_INFORMATION['assignment']}")
    reference_to_database_conversations.push(CONVERSATION_INFORMATION)
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Conversation canceled.")
    return ConversationHandler.END

# Flask endpoint to handle Telegram webhook
@app.route('/webhook', methods=['POST'])
def webhook_handler():
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
    return jsonify({"status": "ok"})

# Telegram dispatcher setup
dispatcher = telegram.ext.Dispatcher(bot, None, workers=0)

conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('start', handle_start_command)],
    states={
        ASK_STUDENTID: [MessageHandler(Filters.text & ~Filters.command, handle_ask_studentid)],
        ASK_ASSIGNMENT: [MessageHandler(Filters.text & ~Filters.command, handle_ask_assignment)],
        ASK_CODE_SUBMISSION: [MessageHandler(Filters.text & ~Filters.command, handle_ask_code_submission)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

dispatcher.add_handler(conversation_handler)

# Set webhook on startup
@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    bot.set_webhook(url=f"{webhook_url}/webhook")
    return jsonify({"status": "webhook set", "url": webhook_url})
