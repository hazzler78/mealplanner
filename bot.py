import logging
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, MenuButtonWebApp, WebAppInfo, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
import random  # For dummy suggestions; replace with API calls
from collections import defaultdict  # For aggregating groceries
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get bot token from environment variable
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# Get WebApp URL from environment variable (e.g., your Vercel deployment URL)
# Strip trailing slash if present
WEBAPP_URL = os.getenv('TELEGRAM_WEBAPP_URL', '').rstrip('/')



# Set up logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)



# New: Diet-specific meal pools for filtering and variety

MEALS = {

    'Vegan': {

        'breakfast': ['Oatmeal with fruits', 'Avocado toast', 'Smoothie bowl'],  # Assuming plant-based yogurt

        'lunch': ['Veggie stir-fry', 'Quinoa bowl'],

        'dinner': ['Pasta primavera', 'Tofu curry']

    },

    'Keto': {

        'breakfast': ['Avocado toast'],  # Low-carb version

        'lunch': ['Grilled chicken salad'],

        'dinner': ['Baked salmon']

    },

    'No restrictions': {

        'breakfast': ['Oatmeal with fruits', 'Avocado toast', 'Smoothie bowl'],

        'lunch': ['Grilled chicken salad', 'Veggie stir-fry', 'Quinoa bowl'],

        'dinner': ['Baked salmon', 'Pasta primavera', 'Tofu curry']

    }

}



# Ingredient mapping (unchanged; expand as needed)

INGREDIENTS = {

    'Oatmeal with fruits': [('Oats', 1, 'cup'), ('Banana', 1, ''), ('Apple', 1, '')],

    'Avocado toast': [('Bread', 2, 'slices'), ('Avocado', 1, ''), ('Tomato', 1, '')],

    'Smoothie bowl': [('Yogurt', 1, 'cup'), ('Berries', 0.5, 'cup'), ('Banana', 1, '')],

    'Grilled chicken salad': [('Chicken', 200, 'g'), ('Lettuce', 1, 'head'), ('Tomato', 2, '')],

    'Veggie stir-fry': [('Broccoli', 1, 'cup'), ('Carrot', 2, ''), ('Bell pepper', 1, '')],

    'Quinoa bowl': [('Quinoa', 1, 'cup'), ('Avocado', 1, ''), ('Beans', 0.5, 'can')],

    'Baked salmon': [('Salmon', 200, 'g'), ('Lemon', 1, ''), ('Herbs', 1, 'tbsp')],

    'Pasta primavera': [('Pasta', 200, 'g'), ('Zucchini', 1, ''), ('Tomato', 2, '')],

    'Tofu curry': [('Tofu', 200, 'g'), ('Coconut milk', 1, 'can'), ('Curry powder', 2, 'tsp')]

}



