import logging
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
import random  # For dummy suggestions; replace with API calls
from collections import defaultdict  # For aggregating groceries
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get bot token from environment variable
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')



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



def main() -> None:
    if TOKEN == 'YOUR_BOT_TOKEN_HERE':
        logging.error("Please set TELEGRAM_BOT_TOKEN environment variable or update TOKEN in bot.py")
        return
    
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("plan_week", plan_week))
    application.add_handler(CommandHandler("grocery_list", grocery_list))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_preference))
    
    logging.info("Bot is starting...")
    application.run_polling()



if __name__ == '__main__':

    main()

