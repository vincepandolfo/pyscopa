import connect
import socket

def main():
    """
    Classe main del server. Accetta le connessioni da parte dei client
    e avvia i thread che le gestiscono
    """
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind( ('', 53074) )
    serversocket.listen(5)

    print "Server avviato"

    while 1:
        (clientsocket, indirizzo) = serversocket.accept()

        clientM = connect.ClientManager(clientsocket)

        clientM.start()

        print "Client connesso"

if __name__ == "__main__":
    main()
