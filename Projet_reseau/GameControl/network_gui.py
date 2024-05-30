import pygame as pg
from GameControl.EventManager import *


def run_network_gui():
    window = GameControl.EventManager.screen
    pygame.init()

    pygame.display.set_caption('Connexion Réseau')

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)

    font = pg.font.Font(None, 32)
    ip_input_rect = pygame.Rect(450, 150, 200, 50)
    port_input_rect = pygame.Rect(450, 250, 200, 50)
    connect_button_rect = pygame.Rect(350, 350, 300, 50)

    ip_text =''
    port_text =''
    active_input = None

    clock = pygame.time.Clock()
    is_running = True

    while is_running :
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if ip_input_rect.collidepoint(event.pos) :
                    active_input = 'ip'
                elif port_input_rect.collidepoint(event.pos) :
                    active_input = 'port'
                elif connect_button_rect.collidepoint(event.pos):
                    print("Trying to connect to {ip_text}:{port_text}")
                else :
                    active_input = None
            
            if event.type == pygame.KEYDOWN:
                if active_input == 'ip':
                    if event.key == pygame.K_BACKSPACE:
                        ip_text = ip_text[:-1]
                    else :
                        ip_text += event.unicode
                elif active_input == 'port' :
                    if event.key == pygame.K_BACKSPACE:
                        port_text = port_text[:-1]
                    else :
                        port_text += event.unicode

            window.fill(BLACK)
            pygame.draw.rect(window, WHITE, ip_input_rect, 2)
            pygame.draw.rect(window, WHITE, port_input_rect, 2)
            pygame.draw.rect(window, WHITE, connect_button_rect, 2)

            ip_surface = font.render(ip_text, True, WHITE)
            port_surface = font.render(port_text, True, WHITE)
            window.blit(ip_surface,(ip_input_rect.x + 10, ip_input_rect.y + 10))
            window.blit(port_surface,(port_input_rect.x + 10, port_input_rect.y + 10))

            ip_label = font.render('Adresse IP:', True, WHITE)
            port_label = font.render('Port:', True, WHITE)
            connect_label = font.render('Connecter', True, WHITE)
            window.blit(ip_label, (350, 150 +10))
            window.blit(port_label, (350, 250 +10))
            window.blit(connect_label,(connect_button_rect.x + 75, connect_button_rect.y + 10))
            pygame.display.flip()
            clock.tick(30)
        pygame.quit()



