# Windows Control MCP Project Knowledge Graph

## Entities

### Project
- **Windows-Control-MCP**
  - Main project implementing Windows control through Model Context Protocol
  - Built with TypeScript, Python, and FastAPI
  - Enables Claude to control Windows through secure API interface
  - Uses three-layer architecture

### Components
- **MCP-Server-Layer**
  - Built with TypeScript
  - Handles Claude interaction
  - Processes commands
  - Part of three-layer architecture

- **API-Layer**
  - Built with Python/FastAPI
  - Provides RESTful endpoints
  - Handles system control requests
  - Middle layer of architecture

- **Computer-Control-Layer**
  - Built in Python
  - Manages low-level Windows operations
  - Bottom layer of architecture
  - Implements actual system control

### Features
- **System-Features**
  - Mouse Operations: movement, clicks, drag operations
  - Keyboard Input: typing, special keys, combinations
  - Screen Operations: screenshots, dimension detection
  - Window Management: focus control, state management

- **Security-Features**
  - Input Validation: coordinate checking, key mapping
  - Safety Measures: PyAutoGUI failsafe, boundary protection
  - Error Handling: exception handling, logging, recovery

### Technology
- **Tech-Stack**
  - Frontend: TypeScript, MCP SDK, Axios
  - Backend: Python 3.8+, FastAPI, Uvicorn, Pydantic
  - System Integration: PyAutoGUI, Win32GUI, OpenCV, PIL, NumPy

## Relationships
1. Windows-Control-MCP contains MCP-Server-Layer
2. Windows-Control-MCP contains API-Layer
3. Windows-Control-MCP contains Computer-Control-Layer
4. Windows-Control-MCP implements System-Features
5. Windows-Control-MCP implements Security-Features
6. Windows-Control-MCP uses Tech-Stack
7. MCP-Server-Layer communicates_with API-Layer
8. API-Layer controls Computer-Control-Layer