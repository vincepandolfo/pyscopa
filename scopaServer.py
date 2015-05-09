# coding=utf-8

import connect
import socket
import threading
import game
import agent
import random
import wx


class ClientManager(threading.Thread):
    """
    Questa classe definisce il thread del server che gestisce la partita di un client
    """

    def __init__(self, commSocket, clientId, clientList):
        """
        Inizializza il gestore del client
        """
        super(ClientManager, self).__init__()
        self.stato = game.GameState()
        self.agente = agent.ScopaAgent()
        self.commManager = connect.SocketManager(commSocket)
        self.clientId = clientId
        self.clientList = clientList

    def run(self):
        """
        Override del metodo run() della classe threading.
        Gestisce la partita del client
        """

        turno = random.randint(0, 1)

        self.commManager.sendState(self.stato)

        self.commManager.sendData(str(turno))

        while not self.stato.isTerminal():
            if turno%2 == 0:
                azione = self.agente.prossimaAzione(self.stato)

                try:
                    self.commManager.sendAction(azione)
                except connect.TimeOutError:
                    break

                self.stato = self.stato.generaSuccessore(azione)
                turno += 1
            else:
                try:
                    azione = self.commManager.receiveAction(120)
                except connect.TimeOutError:
                    break 

                self.stato = self.stato.generaSuccessore(azione)
                turno += 1

        self.clientList.Delete(self.clientList.FindString("Client " + str(self.clientId)))

        self.commManager.close()


class Server(threading.Thread):
    """
    Definisce il server
    """
    def __init__(self, clientList):
        """
        Inizializza il server
        """
        super(Server, self).__init__()

        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind( ('', 53074) )
        self.serverSocket.listen(5)
        self.clientList = clientList

        self.clientId = 0

    def run(self):
        run = True
        while run:
            (clientSocket, indirizzo) = self.serverSocket.accept()

            clientM = ClientManager(clientSocket, self.clientId, self.clientList)

            try:
                firstMessage = clientM.commManager.readData()
            except connect.TimeOutError:
                clientM.commManager.close()
                continue

            if firstMessage == "chiudi":
                run = False
            else:
                clientM.start()
                self.clientList.Append("Client " + str(self.clientId))
                self.clientId += 1

        self.serverSocket.close()

class ServerFrame(wx.Frame):
    """
    GUI del server
    """
    def __init__(self):
        super(ServerFrame, self).__init__(None, style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)

        self.InitUI()

    def InitUI(self):
        """
        Crea l'interfaccia grafica
        """
        # Crea il menu

        self.server = None

        menuBar = wx.MenuBar()

        serverMenu = wx.Menu()
        start = serverMenu.Append(wx.ID_ANY, "Avvia", "Avvia il server")
        stop = serverMenu.Append(wx.ID_ANY, "Ferma", "Ferma il server")

        serverMenu.AppendSeparator()

        exit = serverMenu.Append(wx.ID_EXIT, "Esci", "Chiude il server")

        self.Bind(wx.EVT_MENU, self.OnStart, start)
        self.Bind(wx.EVT_MENU, self.OnStop, stop)
        self.Bind(wx.EVT_MENU, self.OnExit, exit)

        menuBar.Append(serverMenu, "&Server")
        
        self.SetMenuBar(menuBar)

        # Crea la status bar

        self.statusBar = self.CreateStatusBar()
        self.statusBar.SetStatusText("Server non in esecuzione")

        # Crea la lista dei client

        mainPanel = wx.Panel(self, wx.ID_ANY)
        mainBox = wx.BoxSizer(wx.HORIZONTAL)

        self.clientList = wx.ListBox(mainPanel, wx.ID_ANY)
        mainBox.Add(self.clientList, 1, wx.EXPAND | wx.ALL, 5)

        # Crea i bottoni per la gestione dei client

        btnPanel = wx.Panel(mainPanel, wx.ID_ANY)
        btnBox = wx.BoxSizer(wx.VERTICAL)

        labelBtn = wx.StaticText(btnPanel, label="Controllo client")
        infoBtn = wx.Button(btnPanel, wx.ID_ANY, "Info", size=(90, 30))
        closeBtn = wx.Button(btnPanel, wx.ID_ANY, "Chiudi", size=(90, 30))

        self.Bind(wx.EVT_BUTTON, self.OnInfo)
        self.Bind(wx.EVT_BUTTON, self.OnClose)

        btnBox.Add((-1, 10))
        btnBox.Add(labelBtn)
        btnBox.Add(infoBtn, 0, wx.TOP, 5)
        btnBox.Add(closeBtn, 0, wx.TOP, 5)

        btnPanel.SetSizer(btnBox)
        mainBox.Add(btnPanel, 0.6, wx.EXPAND | wx.RIGHT, 5)
        mainPanel.SetSizer(mainBox)

        self.Bind(wx.EVT_CLOSE, self.OnExit)
        self.SetTitle("PyScopa Server")
        self.SetSize((300, 200))
        self.Centre()
        self.Show(True)

    def OnStart(self, event):
        """
        Avvia il server 
        """
        if not self.server:
            self.server = Server(self.clientList)
            self.server.start()
            self.statusBar.SetStatusText("Server in esecuzione")
            wx.MessageBox("Server avviato", "Info server", wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox("Il server è già in funzione", "Info server", wx.OK | wx.ICON_INFORMATION)

    def OnStop(self, event, exit = False):
        """
        Ferma il server
        """
        if self.server:
            closeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            closeSocket.connect(("localhost", 53074))
            closeSocket.sendall("chiudi\n")
            closeSocket.close()

            self.server.join()
            self.server = None

            self.statusBar.SetStatusText("Server non in esecuzione")
            if not exit:
                wx.MessageBox("Server chiuso", "Info server", wx.OK | wx.ICON_INFORMATION)
        elif not exit:
            wx.MessageBox("Il server non è in funzione", "Info server", wx.OK | wx.ICON_INFORMATION)
            

    def OnExit(self, event):
        """
        Chiude il server e l'applicazione
        """
        self.OnStop(None, exit=True)
        self.Destroy()

    def OnInfo(self, event):
        """
        Ottiene le informazioni sul client selezionato e le stampa in una finestra di dialogo
        """
        pass

    def OnClose(self, event):
        """
        Chiude la connessione al client
        """
        pass

if __name__ == "__main__":
   app = wx.App()
   ServerFrame()
   app.MainLoop()
