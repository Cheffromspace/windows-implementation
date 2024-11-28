import subprocess
from typing import List, Optional, Tuple
import pyautogui
import win32gui
import win32con
import win32api
import time
import cv2
import numpy as np
from PIL import ImageGrab
import base64
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ComputerControl:
    def __init__(self):
        # Load config from desktop
        config_path = os.path.expanduser("~/Desktop/mcp_config.json")
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except Exception:
            # Default config if file not found or invalid
            self.config = {
                "pyautogui_settings": {"FAILSAFE": True},
                "screen_settings": {
                    "width": win32api.GetSystemMetrics(0),
                    "height": win32api.GetSystemMetrics(1)
                },
                "mouse_settings": {
                    "movement_duration": 0.1,
                    "click_delay": 0.1
                },
                "keyboard_settings": {
                    "type_delay": 0.1
                }
            }

        # Configure PyAutoGUI settings
        pyautogui.FAILSAFE = self.config["pyautogui_settings"]["FAILSAFE"]
        # Get screen resolution from config or system
        self.screen_width = self.config["screen_settings"]["width"]
        self.screen_height = self.config["screen_settings"]["height"]
        # Track mouse state
        self.is_mouse_down = False
        
        logger.debug(f"Screen dimensions: {self.screen_width}x{self.screen_height}")
        
    def get_screen_frame(self) -> str:
        """Capture current screen frame and return as base64 JPEG"""
        try:
            # Capture screen using PIL
            screen = ImageGrab.grab(bbox=(0, 0, self.screen_width, self.screen_height))
            # Convert to numpy array for OpenCV
            frame = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
            # Encode as JPEG
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
            # Convert to base64
            return base64.b64encode(buffer).decode('utf-8')
        except Exception as e:
            return str(e)

    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen dimensions"""
        return (self.screen_width, self.screen_height)

    def _scale_coordinates(self, x: int, y: int) -> Tuple[int, int]:
        """Scale coordinates from browser viewport (900x600) to screen coordinates"""
        # Browser viewport dimensions
        VIEWPORT_WIDTH = 900
        VIEWPORT_HEIGHT = 600

        # Calculate scale factors
        scale_x = self.screen_width / VIEWPORT_WIDTH
        scale_y = self.screen_height / VIEWPORT_HEIGHT

        # Scale coordinates
        scaled_x = int(x * scale_x)
        scaled_y = int(y * scale_y)

        # Log the scaling calculations
        logger.debug(f"Scaling coordinates:")
        logger.debug(f"Input coordinates: ({x}, {y})")
        logger.debug(f"Scale factors: ({scale_x}, {scale_y})")
        logger.debug(f"Scaled coordinates: ({scaled_x}, {scaled_y})")
        
        # Ensure coordinates stay within screen bounds with padding
        PADDING = 10  # Pixels from screen edge
        scaled_x = max(PADDING, min(scaled_x, self.screen_width - PADDING))
        scaled_y = max(PADDING, min(scaled_y, self.screen_height - PADDING))
        
        logger.debug(f"Bounded coordinates: ({scaled_x}, {scaled_y})")
        return scaled_x, scaled_y

    def _focus_window(self, window_title: str = None) -> bool:
        """Focus window by title, or game window if no title provided"""
        try:
            if window_title:
                # Find window by title
                hwnd = win32gui.FindWindow(None, window_title)
            else:
                # Get foreground window if no title provided
                hwnd = win32gui.GetForegroundWindow()
            
            if hwnd:
                # Restore if minimized
                if win32gui.IsIconic(hwnd):
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                # Force focus
                win32gui.SetForegroundWindow(hwnd)
                # Small delay to ensure window is focused
                time.sleep(self.config["mouse_settings"]["click_delay"])
                return True
            return False
        except Exception:
            return False

    def mouse_move(self, x: int, y: int) -> bool:
        """Move mouse to specified coordinates"""
        try:
            x, y = self._scale_coordinates(x, y)
            logger.debug(f"Moving mouse to: ({x}, {y})")
            if self.is_mouse_down:
                pyautogui.dragTo(x, y, duration=self.config["mouse_settings"]["movement_duration"])
            else:
                pyautogui.moveTo(x, y, duration=self.config["mouse_settings"]["movement_duration"])
            return True
        except Exception as e:
            logger.error(f"Mouse move failed: {str(e)}")
            return False

    def mouse_click(self, button: str = "left") -> bool:
        """Click the specified mouse button"""
        try:
            current_x, current_y = win32gui.GetCursorPos()
            logger.debug(f"Clicking at position: ({current_x}, {current_y})")
            
            # Use pyautogui's click instead of win32api.mouse_event
            pyautogui.click(button=button)
            return True
        except Exception as e:
            logger.error(f"Mouse click error: {str(e)}")
            return False

    def double_click(self, x: int = None, y: int = None) -> bool:
        """Perform a double click at current or specified coordinates"""
        try:
            # Move to coordinates if provided
            if x is not None and y is not None:
                self.mouse_move(x, y)
            
            current_x, current_y = win32gui.GetCursorPos()
            logger.debug(f"Double clicking at position: ({current_x}, {current_y})")
            
            # Use pyautogui's doubleClick
            pyautogui.doubleClick()
            return True
        except Exception as e:
            logger.error(f"Double click failed: {str(e)}")
            return False

    def mouse_up(self, button: str = "left") -> bool:
        """Release the specified mouse button"""
        try:
            if button == "left":
                self.is_mouse_down = False
                pyautogui.mouseUp(button=button)
            else:
                pyautogui.mouseUp(button=button)
            return True
        except Exception:
            return False

    def key_press(self, key: str) -> bool:
        """Press a keyboard key"""
        try:
            pyautogui.PAUSE = self.config["keyboard_settings"]["type_delay"]
            pyautogui.press(key)
            return True
        except Exception:
            return False

    def key_combination(self, key: str, ctrl: bool = False, alt: bool = False, shift: bool = False) -> bool:
        """Press a key combination with modifiers"""
        try:
            keys = []
            if ctrl:
                keys.append('ctrl')
            if alt:
                keys.append('alt')
            if shift:
                keys.append('shift')
            keys.append(key)
            
            pyautogui.PAUSE = self.config["keyboard_settings"]["type_delay"]
            pyautogui.hotkey(*keys)
            return True
        except Exception:
            return False

    def type_text(self, text: str) -> bool:
        """Type text"""
        try:
            pyautogui.PAUSE = self.config["keyboard_settings"]["type_delay"]
            pyautogui.write(text)
            return True
        except Exception:
            return False

    def get_cursor_position(self) -> Tuple[int, int]:
        """Get current cursor position"""
        return win32gui.GetCursorPos()

    def drag_mouse(self, x: int, y: int) -> bool:
        """Click and drag to specified coordinates"""
        try:
            x, y = self._scale_coordinates(x, y)
            pyautogui.dragTo(x, y, duration=self.config["mouse_settings"]["movement_duration"])
            return True
        except Exception:
            return False
