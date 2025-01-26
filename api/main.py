import telegram
import telegram.ext
import json
import requests
import time
from firebase_admin import db
import firebase_admin
import datetime
from html import escape
from mistralai import Mistral
import os

from autograder import AutoGrader

# Flask app for Vercel
app = Flask(__name__)

# Setting up the '/webhook' route 
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        # Process the incoming request
        update = telegram.Update.de_json(request.get_json(), bot)
        bot.process_new_updates([update])
        return 'OK'
        

# Initiating Mistral LLM stuffs
mistralai_api_key = 'mYh9wxRXIpuinbnH6jdBwZZ9Dzxx2KEo'
model = "mistral-large-latest"

client = Mistral(api_key=mistralai_api_key)

# conversation_history_and_other_data = client.chat.complete(
#     model= model,
#     messages = [
#         {
#             "role": "user",
#             "content": "placeholder message",
#         },
#     ]
# )
# print(conversation_history_and_other_data.choices[0].message.content)


# Initiating Chatbase stuffs
# url = 'https://www.chatbase.co/api/v1/chat'

# headers = {
#     'Authorization': 'Bearer 3c7b798b-c5fe-41a7-bdeb-f5d0b6f8536e',
#     'Content-Type': 'application/json'
# }

# conversation_history_and_other_data = {
#     "messages": [],
#     "chatbotId": "7d1-P8B5N9cnZdXkxOwFB",
#     "stream": False,
#     "temperature": 0
# }


# Initiating multiple Firebase Realtime Database/projects in the same Python file

# Setting up the Firebase database for the conversations:
fb_credentials = json.loads(os.getenv('FIREBASE_DB_CONVERSATIONS'))

if "conversations" not in firebase_admin._apps:
    # Initialize Firebase
    credentials_object_conversations = firebase_admin.credentials.Certificate(fb_credentials)
    firebase_admin.initialize_app(credentials_object_conversations, {
        'databaseURL': 'https://urop-telegram-chatbot-default-rtdb.asia-southeast1.firebasedatabase.app/'
    }, name='conversations')

# Get a reference to the database
reference_to_database_conversations = db.reference('/', app=firebase_admin.get_app('conversations'))



# Setting up the Firebase database for the assignments:   
fb_credentials2 = json.loads(os.getenv('FIREBASE_DB_ASSIGNMENTS'))

if "assignments" not in firebase_admin._apps:
    # Initialize Firebase
    credentials_object_assignments = firebase_admin.credentials.Certificate(fb_credentials2)
    firebase_admin.initialize_app(credentials_object_assignments, {
        'databaseURL': 'https://urop-chatbot-assignments-default-rtdb.asia-southeast1.firebasedatabase.app/'
    }, name='assignments')

# Get a reference to the database
reference_to_database_assignments = db.reference('/', app=firebase_admin.get_app('assignments'))


# Firebase's Database for conversations to Streamlit website things:
# Compiling the list of available assignments from the Streamlit (Python) website to Keyboard buttons in the
# Telegram Chatbot 

# Read data from the Realtime Database from Firebase
database_data_assignments = reference_to_database_assignments.get()
# print("Firebase UROP Telegram Chatbot assignments Realtime Database Data:", database_data_assignments)

list_of_assignments = []

# Check if the Firebase Realtime database is None or empty
if database_data_assignments is None:
    print("No data found in the Firebase Realtime Database.")
else:
    # Converting the Firebase Realtime Database to a list of dictionaries
    if isinstance(database_data_assignments, dict):
        database_data_assignments = list(database_data_assignments.values())

        print(database_data_assignments)

    for i in range(len(database_data_assignments)):
        list_of_assignments.append(f"{database_data_assignments[i]['assignment_name']}")


# ////////////////////////////////////////////////////////////////////////////////////


