#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <pthread.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/stat.h>

#define C_TO_PYTHON "CTOPYTHON"

void receiving(int server_fd);
void *receive_thread(void *server_fd);
void send_to_python(char* message);

int main(int argc, char const *argv[]) {
    int PORT = 9999;
    int server_fd;
    struct sockaddr_in address;

    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = inet_addr("127.0.0.1");
    address.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, 5) < 0) {
        perror("listen");
        exit(EXIT_FAILURE);
    }

    pthread_t tid;
    pthread_create(&tid, NULL, &receive_thread, &server_fd);
    pthread_join(tid, NULL);

    close(server_fd);
    return 0;
}

void *receive_thread(void *server_fd) {
    int s_fd = *((int *)server_fd);
    while (1) {
        receiving(s_fd);
    }
}

void receiving(int server_fd) {
    struct sockaddr_in address;
    int valread;
    char buffer[2000] = {0};
    int addrlen = sizeof(address);
    fd_set current_sockets, ready_sockets;

    FD_ZERO(&current_sockets);
    FD_SET(server_fd, &current_sockets);

    while (1) {
        ready_sockets = current_sockets;

        if (select(FD_SETSIZE, &ready_sockets, NULL, NULL, NULL) < 0) {
            perror("Error");
            exit(EXIT_FAILURE);
        }

        for (int i = 0; i < FD_SETSIZE; i++) {
            if (FD_ISSET(i, &ready_sockets)) {
                if (i == server_fd) {
                    int client_socket;
                    if ((client_socket = accept(server_fd, (struct sockaddr *)&address,
                                                (socklen_t *)&addrlen)) < 0) {
                        perror("accept");
                        exit(EXIT_FAILURE);
                    }
                    FD_SET(client_socket, &current_sockets);
                } else {
                    valread = recv(i, buffer, sizeof(buffer), 0);
                    if (valread > 0) {
                        buffer[valread] = '\0';
                        send_to_python(buffer);
                    }
                    FD_CLR(i, &current_sockets);
                    close(i);
                }
            }
        }
    }
}

void send_to_python(char* message) {
    int fd;
    mknod(C_TO_PYTHON, __S_IFIFO | 0640, 0);
    fd = open(C_TO_PYTHON, O_WRONLY);
    if (fd == -1) {
        perror("Error opening FIFO for writing");
    } else {
        write(fd, message, strlen(message));
        close(fd);
        printf("Message sent to Python: %s\n", message);
    }
}
