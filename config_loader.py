"""
Configuration loader for Face Security System
Loads settings from config.ini file
"""

import configparser
import os

class Config:
    def __init__(self, config_file='config.ini'):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        """Load configuration from file with defaults"""
        # Set default values
        self.config['Security'] = {
            'GRACE_PERIOD': '3',
            'DETECTION_CONFIDENCE': '0.7',
            'SIMILARITY_THRESHOLD': '0.8',
            'REGISTRATION_SAMPLES': '5'
        }
        
        self.config['Camera'] = {
            'CAMERA_INDEX': '0',
            'CAMERA_WIDTH': '640',
            'CAMERA_HEIGHT': '480',
            'CAMERA_FPS': '30'
        }
        
        self.config['Display'] = {
            'SHOW_MONITOR_WINDOW': 'True',
            'SHOW_FACE_RECTANGLES': 'True',
            'MONITOR_WINDOW_TITLE': 'Face Security Monitor'
        }
        
        self.config['Security_Messages'] = {
            'LOCK_MESSAGE': '''a''',
            'UNLOCK_HOTKEY': 'ctrl+alt+o'
        }
        
        self.config['Files'] = {
            'MEDIAPIPE_CONFIG_FILE': 'mediapipe_security_config.pkl',
            'BASIC_CONFIG_FILE': 'face_security_config.pkl',
            'ENCRYPTION_KEY_FILE': 'security.key'
        }
        
        self.config['Performance'] = {
            'PROCESSING_DELAY': '0.1',
            'DETECTION_INTERVAL': '1.0'
        }
        
        # Load from file if it exists
        if os.path.exists(self.config_file):
            try:
                self.config.read(self.config_file, encoding='utf-8')
            except Exception as e:
                print(f"Error reading config file: {e}")
                # Try to read with default encoding
                try:
                    self.config.read(self.config_file)
                except:
                    print("Using default configuration due to config file error")
        else:
            # Create default config file
            self.save_config()
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
        except Exception as e:
            print(f"Error saving config file: {e}")
    
    def get_int(self, section, key):
        """Get integer value from config"""
        try:
            return self.config.getint(section, key)
        except:
            return 0
    
    def get_float(self, section, key):
        """Get float value from config"""
        try:
            return self.config.getfloat(section, key)
        except:
            return 0.0
    
    def get_bool(self, section, key):
        """Get boolean value from config"""
        try:
            return self.config.getboolean(section, key)
        except:
            return False
    
    def get_string(self, section, key):
        """Get string value from config"""
        try:
            return self.config.get(section, key)
        except:
            return ""
    
    # Convenience properties
    @property
    def grace_period(self):
        return self.get_int('Security', 'GRACE_PERIOD')
    
    @property
    def detection_confidence(self):
        return self.get_float('Security', 'DETECTION_CONFIDENCE')
    
    @property
    def similarity_threshold(self):
        return self.get_float('Security', 'SIMILARITY_THRESHOLD')
    
    @property
    def registration_samples(self):
        return self.get_int('Security', 'REGISTRATION_SAMPLES')
    
    @property
    def camera_index(self):
        return self.get_int('Camera', 'CAMERA_INDEX')
    
    @property
    def camera_width(self):
        return self.get_int('Camera', 'CAMERA_WIDTH')
    
    @property
    def camera_height(self):
        return self.get_int('Camera', 'CAMERA_HEIGHT')
    
    @property
    def camera_fps(self):
        return self.get_int('Camera', 'CAMERA_FPS')
    
    @property
    def show_monitor_window(self):
        return self.get_bool('Display', 'SHOW_MONITOR_WINDOW')
    
    @property
    def show_face_rectangles(self):
        return self.get_bool('Display', 'SHOW_FACE_RECTANGLES')
    
    @property
    def monitor_window_title(self):
        return self.get_string('Display', 'MONITOR_WINDOW_TITLE')
    
    @property
    def lock_message(self):
        return self.get_string('Security_Messages', 'LOCK_MESSAGE')
    
    @property
    def unlock_hotkey(self):
        return self.get_string('Security_Messages', 'UNLOCK_HOTKEY')
    
    @property
    def mediapipe_config_file(self):
        return self.get_string('Files', 'MEDIAPIPE_CONFIG_FILE')
    
    @property
    def basic_config_file(self):
        return self.get_string('Files', 'BASIC_CONFIG_FILE')
    
    @property
    def encryption_key_file(self):
        return self.get_string('Files', 'ENCRYPTION_KEY_FILE')
    
    @property
    def processing_delay(self):
        return self.get_float('Performance', 'PROCESSING_DELAY')
    
    @property
    def detection_interval(self):
        return self.get_float('Performance', 'DETECTION_INTERVAL')
    
    # Blur effect properties
    @property
    def enable_screen_blur(self):
        return self.get_bool('Blur_Effect', 'ENABLE_SCREEN_BLUR')
    
    @property
    def blur_intensity(self):
        return self.get_int('Blur_Effect', 'BLUR_INTENSITY')
    
    @property
    def blur_quality_reduction(self):
        return self.get_int('Blur_Effect', 'BLUR_QUALITY_REDUCTION')
    
    @property
    def blur_overlay_darkness(self):
        return self.get_int('Blur_Effect', 'BLUR_OVERLAY_DARKNESS')

# Global config instance
config = Config()
