# Face Security System - User Guide

## 🚀 Quick Start Guide

### 1. Installation & Setup

**Option A: Easy Start (Recommended)**
1. Double-click `start.bat` 
2. The script will automatically check and install dependencies
3. The GUI launcher will open

**Option B: Manual Installation**
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python launcher.py
```

### 2. First Time Setup

1. **Launch the application** using `start.bat` or `python launcher.py`
2. **Choose Recognition System**: Select "MediaPipe (Recommended)" 
3. **Register as Owner**:
   - Click "👤 Register Owner"
   - Set a secure password (remember this!)
   - Position yourself in front of the camera
   - Press SPACE to capture face samples (5 needed)
   - Wait for "Registration successful!" message

### 3. Start Protection

1. **Click "🔍 Start Monitoring"**
2. **Your screen is now protected!**
   - Green status = You're recognized as owner
   - Red status = Unauthorized person detected
   - Screen will blur if stranger approaches

### 4. Unlock When Needed

- **If screen gets locked**: Press `Ctrl+Alt+O`
- **Enter your password** to unlock
- **Screen unlocks automatically** when you return

---

## 📋 Detailed Instructions

### System Requirements
- **Operating System**: Windows 10/11
- **Python**: 3.8 or higher
- **Hardware**: Webcam, 4GB RAM minimum
- **Internet**: Required for initial setup only

### Features Overview

#### 🔒 Security Features
- **Facial Recognition**: Advanced AI-powered face detection
- **Encrypted Storage**: All face data encrypted locally
- **Password Protection**: Dual security with face + password
- **Real-time Monitoring**: Continuous background protection
- **Grace Period**: 3-second delay before locking (customizable)

#### 🎛️ Customization Options
Edit `config.ini` to customize:
- Detection sensitivity
- Grace period duration
- Camera settings
- Display options
- Security messages

#### 🖥️ User Interface
- **GUI Launcher**: Easy-to-use graphical interface
- **Status Indicators**: Real-time monitoring status
- **Monitor Window**: Optional face detection display
- **System Tray**: Runs quietly in background

### Detailed Setup Process

#### Step 1: System Preparation
1. **Check Camera**: Ensure webcam is connected and working
2. **Close Conflicting Apps**: Close other apps using the camera
3. **Good Lighting**: Ensure adequate lighting on your face
4. **Stable Position**: Sit at normal distance from camera

#### Step 2: Owner Registration
1. **Launch Registration**: Click "Register Owner" in launcher
2. **Set Password**: 
   - Choose a strong password
   - Remember it - you'll need it to unlock
   - Confirm password when prompted
3. **Face Capture**:
   - Position yourself centered in camera view
   - Look directly at camera
   - Press SPACE when face is clearly visible
   - System needs 5 good samples
   - Green rectangle shows face detection
4. **Completion**: Wait for "Registration successful!" message

#### Step 3: Start Monitoring
1. **Begin Protection**: Click "Start Monitoring"
2. **Monitor Window**: Shows live camera feed (optional)
   - Green rectangle = Owner recognized
   - Red rectangle = Unknown person
   - Status text shows current state
3. **Background Operation**: System runs in background
4. **Status Updates**: Launcher shows current protection status

### Using the System

#### Normal Operation
- **Authorized Access**: Screen remains normal when owner is present
- **Unauthorized Detection**: Screen blurs when stranger detected
- **Auto-unlock**: Screen unlocks when owner returns
- **Manual Unlock**: Use Ctrl+Alt+O + password anytime

#### Troubleshooting Common Issues

**Camera Not Working**
```
Problem: "Could not open camera"
Solutions:
- Close other apps using camera (Skype, Teams, etc.)
- Check camera privacy settings in Windows
- Try different USB port for external cameras
- Restart the application
```

**Face Not Recognized**
```
Problem: Owner not being recognized
Solutions:
- Ensure good lighting on face
- Look directly at camera
- Remove glasses/hat if worn during registration
- Re-register if lighting conditions changed significantly
- Adjust similarity threshold in config.ini
```

**Screen Locks Too Quickly**
```
Problem: Screen locks when owner steps away briefly
Solutions:
- Increase grace_period in config.ini
- Disable monitoring when stepping away
- Use Ctrl+Alt+O to quick unlock
```

**Performance Issues**
```
Problem: High CPU usage or slow response
Solutions:
- Increase processing_delay in config.ini
- Lower camera resolution in config.ini
- Close unnecessary applications
- Use "Basic" recognition system instead
```

#### Advanced Configuration

**Config File Settings** (`config.ini`):

```ini
[Security]
GRACE_PERIOD = 5          # Seconds before locking (default: 3)
DETECTION_CONFIDENCE = 0.6 # Lower = more sensitive (default: 0.7)
SIMILARITY_THRESHOLD = 0.7 # Lower = more lenient (default: 0.8)

