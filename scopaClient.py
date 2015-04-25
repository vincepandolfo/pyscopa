# coding=utf-8

import pygame
import sys
import game
import connect
import socket

from pygame.locals import *
from time import sleep


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

        self.selezionata = -1
        self.actionIdx = 0
        self.azioniDisponibili = self.getAzioni()

        self.render()
        self.run = True
        
        self.gameLoop()

    def gameLoop(self):
        """
        Definisce il loop principale del gioco
        """
        while self.run:
            self.onLoop()
            self.manageEvents()

        print self.connManager.receivePunteggio()

        self.exit()

    def render(self):
        """
        Disegna le carte sullo schermo
        """
        self.scopaSurface.fill((0, 128, 0))

        for idx in range(0, len(self.state.manoPlayer)):
            if idx == self.selezionata:
                pygame.draw.rect(self.scopaSurface, (30, 144, 255), (self.inManoPos[idx][0]-4, self.inManoPos[idx][1]-4, 78, 128))

            carta = (self.state.manoPlayer[idx][0], self.state.manoPlayer[idx][1])
            self.scopaSurface.blit(self.carte[carta], self.inManoPos[idx])

        for idx in range(0, len(self.state.terra)):
            carta = (self.state.terra[idx][0], self.state.terra[idx][1])

            if self.selezionata != -1:
                if self.state.terra[idx] in self.azioniDisponibili[tuple(self.state.manoPlayer[self.selezionata])][self.actionIdx]:
                    pygame.draw.rect(self.scopaSurface, (30, 144, 255), (self.terraPos[0] + 75*idx - 4, self.terraPos[1] - 4, 78, 128))
                
            self.scopaSurface.blit(self.carte[carta], (self.terraPos[0] + 75*idx, self.terraPos[1]))

        for idx in range(0, self.state.carteAgent):
            self.scopaSurface.blit(self.retro, self.avvPos[idx])

        pygame.display.flip()

    def checkTerminal(self):
        """
        Se lo stato è terminale, interrompe il gameLoop
        """
        if len(self.state.manoPlayer) == 0 and len(self.state.terra) == 0:
            self.run = False

    def onLoop(self):
        """
        Legge l'azione dell'avversario durante il turno avversario, riceve le azioni effettuabili dall'utente nel suo turno. Termina se lo stato è terminale
        """
        if self.turno % 2 == 0:
            self.state = game.ClientState(self.connManager.receiveMinimalState())
            self.turno += 1
            self.selezionata = -1
            self.actionIdx = 0
            self.azioniDisponibili = self.getAzioni()
            self.render()
            self.checkTerminal()

    def initGraphic(self):
        """
        Carica le immagini da utilizzare durante il rendering e definisce le posizioni delle carte in mano e a terra
        """
        semi = ['Denari', 'Bastoni', 'Spade', 'Coppe']

        self.retro = pygame.image.load("img/retro.jpg")
        self.retro.convert()
        self.retro = pygame.transform.scale(self.retro, (70, 120))

        self.carte = {(seme, i): pygame.image.load("img/" + seme + str(i) + ".png") for seme in semi for i in range(1, 11)}
        for key in self.carte:
            self.carte[key].convert()
            self.carte[key] = pygame.transform.scale(self.carte[key], (70, 120))

        self.inManoPos = [(170, 270), (250, 270), (330, 270)]
        self.terraPos = (10, 140)
        self.avvPos = [(170, 10), (250, 10), (330, 10)]

        self.clickableRect = [pygame.Rect(170, 270, 70, 120), pygame.Rect(250, 270, 70, 120), pygame.Rect(330, 270, 70, 120)]

    def manageEvents(self):
        """
        Gestisce gli eventi del gioco (click, uscita, ecc.)
        """
        if len(self.state.manoPlayer) == 0 and len(self.state.terra) == 0:
            self.run = False
            return

        for event in pygame.event.get():
            if event.type == QUIT:
                self.run = False

            if self.turno % 2 == 1:
                if event.type == MOUSEBUTTONUP:
                    clickPos = event.pos
                    for idx in range(0, 3):
                        if self.clickableRect[idx].collidepoint(clickPos):
                            self.selezionata = idx
                            self.actionIdx = 0
                            self.render()

                if event.type == KEYDOWN:
                    if event.key == K_LEFT:
                        self.actionIdx = (self.actionIdx-1)%len(self.azioniDisponibili[tuple(self.state.manoPlayer[self.selezionata])])
                        self.render()
                    if event.key == K_RIGHT:
                        self.actionIdx = (self.actionIdx+1)%len(self.azioniDisponibili[tuple(self.state.manoPlayer[self.selezionata])])
                        self.render()
                    if event.key == K_RETURN and self.selezionata != -1:
                        self.execAction()

    def getAzioni(self):
        """
        Riceve le azioni possibili dal server e le memorizza 
        nel formato utilizzato per il rendering delle azioni selezionate
        """
        azioniLegali = self.state.getAzioniLegali('player')
        azioni = {}
        for carta in self.state.manoPlayer:
            azioni[tuple(carta)] = []

        for azione in azioniLegali:
            azioni[tuple(azione['carta'])].append(azione['pigliata'])

        return azioni

    def execAction(self):
        """
        Esegue l'azione selezionata dall'utente
        """
        carta = self.state.manoPlayer[self.selezionata]
        azione = {'giocatore': 'player', 'carta': carta, 'pigliata': self.azioniDisponibili[tuple(carta)][self.actionIdx]}
        self.connManager.sendAction(azione)
        self.turno += 1
        self.state.aggiorna(self.connManager.receiveMinimalState())
        self.azioniDisponibili = self.getAzioni()
        self.selezionata = -1
        self.actionIdx = 0
        self.render()
        self.checkTerminal()

    def exit(self):
        """
        Chiude l'interfaccia, la connessione e il programma
        """
        pygame.quit()
        self.connManager.close()
        sys.exit()

if __name__ == "__main__":
    gioco = ScopaGame()
