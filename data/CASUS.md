# Test Correct Leerlingen Analyse

## Context opdrachtgever
Test Correct is een bedrijf dat digitale toetsen aanbiedt in het onderwijs, op een manier die het leerproces van leerlingen verder ondersteunt. In deze casus werk je aan een proof-of-concept dat aansluit bij de visie van Test Correct: toetsresultaten moeten niet alleen beoordelen, maar ook richting geven aan het verdere leren.

De opdrachtgever is geïnteresseerd in een werkend proof-of-concept. Als er een mooi en nuttig product ontstaat, bestaat de kans dat (delen van) jullie oplossing worden doorontwikkeld.

## Opdracht in één zin
Ontwerp en realiseer een webapplicatie die leerlingen helpt inzicht te krijgen in hun kennisvoortgang door hun resultaten uit Test Correct visueel te representeren en deze te gebruiken om gerichte adviezen en suggesties te genereren.

## Globale beschrijving
Je bouwt een webapplicatie waarin een dataset vanuit Test Correct (TC) geïmporteerd kan worden. In deze dataset staat informatie over het kennen en kunnen van een leerling voor een specifiek vak. De applicatie helpt leerlingen door een visualisatie van hun resultaten per leerdoel, kernwoord/onderwerp en taxonomieniveau.

Als bonusdoel biedt de applicatie functionaliteit voor docenten om op individueel én klasniveau inzicht te krijgen in sterke en zwakke punten. Optioneel kan een LLM (Large Language Model) worden ingezet om bronnen en lesideeën te suggereren op basis van geconstateerde zwaktes.


---

## Gebruikers en rollen

### Leerling
De leerling van de applicatie en kan:
- Alleen zijn/haar eigen voortgang en resultaten bekijken.
- Inzicht krijgen in sterke en zwakke punten per leerdoel en per kernwoord/onderwerp.
- Aanbevolen leerbronnen zien die aansluiten bij persoonlijke zwaktes.

### Docent
De docent is de primaire eindgebruiker en gebruikt de applicatie om:
- De voortgang van individuele leerlingen te bekijken.
- De voortgang en zwakke/sterke punten van een gehele klas te analyseren.
- Op basis daarvan gerichte vervolgstappen te plannen (bijv. welke onderwerpen in de les terug moeten komen).

De docent kan meer data over meerdere leerlingen/klassen zien; de leerling ziet uitsluitend eigen data.

---

## Dataset en domeinmodel

### Voorbeeld JSON-structuur uit Test Correct
Onderstaand voorbeeld illustreert hoe een dataset voor één leerling en één vak er in JSON uit kan zien. Teams mogen (in overleg met de opdrachtgever/docent) hier licht van afwijken, maar de betekenis van de velden moet vergelijkbaar blijven.

