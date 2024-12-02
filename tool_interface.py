from typing import Dict, Any, Optional, List, Union
from computer_control import ComputerControl
import json

class ComputerTools:
    """Tools for controlling computer input/output"""
    
    def __init__(self):
        self.computer = ComputerControl()

    def get_tool_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Return the tool definitions in a format compatible with LLM tool use"""
        return {
            "take_screenshot": {
                "description": "Capture the current screen contents and return as base64 JPEG",
                "parameters": {}
            },
            "mouse_move": {
                "description": "Move the mouse cursor to specified coordinates",
                "parameters": {
                    "x": {
                        "type": "integer",
                        "description": "X coordinate to move to"
                    },
                    "y": {
                        "type": "integer", 
                        "description": "Y coordinate to move to"
                    }
                }
            },
            "mouse_click": {
                "description": "Click the mouse at current position",
                "parameters": {
                    "button": {
                        "type": "string",
                        "description": "Mouse button to click (left/right)",
                        "default": "left"
                    }
                }
            },
            "type_text": {
                "description": "Type text at current cursor position",
                "parameters": {
                    "text": {
                        "type": "string",
                        "description": "Text to type"
                    }
                }
            },
            "key_press": {
                "description": "Press a keyboard key",
                "parameters": {
                    "key": {
                        "type": "string",
                        "description": "Key to press (e.g. Enter, Tab, a, b, etc)"
                    }
                }
            },
            "key_combination": {
                "description": "Press a key combination with modifiers",
                "parameters": {
                    "key": {
                        "type": "string",
                        "description": "Main key to press"
                    },
                    "ctrl": {
                        "type": "boolean",
                        "description": "Hold Ctrl key",
                        "default": False
                    },
                    "alt": {
                        "type": "boolean",
                        "description": "Hold Alt key",
                        "default": False
                    },
                    "shift": {
                        "type": "boolean",
                        "description": "Hold Shift key",
                        "default": False
                    }
                }
            },
            "get_screen_info": {
                "description": "Get screen dimensions and cursor position",
                "parameters": {}
            }
        }

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given parameters and return the result"""
        
        if tool_name == "take_screenshot":
            screenshot = self.computer.get_screen_frame()
            return {"success": bool(screenshot), "screenshot": screenshot}

        elif tool_name == "mouse_move":
            success = self.computer.mouse_move(parameters["x"], parameters["y"])
            return {"success": success}

        elif tool_name == "mouse_click":
            success = self.computer.mouse_click(parameters.get("button", "left"))
            return {"success": success}

        elif tool_name == "type_text":
            success = self.computer.type_text(parameters["text"])
            return {"success": success}

        elif tool_name == "key_press":
            success = self.computer.key_press(parameters["key"])
            return {"success": success}

        elif tool_name == "key_combination":
            success = self.computer.key_combination(
                parameters["key"],
                parameters.get("ctrl", False),
                parameters.get("alt", False),
                parameters.get("shift", False)
            )
            return {"success": success}

        elif tool_name == "get_screen_info":
            size = self.computer.get_screen_size()
            pos = self.computer.get_cursor_position()
            return {
                "screen_width": size[0],
                "screen_height": size[1],
                "cursor_x": pos[0],
                "cursor_y": pos[1]
            }

        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def get_tool_schema(self) -> str:
        """Return the tool definitions as a formatted string"""
        return json.dumps(self.get_tool_definitions(), indent=2)
