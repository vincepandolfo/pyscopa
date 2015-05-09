# coding=utf-8

import pygame
import sys
import game
import graphic
import connect
import socket
import wx

from pygame.locals import *


class ScopaGame():
    """
    In questa classe viene gestita l'interfaccia del gioco e l'interazione con l'utente
    """
    def __init__(self):
        """
        Inizializza l'ambiente di gioco. Si collega al server,
        inizializza lo stato di gioco e l'interfaccia grafica
        """
        self.app = wx.App()

        connSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.connManager = None
        ipServer = self.getIpServer()

        try:
            connSocket.connect((ipServer, 53074))
        except socket.error as e:
            wx.MessageBox("Connessione non riuscita", "Errore", wx.OK | wx.ICON_ERROR)
            self.exit()

        self.connManager = connect.SocketManager(connSocket)

        try:
            self.connManager.sendData("play")
            self.stato = self.connManager.receiveState()
            self.turno = int(self.connManager.readData())
        except connect.TimeOutError:
            self.timeOut()

        pygame.init()
        pygame.display.set_caption("PyScopa 0.1")
        self.scopaSurface = pygame.display.set_mode((600, 500))
        self.initGraphic()

        self.selezionata = -1
        self.actionIdx = 0
        self.azioniDisponibili = self.getAzioni()

        self.render()
        self.run = True

        self.gameLoop()

    def getIpServer(self):
        """
        Prende in input l'indirizzo del server dall'utente, ne controlla la validità e lo ritorna
        """
        valid = False
        ipServer = ""
        while not valid:
            ipServer = wx.GetTextFromUser("Inserisci l'indirizzo IP del server", "IP server", "127.0.0.1")

            if ipServer == "":
                self.exit()

            try:
                socket.inet_aton(ipServer)
                valid = True
            except socket.error:
                wx.MessageBox("Indirizzo IP non valido", "Errore", wx.OK | wx.ICON_ERROR)

        return ipServer

    def gameLoop(self):
        """
        Definisce il loop principale del gioco
        """
        while not self.stato.isTerminal():
            self.onLoop()
            self.manageEvents()

        self.printPunteggio(self.stato.punteggio())

        self.exit()

    def printPunteggio(self, punteggio):
        """
        Stampa il punteggio in un dialog
        """
        punteggioDialog = graphic.PunteggioDialog(punteggio)

        punteggioDialog.ShowModal()

    def render(self):
        """
        Disegna le carte sullo schermo
        """
        self.scopaSurface.fill((0, 128, 0))

        for idx in range(0, len(self.stato.manoPlayer)):
            if idx == self.selezionata:
                pygame.draw.rect(self.scopaSurface, (30, 144, 255), (self.inManoPos[idx][0]-4, self.inManoPos[idx][1]-4, 78, 128))

            carta = self.stato.manoPlayer[idx]

            self.scopaSurface.blit(self.carte[carta], self.inManoPos[idx])

        for idx in range(0, len(self.stato.terra)):
            carta = self.stato.terra[idx]

            if self.selezionata != -1:
                if self.stato.terra[idx] in self.azioniDisponibili[self.stato.manoPlayer[self.selezionata]][self.actionIdx]:
                    pygame.draw.rect(self.scopaSurface, (30, 144, 255), (self.terraPos[0] + 75*idx - 4, self.terraPos[1] - 4, 78, 128))

            self.scopaSurface.blit(self.carte[carta], (self.terraPos[0] + 75*idx, self.terraPos[1]))

        for idx in range(0, len(self.stato.manoAgent)):
            self.scopaSurface.blit(self.retro, self.avvPos[idx])

        pygame.display.flip()

    def onLoop(self):
        """
        Legge l'azione dell'avversario durante il turno avversario, riceve le azioni effettuabili dall'utente nel suo turno. Termina se lo stato è terminale
        """
        if self.stato.isTerminal():
            return

        if self.turno % 2 == 0:
            try:
                azionePC = self.connManager.receiveAction()
            except connect.TimeOutError:
                self.timeOut()

            self.stato = self.stato.generaSuccessore(azionePC)
            self.azioniDisponibili = self.getAzioni()

            self.turno += 1
            self.selezionata = -1
            self.actionIdx = 0

            self.render()

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

        self.inManoPos = [(185, 370), (265, 370), (345, 370)]
        self.terraPos = (10, 190)
        self.avvPos = [(185, 10), (265, 10), (345, 10)]

        self.clickableRect = [pygame.Rect(170, 370, 70, 120), pygame.Rect(250, 370, 70, 120), pygame.Rect(330, 370, 70, 120)]

    def manageEvents(self):
        """
        Gestisce gli eventi del gioco (click, uscita, ecc.)
        """
        if self.stato.isTerminal():
            return

        for event in pygame.event.get():
            if event.type == QUIT:
                self.run = False

            if self.turno % 2 == 1:
                if event.type == MOUSEBUTTONUP:
                    clickPos = event.pos
                    for idx in range(0, len(self.stato.manoPlayer)):
                        if self.clickableRect[idx].collidepoint(clickPos):
                            self.selezionata = idx
                            self.actionIdx = 0
                            self.render()

                if event.type == KEYDOWN:
                    if event.key == K_LEFT:
                        self.actionIdx = (self.actionIdx-1) % len(self.azioniDisponibili[self.stato.manoPlayer[self.selezionata]])
                        self.render()
                    if event.key == K_RIGHT:
                        self.actionIdx = (self.actionIdx+1) % len(self.azioniDisponibili[self.stato.manoPlayer[self.selezionata]])
                        self.render()
                    if event.key == K_RETURN and self.selezionata != -1:
                        self.execAction()

    def getAzioni(self):
        """
        Riceve le azioni possibili dal server e le memorizza
        nel formato utilizzato per il rendering delle azioni selezionate
        """
        azioniLegali = self.stato.getAzioniLegali('player')
        azioni = {}
        for carta in self.stato.manoPlayer:
            azioni[carta] = []

        for azione in azioniLegali:
            azioni[azione['carta']].append(azione['pigliata'])

        return azioni

    def execAction(self):
        """
        Esegue l'azione selezionata dall'utente
        """
        carta = self.stato.manoPlayer[self.selezionata]
        pigliata = self.azioniDisponibili[carta][self.actionIdx]
        azione = {'giocatore': 'player', 'carta': carta, 'pigliata': pigliata}

        try:
            self.connManager.sendAction(azione)
        except connect.TimeOutError:
            self.timeOut()

        self.stato = self.stato.generaSuccessore(azione)

        self.azioniDisponibili = self.getAzioni()
        self.selezionata = -1
        self.actionIdx = 0
        self.turno += 1

        self.render()

    def timeOut(self):
        """
        Apre una finestra di dialogo avvisando del timeout della comunicazione con il server e chiude il gioco
        """
        wx.MessageBox("Impossibile comunicare con il server", "Errore", wx.OK | wx.ICON_ERROR)
        self.exit()

    def exit(self):
        """
        Chiude l'interfaccia, la connessione e il programma
        """
        pygame.quit()
        if self.connManager:
            self.connManager.close()
        sys.exit()

if __name__ == "__main__":
    gioco = ScopaGame()
