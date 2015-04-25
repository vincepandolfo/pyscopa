import connect
import socket
import threading
import game
import agent
import random


class ClientManager(threading.Thread):
    """
    Questa classe definisce il thread del server che gestisce la partita di un client
    """

    def __init__(self, commSocket, clientId):
        """
        Inizializza il gestore del client
        """
        super(ClientManager, self).__init__()
        self.stato = game.GameState()
        self.agente = agent.ScopaAgent()
        self.commManager = connect.SocketManager(commSocket)
        self.clientId = clientId

    def run(self):
        """
        Override del metodo run() della classe threading.
        Gestisce la partita del client
        """

        turno = random.randint(0, 1)

        self.commManager.sendMinimalState(self.stato)

        self.commManager.sendData(str(turno))

        while not self.stato.isTerminal():
            if turno%2 == 0:
                azione = self.agente.prossimaAzione(self.stato)
                self.stato = self.stato.generaSuccessore(azione)
                turno += 1
            else:
                azione = self.commManager.receiveAction()
                self.stato = self.stato.generaSuccessore(azione)
                turno += 1

            self.commManager.sendMinimalState(self.stato)

        self.commManager.sendPunteggio(self.stato)

        self.commManager.close()

        print "Connessione al client %d chiusa" % self.clientId


def main():
    """
    Classe main del server. Accetta le connessioni da parte dei client
    e avvia i thread che le gestiscono
    """
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind( ('', 53074) )
    serversocket.listen(5)
    clientId = 0

    print "Server avviato"

    while 1:
        (clientsocket, indirizzo) = serversocket.accept()

        clientM = ClientManager(clientsocket, clientId)

        clientM.start()

        print "Client %d connesso" % clientId

        clientId += 1

if __name__ == "__main__":
    main()


