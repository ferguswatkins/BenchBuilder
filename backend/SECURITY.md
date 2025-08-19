# Security Guidelines

## Environment Variables

### Setup Process
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your actual credentials:
   ```bash
   # Use a secure editor
   nano .env  # or vim, vscode, etc.
   ```

3. Verify `.env` is in `.gitignore`:
   ```bash
   git check-ignore .env
   # Should output: .env
   ```

## API Key Security

### Yahoo API Keys
- Get from: https://developer.yahoo.com/fantasysports/
- Permissions needed: `fspt-r` (Fantasy Sports Read)
- Rate limit: 999 requests/hour per IP
- Store in `.env` file only

### LLM API Keys
- **OpenAI**: Get from https://platform.openai.com/
- **Anthropic**: Get from https://console.anthropic.com/
- Choose one based on your preference
- Both require payment method for API access

## Production Deployment

### Environment Variables in Production
- Use your hosting platform's environment variable settings
- **Railway**: Environment variables in dashboard
- **Render**: Environment variables in service settings  
- **Vercel**: Environment variables in project settings
- **Heroku**: Config vars in dashboard

### Never Do This:
- ❌ Commit `.env` files
- ❌ Put secrets in code comments
- ❌ Share API keys in chat/email
- ❌ Use production keys for development

### Security Checklist
- [ ] `.env` is in `.gitignore`
- [ ] Real credentials only in `.env` (not `.env.example`)
- [ ] Different API keys for development vs production
- [ ] Regular key rotation (every 3-6 months)
- [ ] Monitor API usage for unusual activity

## Emergency Response
If you accidentally commit credentials:
1. **Immediately revoke** the exposed keys
2. Generate new keys
3. Update your `.env` file
4. Consider using `git filter-branch` to remove from history
5. Force push the cleaned history (if safe to do so)

## Development vs Production
- Use separate Yahoo apps for dev/prod
- Use different LLM API keys
- Never use production data in development
- Test with mock/sample data when possible
