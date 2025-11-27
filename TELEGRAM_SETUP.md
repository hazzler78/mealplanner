# Telegram WebApp Setup Guide

## 1. Environment Variables in Vercel

Make sure you have set the environment variable in Vercel:
- **Variable name**: `YOUR_SPOONACULAR_API_KEY` (or `SPOONACULAR_API_KEY`)
- **Value**: Your Spoonacular API key (e.g., `86bccf274d4a4d5ea43051835a076d41`)

To verify:
1. Go to your Vercel project dashboard
2. Navigate to Settings → Environment Variables
3. Ensure the variable is set for Production, Preview, and Development

## 2. Deploy to Vercel

After pushing your code, Vercel will automatically deploy. Make sure:
- `index.html` is in the root directory
- `api/recipe.js` is in the `api/` folder
- `vercel.json` and `package.json` are present

Your app will be available at: `https://your-project-name.vercel.app`

## 3. Configure Telegram Bot

### Option A: Using BotFather (Recommended)

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow instructions to create a bot (if you haven't already)
3. Send `/newapp` to create a new WebApp
4. Select your bot when prompted
5. When asked for the WebApp URL, provide:
   ```
   https://your-project-name.vercel.app
   ```
6. Follow the prompts to complete setup
7. BotFather will give you a button link - you can use this to test!

### Option B: Using Bot Settings

1. Go to [@BotFather](https://t.me/BotFather)
2. Send `/mybots`
3. Select your bot
4. Choose "Bot Settings" → "Menu Button"
5. Set the menu button URL to: `https://your-project-name.vercel.app`

## 4. Test Your WebApp

### Method 1: Direct Link
- Use the link provided by BotFather after creating the WebApp
- Or open: `https://t.me/your_bot_name/your_webapp_name`

### Method 2: Menu Button
- Open your bot in Telegram
- Click the menu button (bottom left)
- The WebApp should open

### Method 3: Inline Button (for testing)
You can also add an inline button in your Python bot:
```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

keyboard = [[InlineKeyboardButton("Open Meal Planner", web_app=WebAppInfo(url="https://your-project-name.vercel.app"))]]
reply_markup = InlineKeyboardMarkup(keyboard)
await update.message.reply_text("Click below to open the meal planner!", reply_markup=reply_markup)
```

## 5. Troubleshooting

### WebApp not loading?
- Check that your Vercel deployment is successful
- Verify the URL is accessible in a browser
- Check browser console for errors

### API not working?
- Verify environment variable is set correctly in Vercel
- Check Vercel function logs: Dashboard → Your Project → Functions → View Logs
- Ensure the variable name matches: `YOUR_SPOONACULAR_API_KEY` or `SPOONACULAR_API_KEY`

### CORS errors?
- The serverless function includes CORS headers
- Make sure you're accessing via Telegram WebApp (not directly in browser)

## 6. Quick Test

1. Open your bot in Telegram
2. Click the menu button or use the WebApp link
3. Select a diet preference
4. Click "Generate Weekly Plan"
5. Wait for recipes to load (may take a few seconds)
6. Click "View Grocery List" to see aggregated ingredients

Your WebApp should now be working! 🎉

