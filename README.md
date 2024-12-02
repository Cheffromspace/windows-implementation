# Windows Control MCP Server

This MCP server provides an interface for Claude to control Windows through API endpoints while viewing a live desktop stream.

## Prerequisites

- Node.js 18 or higher
- Python 3.8 or higher
- Windows 10 or higher

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Build the MCP server:
```bash
npm run build
```

## Usage with Claude Desktop

1. Start the Python API server:
```bash
python main.py
```
This will start the API server on port 8000.

2. Add this configuration to your Claude Desktop config file (`%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "windows-control": {
      "command": "C:\\Program Files\\nodejs\\node.exe",
      "args": [
        "C:\\Users\\YourUsername\\path\\to\\windows-implementation\\dist\\index.js",
        "--api-url=http://localhost:8000"
      ],
      "cwd": "C:\\Users\\YourUsername\\path\\to\\windows-implementation"
    }
  }
}
```

Replace:
- `YourUsername` with your Windows username
- `path\\to\\windows-implementation` with the actual path to this project
- `http://localhost:8000` with your Python API server URL if different

Note: All Windows paths must:
- Use absolute paths (starting with `C:\\` or appropriate drive letter)
- Use double backslashes (`\\`) to escape path separators
- Point to the exact file locations on your system

### Configuration Options

- `--api-url`: The URL of the Python API server (default: `http://localhost:8000`)

## Available Tools

The MCP server provides the following tools:

- `move_mouse`: Move the mouse cursor to specific coordinates
  - Parameters: `x` (number), `y` (number)

- `click_mouse`: Click the mouse at the current position
  - Optional parameter: `button` ("left", "right", "middle")

- `double_click`: Double click at current or specified position
  - Optional parameters: `x` (number), `y` (number)

- `type_text`: Type text using the keyboard
  - Parameter: `text` (string)

- `press_key`: Press a specific keyboard key
  - Parameter: `key` (string) - e.g., 'enter', 'tab', 'escape'

- `get_screen_size`: Get the screen dimensions
  - No parameters required

- `get_screenshot`: Take a screenshot of the current screen
  - No parameters required

- `get_cursor_position`: Get the current cursor position
  - No parameters required

## Example Usage in Claude

Once connected, you can ask Claude to perform actions like:

```
Can you move the mouse to coordinates (100, 100) and click?
```

```
Could you type "Hello, World!" into the active window?
```

```
Please take a screenshot of my current screen.
```

```
What are my screen dimensions?
```

```
Where is my mouse cursor currently positioned?
```

## Development

To run in development mode with automatic recompilation:

```bash
npm run dev
```

To run with a custom API URL:

```bash
npm start -- --api-url=http://localhost:8000
```

## Architecture

This project consists of two main components:

1. A Python API server that handles the actual Windows control operations
2. An MCP server written in TypeScript that provides a standardized interface for Claude to interact with the Windows control functionality

The MCP server acts as an adapter layer, translating Claude's requests into API calls to the Python server.

### API Server Communication

The MCP server communicates with the Python API server over HTTP. By default, it expects the API server to be running at `http://localhost:8000`, but this can be configured using the `--api-url` argument.

The API server provides endpoints for:
- Mouse control (`/mouse/move`, `/mouse/click`, `/mouse/double-click`, `/mouse/position`)
- Keyboard input (`/keyboard/type`, `/keyboard/press`)
- Screen information (`/screen/size`, `/screenshot`)

All API endpoints return a standardized response format:
```typescript
{
  success: boolean;
  message: string;
  data?: any;
}
```

### Windows Path Requirements

When configuring the MCP server in Claude Desktop's config file, it's important to follow Windows path conventions:

1. Use absolute paths starting with the drive letter (e.g., `C:\\`)
2. Escape backslashes by doubling them (e.g., `C:\\Users\\YourUsername`)
3. Point to the exact file locations on your system

Example of a properly formatted config:
```json
{
  "mcpServers": {
    "windows-control": {
      "command": "C:\\Program Files\\nodejs\\node.exe",
      "args": [
        "C:\\Users\\YourUsername\\Projects\\windows-implementation\\dist\\index.js",
        "--api-url=http://localhost:8000"
      ],
      "cwd": "C:\\Users\\YourUsername\\Projects\\windows-implementation"
    }
  }
}
