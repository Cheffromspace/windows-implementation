from web_interface import socketio, app

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
