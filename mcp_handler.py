import logging
import asyncio
from mcp.server import Server
import mcp.types as types
from computer_control import ComputerControl
from command_router import CommandRouter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("windows-control")

# Initialize server and components
server = Server("windows-control")
computer = ComputerControl()
router = CommandRouter()

@server.call_tool()
async def execute_command(command: str) -> list[types.TextContent]:
    """Execute a CLI command on the system"""
    if command.startswith("wsl") or "bash" in command:
        result = router.run_bash(command)
    else:
        result = router.run_powershell(command)
    return [types.TextContent(type="text", text=result)]

@server.call_tool()
async def get_screen() -> list[types.ImageContent]:
    """Capture the current screen state"""
    frame = computer.get_screen_frame()
    screen_size = computer.get_screen_size()
    return [types.ImageContent(
        type="image",
        image=frame,
        metadata={
            "width": screen_size[0],
            "height": screen_size[1]
        }
    )]

@server.call_tool()
async def mouse_move(coordinate: str) -> list[types.TextContent]:
    """Move the mouse cursor to specified coordinates"""
    try:
        x, y = map(int, coordinate.split(","))
        success = computer.mouse_move(x, y)
        if success:
            return [types.TextContent(type="text", text=f"Mouse moved to {x},{y}")]
        else:
            return [types.TextContent(type="text", text="Failed to move mouse")]
    except ValueError:
        raise ValueError("Invalid coordinate format")

@server.call_tool()
async def mouse_click() -> list[types.TextContent]:
    """Perform a mouse click at the current cursor position"""
    success = computer.mouse_click()
    pos = computer.get_cursor_position()
    if success:
        return [types.TextContent(type="text", text=f"Clicked at {pos[0]},{pos[1]}")]
    else:
        return [types.TextContent(type="text", text="Failed to click")]

@server.call_tool()
async def type_text(text: str) -> list[types.TextContent]:
    """Type text using the keyboard"""
    success = computer.type_text(text)
    if success:
        return [types.TextContent(type="text", text=f"Typed: {text}")]
    else:
        return [types.TextContent(type="text", text="Failed to type text")]

@server.call_tool()
async def key_press(key: str) -> list[types.TextContent]:
    """Press a specific keyboard key"""
    success = computer.key_press(key)
    if success:
        return [types.TextContent(type="text", text=f"Pressed key: {key}")]
    else:
        return [types.TextContent(type="text", text="Failed to press key")]

@server.call_tool()
async def get_cursor_position() -> list[types.TextContent]:
    """Get the current cursor position"""
    pos = computer.get_cursor_position()
    return [types.TextContent(type="text", text=f"Cursor at {pos[0]},{pos[1]}")]