def get_firebase_data():
    # Firebase's Database for conversations to Streamlit website things:
    # Compiling the list of available assignments from the Streamlit (Python) website to Keyboard buttons in the
    # Telegram Chatbot 

    # Read data from the Realtime Database from Firebase
    database_data_assignments = reference_to_database_assignments.get()
    # print("Firebase UROP Telegram Chatbot assignments Realtime Database Data:", database_data_assignments)

    list_of_assignments = []

    # Check if the Firebase Realtime database is None or empty
    if database_data_assignments is None:
        print("No data found in the Firebase Realtime Database.")
    else:
        # Converting the Firebase Realtime Database to a list of dictionaries
        if isinstance(database_data_assignments, dict):
            database_data_assignments = list(database_data_assignments.values())

            print(database_data_assignments)

        for i in range(len(database_data_assignments)):
            list_of_assignments.append(f"{database_data_assignments[i]['assignment_name']}")

    return list_of_assignments


def build_keyboard(list_of_assignments):
    keyboard_buttons = []
    if list_of_assignments is not None:
        keyboard_buttons = []
        
        for i in list_of_assignments:
            keyboard_buttons.append([telegram.KeyboardButton(i)])

    return telegram.ReplyKeyboardMarkup(keyboard_buttons)


def check_for_new_data(updater):
    old_data = get_firebase_data()

    while True:
        time.sleep(10)  # Poll Firebase every 10 seconds
        new_data = get_firebase_data()

        if new_data != old_data:
            # Update the buttons if new data is found
            for chat_id in updater.dispatcher.chat_data:
                keyboard = build_keyboard(new_data)
                updater.bot.send_message(chat_id=chat_id, text="Oops! There is an update to the assignments available from your course instructor!", reply_markup=keyboard)
            
            old_data = new_data  # Update old_data to the new state
            print(old_data)


# ////////////////////////////////////////////////////////////////////////////////////


# Defining the states for the conversation with the Telegram Chatbot
ASK_STUDENTID, ASK_ASSIGNMENT, ASK_CODE_SUBMISSION = range(3)

# Storing the information received from the student during the conversation, it should contain the
# 3 rquired information, student ID, selected assignment, and code to be submitted
CONVERSATION_INFORMATION = {} 

username = 'placeholder'
user_id = 'placeholder'

def handle_start_command_python_function(update, context):
    print("Start command received")  # Add this line to verify if the command is being received

    global username
    global user_id
    username = update.message.from_user.username or update.message.from_user.first_name
    user_id = update.message.from_user.id
    
    # Clear conversation information (if applicable)
    CONVERSATION_INFORMATION.clear()

    # Send the response with MarkdownV2
    message = f"""Hello [@{username}](tg://user?id={user_id})\!\nI am CodeBuddy\, your friendly teaching assistant for your programming course\, powered by the magic of Retrieval\-Augmented Generation \(RAG\) by Snowflake Cortex Search and Mistral LLM\! ❄️ \n\nTo begin\, please enter your student ID\."""

    update.message.reply_text(
        message,
        parse_mode="MarkdownV2"
    )
    
    return ASK_STUDENTID

def handle_restart_python_function(update, context):
    print("Start command received")  # Add this line to verify if the command is being received

    global username
    global user_id

    # Clear conversation information (if applicable)
    CONVERSATION_INFORMATION.clear()

    # Send the response with MarkdownV2
    message = f"""Hello [@{username}](tg://user?id={user_id})\!\nI am CodeBuddy\, your friendly teaching assistant for your programming course\, powered by the magic of Retrieval\-Augmented Generation \(RAG\) by Snowflake Cortex Search and Mistral LLM\! ❄️ \n\nTo begin\, please enter your student ID\."""

    update.message.reply_text(
        message,
        parse_mode="MarkdownV2"
    )
    
    return ASK_STUDENTID


# Start command + Asking of the student id information
def handle_ask_studentid_messages_python_function(update, context):
    student_id = update.message.text

    # Very sketchy code
    if 'code_submitted' in CONVERSATION_INFORMATION:
        value = CONVERSATION_INFORMATION['code_submitted']
        CONVERSATION_INFORMATION.clear()
        CONVERSATION_INFORMATION['student_id'] = value
        print(CONVERSATION_INFORMATION)
    else:
        CONVERSATION_INFORMATION['student_id'] = student_id
        print(CONVERSATION_INFORMATION)
    

    # ////////////////////////////////////////////////////////////////////////////////////////////////////////


    # Firebase's Database for conversations to Streamlit website things

    # Compiling the list of available assignments from the Streamlit (Python) website to Keyboard buttons in the
    # Telegram Chatbot (see above to see how the 'list_of_assignments' variable is derived)
    if list_of_assignments is not None:
        keyboard_buttons = []
        
        for i in list_of_assignments:
            keyboard_buttons.append([telegram.KeyboardButton(i)])

    update.message.reply_text(f"""
                              Which assignment would you like to submit?
                              """
                              , reply_markup=telegram.ReplyKeyboardMarkup(keyboard_buttons, one_time_keyboard=True))
    
    return ASK_ASSIGNMENT

