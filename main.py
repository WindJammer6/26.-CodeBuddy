import telegram
import telegram.ext
import json
import requests
import time
from firebase_admin import db
import firebase_admin
import datetime


# Initiating Chatbase stuffs
url = 'https://www.chatbase.co/api/v1/chat'

headers = {
    'Authorization': 'Bearer 3c7b798b-c5fe-41a7-bdeb-f5d0b6f8536e',
    'Content-Type': 'application/json'
}

conversation_history_and_other_data = {
    "messages": [],
    "chatbotId": "7d1-P8B5N9cnZdXkxOwFB",
    "stream": False,
    "temperature": 0
}


# Initiating multiple Firebase Realtime Database/projects in the same Python file

# Setting up the Firebase database for the conversations:
if "conversations" not in firebase_admin._apps:
    # Initialize Firebase
    credentials_object_conversations = firebase_admin.credentials.Certificate("firebase_key_conversations.json")
    firebase_admin.initialize_app(credentials_object_conversations, {
        'databaseURL': 'https://urop-telegram-chatbot-default-rtdb.asia-southeast1.firebasedatabase.app/'
    }, name='conversations')

# Get a reference to the database
reference_to_database_conversations = db.reference('/', app=firebase_admin.get_app('conversations'))



# Setting up the Firebase database for the assignments:   
if "assignments" not in firebase_admin._apps:
    # Initialize Firebase
    credentials_object_assignments = firebase_admin.credentials.Certificate("firebase_key_assignments.json")
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


def handle_start_command_python_function(update, context):
    print("Start command received")  # Add this line to verify if the command is being received
    
    # Reset the conversation information
    CONVERSATION_INFORMATION.clear()

    # Sending an image of a Telegram Chatbot teaching assistant
    image = requests.get('https://static05.cminds.com/wp-content/uploads/WP_Telegram_Bot_Plugin_Illustravive_Banner-1024x300.jpg').content
    update.message.reply_media_group(media=[telegram.InputMediaPhoto(image, caption="""👋 Hello there! Welcome to your friendly Teaching Assistant Telegram Bot, powered by the magic of Retrieval-Augmented Generation (RAG) by Snowflake Cortex Search and Mistral LLM! ❄️\n\nYou're now connected with the Teaching Assistant for First Beginner Programming Course! 🎓📘\n(Psst... Just so you know, this conversation will be recorded for your instructors to help improve your learning!)\n\nFirst things first, could you kindly enter your student ID so we can get started? 📝""")])
    
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
                              Nice to meet you, student ID: {CONVERSATION_INFORMATION['student_id']}!\n\nNow, let's get down to business. Which assignment would you like to submit today? 📋"
                              """
                              , reply_markup=telegram.ReplyKeyboardMarkup(keyboard_buttons, one_time_keyboard=True))
    
    return ASK_ASSIGNMENT


# Asking of the assignment information
def handle_ask_assignment_messages_python_function(update, context):
    assignment = update.message.text
    CONVERSATION_INFORMATION['assignment'] = assignment
    print(CONVERSATION_INFORMATION)
    
    inline_keyboard_buttons = [[telegram.InlineKeyboardButton("Proceed to code submission", callback_data="proceed_to_code_submission")]]

    # To extract the assignment link for the extracted assignment name in the 'list_of_assignments' list
    extracted_assignment_link = None

    for assignment in database_data_assignments:
        if assignment['assignment_name'] == CONVERSATION_INFORMATION['assignment']:
            extracted_assignment_link = assignment['assignment_link']

    update.message.reply_text(f"""
                               📝 You picked {CONVERSATION_INFORMATION['assignment']}.\n\nHere’s everything you need to know about this assignment: {extracted_assignment_link}\n\nReady to proceed? Let me know what you’d like to do next:\n\n\nIf you'd like to submit for another assignment, feel free to restart with the /start command anytime! I’m here whenever you need me! 😁🤖
                               """
                               , reply_markup=telegram.InlineKeyboardMarkup(inline_keyboard_buttons, one_time_keyboard=True))

    return ASK_CODE_SUBMISSION


# Confirmation of all 3 information (student id, assignment and code submitted) before submission
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
                                🎉 Thanks for sharing your code! Here's a quick recap of everything you've provided:\n\n📌 Student ID: {CONVERSATION_INFORMATION['student_id']}\n📌 Assignment: {CONVERSATION_INFORMATION['assignment']}\n📌 Code:\n<pre><code>{CONVERSATION_INFORMATION['code_submitted']}</code></pre>\n\nLooking good? Ready to submit it for evaluation? 😄
                                """, reply_markup=telegram.InlineKeyboardMarkup(inline_keyboard_buttons, one_time_keyboard=True), parse_mode="HTML")


