# Telegram Bot Deployment Guide

Your Telegram bot (`bot.py`) needs to run continuously to receive messages. Vercel only hosts your WebApp frontend, not the Python bot.

## Option 1: Deploy to Railway (Recommended - Free Tier Available)

1. **Sign up at [Railway.app](https://railway.app)** (free tier available)

2. **Create a new project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `mealplanner` repository

3. **Configure the service:**
   - Railway will auto-detect Python
   - Set the start command: `python bot.py`
   - Add environment variables:
     - `TELEGRAM_BOT_TOKEN` - Your bot token
     - `TELEGRAM_WEBAPP_URL` - `https://mealplanner-wheat.vercel.app`

4. **Deploy:**
   - Railway will automatically deploy
   - Check logs to see if bot starts successfully

## Option 2: Deploy to Render (Free Tier Available)

1. **Sign up at [Render.com](https://render.com)** (free tier available)

2. **Create a new Background Worker:**
   - Click "New +" → "Background Worker"
   - Connect your GitHub repository
   - Set:
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `python bot.py`
     - **Environment:** Python 3

3. **Add Environment Variables:**
   - `TELEGRAM_BOT_TOKEN` - Your bot token
   - `TELEGRAM_WEBAPP_URL` - `https://mealplanner-wheat.vercel.app`

4. **Deploy:**
   - Click "Create Background Worker"
   - Check logs to verify bot is running

## Option 3: Run Locally (For Testing)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   - Create/update `.env` file:
     ```
     TELEGRAM_BOT_TOKEN=your_bot_token_here
     TELEGRAM_WEBAPP_URL=https://mealplanner-wheat.vercel.app
     ```

3. **Run the bot:**
   ```bash
   python bot.py
   ```

4. **Keep it running:**
   - The bot needs to stay running to receive messages
   - Use `Ctrl+C` to stop it

## Option 4: Use a VPS (DigitalOcean, AWS, etc.)

If you have a VPS, you can:
1. SSH into your server
2. Install Python and dependencies
3. Run the bot with `nohup python bot.py &` or use a process manager like `systemd` or `supervisor`

## Verifying Bot is Running

After deployment, test your bot:
1. Send `/start` to your bot in Telegram
2. Send `/help` to see all commands
3. Check the deployment logs for any errors

## Important Notes

- **The bot must run continuously** - if it stops, it won't receive messages
- **Free tiers may sleep** - Railway and Render free tiers may pause inactive services
- **Environment variables** - Make sure to set them in your hosting platform, not just locally
- **Logs** - Always check deployment logs if commands aren't working

