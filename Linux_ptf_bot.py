import socket  # To create a socket for networking
import openai  # To interact with OpenAI's GPT-4 model
import threading  # To handle multiple connections concurrently
import Creds

# Set your OpenAI API key
openai.api_key = Creds.API_KEY


class GPTFTPHoneypotIntegration:
    def __init__(self, honeypot_ip='127.0.0.1', honeypot_port=21):
        # Initialize the integration with the honeypot's IP and port
        self.honeypot_ip = honeypot_ip
        self.honeypot_port = honeypot_port

    def listen_for_commands(self):
        # Create a TCP socket for listening to incoming commands
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Bind the socket to the specified IP and port
            s.bind((self.honeypot_ip, self.honeypot_port))
            s.listen()  # Start listening for incoming connections

            print(f"Listening for commands on {
                  self.honeypot_ip}:{self.honeypot_port}...")

            while True:
                # Accept incoming connections
                # conn is the connection object, addr is the address of the client
                conn, addr = s.accept()
                # Start a new thread to handle the client connection
                threading.Thread(target=self.handle_client,
                                 args=(conn, addr)).start()

    def handle_client(self, conn, addr):
        # Print the address of the connected client
        print(f"Connection from {addr}")
        while True:
            # Receive commands from the client (the hacker)
            command = conn.recv(1024).decode(
                'utf-8').strip()  # Read up to 1024 bytes
            if not command:
                break  # Exit the loop if no command is received

            print(f"Received command: {command}")  # Print the received command
            # Query OpenAI to get a response for the command
            response = self.query_openai(command)
            # Send the response back to the client
            conn.send(response.encode('utf-8'))

        conn.close()  # Close the connection when done

    def query_openai(self, command):
        # Prepare the prompt for the OpenAI API
        prompt = f"You are a helpful FTP server. Respond to the following command: {
            command}"

        try:
            # Send the command to the OpenAI API and get the response
            completion = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    # Format the message for the GPT-4 model
                    {"role": "user", "content": prompt}
                ]
            )
            # Return the generated response from GPT-4
            return completion['choices'][0]['message']['content'].strip()
        except Exception as e:
            # Print any errors encountered while querying OpenAI
            print(f"Error querying OpenAI: {e}")
            return "500 Internal Server Error"  # Return a generic error message


if __name__ == "__main__":
    # Create an instance of the integration class
    honeypot_integration = GPTFTPHoneypotIntegration()
    # Start listening for incoming commands
    honeypot_integration.listen_for_commands()
