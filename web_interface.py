from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
from command_router import CommandRouter
from computer_control import ComputerControl
import logging
import time
import threading
from engineio.async_drivers import threading as async_threading

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, 
                   cors_allowed_origins="*",
                   async_mode='threading',
                   logger=True,
                   engineio_logger=True)

router = CommandRouter()
computer = ComputerControl()

# Flag to control streaming
streaming = False

def stream_desktop():
    """Stream desktop frames over WebSocket"""
    global streaming
    logger.info("Starting desktop stream")
    while streaming:
        try:
            frame = computer.get_screen_frame()
            socketio.emit('desktop_frame', {'frame': frame})
            time.sleep(1/30)  # 30 FPS
        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            break
    logger.info("Stopping desktop stream")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')
    # Send screen dimensions to client
    screen_size = computer.get_screen_size()
    emit('screen_dimensions', {
        'width': screen_size[0],
        'height': screen_size[1]
    })
    # Start streaming
    global streaming
    if not streaming:
        streaming = True
        threading.Thread(target=stream_desktop, daemon=True).start()

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')
    global streaming
    streaming = False

@socketio.on('mouse_move')
def handle_mouse_move(data):
    try:
        x, y = data['x'], data['y']
        computer.mouse_move(x, y)
    except Exception as e:
        logger.error(f"Mouse move error: {str(e)}")

@socketio.on('mouse_click')
def handle_mouse_click(*args):
    try:
        computer.mouse_click()
    except Exception as e:
        logger.error(f"Mouse click error: {str(e)}")

@socketio.on('key_press')
def handle_key_press(data):
    try:
        key = data['key']
        logger.debug(f"Received key press: {data}")
        
        # Handle regular keys and modifiers
        modifiers = {
            'ctrl': data.get('ctrl', False),
            'alt': data.get('alt', False),
            'shift': data.get('shift', False)
        }
        
        if any(modifiers.values()):
            # Handle key combinations
            computer.key_combination(key, **modifiers)
        else:
            # Handle single key press
            computer.key_press(key)
            
            # Add small delay after Enter key
            if key.lower() == 'enter':
                time.sleep(0.1)
                
        logger.debug(f"Processed key press: {key}")
    except Exception as e:
        logger.error(f"Key press error: {str(e)}")

@app.route('/api/computer', methods=['POST'])
def handle_computer():
    data = request.json
    action = data.get('action')
    logger.info(f'Computer control action: {action}')
    
    if action == 'mouse_move':
        coords = data.get('coordinate', [0, 0])
        success = computer.mouse_move(coords[0], coords[1])
        return jsonify({'success': success})
    
    elif action == 'type':
        text = data.get('text', '')
        success = computer.type_text(text)
        return jsonify({'success': success})
    
    elif action == 'key':
        key = data.get('text', '')
        success = computer.key_press(key)
        return jsonify({'success': success})
    
    elif action == 'cursor_position':
        pos = computer.get_cursor_position()
        return jsonify({'position': pos})
    
    return jsonify({'error': f'Unknown action: {action}'})

if __name__ == '__main__':
    try:
        logger.info("Starting server...")
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
