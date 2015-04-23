import pygame
import sys
import game
import connect
import socket

from pygame.locals import *


class ScopaGame():
    """
    In questa classe viene gestita l'interfaccia del gioco e l'interazione con l'utente
    """
    def __init__(self):
        """
        Inizializza l'ambiente di gioco. Si collega al server, inizializza lo stato di gioco e l'interfaccia grafica
        """
        connSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connSocket.connect(('localhost', 53074))
        self.connManager = connect.SocketManager(connSocket)

        self.state = game.ClientState(self.connManager.receiveMinimalState())
        self.nextAction = {} 
        self.turno = int(self.connManager.readData())

        pygame.init()
        pygame.display.set_caption("PyScopa 0.1")
        self.scopaSurface = pygame.display.set_mode((600, 400))
        self.initGraphic()
        self.render()

        self.run = True

    def gameLoop(self):
        """
        Definisce il loop principale del gioco
        """
        while self.run:
            self.manageEvents()
            self.onLoop()
            self.render()

        self.exit()
    
    def render(self):
        """
        Disegna le carte sullo schermo
        """
        self.scopaSurface.fill((0, 128, 0))
        
        for idx in range(0, len(self.state.manoPlayer)):
            carta = (self.state.manoPlayer[idx][0], self.state.manoPlayer[idx][1])
            self.scopaSurface.blit(self.carte[carta], self.inManoPos[idx]) 

        for idx in range(0, len(self.state.terra)):
            carta = (self.state.terra[idx][0], self.state.terra[idx][1])
            self.scopaSurface.blit(self.carte[carta], self.terraPos[idx])

        for idx in range(0, self.state.carteAgent):
            self.scopaSurface.blit(self.retro, self.avvPos[idx])


        pygame.display.flip()

    def initGraphic(self):
        """
        Carica le immagini da utilizzare durante il rendering e definisce le posizioni delle carte in mano e a terra
        """
        semi = ['Denari', 'Bastoni', 'Spade', 'Coppe']

        self.retro = pygame.image.load("img/retro.jpg")
        self.retro.convert()
        self.retro = pygame.transform.scale(self.retro, (70, 120))

        self.carte = { (seme, i) : pygame.image.load("img/" + seme + str(i) + ".png") for seme in semi for i in range(1, 11)}
        for key in self.carte:
            self.carte[key].convert()
            self.carte[key] = pygame.transform.scale(self.carte[key], (70, 120))

        self.inManoPos = [(170, 270), (250, 270), (330, 270)]
        self.terraPos = [(10, 140), (90, 140), (170, 140), (250, 140)]
        self.avvPos = [(170, 10), (250, 10), (330, 10)]

    def onLoop(self):
        pass

    def manageEvents(self):
        """
        Gestisce gli eventi del gioco (click, uscita, ecc.)
        """
        for event in pygame.event.get():
            if event.type == QUIT:
                self.run = False

    def exit(self):
        """
        Chiude l'interfaccia, la connessione e il programma
        """
        pygame.quit()
        self.connManager.close()
        sys.exit()

if __name__=="__main__":
    gioco = ScopaGame()
    gioco.gameLoop()
