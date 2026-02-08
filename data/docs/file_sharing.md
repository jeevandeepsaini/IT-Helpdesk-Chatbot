# File Sharing Permissions Guide

## Overview

Learn how to share files and folders securely with colleagues.

## OneDrive for Business

### Share a File

1. Right-click file in OneDrive
2. Click "Share"
3. Choose sharing method:
   - **Specific people**: Enter email addresses
   - **People in organization**: Anyone with company email
   - **Anyone with link**: Not recommended for sensitive data

4. Set permissions:
   - Can view
   - Can edit

5. Add message (optional)
6. Click "Send"

### Share a Folder

1. Right-click folder
2. Click "Share"
3. Enter recipient emails
4. Set permissions
5. Click "Share"

### Manage Shared Files

1. Go to OneDrive online
2. Click "Shared" in left panel
3. View "Shared by me" or "Shared with me"
4. Click "..." > Manage access
5. Add/remove people or change permissions

## SharePoint

### Share Document Library

1. Open SharePoint site
2. Go to document library
3. Click "Share" button
4. Enter names or emails
5. Choose permission level:
   - Read
   - Edit
   - Full Control

6. Click "Share"

### Create Shared Folder

1. In document library, click "New" > Folder
2. Name the folder
3. Click "Create"
4. Right-click folder > Share
5. Add users and set permissions

## Network Drives

### Access Shared Drive

**Windows:**
1. File Explorer > This PC
2. Click "Map network drive"
3. Choose drive letter
4. Enter path: \\fileserver\sharename
5. Check "Reconnect at sign-in"
6. Click "Finish"
7. Enter credentials if prompted

**macOS:**
1. Finder > Go > Connect to Server
2. Enter: smb://fileserver/sharename
3. Click "Connect"
4. Enter credentials

### Request Access to Shared Drive

1. Submit request: https://it.company.com/access-request
2. Specify:
   - Drive/folder name
   - Business justification
   - Required permission level
   - Manager approval

3. Wait for approval (1-2 business days)

## Permission Levels

### Read
- View files
- Download files
- Cannot modify or delete

### Edit
- View and download
- Modify existing files
- Upload new files
- Cannot delete or change permissions

### Full Control
- All edit permissions
- Delete files
- Change permissions
- Manage folder structure

## Best Practices

### Security

- Share only with people who need access
- Use "Specific people" when possible
- Set expiration dates for temporary access
- Review shared files regularly
- Remove access when no longer needed

### Organization

- Use descriptive folder names
- Maintain clear folder structure
- Document permission requirements
- Keep sensitive data in restricted folders

### Compliance

- Never share:
  - Customer PII without authorization
  - Financial data externally
  - Passwords or credentials
  - Confidential business plans

- Always:
  - Follow data classification policies
  - Use company-approved sharing methods
  - Get manager approval for external sharing
  - Encrypt sensitive files

## External Sharing

### Share with External Partners

1. Verify external sharing is allowed for your data
2. Get manager approval
3. Use OneDrive/SharePoint sharing
4. Set expiration date
5. Require sign-in
6. Monitor access

### Secure External Sharing

- Set link expiration (max 90 days)
- Require password
- Limit to view-only when possible
- Use encrypted email for sensitive files
- Track who accessed files

## Troubleshooting

### Cannot Access Shared Folder

**Check:**
- VPN connection (if remote)
- Permissions granted
- Correct path/link
- Account not locked

**Solutions:**
- Request access from owner
- Verify network connection
- Check spelling of path
- Contact IT if persists

### Cannot Share File

**Possible causes:**
- File is checked out
- Insufficient permissions
- External sharing disabled
- File in personal folder

**Solutions:**
- Check in file if checked out
- Move to shared location
- Request permission from owner
- Contact IT for external sharing

### Shared Link Not Working

- Check link hasn't expired
- Verify recipient has permission
- Ensure recipient signed in
- Regenerate link if needed

## Revoking Access

### Remove Individual Access

1. Right-click file/folder
2. Manage access
3. Find person
4. Click "X" or "Remove"
5. Confirm

### Stop Sharing Completely

1. Manage access
2. Click "Stop sharing"
3. Confirm

All users will lose access immediately.

## Audit Shared Files

Regular review (monthly):
1. Check "Shared by me"
2. Remove unnecessary sharing
3. Update permissions as needed
4. Delete old shared links

## Support

For sharing issues:
- Check permissions first
- Verify recipient email
- IT Support: ext. 5555
- Access requests: https://it.company.com/access-request
