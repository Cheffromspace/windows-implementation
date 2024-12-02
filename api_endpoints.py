from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Tuple
from computer_control import ComputerControl
import uvicorn

app = FastAPI(title="Computer Control API")
computer = ComputerControl()

class MousePosition(BaseModel):
    x: int
    y: int

class KeyPress(BaseModel):
    key: str
    ctrl: Optional[bool] = False
    alt: Optional[bool] = False
    shift: Optional[bool] = False

class TextInput(BaseModel):
    text: str

@app.get("/screenshot")
async def get_screenshot():
    """Get current desktop screenshot as base64 encoded JPEG"""
    try:
        screenshot = computer.get_screen_frame()
        return {
            "success": True,
            "message": "Screenshot captured successfully",
            "data": {
                "screenshot": screenshot
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

@app.get("/screen/size")
async def get_screen_size():
    """Get screen dimensions"""
    size = computer.get_screen_size()
    return {"width": size[0], "height": size[1]}

@app.post("/mouse/move")
async def move_mouse(position: MousePosition):
    """Move mouse to specified coordinates"""
    success = computer.mouse_move(position.x, position.y)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to move mouse")
    return {"success": True}

@app.post("/mouse/click")
async def mouse_click(button: str = "left"):
    """Click specified mouse button"""
    success = computer.mouse_click(button)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to click mouse")
    return {"success": True}

@app.post("/mouse/double-click")
async def double_click(position: Optional[MousePosition] = None):
    """Double click at current or specified position"""
    if position:
        success = computer.double_click(position.x, position.y)
    else:
        success = computer.double_click()
    if not success:
        raise HTTPException(status_code=500, detail="Failed to double click")
    return {"success": True}

@app.post("/keyboard/press")
async def press_key(key_data: KeyPress):
    """Press a key with optional modifiers"""
    if key_data.ctrl or key_data.alt or key_data.shift:
        success = computer.key_combination(
            key_data.key,
            ctrl=key_data.ctrl,
            alt=key_data.alt,
            shift=key_data.shift
        )
    else:
        success = computer.key_press(key_data.key)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to press key")
    return {"success": True}

@app.post("/keyboard/type")
async def type_text(text_data: TextInput):
    """Type text"""
    success = computer.type_text(text_data.text)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to type text")
    return {"success": True}

@app.get("/mouse/position")
async def get_cursor_position():
    """Get current cursor position"""
    position = computer.get_cursor_position()
    return {"x": position[0], "y": position[1]}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
