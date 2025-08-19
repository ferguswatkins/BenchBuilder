# ngrok Setup for HTTPS Development

## What is ngrok?
ngrok creates a secure HTTPS tunnel to your local development server, allowing Yahoo OAuth to work properly.

## Setup Steps

### 1. Sign up for ngrok (Free)
1. Go to https://ngrok.com/
2. Sign up for a free account
3. Get your authtoken from the dashboard

### 2. Authenticate ngrok
```bash
ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
```

### 3. Start your FastAPI server (in one terminal)
```bash
cd backend
source venv/bin/activate
python main.py
```

### 4. Start ngrok tunnel (in another terminal)
```bash
ngrok http 8000
```

This will give you output like:
```
Session Status                online
Account                       your-email@example.com
Version                       3.26.0
Region                        United States (us)
Latency                       25ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok.io -> http://localhost:8000
```

### 5. Update Yahoo Application
Use the HTTPS URL from ngrok as your redirect URI:
```
https://abc123.ngrok.io/auth/callback
```

### 6. Update your .env file
```env
YAHOO_REDIRECT_URI=https://abc123.ngrok.io/auth/callback
```

## Important Notes

- **Free ngrok URLs change** every time you restart ngrok
- You'll need to update your Yahoo app settings each time
- For production, you'd use a permanent domain

## Alternative: Use a Fixed Subdomain (Paid)
With ngrok Pro ($8/month), you can use a fixed subdomain:
```bash
ngrok http 8000 --subdomain=your-app-name
```

Then your redirect URI would always be:
```
https://your-app-name.ngrok.io/auth/callback
```

## Testing the Setup

1. Start your server: `python main.py`
2. Start ngrok: `ngrok http 8000`
3. Copy the HTTPS URL to Yahoo app settings
4. Update your .env file with the ngrok URL
5. Restart your server to load the new environment
6. Test: `curl https://your-ngrok-url.ngrok.io/health`
