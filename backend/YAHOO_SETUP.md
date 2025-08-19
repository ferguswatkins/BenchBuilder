# Yahoo API Setup Guide

## After Creating Your Yahoo Application

Once you click "Create Application", you'll get:

### 1. Client Credentials
- **Client ID**: A long string like `dj0yJmk9...`
- **Client Secret**: Another long string (keep this secret!)

### 2. Update Your .env File

```bash
cd backend
# Edit your .env file with the actual credentials
nano .env
```

Replace these lines in your `.env` file:
```env
YAHOO_CLIENT_ID=your_actual_client_id_from_yahoo
YAHOO_CLIENT_SECRET=your_actual_client_secret_from_yahoo
YAHOO_REDIRECT_URI=http://localhost:8000/auth/callback
```

### 3. Test the OAuth Flow

After updating your .env file and restarting your server, test with:

```bash
# Test the OAuth initiation
python test_oauth.py
```

Or manually:
```bash
curl http://localhost:8000/auth/yahoo
```

### 4. Complete OAuth Flow

1. Visit the `auth_url` returned from the test
2. Log in with your Yahoo account
3. Authorize the application
4. You'll be redirected to `http://localhost:8000/auth/callback?code=...`
5. The callback will exchange the code for an access token

### 5. Test API Access

Once authenticated, test league access:
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" http://localhost:8000/api/leagues
```

## Troubleshooting

### Common Issues:
- **"Invalid redirect URI"**: Make sure the redirect URI in Yahoo exactly matches your .env file
- **"Invalid client"**: Double-check your Client ID and Secret
- **"Scope not authorized"**: Make sure you selected "Fantasy Sports" permissions

### Development vs Production:
- **Development**: Use `http://localhost:8000/auth/callback`
- **Production**: You'll need to add your production domain's HTTPS callback URL

### Rate Limits:
- Yahoo allows 999 requests per hour per IP
- Be mindful of this during development and testing
