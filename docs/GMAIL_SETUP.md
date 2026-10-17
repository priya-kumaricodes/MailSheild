# Google Cloud OAuth & Gmail Integration Setup Guide

This guide explains how to configure Google Cloud OAuth 2.0 credentials for MailShield 2.1, detailing the differences between **Development Testing Mode** and **Production Readiness**.

---

## 1. Overview & Permissions Policy

MailShield requests the **absolute minimum scopes** required to list and classify inbox emails:

| Scope | Category | Description | Permission Requested |
|---|---|---|---|
| `https://www.googleapis.com/auth/gmail.readonly` | Restricted | View email messages and settings | **Read-Only** (No send, modify, or delete) |
| `https://www.googleapis.com/auth/userinfo.email` | Non-sensitive | View connected user's email address | Account identity binding |

> [!IMPORTANT]
> **Strict Read-Only Guarantee**: MailShield will **never** request message modification (`gmail.modify`), sending (`gmail.send` / `gmail.compose`), or deletion scopes. MailShield cannot alter, move, or delete your Gmail messages.

---

## 2. Google Cloud Console Setup

### Step 1: Create a Project
1. Navigate to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click the project dropdown at the top and select **New Project**.
3. Name your project (e.g., `MailShield-Client`) and click **Create**.

### Step 2: Enable the Gmail API
1. In the navigation menu, go to **APIs & Services** > **Library**.
2. Search for **Gmail API**.
3. Select **Gmail API** and click **Enable**.

### Step 3: Configure the OAuth Consent Screen
1. Go to **APIs & Services** > **OAuth consent screen**.
2. Select User Type:
   - **Internal**: If you use Google Workspace within your organization (recommended for enterprise pilots).
   - **External**: For testing with personal `@gmail.com` accounts or public distribution.
3. Fill in the App Information:
   - **App name**: `MailShield`
   - **User support email**: Your support or administrator email.
   - **Developer contact information**: Your contact email.
4. Click **Save and Continue**.
5. On the **Scopes** page:
   - Click **Add or Remove Scopes**.
   - Add `.../auth/gmail.readonly` and `.../auth/userinfo.email`.
   - Click **Update** and then **Save and Continue**.

---

## 3. Development Testing Mode vs. Production Readiness

### Development Testing Mode
When your Google Cloud OAuth app is in **Testing** status:
- **Test Users**: Only Google accounts explicitly added under **Test Users** in the Google Cloud Console can authorize the application. You can add up to **100 test users**.
- **Refresh Token Lifetime**: In Testing mode, Google refresh tokens expire automatically after **7 days** (604,800 seconds). Users must re-authorize once per week.
- **Unverified App Warning**: Users will see a warning screen ("Google hasn't verified this app") during authorization. Users click **Advanced** > **Go to MailShield (unsafe)** to proceed with development testing.

### Production Readiness & Google App Verification
Because `gmail.readonly` is classified as a **Restricted Scope**, moving the OAuth consent screen to **In production** requires formal Google Verification:
1. **Domain Verification**: You must prove ownership of your application's domain via Google Search Console.
2. **Public Legal Policies**: Publicly accessible Privacy Policy and Terms of Service URLs explaining how user data is handled.
3. **Cloud Application Security Assessment (CASA Tier 2)**:
   - Google requires an independent third-party security assessment (CASA Tier 2) performed by an authorized security lab.
   - Annual recertification is required for continuous production access.
4. **Demonstration Video**: A video demonstrating how your application requests scopes, why each scope is necessary, and showing the in-app user journey.

---

## 4. Creating OAuth 2.0 Credentials

### Web Application Credentials
1. Go to **APIs & Services** > **Credentials**.
2. Click **Create Credentials** > **OAuth client ID**.
3. Select Application type: **Web application**.
4. Name: `MailShield Web Client`.
5. Under **Authorized redirect URIs**, add:
   - Local development: `http://localhost:5173/gmail/callback`
   - Production web: `https://your-domain.com/gmail/callback`
6. Click **Create**. Note the **Client ID** and **Client Secret**.

### Desktop Application (Loopback)
For the Electron Desktop application:
1. You can use the same Web client or create a dedicated OAuth client ID of type **Desktop app** or **Web application** (for loopback redirects).
2. Under **Authorized redirect URIs**, register the local loopback redirect URI:
   - `http://127.0.0.1:8000/api/v1/gmail/callback/desktop`
   - `http://localhost:8000/api/v1/gmail/callback/desktop`

---

## 5. Configuring MailShield Environment Variables

Add the following variables to your `.env` file (or set them in your deployment environment):

```bash
# Google OAuth 2.0 Credentials
GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="your-client-secret"

# Redirect URIs (Defaults shown below)
GOOGLE_REDIRECT_URI_WEB="http://localhost:5173/gmail/callback"
GOOGLE_REDIRECT_URI_DESKTOP="http://127.0.0.1:8000/api/v1/gmail/callback/desktop"

# Dedicated Token Encryption Key (Recommended: 32+ high-entropy characters or 64 hex characters)
TOKEN_ENCRYPTION_KEY="your-dedicated-32-byte-token-encryption-secret-key"

# Key Rotation Fallback (Optional, used during zero-downtime key rotation)
# TOKEN_ENCRYPTION_KEY_FALLBACK="previous-encryption-key"
```

---

## 6. Verification Checklist

- [ ] Gmail API is enabled in Google Cloud Console.
- [ ] OAuth Consent Screen configured with `gmail.readonly` and `userinfo.email`.
- [ ] Test users added to Google Cloud Console (if in Testing mode).
- [ ] Exact redirect URIs match between Google Console and MailShield settings.
- [ ] `TOKEN_ENCRYPTION_KEY` configured with at least 256 bits of entropy.
- [ ] Disconnect flow verified (purging local credentials and calling Google revocation).
