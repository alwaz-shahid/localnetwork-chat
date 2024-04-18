from flask import Flask, render_template, request, jsonify
import socket
import threading

app = Flask(__name__)

# Global variable to store messages
messages = []

def server_thread(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(1)
    print(f"Server listening on port {port}")
    
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        
        msg = client_socket.recv(1024).decode('utf-8')
        print(f"Received: {msg}")
        
        messages.append(msg)
        
        client_socket.send("Message received".encode('utf-8'))
        client_socket.close()

@app.route('/')
def index():
    # Get the public IP address of the server
    public_ip = socket.gethostbyname(socket.gethostname())
    return render_template('./index.html', public_ip=public_ip, messages=messages)

@app.route('/send', methods=['POST'])
def send_message():
    message = request.form['message']
    messages.append(message)
    return jsonify({'status': 'success'})

if __name__ == "__main__":
    # Define the port number
    port = 12345
    
    # Start the server thread
    server_thread = threading.Thread(target=server_thread, args=(port,))
    server_thread.start()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000)
