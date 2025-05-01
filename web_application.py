from flask import Flask, jsonify, request, send_from_directory, abort
import time
import os

app = Flask(__name__)

# Serve static files (favicon, image, etc.)
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# Basic route
@app.route('/')
def index():
    return "Welcome to Flask test server behind mini-Nginx!"

# Simple API
@app.route('/api/hello')
def hello_api():
    return jsonify(message="Hello from backend")

# POST echo
@app.route('/api/echo', methods=['POST'])
def echo():
    '''
    body ={
    'name':'prasad'
    }
    '''
    data = request.form.get('name')
    return jsonify(received=data)

# Error simulation
@app.route('/api/error')
def error_route():
    abort(500)

# Delayed response to simulate timeout
@app.route('/api/slow')
def slow():
    time.sleep(5)
    return "Delayed response"

# Dynamic route
@app.route('/api/user/<username>')
def user_profile(username):
    return jsonify(user=username)

# 404 fallback
@app.errorhandler(404)
def not_found(e):
    return jsonify(error="Not Found"), 404

# 500 error handler
@app.errorhandler(500)
def internal_error(e):
    return jsonify(error="Internal Server Error"), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