```json
{
  "student": { "id": 12345, "name": "Sam" },
  "subject": { "id": 12, "name": "Biologie" },

  "taxonomyScale": ["Onthouden", "Begrijpen", "Toepassen", "Analyseren"],

  "learningGoals": [
    {
      "id": "LG-1",
      "title": "Fotosynthese uitleggen",
      "keywords": ["chlorofyl", "glucose", "CO2", "zuurstof"],

      "snapshots": [
        {
          "at": "2025-11-01",
          "source": { "type": "quiz", "id": "QZ-88" },
          "taxonomy": [
            { "level": "Onthouden", "kennen": 0.80, "kunnen": 0.55, "confidence": 0.8 },
            { "level": "Begrijpen", "kennen": 0.65, "kunnen": 0.45, "confidence": 0.7 },
            { "level": "Toepassen", "kennen": 0.45, "kunnen": 0.25, "confidence": 0.6 },
            { "level": "Analyseren", "kennen": 0.20, "kunnen": 0.10, "confidence": 0.5 }
          ]
        },
        {
          "at": "2025-12-10",
          "source": { "type": "test", "id": "TS-12" },
          "taxonomy": [
            { "level": "Onthouden", "kennen": 0.88, "kunnen": 0.70, "confidence": 0.85 },
            { "level": "Begrijpen", "kennen": 0.72, "kunnen": 0.58, "confidence": 0.78 },
            { "level": "Toepassen", "kennen": 0.55, "kunnen": 0.40, "confidence": 0.70 },
            { "level": "Analyseren", "kennen": 0.25, "kunnen": 0.15, "confidence": 0.55 }
          ]
        }
      ]
    },

    {
      "id": "LG-2",
      "title": "Cellen en organellen herkennen",
      "keywords": ["celkern", "mitochondriën", "celmembraan"],
      "snapshots": [
        {
          "at": "2025-12-10",
          "source": { "type": "observatie", "id": "OBS-3" },
          "taxonomy": [
            { "level": "Onthouden", "kennen": 0.62, "kunnen": 0.50, "confidence": 0.65 },
            { "level": "Begrijpen", "kennen": 0.55, "kunnen": 0.48, "confidence": 0.60 },
            { "level": "Toepassen", "kennen": 0.35, "kunnen": 0.28, "confidence": 0.55 },
            { "level": "Analyseren", "kennen": 0.18, "kunnen": 0.12, "confidence": 0.45 }
          ]
        }
      ]
    }
  ]
}
```

### Toelichting op de velden

- `student.id`  
  Unieke identificatie van de leerling binnen de dataset.

- `student.name`  
  Naam van de leerling. 

- `subject.id`  
  Unieke identificatie van het vak binnen het systeem (bijv. een interne code).

- `subject.name`  
  Naam van het vak (bijv. "Biologie").

- `taxonomyScale`  
  De lijst van mogelijke taxonomie niveaus die in deze dataset gebruikt worden (bijv. een subset van Bloom). Dit kan gebruikt worden om grafieken/overzichten in een vaste volgorde te tonen, en om te controleren of alle niveaus ingevuld zijn.

- `learningGoals`  
  Een lijst van leerdoelen binnen dit vak waarvoor resultaten beschikbaar zijn.

  - `learningGoals[].id`  
    Unieke identificatie van het leerdoel.

  - `learningGoals[].title`  
    Korte omschrijving van het leerdoel.

  - `learningGoals[].keywords`  
    Een lijst van kernwoorden/onderwerpen die bij dit leerdoel horen.

  - `learningGoals[].snapshots`  
    Een lijst van metingen/momentopnames voor dit leerdoel. Elke snapshot komt bijvoorbeeld uit een toets, quiz, observatie of andere bron.

    - `snapshots[].at`  
      Datum (of datum/tijd) waarop deze meting is gedaan.

    - `snapshots[].source.type`  
      Type bron van de meting (bijv. `"quiz"`, `"test"`, `"observatie"`).

    - `snapshots[].source.id`  
      Identificatie van de bron.

    - `snapshots[].taxonomy`  
      Een lijst met scores per taxonomieniveau voor dit leerdoel op dit moment. Verwacht wordt dat de niveaus overeenkomen met `taxonomyScale`.

      - `taxonomy[].level`  
        Naam van het taxonomieniveau (bijv. `"Onthouden"`, `"Begrijpen"`).

      - `taxonomy[].kennen`  
        Een score tussen 0 en 1 voor wat de leerling weet op dit niveau binnen dit leerdoel.

      - `taxonomy[].kunnen`  
        Een score tussen 0 en 1 voor wat de leerling kan toepassen op dit niveau binnen dit leerdoel.

      - `taxonomy[].confidence`  
        Een maat voor de betrouwbaarheid/zekerheid van deze meting.


---

## Functionele eisen

### 1. Leerlingfunctionaliteit (verplicht)
De applicatie biedt voor de leerling minimaal de volgende functionaliteiten:

1. Voortgang inzien over de tijd  
   De leerling kan zijn/haar voortgang per vak/toets inzien, bijvoorbeeld via een overzicht of grafiek die resultaten over de tijd toont.

