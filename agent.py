# coding=utf-8

import game


class ScopaAgent:

    """
    Contiene i metodi e le informazioni dell'agente
    """

    def __init__(self, diff='difficile'):
        self.depth = 1
        if diff == 'difficile':
            self.value = self.alphabeta
            self.depth = 6
        elif diff == 'facile':
            self.value = self.reflex

    # Metodo per la valutazione di uno stato

    def valuta(self, stato):
        punteggio = stato.punteggio()

        pesoCarte = 5
        pesoDenari = 20
        pesoScope = 100
        pesoSettanta = 0
        sette = 0

        if punteggio['settantaPlayer'] > punteggio['settantaAgent']:
            pesoSettanta = -100
        elif punteggio['settantaPlayer'] < punteggio['settantaAgent']:
            pesoStettanta = 100

        if punteggio['sette'] == 'agent':
            sette = 100
        elif punteggio['sette'] == 'player':
            sette = -100

        if punteggio['lungoPlayer'] > 20:
            pesoCarte = 0

        if punteggio['denariPlayer'] > 5:
            pesoDenari = 0

        return sette + pesoCarte * punteggio['lungoAgent'] + pesoDenari * punteggio[
            'denariAgent'] + pesoScope * punteggio['scopeAgent'] + pesoSettanta

    def minValue(self, stato, prof, a, b):
        azioneMigliore = [None, float('inf')]

        for azione in stato.getAzioniLegali('player'):
            nuovoStato = stato.generaSuccessore(azione)
            nuovoValore = self.alphabeta(nuovoStato, prof, 'agent', a, b)[1]

            if azioneMigliore[1] > nuovoValore:
                azioneMigliore = [azione, nuovoValore]

                if nuovoValore < a:
                    return azioneMigliore

                b = min(b, nuovoValore)

        return azioneMigliore

    def maxValue(self, stato, prof, a, b):
        azioneMigliore = [None, float('-inf')]

        for azione in stato.getAzioniLegali('agent'):
            nuovoStato = stato.generaSuccessore(azione)
            nuovoValore = self.value(nuovoStato, prof, 'player', a, b)[1]

            if azioneMigliore[1] < nuovoValore:
                azioneMigliore = [azione, nuovoValore]

                if nuovoValore > b:
                    return azioneMigliore

                a = max(a, nuovoValore)

        return azioneMigliore

    def alphabeta(self, stato, prof, agent, a, b):
        if prof == self.depth or stato.isTerminal():
            return [None, self.valuta(stato)]

        if agent == 'agent':
            return self.maxValue(stato, prof + 1, a, b)
        else:
            return self.minValue(stato, prof, a, b)

    def reflex(self, stato, *args):
        """
        Seleziona l'azione migliore che da il miglior risultato subito dopo essere eseguita
        """
        azioneMigliore = [None, float('-inf')]

        for azione in stato.getAzioniLegali('agent'):
            nuovoStato = stato.generaSuccessore(azione)

            if self.valuta(nuovoStato) > azioneMigliore[1]:
                azioneMigliore = [azione, self.valuta(nuovoStato)]

        return azioneMigliore

    def prossimaAzione(self, stato):
        return self.value(stato, 0, 'agent', float('-inf'), float('inf'))[0]
