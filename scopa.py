# coding=utf-8
import game, agent, sys, socket 

def main():
    """
    Main temporaneo per il testing
    """

    stato = game.GameState()
    agente = agent.ScopaAgent()
    turno = 0

    while stato.isTerminal() == False:
        print "A terra c'è:"
        print stato.terra
        if turno%2 == 0:
            azione = agente.prossimaAzione(stato)
            print "Il computer ha buttato: " 
            print azione['carta'] 
            print "e ha preso: " 
            print azione['pigliata']
            stato = stato.generaSuccessore(azione)
            turno += 1
        else:
            print "Tu hai in mano: " 
            print stato.manoPlayer
            print "Puoi prendere: "
            azioniLegali = stato.getAzioniLegali('player')
            
            for x in range(0, len(azioniLegali)):
                print str(x) + ") " 
                print azioniLegali[x]

            print "Inserisci il numero dell'azione da eseguire: "
            daEseguire = int(sys.stdin.readline())

            while daEseguire < 0 or daEseguire >= len(azioniLegali):
                print "Valore invalido: reinserire"
                daEseguire = int(sys.stdin.readline())

            stato = stato.generaSuccessore(azioniLegali[daEseguire])
            turno += 1

    print "Partita terminata!"
    print stato.punteggio()

if __name__ == "__main__":
    main()