2. Inzicht per leerdoel  
   De leerling kan per leerdoel zien hoe sterk of zwak hij/zij staat (bijv. door scores, kleuren, of een schaalindicatie).

3. Inzicht per kernwoord/onderwerp  
   De leerling kan per kernwoord of onderwerp zien waar de sterke en zwakke punten liggen.

### 2. Leerlingfunctionaliteit (bonus)

1. Aanbevolen leerbronnen  
   De leerling kan een lijst met aanbevolen leerbronnen zien die aansluiten bij zijn/haar zwakke punten, met per bron:
   - Een link naar de bron.
   - Een korte omschrijving van de inhoud en waarom deze relevant is.

2. Detail/reden van aanbeveling  
   De leerling kan een bron aanklikken om meer detail te zien, bijvoorbeeld:
   - Welke leerdoelen of onderwerpen hiermee geoefend worden.
   - Waarom deze bron passend is bij het niveau van de leerling.


### 3. Docentfunctionaliteit (verplicht)
De applicatie biedt voor de docent minimaal de volgende functionaliteiten:

1. Overzicht per klas  
   Een docent kan voor een gekozen klas:
   - Een overzicht zien van alle leerlingen met globale voortgang/status.
   - In één oogopslag zien welke leerlingen achterlopen of uitblinken.

2. Aggregatie per leerdoel en taxonomieniveau  
   De docent kan op klasniveau zien:
   - Welke leerdoelen gemiddeld zwak/sterk zijn.
   - Op welke taxonomieniveaus (bijv. toepassen/analyseren) de klas moeite heeft.
   - Welke kernwoorden/onderwerpen voor de klas problematisch zijn.

### 4. Docentfunctionaliteit (bonus)
De volgende functionaliteiten zijn bonusdoelen en kunnen gebruikt worden als uitbreidingen voor sterkere teams:

1. Lesvoorstel op basis van klassenanalyse (LLM)  
   De docent kan, op basis van de geconstateerde zwaktes in de klas, een suggestie voor lesinhoud laten genereren door een LLM, bijvoorbeeld:
   - Beschrijving van een les of lesreeks.
   - Concrete leerdoelen en kernwoorden.
   - Suggesties voor werkvormen.

2. Exportmogelijkheden  
   Mogelijkheid om een overzicht (bijv. per klas of per leerdoel) te exporteren naar een formaat zoals CSV of PDF.

---

## Visualisaties
De opdracht schrijft geen exacte visualisatievormen voor; teams hebben hier ontwerpvrijheid. Wel wordt van jullie verwacht dat visualisaties:
- Overzichtelijk en interpreteerbaar zijn voor leerling en docent.
- Inzicht geven in trends (over tijd) en in verdeling van resultaten over leerdoelen, kernwoorden en taxonomieniveaus.

Voorbeelden (niet verplicht, maar als inspiratie):
- Een voortgangsbalk per leerdoel of onderwerp.
- Een radar-/spiderchart die prestaties per leerdoel of taxonomieniveau toont.
- Een heatmap die laat zien welke onderwerpen of leerdoelen zwak/sterk zijn.

---

## Technische eisen

### Backend
- De backend is geschreven in Python.
- Gebruik van Python-webframeworks (bijv. Flask, FastAPI, Django) is toegestaan en aanbevolen.
- Gebruik van een ORM is toegestaan (en aan te raden) om met de database te werken.

### Frontend
- De frontend maakt minimaal gebruik van HTML, CSS en JavaScript.
- Het gebruik van CSS-frameworks zoals Bootstrap of Tailwind CSS is toegestaan.
- Pagina's met interactie (zoals filters, het laden van detailinformatie, het opvragen van nieuwe visualisaties) worden asynchroon bijgewerkt met AJAX (bijv. via `fetch` of `XMLHttpRequest`), dus zonder volledige paginavernieuwing.
- Er wordt rekening gehouden met de WCAG-richtlijnen.

