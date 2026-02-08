# Remote Desktop Access Guide

## Overview

Remote Desktop allows you to access your office computer from anywhere.

## Prerequisites

- VPN connection (required for remote access)
- Remote Desktop enabled on office computer
- Computer must be powered on
- Know your computer name

## Find Your Computer Name

**Windows:**
1. Right-click This PC > Properties
2. Look for "Device name"
3. Example: WKS-12345

**macOS:**
1. System Preferences > Sharing
2. Look for "Computer Name"

## Remote Desktop Setup

### Windows to Windows

**Enable Remote Desktop (Office Computer):**
1. Settings > System > Remote Desktop
2. Toggle "Enable Remote Desktop" ON
3. Note your computer name

**Connect from Home:**
1. Connect to VPN first
2. Open Remote Desktop Connection
3. Enter computer name: WKS-12345.company.local
4. Click Connect
5. Enter your credentials
6. Click OK

### macOS to macOS

**Enable Screen Sharing (Office Mac):**
1. System Preferences > Sharing
2. Check "Screen Sharing"
3. Set access permissions

**Connect from Home:**
1. Connect to VPN
2. Finder > Go > Connect to Server
3. Enter: vnc://computername.company.local
4. Click Connect
5. Enter credentials

### Connect to Windows from macOS

1. Download Microsoft Remote Desktop from App Store
2. Open app
3. Click "+" > Add PC
4. Enter PC name: WKS-12345.company.local
5. Add credentials
6. Click Add
7. Double-click to connect

### Connect to macOS from Windows

1. Download VNC Viewer
2. Enter: computername.company.local
3. Enter credentials
4. Connect

## Tips for Better Performance

### Optimize Connection

- Close unnecessary applications on remote computer
- Reduce screen resolution
- Disable desktop background
- Turn off visual effects

**Windows RDP Settings:**
1. Show Options > Experience tab
2. Select connection speed
3. Uncheck unnecessary features
4. Apply

### Bandwidth Usage

- Low: 256 Kbps (basic tasks)
- Medium: 512 Kbps (office work)
- High: 1+ Mbps (graphics work)

## File Transfer

### Windows RDP

**Enable:**
1. RDP > Show Options > Local Resources
2. Click "More"
3. Check "Drives"
4. Connect

**Transfer:**
- Copy/paste between computers
- Access local drives in remote session

### macOS Screen Sharing

- Use file sharing separately
- Or use cloud storage (OneDrive, SharePoint)

## Troubleshooting

### Cannot Connect

**Check:**
1. VPN is connected
2. Office computer is on
3. Computer name is correct
4. Firewall allows RDP

**Solutions:**
- Restart VPN connection
- Verify computer name
- Contact IT to verify RDP is enabled
- Check if computer is on network

### Connection Slow

- Reduce screen resolution
- Close bandwidth-heavy apps
- Check home internet speed
- Disable visual effects
- Use wired connection instead of Wi-Fi

### Authentication Failed

- Verify username format: COMPANY\username
- Check password is correct
- Ensure account not locked
- Reset password if needed

### Black Screen

- Press Ctrl+Alt+End (instead of Ctrl+Alt+Del)
- Restart remote session
- Check graphics drivers

### Session Disconnected

- Check VPN connection
- Verify network stability
- Reconnect to session
- Previous session should resume

## Security Best Practices

- Always use VPN
- Lock screen when away (Win+L)
- Log off when done (don't just close window)
- Never save passwords on shared computers
- Use strong passwords
- Enable MFA

## Alternative: Virtual Desktop (VDI)

For users without office computer:
1. Go to https://vdi.company.com
2. Sign in
3. Select virtual desktop
4. Launch session

Benefits:
- No need for office computer to be on
- Consistent environment
- Better for mobile users

## Support

Issues with Remote Desktop:
- Verify VPN first
- Check computer is on (ask colleague)
- IT Support: ext. 5555
- Email: support@company.com
