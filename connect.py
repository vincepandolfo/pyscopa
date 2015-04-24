# coding=UTF-8

import random
import socket 
import threading
import game
import agent
import json


class SocketManager(threading.Thread):
    """
    Questa è la superclasse contentente i metodi comuni sia al client che al server
    L'override del metodo run() verrà effettuato nelle classi derivate che ne necessitano
    """

    def __init__(self, commSocket):
        """
        Inizializza l'oggetto SocktManager con il socket da utilizzare per la comunicazione 
        """
        super(SocketManager, self).__init__()
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

class ClientManager(SocketManager):
    """
    Questa classe definisce il thread del server che gestisce la partita di un client
    """

    def __init__(self, commSocket):
        """
        Inizializza il gestore del client
        """
        super(ClientManager, self).__init__(commSocket)
        self.stato = game.GameState()
        self.agente = agent.ScopaAgent()

    def run(self):
        """
        Override del metodo run() della classe threading.
        Gestisce la partita del client
        """

        turno = random.randint(0, 1)

        self.sendMinimalState(self.stato)

        self.sendData(str(turno))

        while not self.stato.isTerminal():
            if turno%2 == 0:
                azione = self.agente.prossimaAzione(self.stato)
                self.stato = self.stato.generaSuccessore(azione)
                turno += 1
            else:
                azione = self.receiveAction()
                self.stato = self.stato.generaSuccessore(azione)
                turno += 1

            self.sendMinimalState(self.stato)

        self.sendPunteggio(self.stato)

        self.close()

        print "Connessione al client chiusa"

            
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
