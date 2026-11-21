from database.parco_DAO import ParcoDAO
from database.escursione_DAO import EscursioneDAO
from database.punto_interesse_DAO import PuntoInteresseDAO

class Model:
    def __init__(self):
        self.escursioni_map = {} # Mappa ID escursione -> oggetti Escursione
        self.punti_interesse_map = {} # Mappa ID punto di interesse -> oggetti PuntoInteresse

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0


        # Caricamento
        self.load_escursioni()
        self.load_punti_interesse()
        self.load_relazioni()

    @staticmethod
    def load_parchi():
        """ Restituisce tutti i parchi disponibili """
        return ParcoDAO.get_parchi()

    def load_escursioni(self):
        """ Carica tutte le escursioni in un dizionario [id, Escursione]"""
        self.escursioni_map = EscursioneDAO.get_escursioni()

    def load_punti_interesse(self):
        """ Carica tutti i punti di interesse in un dizionario [id, PuntoInteresse]"""
        self.punti_interesse_map = PuntoInteresseDAO.get_punti_interesse()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra escursioni e punti di interesse e salvarle nelle strutture dati
            Collega escursione <-> punti di interesse.
            --> Ogni Escursione ha un set di PuntoInteresse.
            --> Ogni PuntoInteresse ha un set di Escursioni.
        """
        set_relazioni = EscursioneDAO.get_escursioni_punti_interesse()
        for coppia in set_relazioni :
            escursioni = self.escursioni_map[coppia["id_escursione"]]
            punti = self.punti_interesse_map[coppia["id_punto_interesse"]]
            escursioni.punti_interesse.add(punti)
            punti.escursioni.add(escursioni)



    def genera_pacchetto(self, id_parco: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto di escursioni ottimale per un parco rispettando i vincoli di durata, budget e punti di interesse unici.
        :param id_parco: id del parco
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Escursione)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il voto complessivo dei visitatori per il pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        self._escursioni_parco = []
        self._max_giorni = max_giorni
        self._max_budget = max_budget
        pacchetto =[]
        punti = set()

        for s in self.escursioni_map.values():
            if s.id_parco == id_parco:
                self._escursioni_parco.append(s)

        self._ricorsione(0, pacchetto, 0, 0, 0, punti)

        return self._pacchetto_ottimo, self._costo, self._valore_ottimo



    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, punti_usati: set):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il voto complessivo dei visitatori"""
        # è possibile cambiare i parametri formali della funzione se ritenuto opportuno

        if valore_corrente > self._valore_ottimo:#do always
            self._valore_ottimo = valore_corrente
            self._costo = costo_corrente
            self._pacchetto_ottimo = pacchetto_parziale.copy()

        for i in range(start_index, len(self._escursioni_parco)):
            e = self._escursioni_parco[i]
            if e.punti_interesse & punti_usati:#& è l'intersezione tra set
                continue
            if self._max_giorni is not None and (durata_corrente + e.durata_giorni) > self._max_giorni:
                continue
            if self._max_budget is not None and costo_corrente + e.costo > self._max_budget:
                continue

            voto_e = sum(p.voto_visitatori for p in e.punti_interesse)

            pacchetto_parziale.append(e)
            punti_usati.update(e.punti_interesse)

            self._ricorsione(i+1,pacchetto_parziale,
                             durata_corrente+e.durata_giorni,
                             costo_corrente+e.costo,
                             valore_corrente+ voto_e,
                             punti_usati)

            pacchetto_parziale.pop()
            punti_usati.discard(e.punti_interesse)






