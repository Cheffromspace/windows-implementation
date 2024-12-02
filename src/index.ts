import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { 
  ListToolsRequestSchema, 
  CallToolRequestSchema,
  TextContent,
  ImageContent
} from "@modelcontextprotocol/sdk/types.js";
import axios from "axios";
import type { WindowsControlResponse, MousePosition, KeyboardInput, WindowInfo } from "./types.js";

// Parse command line arguments
const args = process.argv.slice(2);
const apiUrlArg = args.find(arg => arg.startsWith('--api-url='));
const API_BASE_URL = apiUrlArg ? apiUrlArg.split('=')[1] : 'http://localhost:5050';
const MCP_PORT = 5051; // Different port for MCP server
const MAX_SCREENSHOT_SIZE = 10 * 1024 * 1024; // 10MB limit

if (!API_BASE_URL.startsWith('http://') && !API_BASE_URL.startsWith('https://')) {
  console.error('Error: API URL must start with http:// or https://');
  process.exit(1);
}

// Type guards for argument validation
function isMousePosition(args: unknown): args is MousePosition {
  if (typeof args !== 'object' || args === null) return false;
  const pos = args as Record<string, unknown>;
  return typeof pos.x === 'number' && typeof pos.y === 'number';
}

function isKeyboardInput(args: unknown): args is KeyboardInput {
  if (typeof args !== 'object' || args === null) return false;
  const input = args as Record<string, unknown>;
  return typeof input.text === 'string';
}

interface ScreenshotOptions {
  quality?: number;
  width?: number;
  height?: number;
}

function isBase64(str: string): boolean {
  const base64Regex = /^[A-Za-z0-9+/]+={0,2}$/;
  return base64Regex.test(str) || str.startsWith('data:image/png;base64,');
}

function sanitizeBase64(data: string): string {
  // Remove data URL prefix if present
  if (data.startsWith('data:image/png;base64,')) {
    return data.replace('data:image/png;base64,', '');
  }
  return data;
}

class WindowsControlServer {
  private server: Server;

  constructor() {
    this.server = new Server({
      name: "windows-control",
      version: "1.0.0",
      port: MCP_PORT
    }, {
      capabilities: {
        tools: {}
      }
    });

    this.setupTools();
    this.setupErrorHandling();
  }

