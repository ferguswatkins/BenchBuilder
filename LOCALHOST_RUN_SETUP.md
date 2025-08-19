# localhost.run Setup (No Signup Required)

## Quick HTTPS tunnel without registration

### 1. Start your server
```bash
cd backend
source venv/bin/activate  
python main.py
```

### 2. In another terminal, create HTTPS tunnel
```bash
ssh -R 80:localhost:8000 nokey@localhost.run
```

This will give you a URL like: `https://abc123.lhr.life`

### 3. Update Yahoo Application
Use the HTTPS URL as your redirect URI:
```
https://abc123.lhr.life/auth/callback
```

### 4. Update your .env file
```env
YAHOO_REDIRECT_URI=https://abc123.lhr.life/auth/callback
```

### 5. Test
```bash
curl https://abc123.lhr.life/health
```

## Pros/Cons vs ngrok
- ✅ No signup required
- ✅ Works immediately  
- ❌ URLs change every restart
- ❌ Less reliable than ngrok
- ❌ No web dashboard