[Camera]
CAMERA_INDEX = 1          # Use second camera (default: 0)
CAMERA_WIDTH = 1280       # Higher resolution (default: 640)
CAMERA_HEIGHT = 720       # Higher resolution (default: 480)

[Display]
SHOW_MONITOR_WINDOW = False # Hide monitoring window for stealth
SHOW_FACE_RECTANGLES = True # Show face detection boxes

[Performance]
PROCESSING_DELAY = 0.2    # Higher = less CPU usage (default: 0.1)
```

### Security Best Practices

#### Registration Tips
- **Good Lighting**: Register in typical room lighting
- **Multiple Angles**: Slightly move head during capture
- **Consistent Setup**: Register in your normal working position
- **Regular Updates**: Re-register if appearance changes significantly

#### Password Security
- **Strong Password**: Use complex password with mixed characters
- **Unique Password**: Don't reuse passwords from other accounts
- **Secure Storage**: Store password securely (password manager)
- **Regular Changes**: Consider changing password periodically

#### Privacy Considerations
- **Local Processing**: All face data stays on your computer
- **No Network**: System works completely offline
- **Encrypted Storage**: Face data is encrypted on disk
- **Easy Removal**: Delete config files to remove all data

### Multiple Users

To set up for multiple authorized users:
1. **Backup Current Config**: Copy existing .pkl files
2. **Register Each User**: Run registration for each person
3. **Modify Code**: Edit comparison logic to check against all users
4. **Test Thoroughly**: Ensure all users are recognized

### Uninstalling

To completely remove the system:
1. **Stop Monitoring**: Click "Stop Monitoring" in launcher
2. **Delete Files**: Remove entire project folder
3. **Remove Dependencies**: (Optional) `pip uninstall -r requirements.txt`

### Command Line Usage

For advanced users, direct system access:

```bash
# MediaPipe system
python mediapipe_face_security.py

# Camera test
python test_camera.py

# System test
python test_system.py
```

### Troubleshooting Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| "No owner data found" | Not registered yet | Run registration first |
| "Could not open camera" | Camera unavailable | Close other camera apps |
| "Registration failed" | Insufficient samples | Ensure good lighting, try again |
| "Invalid password" | Wrong unlock password | Check caps lock, try again |
| "Import error" | Missing dependencies | Run `pip install -r requirements.txt` |

### Performance Optimization

**For Low-End Systems**:
- Increase `PROCESSING_DELAY` to 0.3
- Reduce camera resolution to 320x240
- Set `SHOW_MONITOR_WINDOW = False`
- Use `GRACE_PERIOD = 5` for less frequent checks

**For High-End Systems**:
- Decrease `PROCESSING_DELAY` to 0.05
- Increase camera resolution to 1280x720
- Set higher detection confidence for accuracy

### Support & Updates

**Getting Help**:
1. Check this user guide first
2. Run `test_system.py` to diagnose issues
3. Check error messages in terminal
4. Verify all dependencies are installed

**Keeping Updated**:
- Backup your configuration files before updates
- Test new versions with `test_system.py`
- Re-register if face recognition accuracy decreases

---

## 🎯 Quick Reference

### Keyboard Shortcuts
- **Ctrl+Alt+O**: Unlock screen
- **Q**: Quit monitoring window
- **Space**: Capture face during registration
- **Esc**: Cancel registration

### File Locations
- **Configuration**: `config.ini`
- **Face Data**: `mediapipe_security_config.pkl` (encrypted)
- **Encryption Key**: `security.key`
- **Logs**: Check terminal output

### Status Indicators
- **🟢 Green**: Owner detected, system active
- **🔴 Red**: Unauthorized person detected
- **⚪ Gray**: System stopped/inactive
- **🚨 Flashing**: Screen locked, unauthorized access

Remember: This system provides privacy protection but should not be your only security measure. Always use proper system passwords and security practices!
