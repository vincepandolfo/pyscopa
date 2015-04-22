import socket, threading, game, agent, json

class SocketManager(threading):
    """
    Questa è la superclasse contentente i metodi comuni sia al client che al server
    L'override del metodo run() verrà effettuato nelle classi derivate
    """

    def __init__(self, commSocket)
        """
        Inizializza l'oggetto SocktManager con il socket da utilizzare per la comunicazione 
        """
        self.commSocket = commSocket

    def receiveAction(self):
        """
        Riceve un azione la ritorna
        """
        datiLetti = ""

        while 1:
            data = conn.recv(2048)
            if not data: break
            datiLetti += data

        azione = json.loads(datiLetti)

        return azione

    def sendAction(self, azione):
        """
        Invia un azione sul socket
        """
        azioneStringa = json.dumps(azione)

        lunghezzaMessaggio = len(azioneStringa)

        byteInviati = 0

        while byteInviati < lunghezzaMessaggio:
            inviati = self.commSocket.send(azioneStringa[byteInviati:])

            if inviati == 0:
                raise RuntimeError("Connessione al socket interrotta")

            byteInviati += inviati

    def sendMinimalState(self, stato):
        """
        Invia uno stato minimale (cioè carte nella mano del giocatore, carte a terra)
        """
        TODO
        pass

    def receiveMinimalState(self):
        """
        Riceve uno stato minimale dal socket e lo ritorna
        """
        TODO
        pass

class ClientManager(SocketManager):
    """
    Questa classe definisce il thread del server che gestisce la partita di un client
    """
    TODO
