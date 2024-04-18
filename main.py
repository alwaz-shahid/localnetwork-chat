from flask import Flask, render_template, request, jsonify
import socket
import threading
import random

app = Flask(__name__)

# Global dictionary to store client information and messages
client_data = {}
messages = []
lock = threading.Lock()

def generate_random_color():
    # Generate a random hexadecimal color code
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

def server_thread(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(1)
    print(f"Server listening on port {port}")
    
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        
        # Generate a random name and color for the client
        client_name = f"Client{random.randint(1000, 9999)}"
        client_color = generate_random_color()
        
        with lock:
            client_data[addr] = {'name': client_name, 'color': client_color}
        
        while True:
            msg = client_socket.recv(1024).decode('utf-8')
            if not msg:
                break
            
            print(f"Received from {addr}: {msg}")
            
            with lock:
                messages.append({'name': client_name, 'color': client_color, 'message': msg})
        
        client_socket.close()

@app.route('/')
def index():
    # Get the public IP address of the server
    public_ip = socket.gethostbyname(socket.gethostname())
    
    with lock:
        messages_copy = messages[:]
        client_data_copy = client_data.copy()
    
    return render_template('./index.html', public_ip=public_ip, messages=messages_copy, client_data=client_data_copy)

@app.route('/send', methods=['POST'])
def send_message():
    message = request.form.get('message')
    if message:
        with lock:
            messages.append({'name': 'Server', 'color': '#000000', 'message': message})
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Empty message'})
    
@app.route('/change_name', methods=['POST'])
def change_name():
    new_name = request.form.get('name')
    if new_name:
        addr = request.remote_addr
        with lock:
            if addr in client_data:
                client_data[addr]['name'] = new_name
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Empty name'})

if __name__ == "__main__":
    # Define the port number
    port = 5000
    
    # Start the server thread
    server_thread = threading.Thread(target=server_thread, args=(port,))
    server_thread.start()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000)
