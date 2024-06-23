import os

def handle_recv():
    input_pipe = "CTOPYTHON"
    if not os.path.exists(input_pipe):
        os.mkfifo(input_pipe)

    while True:
        with open(input_pipe, 'r') as fifo:
            message = fifo.read()
            if message:
                print(f"Received from C: {message}")

def handle_send():
    output_pipe = "PYTHONTOC"
    if not os.path.exists(output_pipe):
        os.mkfifo(output_pipe)

    while True:
        message = input("Enter message to send to C: ")
        with open(output_pipe, 'w') as fifo:
            fifo.write(message)
            print(f"Message sent to C: {message}")
