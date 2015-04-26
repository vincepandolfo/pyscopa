# coding=UTF-8

import socket 
import json
import game


class SocketManager():
    """
    Gestisce la comunicazione tra client e server. Può essere utilizzata sia dal client che dal server
    """

    def __init__(self, commSocket):
        """
        Inizializza l'oggetto SocktManager con il socket da utilizzare per la comunicazione 
        """
        self.commSocket = commSocket
        self.readBuffer = ""

    def close(self):
        """
        Chiude la connessione
        """
        self.commSocket.close()

    def readData(self):
        """
        Legge l'ultimo messaggio in arrivo sul socket. Utilizza un buffer per gestire più messaggi.
        """
        messaggio = ""

        while 1:
            data = self.commSocket.recv(2048)
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
        self.commSocket.sendall(messaggio+'\n')

    def receiveAction(self):
        """
        Riceve un azione la ritorna
        """
        datiLetti = self.readData()

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

        self.sendData(azioneStringa)

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

        self.sendData(statoDaInviare)

    def receiveState(self):
        """
        Riceve uno stato di gioco
        """
        stato = self.readData().split("|")
        params = {}

        for idx in range(0, len(stato), 2):
            params[stato[idx]] = json.loads(stato[idx+1])

        return game.GameState(**params)