### Database
- De applicatie gebruikt SQLite als database.
- Het datamodel is zodanig opgezet dat de eerder beschreven velden (leerling, vak, toets, leerdoel, taxonomieniveau, kernwoorden, scores) logisch zijn vastgelegd.
- De documentatie bevat een ERD van de database.

### Installatie en documentatie
- Er is een heldere installatie-instructie (bijv. in een `README.md`) waarin minimaal staat:
  - Vereiste software (bijv. Python-versie).
  - Hoe dependencies geïnstalleerd worden.
  - Hoe de database wordt aangemaakt/geïnitialiseerd.
  - Hoe de applicatie gestart kan worden.

---

## Niet-functionele eisen

De applicatie voldoet minimaal aan de volgende kwaliteitseisen:

1. Foutafhandeling  
   - De applicatie geeft duidelijke, gebruikersvriendelijke foutmeldingen.
   - Interne fouten (bijv. stacktraces) worden niet direct aan de eindgebruiker getoond.

2. Duidelijke frontend-backend scheiding  
   - De frontend communiceert met de backend via een duidelijke API (bijv. REST-endpoints).
   - Belangrijke endpoints zijn beknopt gedocumenteerd (bijv. in een korte API-sectie of via comments).
   - Interactieve onderdelen gebruiken AJAX-calls naar deze API.

3. Beveiliging en autorisatie (basisniveau)  
   - Er is een eenvoudige vorm van inloggen die onderscheid maakt tussen:
     - Leerling: ziet uitsluitend eigen resultaten.
     - Docent: kan resultaten per leerling en per klas inzien.
   - Leerlingen kunnen geen gegevens van andere leerlingen inzien.

---

## Mogelijke uitbreidingen (bonusfeatures)
Naast de eerder genoemde bonusfunctionaliteiten (LLM-aanbevelingen voor leerlingen, lesvoorstellen voor docenten, exports) kun je denken aan de volgende uitbreidingen:

1. Dashboards met klassikale vergelijking  
   - Een leerling kan (anoniem of geaggregeerd) zien hoe zijn/haar resultaten zich verhouden tot het klasgemiddelde.
   - Een docent krijgt uitgebreide dashboards waarin leerlingen, leerdoelen en niveaus onderling vergeleken kunnen worden.

2. Gamification-elementen  
   - Badges, levels of andere beloningen voor behaalde mijlpalen (bijv. verbetering op een leerdoel, aantal gemaakte oefeningen).
   - Visuele feedback die het werken met de applicatie motiverend maakt.

3. Eigen uitbreiding door studenten  
   - Een door het team zelf bedachte, waardevolle toevoeging die past bij de doelgroep en het doel van de applicatie.  
   - Deze uitbreiding moet duidelijk worden beschreven en gemotiveerd: waarom is dit nuttig voor leerling/docent en hoe sluit het aan bij de casus?

---

## Samenvatting minimale scope (MVP)
Een project voldoet minimaal aan de casus als:
- Er een werkende webapplicatie is met een Python-backend, HTML/CSS/JS-frontend en SQLite-database.
- Een dataset met leerlingresultaten uit TC (of een gesimuleerde versie) geïmporteerd en opgeslagen kan worden.
- Leerlingen hun eigen voortgang en sterke/zwakke punten per leerdoel en kernwoord/onderwerp kunnen inzien.
- Docenten op klas- én leerlingniveau inzicht krijgen in resultaten, inclusief aggregatie per leerdoel en taxonomieniveau.
- Er basisfoutafhandeling, een eenvoudige vorm van autorisatie en AJAX-gebaseerde interactie aanwezig is.
- Er een duidelijke installatie-instructie en korte toelichting van architectuur/API aanwezig is.

Bonusfeatures (zoals LLM-integratie, geavanceerde dashboards, gamification, exports en eigen uitbreidingen) zijn niet verplicht, maar worden positief gewaardeerd en bieden ruimte voor verdieping voor wie dat zoekt.
