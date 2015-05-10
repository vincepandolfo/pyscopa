import wx

class PunteggioDialog(wx.Dialog):
    """
    Gestisce una finestra di dialogo customizzata per la visualizzazione del punteggio
    """

    def __init__(self, punteggio, totalePlayer, totaleAgent):
        """
        Inizializza la finestra di dialogo
        """
        super(PunteggioDialog, self).__init__(None, title="Punteggio")

        self.punteggio = punteggio
        self.totalePlayer = totalePlayer
        self.totaleAgent = totaleAgent

        self.SetSize((300, 250))
        self.initUI()

    def initUI(self):
        """
        Crea la grafica e ne carica il contenuto
        """
        mainBox = wx.BoxSizer(wx.VERTICAL)
        punteggioBox = wx.BoxSizer(wx.HORIZONTAL)

        playerPanel = wx.Panel(self)

        sbPlayer = wx.StaticBox(playerPanel, label="Giocatore")

        sbsPlayer = wx.StaticBoxSizer(sbPlayer, orient=wx.VERTICAL)

        sbsPlayer.Add(wx.StaticText(playerPanel, label="Carte prese: " + str(self.punteggio['lungoPlayer'])), border=5)
        sbsPlayer.Add(wx.StaticText(playerPanel, label="Carte a denari: " + str(self.punteggio['denariPlayer'])), border=5)
        sbsPlayer.Add(wx.StaticText(playerPanel, label="Sette bello: " + ("Si" if self.punteggio['sette'] == 'player' else "No")), border=5)
        sbsPlayer.Add(wx.StaticText(playerPanel, label="Settanta: " + str(self.punteggio['settantaPlayer'])), border=5)
        sbsPlayer.Add(wx.StaticText(playerPanel, label="Scope: " + str(self.punteggio['scopePlayer'])), border=5)
        sbsPlayer.Add(wx.StaticLine(playerPanel), border=5)
        sbsPlayer.Add(wx.StaticText(playerPanel, label="Punteggio: " + str(self.punteggio['player'])), border=5)
        sbsPlayer.Add(wx.StaticLine(playerPanel), border=5)
        sbsPlayer.Add(wx.StaticText(playerPanel, label="Totale partita: " + str(self.totalePlayer)))

        playerPanel.SetSizer(sbsPlayer)

        agentPanel = wx.Panel(self)

        sbAgent = wx.StaticBox(agentPanel, label="Server")

        sbsAgent = wx.StaticBoxSizer(sbAgent, orient=wx.VERTICAL)

        sbsAgent.Add(wx.StaticText(agentPanel, label="Carte prese: " + str(self.punteggio['lungoAgent'])), border=5)
        sbsAgent.Add(wx.StaticText(agentPanel, label="Carte a denari: " + str(self.punteggio['denariAgent'])), border=5)
        sbsAgent.Add(wx.StaticText(agentPanel, label="Sette bello: " + ("Si" if self.punteggio['sette'] == 'agent' else "No")), border=5)
        sbsAgent.Add(wx.StaticText(agentPanel, label="Settanta: " + str(self.punteggio['settantaAgent'])), border=5)
        sbsAgent.Add(wx.StaticText(agentPanel, label="Scope: " + str(self.punteggio['scopeAgent'])), border=5)
        sbsAgent.Add(wx.StaticLine(agentPanel), border=5)
        sbsAgent.Add(wx.StaticText(agentPanel, label="Punteggio: " + str(self.punteggio['agent'])), border=5)
        sbsAgent.Add(wx.StaticLine(agentPanel), border=5)
        sbsAgent.Add(wx.StaticText(agentPanel, label="Totale partita: " + str(self.totaleAgent)))

        agentPanel.SetSizer(sbsAgent)

        punteggioBox.Add(playerPanel, flag=wx.LEFT, proportion=1, border=5)
        punteggioBox.Add(agentPanel, flag=wx.RIGHT, proportion=1, border=5)

        okButton = wx.Button(self, label="Ok")

        mainBox.Add(punteggioBox, flag=wx.ALL|wx.EXPAND, border=5)
        mainBox.Add(okButton, flag=wx.ALIGN_CENTER|wx.BOTTOM, border=10)

        self.SetSizer(mainBox)

        okButton.Bind(wx.EVT_BUTTON, self.onClose)

    def onClose(self, e):
        """
        Chiude la finestra
        """
        self.Destroy()
