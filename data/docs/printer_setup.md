# Printer Setup Guide

## Adding a Network Printer

### Windows

1. Click Start > Settings > Devices > Printers & Scanners
2. Click "Add a printer or scanner"
3. Wait for scan to complete
4. If printer appears, click it and select "Add device"

**If printer not found:**
1. Click "The printer that I want isn't listed"
2. Select "Select a shared printer by name"
3. Enter: \\printserver\PrinterName
4. Click Next
5. Install driver if prompted
6. Set as default if desired

### macOS

1. System Preferences > Printers & Scanners
2. Click "+" to add printer
3. Select printer from list
4. Click "Add"

**For network printer:**
1. Click "+" > IP tab
2. Enter printer IP address
3. Protocol: HP Jetdirect - Socket
4. Click "Add"

## Common Printers by Location

- Floor 1 Reception: \\printserver\Floor1-Reception
- Floor 2 East: \\printserver\Floor2-East
- Floor 2 West: \\printserver\Floor2-West
- Floor 3 IT: \\printserver\Floor3-IT
- Conference Rooms: \\printserver\Conference-Color

## Printing from Mobile

### iOS
1. Ensure on corporate Wi-Fi
2. Open document
3. Tap Share > Print
4. Select printer
5. Configure options
6. Tap Print

### Android
1. Connect to corporate Wi-Fi
2. Open document
3. Menu > Print
4. Select printer
5. Tap Print

## Troubleshooting

### Printer Offline

1. Check printer power and connections
2. Restart printer
3. Remove and re-add printer
4. Check network connection

### Print Job Stuck

1. Open print queue
2. Cancel stuck jobs
3. Restart Print Spooler service:
   - Windows: services.msc > Print Spooler > Restart
4. Try printing again

### Poor Print Quality

- Check ink/toner levels
- Run printer cleaning cycle
- Check paper quality
- Adjust print quality settings

### Access Denied

- Verify you have printer permissions
- Contact IT to add you to printer group
- Check if printer requires badge authentication

## Secure Printing

For confidential documents:
1. Send print job
2. Go to printer
3. Tap your badge on reader
4. Select your print job
5. Confirm to print

## Scanning

1. Place document on scanner
2. At printer panel, select "Scan"
3. Choose destination:
   - Email (enter your email)
   - Network folder
   - USB drive
4. Configure settings
5. Press Start

## Support

For printer issues:
- Check printer status lights
- View printer display for errors
- Contact IT: ext. 5555
- Submit ticket for toner replacement