  private setupErrorHandling(): void {
    this.server.onerror = (error) => {
      console.error("[MCP Error]", error);
    };

    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  private setupTools(): void {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: "move_mouse",
          description: "Move the mouse cursor to specific coordinates",
          inputSchema: {
            type: "object",
            properties: {
              x: { type: "number", description: "X coordinate" },
              y: { type: "number", description: "Y coordinate" }
            },
            required: ["x", "y"]
          }
        },
        {
          name: "click_mouse",
          description: "Click the mouse at the current position",
          inputSchema: {
            type: "object",
            properties: {
              button: { 
                type: "string", 
                enum: ["left", "right", "middle"],
                default: "left",
                description: "Mouse button to click" 
              }
            }
          }
        },
        {
          name: "type_text",
          description: "Type text using the keyboard",
          inputSchema: {
            type: "object",
            properties: {
              text: { type: "string", description: "Text to type" }
            },
            required: ["text"]
          }
        },
        {
          name: "press_key",
          description: "Press a specific keyboard key",
          inputSchema: {
            type: "object",
            properties: {
              key: { 
                type: "string",
                description: "Key to press (e.g., 'enter', 'tab', 'escape')" 
              }
            },
            required: ["key"]
          }
        },
        {
          name: "get_screen_size",
          description: "Get the screen dimensions",
          inputSchema: {
            type: "object",
            properties: {}
          }
        },
        {
          name: "get_screenshot",
          description: "Take a screenshot of the current screen",
          inputSchema: {
            type: "object",
            properties: {
              quality: {
                type: "number",
                description: "Image quality (1-100)",
                minimum: 1,
                maximum: 100
              },
              width: {
                type: "number",
                description: "Maximum width in pixels"
              },
              height: {
                type: "number",
                description: "Maximum height in pixels"
              }
            }
          }
        },
        {
          name: "get_cursor_position",
          description: "Get the current cursor position",
          inputSchema: {
            type: "object",
            properties: {}
          }
        },
        {
          name: "double_click",
          description: "Double click at current or specified position",
          inputSchema: {
            type: "object",
            properties: {
              x: { type: "number", description: "X coordinate (optional)" },
              y: { type: "number", description: "Y coordinate (optional)" }
            }
          }
        }
      ]
    }));

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        let response: WindowsControlResponse;

        switch (name) {
          case "move_mouse":
            if (!isMousePosition(args)) {
              throw new Error("Invalid mouse position arguments");
            }
            response = await this.moveMouse(args);
            break;

          case "click_mouse":
            response = await this.clickMouse(
              typeof args?.button === 'string' ? args.button : 'left'
            );
            break;

          case "type_text":
            if (!isKeyboardInput(args)) {
              throw new Error("Invalid keyboard input arguments");
            }
            response = await this.typeText(args);
            break;

          case "press_key":
            if (typeof args?.key !== 'string') {
              throw new Error("Invalid key press arguments");
            }
            response = await this.pressKey(args.key);
            break;

          case "get_screen_size":
            response = await this.getScreenSize();
            break;

          case "get_screenshot":
            const options: ScreenshotOptions = {
              quality: typeof args?.quality === 'number' ? args.quality : undefined,
              width: typeof args?.width === 'number' ? args.width : undefined,
              height: typeof args?.height === 'number' ? args.height : undefined
            };
            response = await this.getScreenshot(options);
            
            // For screenshots, we'll handle the response differently
            if (response.success && response.data?.screenshot) {
              let imageData = response.data.screenshot;
              
              // Verify and sanitize base64 data
              if (!isBase64(imageData)) {
                throw new Error("Invalid screenshot data format");
              }
              
              imageData = sanitizeBase64(imageData);
              
              // Check size
              const estimatedSize = Math.ceil(imageData.length * 0.75);
              if (estimatedSize > MAX_SCREENSHOT_SIZE) {
                throw new Error(`Screenshot too large (${Math.ceil(estimatedSize / 1024 / 1024)}MB)`);
              }

              // Return only the image content
              return {
                content: [{
                  type: "image",
                  data: imageData,
                  mimeType: "image/png"
                }]
              };
            }
            break;

          case "get_cursor_position":
            response = await this.getCursorPosition();
            break;

          case "double_click":
            if (args && typeof args.x === 'number' && typeof args.y === 'number') {
              response = await this.doubleClick({ x: args.x, y: args.y });
            } else {
              response = await this.doubleClick();
            }
            break;

          default:
            throw new Error(`Unknown tool: ${name}`);
        }

        // For non-screenshot responses, return as text
        return {
          content: [{
            type: "text",
            text: JSON.stringify(response, null, 2)
          }]
        };

      } catch (error) {
        const errorContent: TextContent = {
          type: "text",
          text: `Error: ${error instanceof Error ? error.message : String(error)}`
        };

        return {
          content: [errorContent],
          isError: true
        };
      }
    });
  }

  private async makeRequest(endpoint: string, method: string = 'GET', data?: any): Promise<WindowsControlResponse> {
    try {
      const response = await axios({
        method,
        url: `${API_BASE_URL}${endpoint}`,
        data
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`API error: ${error.response?.data?.message || error.message}`);
      }
      throw error;
    }
  }

  private async moveMouse(position: MousePosition): Promise<WindowsControlResponse> {
    return this.makeRequest('/mouse/move', 'POST', position);
  }

  private async clickMouse(button: string): Promise<WindowsControlResponse> {
    return this.makeRequest('/mouse/click', 'POST', { button });
  }

  private async typeText(input: KeyboardInput): Promise<WindowsControlResponse> {
    return this.makeRequest('/keyboard/type', 'POST', input);
  }

  private async pressKey(key: string): Promise<WindowsControlResponse> {
    return this.makeRequest('/keyboard/press', 'POST', { key });
  }

  private async getScreenSize(): Promise<WindowsControlResponse> {
    return this.makeRequest('/screen/size');
  }

  private async getScreenshot(options?: ScreenshotOptions): Promise<WindowsControlResponse> {
    try {
      const response = await this.makeRequest('/screenshot', 'GET', options);
      
      if (response.success && response.data?.screenshot) {
        if (!isBase64(response.data.screenshot)) {
          throw new Error("Screenshot data is not properly encoded");
        }

        const imageData = sanitizeBase64(response.data.screenshot);
        const estimatedSize = Math.ceil(imageData.length * 0.75);
        
        if (estimatedSize > MAX_SCREENSHOT_SIZE) {
          throw new Error(`Screenshot exceeds size limit of ${MAX_SCREENSHOT_SIZE / 1024 / 1024}MB`);
        }

        return {
          success: true,
          message: "Screenshot captured successfully",
          data: {
            screenshot: imageData
          }
        };
      }
      return response;
    } catch (error) {
      if (error instanceof Error) {
        return {
          success: false,
          message: `Screenshot failed: ${error.message}`
        };
      }
      throw error;
    }
  }

  private async getCursorPosition(): Promise<WindowsControlResponse> {
    return this.makeRequest('/mouse/position');
  }

  private async doubleClick(position?: MousePosition): Promise<WindowsControlResponse> {
    return this.makeRequest('/mouse/double-click', 'POST', position);
  }

  async run(): Promise<void> {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error(`Windows Control MCP server running on port ${MCP_PORT} (API URL: ${API_BASE_URL})`);
  }
}

const server = new WindowsControlServer();
server.run().catch(console.error);