########################################
# Asking of the assignment information #
########################################
def handle_ask_assignment_messages_python_function(update, context):
    assignment = update.message.text
    CONVERSATION_INFORMATION['assignment'] = assignment
    print(CONVERSATION_INFORMATION)
    
    inline_keyboard_buttons = [[telegram.InlineKeyboardButton("Proceed to code submission", callback_data="proceed_to_code_submission")]]

    # To extract the assignment link for the extracted assignment name in the 'list_of_assignments' list
    extracted_assignment_notes = None

    for assignment in database_data_assignments:
        if assignment['assignment_name'] == CONVERSATION_INFORMATION['assignment']:
            extracted_assignment_notes = assignment['assignment_notes']

    update.message.reply_text(f"""                               
                               To refresh your memory, here is the question for {CONVERSATION_INFORMATION['assignment']}:\n<pre><code>{extracted_assignment_notes}</code></pre>
                               """
                               , parse_mode="HTML", reply_markup=telegram.InlineKeyboardMarkup(inline_keyboard_buttons, one_time_keyboard=True))

    return ASK_CODE_SUBMISSION

###################################################################################################
# Confirmation of all 3 information (student id, assignment and code submitted) before submission #
###################################################################################################
def handle_ask_code_submission_messages_python_function(update, context):
    code_submitted = update.message.text  
    CONVERSATION_INFORMATION['code_submitted'] = code_submitted
    print(CONVERSATION_INFORMATION)

    # Very sketchy code
    if 'student_id' not in CONVERSATION_INFORMATION:
        return handle_ask_studentid_messages_python_function(update, context)
    else:
        inline_keyboard_buttons = [[telegram.InlineKeyboardButton("Submit code", callback_data="submit_code")], [telegram.InlineKeyboardButton("Restart", callback_data="restart")]]

        update.message.reply_text(f"""
                                   Code received! Please confirm your submission:\n- Student ID: {CONVERSATION_INFORMATION['student_id']}\n- Assignment: {CONVERSATION_INFORMATION['assignment']}\n- Submitted Code:\n<pre><code>{CONVERSATION_INFORMATION['code_submitted']}</code></pre>
                                   """, reply_markup=telegram.InlineKeyboardMarkup(inline_keyboard_buttons, one_time_keyboard=True), parse_mode="HTML")