# Displaying response 
def telegram_chatbot_response_to_code_submission_python_function(update, context):
    # Appending the user message/prompt to the 'conversation_history_and_other_data' before making the API call
    conversation_history_and_other_data["messages"].append({"content": update.message.text, "role": "user"})

    # Generating the response to the user message/prompt when making the API call
    response = requests.post(url, headers=headers, data=json.dumps(conversation_history_and_other_data))
    json_data = response.json()

    # If there is no error generating response
    if response.status_code == 200:
        # Appending the generated response to the 'conversation_history_and_other_data' 
        conversation_history_and_other_data["messages"].append({"content": json_data['text'], "role": "assistant"})
        print(f'Hello {conversation_history_and_other_data}')

        update.message.reply_text("""
                                  ⏳ Give me a second while I work my magic and analyze your submission… 🙏 
                                  """)
        time.sleep(3)
        update.message.reply_text(f"""
                                  🎉 All done! Here’s the feedback for your submission to {CONVERSATION_INFORMATION['assignment']}.<pre><code>{json_data['text']}</code></pre>(Your submission has been recorded)""", parse_mode="HTML")     
        
        inline_keyboard_buttons = [[telegram.InlineKeyboardButton("Restart", callback_data="restart")]]
        update.message.reply_text(f"""
                                  If you'd like to submit for another assignment, feel free to click restart! I’m here whenever you need me! 😁🤖
                                  """, reply_markup=telegram.InlineKeyboardMarkup(inline_keyboard_buttons, one_time_keyboard=True))     
        

        # ////////////////////////////////////////////////////////////////////////////////////////////////////////
        

        # Telegram Chatbot to Firebase's Realtime Database things

        # Adding response to each submission into each submission data
        CONVERSATION_INFORMATION['telegram_chatbot_chatbase_response'] = f"```\n{json_data['text']}\n```"
        print(CONVERSATION_INFORMATION)


        # Adding date and time information of the submission to each submission data
        date_and_time_of_submission = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        CONVERSATION_INFORMATION['date_and_time_of_submission'] = date_and_time_of_submission
        print(CONVERSATION_INFORMATION)


        # Once the code is submitted by the user, the Telegram Chatbot will 'push' basically add these new pieces of user data 
        # into the Realtime database in Firebase
        reference_to_database_conversations.push(CONVERSATION_INFORMATION)    


        # ////////////////////////////////////////////////////////////////////////////////////////////////////////
        

    # If there is an error when generating the response for some reason
    else:
        print(f"Error: {json_data}")
        update.message.reply_text(f"CodeBuddy Bot: Oh no! You encountered an error in the code! The error is: \n'{json_data['message']}'")
        
    
    return telegram.ext.ConversationHandler.END


# Handling callback queries from the Inline Keyboard Buttons
def handle_callback_queries(update, context):
    callback_query = update.callback_query
    callback_query.answer()

    # Handling assignment selection callback
    if callback_query.data == 'proceed_to_code_submission':
        callback_query.message.reply_text("Awesome! 🛠️ Time to get those gears turning. Please go ahead and send me your working code when you're ready.\nI’m excited to see what you've got! 🚀💡")
        return ASK_CODE_SUBMISSION

    # Handling code submission callback
    elif callback_query.data == 'submit_code':
        return telegram_chatbot_response_to_code_submission_python_function(callback_query, context)

    # Handling restart submission callback
    elif callback_query.data == 'restart':
        handle_start_command_python_function(callback_query, context)
        return ASK_STUDENTID

# Cancel function here to map to the cancel command as per required by the telegram Python library's 
# 'ConversationHandler' class instance/object 
def cancel(update, context):
    update.message.reply_text(
        'Conversation cancelled.',
        reply_markup=telegram.ReplyKeyboardRemove()
    )
    return telegram.ext.ConversationHandler.END


# Initiate the Telegram Chatbot
token_of_telegram_bot = "7665259187:AAHg986wLOXoMKDJStpTMV0LEME6thvQ-ZA"
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


# Start the Telegram Chatbot
updater.start_polling()

# The 'check_for_new_data()' self-made function (see above)
check_for_new_data(updater)

updater.idle()
