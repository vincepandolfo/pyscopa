# coding=UTF-8

import socket 
import json
import game
import time
import select

class TimeOutError(Exception):
    """
    Definisce l'errore da richiamare nel caso di timeout delle comunicazioni.
    """
    pass


class SocketManager():
    """
    Gestisce la comunicazione tra client e server. Può essere utilizzata sia dal client che dal server
    """

    def __init__(self, commSocket):
        """
        Inizializza l'oggetto SocktManager con il socket da utilizzare per la comunicazione 
        """
        self.commSocket = commSocket
        self.commSocket.setblocking(0)
        self.readBuffer = ""

    def close(self):
        """
        Chiude la connessione
        """
        self.commSocket.close()

    def readData(self, timeout=10):
        """
        Legge l'ultimo messaggio in arrivo sul socket. Utilizza un buffer per gestire più messaggi.
        """
        prontiLettura, prontiScrittura, errori = select.select([self.commSocket], [], [], timeout)

        if len(prontiLettura) == 0:
            raise TimeOutError()

        messaggio = ""

        while 1:
            data = self.commSocket.recv(4096)
            if not data:
                continue

            self.readBuffer += data
            endMex = self.readBuffer.find("\n")

            if endMex != -1:
                messaggio = self.readBuffer[:endMex+1]
                self.readBuffer = self.readBuffer[endMex+1:]
                break

        return messaggio[:-1]

    def sendData(self, messaggio):
        """
        Invia dei dati sul socket
        """
        prontiLettura, prontiScrittura, errori = select.select([], [self.commSocket], [], 10)

        if len(prontiScrittura) == 0:
            raise TimeOutError()

        self.commSocket.sendall(messaggio+'\n')

    def receiveAction(self, timeout=10):
        """
        Riceve un azione la ritorna
        """
        try:
            datiLetti = self.readData(timeout)
        except TimeOutError:
            raise

        azione = json.loads(datiLetti)
        azione['carta'] = tuple(azione['carta'])

        for idx in range(0, len(azione['pigliata'])):
            azione['pigliata'][idx] = tuple(azione['pigliata'][idx])

        azione['pigliata'] = tuple(azione['pigliata'])

        return azione

    def sendAction(self, azione):
        """
        Invia un azione sul socket
        """
        azioneStringa = json.dumps(azione)

        try:
            self.sendData(azioneStringa)
        except TimeOutError:
            raise

    def sendState(self, stato):
        """
        Invia uno stato di gioco
        """
        statoDaInviare = ("terra|" + json.dumps(stato.terra) +
            "|mazzo|" + json.dumps(stato.mazzo) +
            "|manoPlayer|" + json.dumps(stato.manoPlayer) +
            "|manoAgent|" + json.dumps(stato.manoAgent) +
            "|pigliatePlayer|" + json.dumps(stato.pigliatePlayer) +
            "|pigliateAgent|" + json.dumps(stato.pigliateAgent) +
            "|scopePlayer|" + json.dumps(stato.scopePlayer) +
            "|scopeAgent|" + json.dumps(stato.scopeAgent))

        try:
            self.sendData(statoDaInviare)
        except TimeOutError:
            raise

    def receiveState(self):
        """
        Riceve uno stato di gioco
        """
        try:
            stato = self.readData().split("|")
        except TimeOutError:
            raise

        params = {}

        for idx in range(0, len(stato), 2):
            params[stato[idx]] = json.loads(stato[idx+1])

        return game.GameState(**params)