#######################
# Displaying response #
#######################
def telegram_chatbot_response_to_code_submission_python_function(update, context):

    ################################
    # Generate Chatbase's response #
    ################################
    conversation_history_and_other_data = client.chat.complete(
        model= model,
        messages = [
            {
                "role": "user",
                "content": f"{update.message.text}",
            },
        ]
    )
    # Appending the user message/prompt to the 'conversation_history_and_other_data' before making the API call
    # conversation_history_and_other_data.append({"content": update.message.text, "role": "user"})

    # Generating the response to the user message/prompt when making the API call
    json_data = conversation_history_and_other_data.choices[0].message.content

    # Appending the generated response to the 'conversation_history_and_other_data' 
    # conversation_history_and_other_data.append({"content": json_data['text'], "role": "assistant"})

    inline_keyboard_buttons = [[telegram.InlineKeyboardButton("Restart", callback_data="restart")]]

    safe_text = escape(json_data)

    update.message.reply_text(f"""
                                Here’s my feedback for your submission to {CONVERSATION_INFORMATION['assignment']}.<pre><code>{safe_text}</code></pre>(Your submission has been recorded into the Streamlit website: https://27-codebuddy-app-website-epgyqtybxho9kbdcussvyt.streamlit.app/ which is only accessible by your course instructors)
                                """, parse_mode="HTML")    

    ###############
    # Autograding #
    ###############
    grader = AutoGrader()

    test_cases_for_assignment = None
    for assignment in database_data_assignments:
        if assignment['assignment_name'] == CONVERSATION_INFORMATION['assignment']:
            test_cases_for_assignment = assignment['test_cases']

    print(f'These are the test cases: {test_cases_for_assignment}')
    print(f"This is the code submitted: {CONVERSATION_INFORMATION['code_submitted']}")
    
    results = grader.run_test_cases(test_cases_for_assignment, CONVERSATION_INFORMATION['code_submitted'])
    CONVERSATION_INFORMATION['scores'] = results

    update.message.reply_text(f"""
                                <pre><code>{results}</code></pre>
                                """, parse_mode="HTML", reply_markup=telegram.InlineKeyboardMarkup(inline_keyboard_buttons, one_time_keyboard=True))    


    # ////////////////////////////////////////////////////////////////////////////////////////////////////////
    

    # Telegram Chatbot to Firebase's Realtime Database things

    # Adding response to each submission into each submission data
    # CONVERSATION_INFORMATION['telegram_chatbot_chatbase_response'] = f"```\n{json_data['text']}\n```"
    CONVERSATION_INFORMATION['telegram_chatbot_chatbase_response'] = f"```\n{json_data}\n```"
    print(CONVERSATION_INFORMATION)


    # Adding date and time information of the submission to each submission data
    date_and_time_of_submission = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    CONVERSATION_INFORMATION['date_and_time_of_submission'] = date_and_time_of_submission
    print(CONVERSATION_INFORMATION)


    # Once the code is submitted by the user, the Telegram Chatbot will 'push' basically add these new pieces of user data 
    # into the Realtime database in Firebase
    reference_to_database_conversations.push(CONVERSATION_INFORMATION)    

    return telegram.ext.ConversationHandler.END

##############################################################
# Handling callback queries from the Inline Keyboard Buttons #
##############################################################
def handle_callback_queries(update, context):
    callback_query = update.callback_query
    callback_query.answer()

    # Handling assignment selection callback
    if callback_query.data == 'proceed_to_code_submission':
        callback_query.message.reply_text("Please go ahead and send me your working code when you're ready!\n(Just simply copy and paste your code directly from your IDE 📋)")
        return ASK_CODE_SUBMISSION

    # Handling code submission callback
    elif callback_query.data == 'submit_code':
        return telegram_chatbot_response_to_code_submission_python_function(callback_query, context)

    # Handling restart submission callback
    elif callback_query.data == 'restart':
        handle_restart_python_function(callback_query, context)
        return ASK_STUDENTID

# Cancel function here to map to the cancel command as per required by the telegram Python library's 
# 'ConversationHandler' class instance/object 
def cancel(update, context):
    update.message.reply_text(
        'Conversation cancelled.',
        reply_markup=telegram.ReplyKeyboardRemove()
    )
    return telegram.ext.ConversationHandler.END

# Flask endpoint to handle Telegram webhook
@app.route('/webhook', methods=['POST'])
def webhook_handler():
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
    return jsonify({"status": "ok"})

# Telegram dispatcher setup
dispatcher = telegram.ext.Dispatcher(bot, None, workers=0)

# Initiate the Telegram Chatbot
telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
updater = telegram.ext.Updater(token_of_telegram_bot, use_context=True)
dispatcher = updater.dispatcher

# Handlers
conversation_handler = telegram.ext.ConversationHandler(
    entry_points=[telegram.ext.CommandHandler('start', handle_start_command_python_function)],
    states={
        ASK_STUDENTID: [telegram.ext.MessageHandler(telegram.ext.Filters.text, handle_ask_studentid_messages_python_function)],
        ASK_ASSIGNMENT: [telegram.ext.MessageHandler(telegram.ext.Filters.text, handle_ask_assignment_messages_python_function)],
        ASK_CODE_SUBMISSION: [telegram.ext.MessageHandler(telegram.ext.Filters.text, handle_ask_code_submission_messages_python_function)]
    },
    fallbacks=[telegram.ext.CommandHandler('cancel', cancel)]
)

dispatcher.add_handler(conversation_handler)
dispatcher.add_handler(telegram.ext.CallbackQueryHandler(handle_callback_queries))

# Set webhook on startup
@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    bot.set_webhook(url=f"{webhook_url}/webhook")
    return jsonify({"status": "webhook set", "url": webhook_url})
