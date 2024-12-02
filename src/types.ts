export interface MousePosition {
  x: number;
  y: number;
}

export interface KeyboardInput {
  text: string;
}

export interface WindowInfo {
  title: string;
  position: {
    x: number;
    y: number;
  };
  size: {
    width: number;
    height: number;
  };
}

export interface ScreenshotResponse {
  screenshot: string;  // base64 encoded image data
  timestamp: string;
}

export interface WindowsControlResponse {
  success: boolean;
  message: string;
  data?: any;
  screenshot?: string;  // base64 encoded image data for screenshot responses
}
