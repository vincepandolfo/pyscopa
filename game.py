# coding=utf-8

from random import shuffle
import copy
from itertools import combinations

class GameState:
    """
    Definisce lo stato di una partita: le carte a terra, in mano, prese e nel mazzo.
    Contiene i metodi per la gestione dello stato in corso e la creazione di nuovi stati
    """
    def __init__(self):
        self.semi = ("Bastoni", "Coppe", "Denari", "Spade")
        self.mazzo = [(seme, valore) for seme in self.semi for valore in range(1, 11)]
        self.pigliatePlayer = []
        self.pigliateAgent = []
        self.terra = []
        
        self.manoPlayer = []
        self.manoAgent = []
        
        self.scopePlayer = 0
        self.scopeAgent = 0
        
        shuffle(self.mazzo)
        
        self.daiCarte()
            
        for x in range(0, 4):
            self.terra.append(self.mazzo.pop())
    
    def daiCarte(self):
        """
        Distribuisce le carte ai due giocatori
        """
        for x in range(0, 3):
            self.manoPlayer.append(self.mazzo.pop())
            self.manoAgent.append(self.mazzo.pop())
   
    def generaSuccessore(self, azione):
        """
        Genera un nuovo stato partendo da uno stato precedente e da un'azione
        """
        nuovoStato = copy.deepcopy(self)
        
        if azione['giocatore'] == "agent":
            nuovoStato.manoAgent.remove(azione['carta'])
            if len(azione['pigliata']) == 0:
                nuovoStato.terra.append(azione['carta'])
            else:
                nuovoStato.pigliateAgent.append(azione['carta'])
                nuovoStato.pigliateAgent += azione['pigliata']
           
            if len(nuovoStato.terra) == len(azione['pigliata']):
                nuovoStato.scopeAgent += 1
        else:
            nuovoStato.manoPlayer.remove(azione['carta'])


            if len(azione['pigliata']) == 0:
                nuovoStato.terra.append(azione['carta'])
            else:
                nuovoStato.pigliatePlayer.append(azione['carta'])
                nuovoStato.pigliatePlayer += azione['pigliata']
            

            if len(nuovoStato.terra) == len(azione['pigliata']):
                nuovoStato.scopePlayer += 1
        
        nuovoStato.terra = list(set(nuovoStato.terra) - set(azione['pigliata']))
                
        if len(nuovoStato.manoAgent) == 0 and len(nuovoStato.manoPlayer) == 0:
            if len(nuovoStato.mazzo) == 0:
                if azione['giocatore'] == "agent":
                    nuovoStato.pigliateAgent += nuovoStato.terra
                else:
                    nuovoStato.pigliatePlayer += nuovoStato.terra
                
                nuovoStato.terra = []
            else:
                nuovoStato.daiCarte()
                
        return nuovoStato

    def getAzioniLegali(self, giocatore):
        """
        Ritorna una lista contenente le possibili azioni effettuabili da un giocatore
        """
        azioniLegali = []
        
        if giocatore == 'player':
            mano = self.manoPlayer
        else:
            mano = self.manoAgent
            
        possibili = [possibile for r in range(1, len(self.terra)+1) for possibile in combinations(self.terra, r)]
        
        for carta in mano:
            prese = False
            poss = False
            for pigliata in possibili:
                if len(pigliata) > 1 and poss:
                    break
                
                somma = 0
                for possCarta in pigliata:
                    somma += possCarta[1]
                
                if somma == carta[1]:
                    azione = { 'giocatore': giocatore, 'carta': carta, 'pigliata': pigliata }
                    azioniLegali.append(azione)
                    prese = True
                    if carta[1] == pigliata[0][1]:
                        poss = True
            
            if not prese:
                azione = { 'giocatore': giocatore, 'carta': carta, 'pigliata': () }
                azioniLegali.append(azione)

        return azioniLegali
    
    def isTerminal(self):
        """
        Determina se lo stato corrente è terminale o meno
        """
        if (len(self.pigliateAgent) + len(self.pigliatePlayer)) == 40:
            return True
        else:
            return False
    
    def punteggio(self):
        """
        Ritorna il punteggio dei due giocatori.
        Da chiamare al termine di una partita (stato terminale)
        """
        punteggio = {}
        
        punteggio['player'] = 0
        punteggio['agent'] = 0
               
        # Calcola chi ha fatto "carte a denari" 
        
        punteggio['denariPlayer'] = 0
        punteggio['denariAgent'] = 0

        for carta in self.pigliatePlayer:
            if carta[0] == "Denari":
                punteggio['denariPlayer'] += 1
        
        for carta in self.pigliateAgent:
            if carta[0] == "Denari":
                punteggio['denariAgent'] += 1
                
        if punteggio['denariPlayer'] > punteggio['denariAgent']:
            punteggio['player'] += 1 
        elif punteggio['denariAgent'] > punteggio['denariPlayer']:
            punteggio['agent'] += 1
        
        # Calcola chi ha fatto "carte a lungo"
        
        punteggio['lungoAgent'] = len(self.pigliateAgent)
        punteggio['lungoPlayer'] = len(self.pigliatePlayer)
        
        if len(self.pigliatePlayer) > len(self.pigliateAgent):
            punteggio['player'] += 1
        elif len(self.pigliateAgent) > len(self.pigliatePlayer):
            punteggio['agent'] += 1
        
        # Calcola chi ha fatto "sette bello"
        
        settebello = ("Denari", 7)
        
        if settebello in self.pigliateAgent:
            punteggio['sette'] = "agent"
        elif settebello in self.pigliatePlayer:
            punteggio['sette'] = "player"
        else:
            punteggio['sette'] = "nessuno"
            
        # Calcola chi ha fatto la settanta e relativi punteggi
        
        valori = [ 0, 16, 12, 13, 14, 15, 18, 21, 10, 10, 10 ]
            
        settantaAgent = { seme: 0 for seme in self.semi }
        settantaPlayer = { seme: 0 for seme in self.semi }
        
        for carta in self.pigliateAgent:
            settantaAgent[carta[0]] = max(settantaAgent[carta[0]], valori[carta[1]])
            
        for carta in self.pigliatePlayer:
            settantaPlayer[carta[0]] = max(settantaPlayer[carta[0]], valori[carta[1]])
            
        punteggio['settantaAgent'] = 0
        punteggio['settantaPlayer'] = 0
        
        for val in settantaAgent.viewvalues():
            punteggio['settantaAgent'] += val
            
        for val in settantaPlayer.viewvalues():
            punteggio['settantaPlayer'] += val
            
        if punteggio['settantaAgent'] > punteggio['settantaPlayer']:
            punteggio['agent'] += 1
        elif punteggio['settantaPlayer'] > punteggio['settantaAgent']:
            punteggio['player'] += 1
        
        # Memorizza il numero di scope
        
        punteggio['scopePlayer'] = self.scopePlayer
        punteggio['scopeAgent'] = self.scopeAgent
        
        punteggio['player'] += self.scopePlayer
        punteggio['agent'] += self.scopeAgent
        
        return punteggio

class ClientState(GameState):
    """
    Definisce lo stato minimale gestito dal client
    """
    def __init__(self, miniState):
        """
        Inizializza uno stato minimale
        """
        self.manoPlayer = miniState[0]
        self.terra = miniState[1]
        self.carteAgent = miniState[2]

    def aggiorna(self, miniState):
        """
        Aggiorna lo stato minimale
        """
        self.manoPlayer = miniState[0]
        self.terra = miniState[1]
        self.carteAgent = miniState[2]
