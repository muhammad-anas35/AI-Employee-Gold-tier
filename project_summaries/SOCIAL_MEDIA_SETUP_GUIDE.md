# Social Media Developer Accounts Setup Guide

**Date:** 2026-03-27
**Purpose:** Get API credentials for Facebook/Instagram and Twitter integration

---

## Part 1: Facebook Developer Account

### Step 1: Create Facebook Developer Account

1. **Go to:** https://developers.facebook.com
2. **Click:** "Get Started" or "My Apps"
3. **Log in** with your Facebook account
4. **Complete registration:**
   - Accept terms and conditions
   - Verify email if needed
   - Complete any required verification

### Step 2: Create a New App

1. **Click:** "Create App"
2. **Select use case:** "Other" or "Business"
3. **Select app type:** "Business"
4. **Fill in details:**
   - App Name: `AI Employee Gold`
   - App Contact Email: your email
   - Business Account: (optional)
5. **Click:** "Create App"

### Step 3: Get App Credentials

1. **Go to:** Settings → Basic
2. **Copy these values:**
   - App ID: `XXXXXXXXXX`
   - App Secret: Click "Show" and copy
3. **Save these in:** `config/.env`

### Step 4: Add Facebook Login Product

1. **Go to:** Dashboard → Add Product
2. **Find:** "Facebook Login"
3. **Click:** "Set Up"
4. **Configure:**
   - Valid OAuth Redirect URIs: `http://localhost:8069/auth/callback`
   - Click "Save Changes"

### Step 5: Add Instagram Basic Display (Optional)

1. **Go to:** Dashboard → Add Product
2. **Find:** "Instagram Basic Display"
3. **Click:** "Set Up"
4. **Follow setup wizard**

### Step 6: Get Access Token

1. **Go to:** Tools → Graph API Explorer
2. **Select your app**
3. **Add permissions:**
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `instagram_basic`
   - `instagram_content_publish`
4. **Click:** "Generate Access Token"
5. **Copy the token** and save it

---

## Part 2: Twitter Developer Account

### Step 1: Apply for Developer Account

1. **Go to:** https://developer.twitter.com
2. **Click:** "Sign up" or "Apply"
3. **Log in** with your Twitter account
4. **Select account type:** "Hobbyist" or "Professional"
5. **Fill in application:**
   - What's your use case? "Building tools for personal use"
   - Will you make Twitter content available? "No"
   - Will you analyze Twitter data? "No"
   - Will you display Tweets? "Yes, for personal automation"
6. **Submit application**
7. **Wait for approval** (usually instant to 24 hours)

### Step 2: Create a Project and App

1. **Go to:** Developer Portal → Projects & Apps
2. **Click:** "Create Project"
3. **Fill in:**
   - Project Name: `AI Employee`
   - Use Case: "Making a bot"
   - Description: "Personal AI assistant for business automation"
4. **Create App:**
   - App Name: `ai-employee-gold`
   - Environment: "Development"

### Step 3: Get API Keys

1. **After creating app, you'll see:**
   - API Key (Consumer Key)
   - API Key Secret (Consumer Secret)
   - Bearer Token
2. **IMPORTANT:** Copy these immediately - they won't be shown again!
3. **Save in:** `config/.env`

### Step 4: Generate Access Tokens

1. **Go to:** App Settings → Keys and Tokens
2. **Under "Authentication Tokens":**
   - Click "Generate" for Access Token and Secret
3. **Copy:**
   - Access Token
   - Access Token Secret
4. **Save these in:** `config/.env`

### Step 5: Set App Permissions

1. **Go to:** App Settings → User authentication settings
2. **Click:** "Set up"
3. **App permissions:**
   - ✅ Read
   - ✅ Write
   - ❌ Direct Messages (not needed)
4. **Type of App:** "Web App"
5. **Callback URL:** `http://localhost:8069/auth/callback`
6. **Website URL:** `http://localhost:8069`
7. **Click:** "Save"

---

## Part 3: Update config/.env

After getting all credentials, update `config/.env`:

```bash
# Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DB=Ai-Employee
ODOO_USERNAME=ranabro353570@gmail.com
ODOO_PASSWORD=admin

# Facebook/Instagram Configuration
FACEBOOK_APP_ID=your_app_id_here
FACEBOOK_APP_SECRET=your_app_secret_here
FACEBOOK_ACCESS_TOKEN=your_access_token_here
FACEBOOK_PAGE_ID=your_page_id_here

# Twitter Configuration
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_SECRET=your_access_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here

# Gmail API Configuration
GMAIL_CLIENT_ID=your_client_id_here
GMAIL_CLIENT_SECRET=your_client_secret_here

# Vault Configuration
VAULT_PATH=AI_Employee_Vault
DROP_FOLDER=~/AI_Employee_Drop
```

---

## Part 4: Test Credentials

### Test Facebook API

```python
import requests

access_token = "YOUR_ACCESS_TOKEN"
url = f"https://graph.facebook.com/v18.0/me?access_token={access_token}"

response = requests.get(url)
print(response.json())
# Should show your Facebook user info
```

### Test Twitter API

```python
import requests

bearer_token = "YOUR_BEARER_TOKEN"
headers = {"Authorization": f"Bearer {bearer_token}"}
url = "https://api.twitter.com/2/users/me"

response = requests.get(url, headers=headers)
print(response.json())
# Should show your Twitter user info
```

---

## Troubleshooting

### Facebook Issues

**"App not approved for public use"**
- For personal use, you don't need approval
- Use your own account for testing

**"Invalid OAuth redirect URI"**
- Make sure callback URL matches exactly
- Include http:// or https://

**"Access token expired"**
- Tokens expire after 60 days
- Generate a long-lived token or refresh regularly

### Twitter Issues

**"Application pending review"**
- Wait for approval email (usually quick)
- Check spam folder

**"Forbidden - Authentication credentials missing"**
- Check API keys are correct
- Make sure you copied the full token

**"Read-only application"**
- Update app permissions to include Write
- Regenerate access tokens after changing permissions

---

## Security Notes

1. **Never commit .env file to Git**
2. **Keep API keys secret**
3. **Use environment variables only**
4. **Rotate keys if exposed**
5. **Use read-only tokens when possible**

---

## Next Steps

Once you have all credentials:

1. ✅ Update `config/.env` with all API keys
2. ✅ Test credentials with simple API calls
3. ✅ Move to implementing Facebook/Instagram integration
4. ✅ Move to implementing Twitter integration

---

**Current Status:** Waiting for you to create accounts and get credentials

**When done, type "continue" and provide the credentials!**
