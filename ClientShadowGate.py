# Client

from flask import Flask
import secrets

class FlaskServer():

    def __init__(self) -> None:
        self.app = Flask(__name__)
        self.app.secret_key = secrets.token_hex(50)
        self._setup_routes()

    def _setup_routes(self):
        self.app.add_url_rule("/", "index", self.index, methods=['GET'])

    def run(self):
        self.app.run("127.0.0.1", port=8000, debug=True)

    def index(self):
        code_index_html = """

            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>ShadowGate</title>
            </head>
            <body>

                
                <div class="top-section">
                    <span>TARGET</span>
                    <input class="input-target" type="text">
                    <button class="btn-select">SELECT</button>
                </div>
                <div class="terminal">
                    <div class="terminal-output"></div>
                    <input class="terminal-input" type="text" placeholder="Enter command here...">
                </div>

                
            </body>
            </html>

            <style>
                *{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }

                :root {
                    --background-color: #2E3440;   
                    --text-color: #D8DEE9;        
                    --highlight-color: #5E81AC;    
                    --error-color: #BF616A;      
                }

                body{
                    background-color: var(--background-color);
                    display: grid;
                    grid-template-rows: 20% 1fr;
                }

                span{
                    color: var(--text-color);
                    font-size: 25;
                    font-weight: bold;
                }

                .input-target {
                    border: 2px solid var(--highlight-color);
                    background-color: transparent;
                    color: var(--text-color);
                    padding: 10px 15px;
                    font-size: 18px;
                    border-radius: 5px;
                    width: 50vw;
                    outline: none;
                    transition: border-color 0.3s, box-shadow 0.3s;
                }

                .input-target:focus {
                    border-color: var(--text-color);
                    box-shadow: 0 0 8px var(--highlight-color);
                }

                .top-section{
                    width: 100vw;
                    height: 100%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 30px;
                }

                .btn-select {
                    background-color: var(--highlight-color);
                    color: var(--text-color);
                    border: 2px solid var(--highlight-color);
                    padding: 10px 20px;
                    font-size: 18px;
                    font-weight: bold;
                    border-radius: 5px;
                    cursor: pointer;
                    transition: background-color 0.3s, color 0.3s, box-shadow 0.3s;
                }

                .btn-select:hover {
                    background-color: var(--text-color);
                    color: var(--highlight-color);
                    box-shadow: 0 0 8px var(--highlight-color);
                }

                .btn-select:active {
                    background-color: var(--error-color);
                    border-color: var(--error-color);
                }

                .terminal {
                    width: 100vw;
                    height: 100%;
                    padding: 20px;
                    background-color: var(--background-color);
                    color: var(--text-color);
                    font-family: 'Courier New', Courier, monospace;
                    overflow-y: auto;
                    border-top: 2px solid var(--highlight-color);
                    display: flex;
                    flex-direction: column;
                    justify-content: flex-end;
                }

                .terminal-output {
                    flex-grow: 1;
                    white-space: pre-wrap;
                    overflow-y: auto;
                }

                .terminal-input {
                    border: none;
                    background-color: transparent;
                    color: var(--text-color);
                    font-family: inherit;
                    font-size: 16px;
                    outline: none;
                    padding: 10px 0;
                }
            </style>

            <script>
                // Variable pour stocker la cible sélectionnée
                let selectedTarget = '';

                function checkTarget(target) {
                    return fetch(`${selectedTarget}/checkup`)
                        .then(response => {
                            if (response.ok) {
                                return true;
                            } else {
                                throw new Error('Target check failed with status ' + response.status);
                            }
                        })
                        .catch(error => {
                            console.error('Target check error:', error);
                            return false;
                        });
                }

                document.querySelector('.btn-select').addEventListener('click', function() {
                    const targetInput = document.querySelector('.input-target');
                    selectedTarget = targetInput.value.trim();

                    if (selectedTarget) {
                        checkTarget(selectedTarget).then(isValid => {
                            if (isValid) {
                                alert(`Target selected: ${selectedTarget}`);
                            } else {
                                alert('Selected target is not valid.');
                                selectedTarget = ''; // Reset the target if not valid
                            }
                        });
                    } else {
                        alert('Please enter a valid target.');
                    }
                });

                document.querySelector('.terminal-input').addEventListener('keydown', function(event) {
                    if (event.key === 'Enter') {
                        const input = event.target;
                        const command = input.value.trim();
                        const outputDiv = document.querySelector('.terminal-output');

                        if (!selectedTarget) {
                            alert('Please select a target before entering commands.');
                            return;
                        }

                        // Check if the selected target is valid before sending the command
                        checkTarget(selectedTarget).then(isValid => {
                            if (!isValid) {
                                alert('Target is no longer valid. Please select a new target.');
                                selectedTarget = ''; // Reset the target
                                return;
                            }

                            if (command) {
                                if (command.toLowerCase() === 'clear') {
                                    // Effacer l'historique du terminal
                                    outputDiv.innerHTML = '';
                                    input.value = '';
                                    return;
                                }
                                // Affiche la commande dans le terminal
                                const commandElement = document.createElement('p');
                                commandElement.className = 'command-line';
                                commandElement.textContent = `> ${command}`;
                                outputDiv.appendChild(commandElement);

                                // Construire l'URL dynamique en fonction de la cible
                                const url = `${selectedTarget}`;

                                // Envoyer la commande au serveur
                                fetch(url, {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json'
                                    },
                                    body: JSON.stringify({ command: command })
                                })
                                .then(response => {
                                    if (!response.ok) {
                                        throw new Error('Network response was not ok');
                                    }
                                    return response.json();
                                })
                                .then(data => {
                                    // Affiche la réponse du serveur dans le terminal
                                    const responseElement = document.createElement('p');
                                    responseElement.className = 'command-line';
                                    responseElement.textContent = data.response || data.error || 'No response';
                                    outputDiv.appendChild(responseElement);

                                    // Défilement automatique vers le bas
                                    outputDiv.scrollTop = outputDiv.scrollHeight;
                                })
                                .catch(error => {
                                    // Affiche un message d'erreur dans le terminal
                                    const errorElement = document.createElement('p');
                                    errorElement.className = 'command-line';
                                    errorElement.style.color = 'var(--error-color)';
                                    errorElement.textContent = `Error: ${error.message}`;
                                    outputDiv.appendChild(errorElement);
                                });
                            }

                            // Réinitialiser le champ d'entrée
                            input.value = '';
                        });
                    }
                });
            </script>


        """
        return code_index_html
    

if __name__ == "__main__":
    flask_server = FlaskServer()
    flask_server.run()