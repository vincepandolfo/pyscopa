# coding=UTF-8

import socket 
import json


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

    def receiveMinimalState(self):
        """
        Riceve uno stato minimale dal socket e lo ritorna come due liste
        """
        minimalState = self.readData().split('|')
        terra = json.loads(minimalState[0])
        manoPlayer = json.loads(minimalState[1])
        inManoAvv = int(minimalState[2])

        return manoPlayer, terra, inManoAvv

    def receivePunteggio(self):
        """
        Legge il punteggio dal socket
        """
        punteggio = json.loads(self.readData())

        return punteggio

    def sendMinimalState(self, stato):
        """
        Invia uno stato minimale (cioè carte nella mano del giocatore, carte a terra)
        """
        aTerraStringa = json.dumps(stato.terra)
        inManoPlayerStringa = json.dumps(stato.manoPlayer)

        daInviare = aTerraStringa + "|" + inManoPlayerStringa + "|" + str(len(stato.manoAgent))

        self.sendData(daInviare)

    def sendPunteggio(self, stato):
        """
        Invia il punteggio della partita
        """
        punteggioStringa = json.dumps(stato.punteggio())

        self.sendData(punteggioStringa)
