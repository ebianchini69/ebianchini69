// Contenuti del libro. Modifica qui testi, nome del destinatario e dedica,
// poi rigenera il PDF con:  node build.js
//
// Per ogni momento metti la scansione della pagina di giornale nella cartella
// scansioni/ con il nome del campo "id" (es. scansioni/1964-coppa-campioni.jpg).
// Se il file non c'è, nel PDF compare un riquadro segnaposto.

module.exports = {
  formato: {
    // A4 verticale + 3 mm di abbondanza per lato (standard tipografico).
    // Se scegli un altro formato di fotolibro, cambia larghezza/altezza in mm.
    larghezza: 210,
    altezza: 297,
    abbondanza: 3,
  },

  destinatario: "[Nome]",
  dedica: [
    "Per [Nome],",
    "perché certe storie si tramandano.",
    "Questa è la nostra: centodiciotto anni di nerazzurro,",
    "raccontati da chi c'era, la mattina dopo.",
  ],
  firma: "[La tua firma] · Natale 2026",

  epigrafe: {
    testo:
      "Questa notte splendida darà i colori al nostro stemma: il nero e l'azzurro sul fondo d'oro delle stelle. Si chiamerà Internazionale, perché noi siamo fratelli del mondo.",
    autore: "Milano, 9 marzo 1908",
  },

  introduzione: [
    "Ogni grande storia di calcio ha due tempi. Il primo si gioca in campo, novanta minuti e poi la festa o il silenzio. Il secondo comincia la mattina dopo, in edicola, quando i giornali mettono in pagina quello che è successo e lo consegnano alla memoria.",
    "Questo libro raccoglie quelle mattine. Dalla sera del 1908 in cui un gruppo di amici fondò l'Internazionale, fino alla seconda stella: le pagine dei giornali dell'epoca, così come uscirono, una dopo l'altra.",
    "Accanto a ogni pagina, poche righe per ricordare il contesto: chi c'era, come andò, perché quel giorno conta ancora.",
  ],

  capitoli: [
    {
      numero: "I",
      titolo: "Fratelli del mondo",
      anni: "1908 – 1928",
      intro:
        "Una scissione, un nome scelto per accogliere tutti, due scudetti in pochi anni. L'Inter nasce così: ribelle, cosmopolita, subito vincente.",
      momenti: [
        {
          id: "1908-fondazione",
          data: "9 marzo 1908",
          titolo: "Nasce l'Internazionale",
          testo:
            "Al ristorante L'Orologio, in centro a Milano, un gruppo di soci in dissenso con il Milan fonda una nuova squadra. Il nome è una dichiarazione d'intenti: Internazionale, aperta ai giocatori stranieri. I colori sono il nero e l'azzurro.",
          tabellino: "Milano, ristorante L'Orologio",
          giornale: "Pagina ricostruita in stile d'epoca · La Gazzetta dello Sport, 10 marzo 1908",
        },
        {
          id: "1910-primo-scudetto",
          data: "24 aprile 1910",
          titolo: "Il primo scudetto, a due anni dalla nascita",
          testo:
            "Lo spareggio con la Pro Vercelli finisce 10-3. I piemontesi, in polemica con la data fissata, schierano i ragazzi delle giovanili. L'Inter è campione d'Italia per la prima volta.",
          tabellino: "Inter – Pro Vercelli 10-3 · spareggio scudetto",
          giornale: "Pagina ricostruita in stile d'epoca · La Gazzetta dello Sport, 25 aprile 1910",
        },
        {
          id: "1920-secondo-scudetto",
          data: "20 giugno 1920",
          titolo: "Il secondo titolo dopo la Grande Guerra",
          testo:
            "Il calcio riparte dopo il conflitto e l'Inter torna sul tetto d'Italia battendo il Livorno nella finale del campionato.",
          tabellino: "Finale a Bologna: Inter – Livorno 3-2",
          giornale: "Pagina ricostruita in stile d'epoca · La Gazzetta dello Sport, 21 giugno 1920",
        },
      ],
    },
    {
      numero: "II",
      titolo: "Gli anni dell'Ambrosiana",
      anni: "1928 – 1945",
      intro:
        "Il regime impone la fusione e un nuovo nome, Ambrosiana. Ma in campo c'è il più grande attaccante italiano dell'epoca, Giuseppe Meazza, e gli scudetti arrivano lo stesso.",
      momenti: [
        {
          id: "1930-scudetto-meazza",
          data: "29 giugno 1930",
          titolo: "Il primo campionato a girone unico è nerazzurro",
          testo:
            "Nasce la Serie A come la conosciamo e la vince l'Ambrosiana. Giuseppe Meazza, vent'anni appena, è capocannoniere con 31 gol: il ragazzo di Porta Vittoria diventa il simbolo di Milano.",
          tabellino: "Ambrosiana – Juventus 2-0 · Meazza capocannoniere con 31 gol",
          giornale: "Pagina ricostruita in stile d'epoca · La Gazzetta dello Sport, 30 giugno 1930",
        },
        {
          id: "1938-scudetto",
          data: "24 aprile 1938",
          titolo: "Ambrosiana-Inter, di nuovo campione",
          testo:
            "Sotto il nome di Ambrosiana-Inter arriva il quarto scudetto. Meazza è ancora il capocannoniere del campionato.",
          tabellino: "Bari – Ambrosiana-Inter 0-2 · Meazza, Frossi",
          giornale: "Pagina ricostruita in stile d'epoca · La Gazzetta dello Sport, 25 aprile 1938",
        },
        {
          id: "1940-scudetto",
          data: "2 giugno 1940",
          titolo: "Il quinto scudetto alla vigilia della guerra",
          testo:
            "L'ultimo titolo prima che il conflitto fermi tutto. Pochi anni dopo, nel 1945, la squadra riprenderà il suo nome: Internazionale.",
          tabellino: "Ambrosiana-Inter – Bologna 1-0",
          giornale: "Pagina ricostruita in stile d'epoca · La Gazzetta dello Sport, 3 giugno 1940",
        },
      ],
    },
    {
      numero: "III",
      titolo: "Il dopoguerra",
      anni: "1945 – 1959",
      intro:
        "Milano si ricostruisce e l'Inter con lei. Arrivano due scudetti consecutivi e, nel 1955, un petroliere appassionato di nome Angelo Moratti.",
      momenti: [
        {
          id: "1953-scudetto",
          data: "3 maggio 1953",
          titolo: "Lo scudetto di Foni",
          testo: "La Roma batte la Juventus 3-0 e chiude il discorso: lo scudetto è dell'Inter di Alfredo Foni, con l'estro di Nyers, Skoglund e Lorenzi davanti. È il sesto titolo.",
          tabellino: "Roma – Juventus 3-0 · titolo matematico",
          giornale: "l'Unità del lunedì, 4 maggio 1953, pagina sportiva",
        },
        {
          id: "1954-scudetto",
          data: "30 maggio 1954",
          titolo: "Il bis",
          testo: "All'ultima giornata l'Inter batte la Triestina e resiste alla Juventus: il pubblico di San Siro porta in trionfo i campioni. Foni è il primo allenatore nerazzurro a vincere due scudetti.",
          tabellino: "Inter – Triestina 4-2 · settimo scudetto",
          giornale: "l'Unità del lunedì, 31 maggio 1954, pagina sportiva",
        },
      ],
    },
    {
      numero: "IV",
      titolo: "La Grande Inter",
      anni: "1960 – 1967",
      intro:
        "Angelo Moratti chiama Helenio Herrera, il Mago. Sarti, Burgnich, Facchetti; Bedin, Guarneri, Picchi; Jair, Mazzola, Milani, Suárez, Corso. Una filastrocca che ancora oggi si recita a memoria.",
      momenti: [
        {
          id: "1963-scudetto",
          data: "5 maggio 1963",
          titolo: "Il Mago vince il primo scudetto",
          testo: "Paradosso da raccontare: l'Inter perde 3-0 all'Olimpico, ma i risultati delle rivali le consegnano lo scudetto con tre giornate d'anticipo. È l'ottavo titolo, il primo di Helenio Herrera.",
          tabellino: "Roma – Inter 3-0 · ma lo scudetto è nerazzurro",
          giornale: "l'Unità sport, 6 maggio 1963, prima pagina",
        },
        {
          id: "1964-coppa-campioni",
          data: "27 maggio 1964",
          titolo: "Vienna, l'Europa è nerazzurra",
          testo:
            "Al Prater l'avversario è il Real Madrid di Di Stéfano e Puskás. Finisce 3-1 con la doppietta di Sandro Mazzola e il gol di Milani. È la prima Coppa dei Campioni dell'Inter.",
          tabellino: "Inter – Real Madrid 3-1 · Mazzola 2, Milani",
          giornale: "l'Unità, 28 maggio 1964, pagina sportiva",
        },
        {
          id: "1964-intercontinentale",
          data: "26 settembre 1964",
          titolo: "Campioni del mondo",
          testo:
            "Contro l'Independiente serve lo spareggio, a Madrid. Lo decide Mario Corso ai supplementari: l'Inter è campione del mondo per club.",
          tabellino: "Spareggio: Inter – Independiente 1-0 d.t.s. · Corso",
          giornale: "l'Unità, 27 settembre 1964, pagina sportiva",
        },
        {
          id: "1965-coppa-campioni",
          data: "27 maggio 1965",
          titolo: "Il bis sotto la pioggia di San Siro",
          testo:
            "La finale si gioca in casa, su un campo pesante. Contro il Benfica di Eusébio basta un tiro di Jair. Seconda Coppa dei Campioni consecutiva.",
          tabellino: "Inter – Benfica 1-0 · Jair",
          giornale: "l'Unità, 28 maggio 1965, pagina sportiva",
        },
        {
          id: "1965-intercontinentale",
          data: "8 settembre 1965",
          titolo: "Ancora sul tetto del mondo",
          testo: "Di nuovo l'Independiente, di nuovo l'Inter: a San Siro finisce 3-0, con Peiró e la doppietta di Mazzola. Il pareggio in Argentina una settimana dopo vale la seconda Coppa Intercontinentale.",
          tabellino: "Inter – Independiente 3-0 · 0-0",
          giornale: "l'Unità, 9 settembre 1965, pagina sportiva",
        },
        {
          id: "1966-prima-stella",
          data: "15 maggio 1966",
          titolo: "Dieci scudetti: la prima stella",
          testo:
            "Il decimo titolo vale la stella d'oro sulla maglia. La Grande Inter chiude il suo ciclo da leggenda.",
          tabellino: "Inter – Lazio 4-1 · decimo scudetto, prima stella",
          giornale: "l'Unità sport, 16 maggio 1966",
        },
      ],
    },
    {
      numero: "V",
      titolo: "Tra due epoche",
      anni: "1967 – 1994",
      intro:
        "Finita la leggenda, l'Inter resta grande. Tre scudetti in vent'anni, ognuno con il suo carattere, e le prime Coppe UEFA.",
      momenti: [
        {
          id: "1971-scudetto",
          data: "2 maggio 1971",
          titolo: "La rimonta di Invernizzi",
          testo:
            "Partita male, la squadra cambia allenatore e con Giovanni Invernizzi rimonta fino allo scudetto, superando il Milan. Boninsegna è il capocannoniere.",
          tabellino: "Inter – Foggia 5-0 · undicesimo scudetto",
          giornale: "l'Unità, 3 maggio 1971, pagina sportiva",
        },
        {
          id: "1980-scudetto",
          data: "27 aprile 1980",
          titolo: "Lo scudetto di Bersellini",
          testo:
            "Una squadra giovane, con Altobelli e Beccalossi, vince il dodicesimo titolo.",
          tabellino: "Inter – Roma 2-2 · dodicesimo scudetto",
          giornale: "l'Unità, 28 aprile 1980, pagina sportiva",
        },
        {
          id: "1989-scudetto-record",
          data: "28 maggio 1989",
          titolo: "Lo scudetto dei record",
          testo:
            "L'Inter di Trapattoni, con i tedeschi Matthäus e Brehme, chiude a 58 punti: il record dell'epoca dei due punti a vittoria. Serena è capocannoniere.",
          tabellino: "Inter – Napoli 2-1 · 58 punti a fine stagione",
          giornale: "l'Unità, 29 maggio 1989, pagina sportiva",
        },
        {
          id: "1991-coppa-uefa",
          data: "22 maggio 1991",
          titolo: "La prima Coppa UEFA",
          testo:
            "La finale è tutta italiana contro la Roma. Il 2-0 di San Siro basta: la sconfitta per 1-0 all'Olimpico non cambia nulla.",
          tabellino: "Inter – Roma 2-0 · 0-1",
          giornale: "l'Unità, 23 maggio 1991, pagina sportiva",
        },
        {
          id: "1994-coppa-uefa",
          data: "11 maggio 1994",
          titolo: "La seconda Coppa UEFA",
          testo:
            "In una stagione difficile in campionato, l'Inter vince in Europa: doppio 1-0 al Casino Salisburgo.",
          tabellino: "Casino Salisburgo – Inter 0-1 · Inter – Casino Salisburgo 1-0",
          giornale: "l'Unità, 12 maggio 1994, pagina sportiva",
        },
      ],
    },
    {
      numero: "VI",
      titolo: "L'era di Massimo Moratti",
      anni: "1995 – 2004",
      intro:
        "Il figlio di Angelo riporta la famiglia alla guida del club. Arrivano Javier Zanetti e, nel 1997, il giocatore più forte del mondo: Ronaldo.",
      momenti: [
        {
          id: "1997-ronaldo",
          data: "25 luglio 1997",
          titolo: "Arriva il Fenomeno",
          testo:
            "Massimo Moratti porta a Milano Ronaldo, il giocatore più forte del mondo. San Siro non aveva mai visto niente di simile.",
          tabellino: "Ronaldo Luís Nazário de Lima",
          giornale: "l'Unità, 26 luglio 1997, pagina sportiva",
        },
        {
          id: "1998-coppa-uefa",
          data: "6 maggio 1998",
          titolo: "Parigi, la notte del Fenomeno",
          testo:
            "Al Parco dei Principi la finale contro la Lazio finisce 3-0: segnano Zamorano, Zanetti e Ronaldo. Terza Coppa UEFA.",
          tabellino: "Inter – Lazio 3-0 · Zamorano, Zanetti, Ronaldo",
          giornale: "l'Unità, 7 maggio 1998, pagina sportiva",
        },
      ],
    },
    {
      numero: "VII",
      titolo: "Il ciclo d'oro",
      anni: "2005 – 2011",
      intro:
        "Cinque scudetti consecutivi, poi la stagione perfetta. Con José Mourinho l'Inter diventa la prima squadra italiana a vincere campionato, coppa nazionale e Champions League nello stesso anno.",
      momenti: [
        {
          id: "2007-scudetto-record",
          data: "22 aprile 2007",
          titolo: "97 punti",
          testo:
            "L'Inter di Roberto Mancini domina il campionato: 17 vittorie consecutive e 97 punti, il record del campionato italiano di allora.",
          tabellino: "Siena – Inter 1-2 · Materazzi 2 · 97 punti a fine stagione",
          giornale: "l'Unità, 23 aprile 2007, pagina sportiva",
        },
        {
          id: "2008-parma",
          data: "18 maggio 2008",
          titolo: "Ibra sotto la pioggia di Parma",
          testo:
            "All'ultima giornata, con la Roma a un passo, entra Ibrahimović e segna due gol sotto il diluvio. Scudetto.",
          tabellino: "Parma – Inter 0-2 · Ibrahimović 2",
          giornale: "l'Unità, 19 maggio 2008, pagina sportiva",
        },
        {
          id: "2009-scudetto-mourinho",
          data: "16 maggio 2009",
          titolo: "Il primo scudetto di Mourinho",
          testo:
            "Il primo anno dello Special One finisce con il quarto titolo di fila. Ma l'anno dopo sarà un'altra storia.",
          tabellino: "Allenatore: José Mourinho",
          giornale: "La Gazzetta dello Sport, 17 maggio 2009",
        },
        {
          id: "2010-coppa-italia",
          data: "5 maggio 2010",
          titolo: "Triplete, atto primo",
          testo:
            "All'Olimpico, contro la Roma, decide Diego Milito. Coppa Italia.",
          tabellino: "Inter – Roma 1-0 · Milito",
          giornale: "La Gazzetta dello Sport, 6 maggio 2010",
        },
        {
          id: "2010-scudetto-siena",
          data: "16 maggio 2010",
          titolo: "Triplete, atto secondo",
          testo:
            "Ultima giornata, a Siena. Ancora Milito. Diciottesimo scudetto.",
          tabellino: "Siena – Inter 0-1 · Milito",
          giornale: "La Gazzetta dello Sport, 17 maggio 2010",
        },
        {
          id: "2010-champions-madrid",
          data: "22 maggio 2010",
          titolo: "Madrid. Il Triplete.",
          testo:
            "Al Bernabéu, contro il Bayern Monaco, Diego Milito segna due volte. Quarantacinque anni dopo, la Coppa dei Campioni torna a Milano, sponda nerazzurra. Nessuna squadra italiana aveva mai vinto tutto in una sola stagione.",
          tabellino: "Bayern Monaco – Inter 0-2 · Milito 2",
          giornale: "La Gazzetta dello Sport, 23 maggio 2010",
          grande: true,
        },
        {
          id: "2010-mondiale-club",
          data: "18 dicembre 2010",
          titolo: "Campioni del mondo, di nuovo",
          testo:
            "Ad Abu Dhabi l'Inter batte il TP Mazembe e chiude l'anno più bello della sua storia con il Mondiale per club.",
          tabellino: "Inter – TP Mazembe 3-0",
          giornale: "La Gazzetta dello Sport, 19 dicembre 2010",
        },
      ],
    },
    {
      numero: "VIII",
      titolo: "La seconda stella",
      anni: "2019 – oggi",
      intro:
        "Dopo anni di attesa l'Inter torna a vincere, e torna in finale di Champions League. Fino al derby che vale il ventesimo scudetto.",
      momenti: [
        {
          id: "2021-scudetto",
          data: "2 maggio 2021",
          titolo: "Il diciannovesimo",
          testo:
            "Dopo undici anni l'Inter di Antonio Conte è di nuovo campione d'Italia, con Lukaku e Lautaro in attacco. Gli stadi sono vuoti per la pandemia, ma le strade di Milano no.",
          tabellino: "Allenatore: Antonio Conte",
          giornale: "La Gazzetta dello Sport, 3 maggio 2021",
        },
        {
          id: "2023-istanbul",
          data: "10 giugno 2023",
          titolo: "Istanbul, a testa alta",
          testo:
            "La finale di Champions League contro il Manchester City si decide per un gol. Sconfitta, ma una squadra che nessuno dava per finalista se la gioca fino all'ultimo pallone.",
          tabellino: "Manchester City – Inter 1-0",
          giornale: "La Gazzetta dello Sport, 11 giugno 2023",
        },
        {
          id: "2024-seconda-stella",
          data: "22 aprile 2024",
          titolo: "Venti scudetti. La seconda stella, nel derby",
          testo:
            "Lo scudetto numero venti arriva nel modo più dolce: vincendo il derby contro il Milan. Sulla maglia nerazzurra si cuce la seconda stella.",
          tabellino: "Milan – Inter 1-2 · Acerbi, Thuram",
          giornale: "La Gazzetta dello Sport, 23 aprile 2024",
          grande: true,
        },
        {
          id: "2026-scudetto",
          data: "3 maggio 2026",
          titolo: "Ventuno di gloria",
          testo:
            "Al primo anno da allenatore dell'Inter, Cristian Chivu, uno degli eroi del Triplete, vince lo scudetto con tre giornate d'anticipo battendo il Parma a San Siro. È il ventunesimo titolo.",
          tabellino: "Inter – Parma 2-0 · ventunesimo scudetto",
          giornale: "La Gazzetta dello Sport, 4 maggio 2026",
        },
        {
          id: "2026-coppa-italia",
          data: "13 maggio 2026",
          titolo: "E sono due",
          testo:
            "Dieci giorni dopo lo scudetto, all'Olimpico arriva anche la Coppa Italia, la decima della storia nerazzurra. È il double.",
          tabellino: "Lazio – Inter 0-2 · decima Coppa Italia",
          giornale: "La Gazzetta dello Sport, 14 maggio 2026",
        },
      ],
    },
    {
      numero: "IX",
      titolo: "La nostra storia",
      anni: "",
      intro:
        "Ogni tifoso ha una sua storia nerazzurra. Queste pagine sono per la tua.",
      momenti: [
        {
          id: "personale-nascita",
          data: "[Data di nascita]",
          titolo: "Il giorno in cui sei arrivato/a",
          testo:
            "[Cosa diceva il giornale quel giorno, e cosa faceva l'Inter.]",
          tabellino: "",
          giornale: "La Gazzetta dello Sport, [data]",
          verificare: true,
        },
        {
          id: "personale-partita",
          data: "[Data]",
          titolo: "[La nostra partita]",
          testo:
            "[La prima volta a San Siro, o la partita che non dimenticherete. Qui puoi mettere anche il biglietto o una vostra foto.]",
          tabellino: "",
          giornale: "[Giornale o foto]",
          verificare: true,
        },
      ],
    },
  ],

  chiusura: {
    titolo: "La storia continua",
    testo:
      "Le prossime pagine non sono ancora state scritte. Questo spazio è per la prima che varrà la pena conservare.",
  },

  fonti: [
    "Le pagine riprodotte provengono da La Gazzetta dello Sport e dagli altri quotidiani indicati sotto ogni immagine, che ne detengono i diritti.",
    "Questo volume è un esemplare unico, realizzato a mano come regalo privato e non destinato alla vendita.",
  ],
};
