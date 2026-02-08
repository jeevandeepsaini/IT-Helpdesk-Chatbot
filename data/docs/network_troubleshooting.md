# Network Troubleshooting Guide

## Quick Diagnostics

### Check Connection Status

**Windows:**
1. Click network icon in system tray
2. Check if connected to corporate network
3. Look for yellow warning or red X

**macOS:**
1. Click Wi-Fi icon in menu bar
2. Verify connection status
3. Check signal strength

## Common Issues

### No Internet Connection

**Step 1: Basic Checks**
- Verify Wi-Fi is enabled
- Check if connected to correct network
- Ensure airplane mode is OFF
- Check if other devices can connect

**Step 2: Restart Network**
1. Disconnect from network
2. Wait 10 seconds
3. Reconnect
4. Test connection

**Step 3: Restart Device**
- Restart computer
- Test connection after reboot

**Step 4: Reset Network Settings**

Windows:
```
1. Open Command Prompt as Administrator
2. Run: ipconfig /release
3. Run: ipconfig /renew
4. Run: ipconfig /flushdns
```

macOS:
```
1. System Preferences > Network
2. Select Wi-Fi
3. Click Advanced
4. Click "Renew DHCP Lease"
```

### Slow Network Speed

**Diagnose:**
1. Run speed test: https://speedtest.company.com
2. Check bandwidth usage in Task Manager
3. Close unnecessary applications

**Solutions:**
- Move closer to Wi-Fi access point
- Switch to 5GHz network if available
- Disconnect from VPN if not needed
- Clear browser cache
- Restart router (if home network)

### Cannot Access Shared Drives

**Check:**
1. Verify VPN connection (required for remote access)
2. Check credentials are correct
3. Ensure drive is mapped correctly

**Remap Network Drive:**

Windows:
1. Open File Explorer
2. Click "Map network drive"
3. Enter path: \\fileserver\sharename
4. Check "Reconnect at sign-in"
5. Enter credentials

macOS:
1. Finder > Go > Connect to Server
2. Enter: smb://fileserver/sharename
3. Click Connect
4. Enter credentials

### DNS Issues

**Symptoms:**
- Can't access websites by name
- "Server not found" errors
- Some sites work, others don't

**Fix:**
1. Flush DNS cache (see commands above)
2. Change DNS servers:
   - Primary: 8.8.8.8
   - Secondary: 8.8.4.4
3. Restart network adapter

### Wi-Fi Keeps Disconnecting

**Solutions:**
1. Update Wi-Fi drivers
2. Forget and rejoin network
3. Disable power saving for Wi-Fi adapter:
   - Device Manager > Network Adapters
   - Right-click Wi-Fi adapter > Properties
   - Power Management tab
   - Uncheck "Allow computer to turn off this device"
4. Move to different location
5. Request Wi-Fi extender if signal weak

## Advanced Troubleshooting

### Check IP Configuration

Windows:
```
ipconfig /all
```

macOS:
```
ifconfig
```

Look for:
- Valid IP address (not 169.254.x.x)
- Correct subnet mask
- Default gateway
- DNS servers

### Test Connectivity

```
ping google.com
ping 8.8.8.8
tracert google.com (Windows)
traceroute google.com (macOS)
```

## When to Contact IT

Contact support if:
- Issue persists after troubleshooting
- Multiple users affected
- Hardware damage suspected
- Need new network equipment
- Require network port activation

Email: support@company.com
Phone: ext. 5555
