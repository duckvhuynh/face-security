# Face Security System

A comprehensive Python application that uses facial recognition to protect your computer screen. When an unauthorized person is detected looking at your screen, it automatically blurs the display for privacy protection.

## Features

- **🔒 Advanced Facial Recognition Security**: Uses AI-powered computer vision to identify authorized users
- **� Multi-Person Detection**: Enhanced security that locks screen when multiple people are present
- **�📱 Owner Registration**: Secure registration process with password protection  
- **🖥️ Intelligent Screen Protection**: Automatically blurs screen based on sophisticated security rules
- **⌨️ Emergency Hotkey Unlock**: Quick unlock with Ctrl+Alt+O password prompt
- **🔐 Military-Grade Encryption**: Face data is securely encrypted and stored locally
- **⚡ Real-time Monitoring**: Low-latency face detection with minimal CPU usage
- **🎯 Dual AI Systems**: Choose between MediaPipe (advanced) or face_recognition (reliable) backends

## Enhanced Security Logic

The system now implements sophisticated multi-person detection:

### Security Rules:
- ✅ **Owner Alone**: Screen remains unlocked when only the owner is detected
- 🔒 **Owner + Others**: Screen locks immediately when owner is present with other people  
- 🔒 **Unauthorized Only**: Screen locks when only unauthorized persons are detected
- 🔒 **Multiple Unauthorized**: Screen locks when multiple unauthorized people are detected
- ⏸️ **No Faces**: No change in security state

### Why Multi-Person Locking?
This prevents "shoulder surfing" and unauthorized viewing even when the owner is present, providing enterprise-grade security for sensitive work environments.

## Requirements

- Python 3.8 or higher
- Windows OS (tested on Windows 10/11)
- Webcam/Camera
- Internet connection for initial package installation

## Installation

1. **Clone or Download** this repository to your computer

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   Or install manually:
   ```bash
   pip install opencv-python mediapipe numpy Pillow cryptography pywin32 keyboard scikit-learn
   ```

3. **Verify Installation**:
   ```bash
   python launcher.py
   ```

## Quick Start

1. **Launch the Application**:
   ```bash
   python launcher.py
   ```

2. **Register as Owner** (First Time):
   - Click "👤 Register Owner"
   - Set a secure password
   - Position yourself in front of the camera
   - Press SPACE to capture face samples (5 needed)
   - Wait for confirmation

3. **Start Monitoring**:
   - Click "🔍 Start Monitoring"
   - Your screen is now protected!

4. **If Screen Gets Locked**:
   - Press `Ctrl+Alt+O`
   - Enter your password
   - Screen will unlock

## How It Works

### Registration Process
1. **Password Setup**: You create a secure password for unlocking
2. **Face Capture**: System captures multiple face samples for accuracy
3. **Encryption**: Face data is encrypted and stored securely
4. **Verification**: System confirms successful registration

### Monitoring Process
1. **Real-time Detection**: Continuously monitors webcam feed
2. **Face Recognition**: Compares detected faces with registered owner
3. **Security Response**: If unauthorized person detected:
   - 3-second grace period
   - Screen blurs with security message
   - All attempts logged
4. **Automatic Unlock**: When owner returns, screen unlocks automatically

### Security Features
- **Encrypted Storage**: All face data encrypted with Fernet encryption
- **Password Protection**: Registration and unlock require password
- **Grace Period**: 3-second delay before locking (configurable)
- **Hotkey Override**: Emergency unlock with Ctrl+Alt+O
- **Visual Feedback**: Clear status indicators and warnings

## Configuration Options

### System Selection
- **MediaPipe System**: Fast, accurate, recommended for most users
- **Basic System**: Compatible fallback using face_recognition library

### Customizable Settings
You can modify these in the source code:

```python
# In MediaPipeFaceSecuritySystem class
self.grace_period = 3  # Seconds before screen locks
self.face_detection_interval = 1.0  # Detection frequency
```

## File Structure

```
blurscreen/
├── launcher.py                    # Main GUI launcher
├── mediapipe_face_security.py     # MediaPipe-based system
├── face_security_system.py        # Basic face recognition system
├── requirements.txt               # Python dependencies
├── README.md                      # This file
├── security.key                   # Encryption key (auto-generated)
├── mediapipe_security_config.pkl  # Encrypted face data
└── face_security_config.pkl       # Alternative face data storage
```

## Troubleshooting

### Camera Not Working
- **Check Permissions**: Ensure camera access is allowed
- **Close Other Apps**: Close applications using the camera
- **Driver Update**: Update camera drivers
- **USB Camera**: Try different USB port if using external camera

### Face Detection Issues
- **Lighting**: Ensure good lighting on your face
- **Distance**: Sit 2-3 feet from camera
- **Angle**: Look directly at camera during registration
- **Stability**: Minimize head movement during capture

### Screen Lock Problems
- **Password**: Ensure caps lock is off when entering password
- **Hotkey**: Use Ctrl+Alt+O to force unlock prompt
- **Multiple Faces**: Ensure only owner is visible during unlock

### Performance Issues
- **Close Apps**: Close unnecessary applications
- **Lower Resolution**: Use lower camera resolution if available
- **System Choice**: Try different recognition system in launcher

## Advanced Usage

### Command Line Interface
You can also run the systems directly:

```bash
# MediaPipe system
python mediapipe_face_security.py

# Basic system  
python face_security_system.py
```

### Stealth Mode
To run without showing the monitoring window, comment out these lines in the source:

```python
# cv2.imshow('Face Security Monitor', frame)
```

### Multiple Users
To register multiple authorized users, modify the registration system to store multiple face encodings in the configuration.

## Security Considerations

### Data Protection
- Face data is encrypted and stored locally only
- No data is transmitted over the network
- Encryption key is generated uniquely per installation

### Privacy
- Camera feed is processed locally
- No screenshots or recordings are saved
- System can be completely disabled at any time

### Limitations
- Requires good lighting conditions
- May not work with identical twins
- Glasses, hats, or face coverings may affect recognition
- System can be bypassed by covering camera

## Contributing

Feel free to contribute improvements:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

### Ideas for Enhancement
- Mobile app integration
- Multiple camera support
- Facial expression-based unlocking
- Integration with system login
- Cloud backup for settings

## License

This project is provided for educational and personal use. Please ensure compliance with local privacy laws when using facial recognition technology.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review error messages carefully
3. Ensure all dependencies are installed
4. Verify camera functionality with other applications

## Changelog

### Version 1.0
- Initial release
- MediaPipe and basic face recognition support
- Encrypted data storage
- GUI launcher
- Screen blur protection
- Password unlock system

## Disclaimer

This software is provided "as is" without warranty. Users are responsible for ensuring compliance with applicable laws and regulations regarding privacy and surveillance in their jurisdiction.
