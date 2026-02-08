# Multi-Factor Authentication (MFA) Setup

## Why MFA?

MFA adds an extra layer of security by requiring two forms of verification:
1. Something you know (password)
2. Something you have (phone, token)

## Initial Setup

### Step 1: Enroll in MFA

1. Go to https://mfa.company.com
2. Sign in with your credentials
3. Click "Set up MFA"
4. Choose your method:
   - Microsoft Authenticator (recommended)
   - SMS text messages
   - Phone call
   - Hardware token

### Step 2: Configure Authenticator App (Recommended)

**Install App:**
- iOS: Download "Microsoft Authenticator" from App Store
- Android: Download from Google Play Store

**Setup:**
1. Open Microsoft Authenticator
2. Tap "+" to add account
3. Select "Work or school account"
4. Scan QR code shown on computer screen
5. Enter 6-digit code to verify
6. Save backup codes

### Step 3: Configure SMS (Alternative)

1. Select "Text message" option
2. Enter mobile phone number
3. Click "Send code"
4. Enter code received via SMS
5. Click "Verify"

## Using MFA

### Daily Login

1. Enter username and password
2. Approve MFA prompt:
   - **Authenticator App**: Tap "Approve" on notification
   - **SMS**: Enter code from text message
   - **Phone Call**: Answer and press #

### Remember Device

- Check "Don't ask again for 30 days" on trusted devices
- Only use on personal devices
- Never on shared computers

## Managing MFA

### Add Backup Method

1. Go to https://mfa.company.com
2. Click "Security info"
3. Click "Add method"
4. Choose backup option
5. Follow setup steps

### Change Phone Number

1. Security info > Phone
2. Click "Change"
3. Enter new number
4. Verify with code

### Reset MFA Device

**If you lost your device:**
1. Contact IT Support immediately
2. Verify identity (employee ID, manager name)
3. IT will reset your MFA
4. Set up new device

**Use backup codes:**
- Each code works once
- Keep in secure location
- Generate new codes after use

## Troubleshooting

### Not Receiving Codes

**SMS Issues:**
- Check phone signal
- Verify number is correct
- Wait 60 seconds before requesting new code
- Check spam/blocked messages

**App Issues:**
- Ensure app is updated
- Check phone time is correct (auto-sync)
- Re-sync account in app
- Reinstall app if needed

### Locked Out

1. Use backup authentication method
2. Use backup codes
3. Contact IT Support: ext. 5555

### Code Not Working

- Ensure phone time is synced
- Wait for new code (codes expire after 30 seconds)
- Check you're entering code for correct account

## Best Practices

- Set up multiple authentication methods
- Keep backup codes secure
- Update phone number when changed
- Don't share codes
- Report lost devices immediately
- Use Authenticator app over SMS (more secure)

## Backup Codes

- Generate 10 single-use codes
- Store securely (password manager, safe)
- Each code works once
- Generate new set after using several

To generate:
1. https://mfa.company.com
2. Security info > Backup codes
3. Click "Generate new codes"
4. Save or print codes

## Support

For MFA issues:
- Self-service: https://mfa.company.com
- IT Support: ext. 5555
- Emergency: Visit IT desk with photo ID