async def start(update: Update, context: CallbackContext) -> None:

    keyboard = [

        [KeyboardButton("Vegan"), KeyboardButton("Keto")],

        [KeyboardButton("No restrictions")]

    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text('Welcome to MealPlannerBot! What\'s your diet preference?', reply_markup=reply_markup)



def get_random_meal(meal_list: list, default_message: str) -> str:
    """Helper function to get a random meal from a list."""
    if not meal_list:
        return default_message
    return random.choice(meal_list)


async def handle_preference(update: Update, context: CallbackContext) -> None:
    preference = update.message.text
    context.user_data['preference'] = preference
    
    # Get diet-specific meals (default to 'No restrictions' if invalid)
    meal_pools = MEALS.get(preference, MEALS['No restrictions'])
    
    # For daily: Simple random choice (variety not critical for one day)
    breakfast = get_random_meal(meal_pools['breakfast'], "No breakfast options available")
    lunch = get_random_meal(meal_pools['lunch'], "No lunch options available")
    dinner = get_random_meal(meal_pools['dinner'], "No dinner options available")
    
    context.user_data['daily_plan'] = [breakfast, lunch, dinner]
    
    plan = f"Daily Meal Plan for {preference}:\n"
    plan += f"Breakfast: {breakfast}\n"
    plan += f"Lunch: {lunch}\n"
    plan += f"Dinner: {dinner}\n"
    plan += "\nUse /grocery_list to get your shopping list! Or /plan_week for a full week."
    
    await update.message.reply_text(plan)



async def plan_week(update: Update, context: CallbackContext) -> None:

    if 'preference' not in context.user_data:

        await update.message.reply_text("Select a preference first with /start!")

        return

    

    preference = context.user_data['preference']

    meal_pools = MEALS.get(preference, MEALS['No restrictions'])

    

    # New: Shuffle options for each category to enable variety

    breakfast_options = meal_pools['breakfast'][:]

    random.shuffle(breakfast_options)

    lunch_options = meal_pools['lunch'][:]

    random.shuffle(lunch_options)

    dinner_options = meal_pools['dinner'][:]

    random.shuffle(dinner_options)

    

    weekly_plan = []

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    

    plan_text = f"Weekly Meal Plan for {preference}:\n\n"

    for i, day in enumerate(days):
        # Cycle through shuffled options for variety (avoids consecutive repeats where possible)
        breakfast = breakfast_options[i % len(breakfast_options)] if breakfast_options else "No breakfast options"
        lunch = lunch_options[i % len(lunch_options)] if lunch_options else "No lunch options"
        dinner = dinner_options[i % len(dinner_options)] if dinner_options else "No dinner options"
        daily_meals = [breakfast, lunch, dinner]
        weekly_plan.append(daily_meals)
        
        plan_text += f"{day}:\n"
        plan_text += f"  Breakfast: {breakfast}\n"
        plan_text += f"  Lunch: {lunch}\n"
        plan_text += f"  Dinner: {dinner}\n\n"

    

    context.user_data['weekly_plan'] = weekly_plan

    

    plan_text += "Use /grocery_list for the full weekly shopping list!"

    await update.message.reply_text(plan_text)



async def grocery_list(update: Update, context: CallbackContext) -> None:

    if 'weekly_plan' in context.user_data:

        all_meals = [meal for day in context.user_data['weekly_plan'] for meal in day]  # Flatten weekly

        scope = "Weekly"

    elif 'daily_plan' in context.user_data:

        all_meals = context.user_data['daily_plan']

        scope = "Daily"

    else:

        await update.message.reply_text("Generate a meal plan first with /start or /plan_week!")

        return

    

    aggregated = defaultdict(lambda: defaultdict(float))  # Group by item, sum quantities per unit

    

    for meal in all_meals:

        if meal in INGREDIENTS:

            for item, qty, unit in INGREDIENTS[meal]:

                aggregated[item][unit] += qty

    

    # Format the list

    grocery_text = f"Your {scope} Grocery List:\n"

    for item, units in aggregated.items():

        for unit, total_qty in units.items():

            unit_str = f" {unit}" if unit else ""

            qty_str = int(total_qty) if total_qty.is_integer() else total_qty

            grocery_text += f"- {item}: {qty_str}{unit_str}\n"

    

    await update.message.reply_text(grocery_text)



async def set_menu_button(bot) -> bool:
    """Helper function to set the menu button."""
    if not WEBAPP_URL:
        logging.warning("TELEGRAM_WEBAPP_URL not set. Menu button will not be configured.")
        return False
    
    try:
        menu_button = MenuButtonWebApp(
            text="Open Meal Planner",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
        # Set menu button for the bot (chat_id=None sets default menu button)
        await bot.set_chat_menu_button(chat_id=None, menu_button=menu_button)
        logging.info(f"Menu button set successfully with URL: {WEBAPP_URL}")
        return True
    except Exception as e:
        logging.error(f"Failed to set menu button: {e}")
        logging.error(f"Error type: {type(e).__name__}")
        import traceback
        logging.error(traceback.format_exc())
        return False


async def post_init(application) -> None:
    """Set up the menu button and register commands after bot initialization."""
    # Register bot commands with Telegram
    commands = [
        BotCommand("start", "Start the bot and select diet preference"),
        BotCommand("plan_week", "Generate a weekly meal plan"),
        BotCommand("grocery_list", "Get your shopping list"),
        BotCommand("help", "Show available commands"),
    ]
    try:
        await application.bot.set_my_commands(commands)
        logging.info("Bot commands registered successfully")
    except Exception as e:
        logging.warning(f"Failed to register commands: {e}")
    
    # Set up menu button
    await set_menu_button(application.bot)


async def help_command(update: Update, context: CallbackContext) -> None:
    """Show available commands."""
    help_text = (
        "🤖 <b>Meal Planner Bot Commands:</b>\n\n"
        "/start - Start the bot and select your diet preference\n"
        "/plan_week - Generate a weekly meal plan\n"
        "/grocery_list - Get your shopping list\n"
        "/help - Show this help message\n\n"
        "💡 <b>Tip:</b> Use the menu button in the bot profile to open the WebApp!"
    )
    await update.message.reply_text(help_text, parse_mode='HTML')


async def checkmenu(update: Update, context: CallbackContext) -> None:
    """Command to check current menu button status."""
    try:
        current_button = await context.bot.get_chat_menu_button(chat_id=None)
        button_info = f"Type: {type(current_button).__name__}\n"
        if hasattr(current_button, 'text'):
            button_info += f"Text: {current_button.text}\n"
        if hasattr(current_button, 'web_app') and current_button.web_app:
            button_info += f"WebApp URL: {current_button.web_app.url}\n"
        await update.message.reply_text(f"Current menu button:\n{button_info}")
    except Exception as e:
        await update.message.reply_text(f"Error checking menu button: {e}\n\nType: {type(e).__name__}")


async def setmenu(update: Update, context: CallbackContext) -> None:
    """Command to manually set the menu button (for testing)."""
    if update.effective_user.id != update.effective_chat.id:
        await update.message.reply_text("This command can only be used in private chat.")
        return
    
    if not WEBAPP_URL:
        await update.message.reply_text(
            f"❌ TELEGRAM_WEBAPP_URL is not set!\n\n"
            f"Please set it in your .env file:\n"
            f"TELEGRAM_WEBAPP_URL=https://mealplanner-wheat.vercel.app"
        )
        return
    
    await update.message.reply_text(f"Setting menu button with URL: {WEBAPP_URL}\n\nPlease wait...")
    success = await set_menu_button(context.bot)
    if success:
        await update.message.reply_text(
            f"✅ Menu button API call succeeded!\n\n"
            f"URL: {WEBAPP_URL}\n\n"
            f"⚠️ IMPORTANT: If you still don't see the button:\n"
            f"1. The WebApp must be registered with BotFather first\n"
            f"2. Send /newapp to @BotFather and register your WebApp\n"
            f"3. Then try /setmenu again\n\n"
            f"Or set it manually:\n"
            f"1. Go to @BotFather\n"
            f"2. Send /mybots\n"
            f"3. Select your bot\n"
            f"4. Choose 'Bot Settings' → 'Menu Button'\n"
            f"5. Set URL to: {WEBAPP_URL}"
        )
    else:
        await update.message.reply_text(
            f"❌ Failed to set menu button. Check bot logs for details.\n\n"
            f"Current URL: {WEBAPP_URL}\n\n"
            f"Try setting it manually via BotFather:\n"
            f"1. Go to @BotFather\n"
            f"2. Send /mybots\n"
            f"3. Select your bot\n"
            f"4. Choose 'Bot Settings' → 'Menu Button'\n"
            f"5. Set URL to: {WEBAPP_URL}"
        )


def main() -> None:
    if TOKEN == 'YOUR_BOT_TOKEN_HERE':
        logging.error("Please set TELEGRAM_BOT_TOKEN environment variable or update TOKEN in bot.py")
        return
    
    application = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("plan_week", plan_week))
    application.add_handler(CommandHandler("grocery_list", grocery_list))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("setmenu", setmenu))  # Manual menu button setup command (admin)
    application.add_handler(CommandHandler("checkmenu", checkmenu))  # Check current menu button status (admin)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_preference))
    
    logging.info("Bot is starting...")
    application.run_polling()



if __name__ == '__main__':

    main()

