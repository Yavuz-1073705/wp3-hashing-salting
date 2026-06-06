# Installatie-instructie

Deze README bevat de minimale installatie-informatie die volgens de casus vereist is.

## 1. Vereiste software
- Python 3.11 of hoger
- pip
- Windows PowerShell (voor de commando's hieronder)

## 2. Dependencies installeren
1. Maak een virtual environment aan:

```powershell
python -m venv .venv
```

2. Activeer de virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Installeer dependencies:

```powershell
pip install -r requirements.txt
```

Gebruik de virtual environment voor alle volgende commando's. Zo voorkom je problemen met oude of conflicterende Python-packages die al globaal op je computer staan.

## 3. Database aanmaken / initialiseren
Deze applicatie gebruikt SQLite. De database wordt automatisch aangemaakt bij het starten van de app.

Pad databasebestand:
- `data/app.db`

### Flask data import
Initialiseer en vul de database met voorbeelddata via Flask CLI:

```powershell
python -m flask --app run.py import-data data/data-sample-small.json
```

Bij de import worden klassen automatisch aangemaakt en gekoppeld:
- Als je JSON een klas bevat (`class.name`, `class`, `student.class`, `student.className` of `student.group`), dan wordt die klas aangemaakt/gebruikt.
- Als er geen klas in de JSON staat, dan wordt de leerling automatisch gekoppeld aan `Onbekende klas`.

Maak testaccounts voor leerlingen + docent aan:

```powershell
python -m flask --app run.py seed-users
```

## Inloggen
Docent login:
- E-mail: `docent@school.nl`
- Wachtwoord: `docent123`

Leerling logins:
Zo maak je een leerlingaccount aan:
1. Log in als docent met `docent@school.nl` en `docent123`.
2. Open het docentdashboard en kies een leerling.
3. Open de leerlingdetailpagina.
4. Vul e-mailadres en wachtwoord in bij Account aanmaken.
5. Klik op Account aanmaken.

## Klasbeheer
- Log in als docent en ga naar het docentdashboard.
- Maak bovenaan een nieuwe klas aan (bijv. `H2A`).
- Koppel leerlingen aan een klas via de nieuwe kolom `Klas` in de leerlingenlijst.
- Filter het dashboard op een specifieke klas via `Geselecteerde klas`.

## 4. Applicatie starten
Start de applicatie met:

```powershell
python run.py
```

## ERD
![ERD diagram](data/erd_testcorrectpng.png)

Dit is de ERD diagram.

## Screenshots + toelichting

### 1. Loginpagina
![Loginpagina](screenshots/login_page.png)

Inlogpagina voor docent en leerling; na inloggen wordt automatisch doorgestuurd naar het juiste dashboard op basis van de gebruikersrol.

### 2. Leerling dashboard (overzicht)
![Leerling dashboard overzicht](screenshots/leerling_dashboard.png)

Hoofdscherm van de leerling met filters, statistieken en grafieken voor voortgang over tijd en taxonomieniveaus.

### 3. Leerling dashboard (leerdoelen en kernwoorden)
![Leerling dashboard leerdoelen](screenshots/leerling_dashboard2.png)

Overzicht van leerdoelen met kennen/kunnen scores en onderaan aandachtspunten per kernwoord.

### 4. Docent dashboard (klassikaal)
![Docent dashboard klassikaal](screenshots/docent_dashboard.png)

Klassikaal docentdashboard met kerncijfers en grafieken voor zwakke leerdoelen en taxonomieniveaus.

### 5. Docent dashboard (leerling als dashboard)
![Docent dashboard leerling](screenshots/docent_dashboard_leerling.png)

Docentweergave van een individuele leerling in dashboardvorm met filters, trends en taxonomievisualisatie.

### 6. Docent dashboard (leerlingoverzicht tabel + kernwoorden)
![Docent dashboard leerlingoverzicht](screenshots/docent_dashboard_leerling2.png)

Tabel met alle leerlingen, gemiddelde scores, snapshots en status, met daaronder klassikale aandachtspunten op kernwoorden.

### 7. Docent leerlingenoverzicht
![Docent leerlingenoverzicht](screenshots/docent_leerlingoverzicht.png)

Overzichtspagina waarin de docent leerlingen kan selecteren en snel naar leerlingdetails kan navigeren.

### 8. Docent leerling detail
![Docent leerling detail](screenshots/docent_leerling_detail.png)

Detailpagina per leerling met resultaten per leerdoel en meetmoment, inclusief tabellen met kennen, kunnen en confidence per taxonomieniveau.

## Gebruikte bronnen (Yavuz)

### Python, Flask en database
- Gebruikte technieken: Python-functies, `if`/`else`, loops, list comprehensions, dictionaries, `set`, `try`/`except`, imports, returnwaarden, classes, `to_dict()`-serialisatie, Flask Blueprints, routes, `request.args`, `request.form`, `request.get_json()`, `jsonify()`, redirects, `url_for()`, `flash()`, `g.current_user`, CLI-commando's, foutafhandeling met HTTP-statuscodes, SQLAlchemy-modellen, kolommen, foreign keys, relationships, many-to-many tabellen, query's, `filter()`, `filter_by()`, `in_()`, `order_by()`, `first()`, `all()`, `db.session.add()`, `db.session.commit()`, SQLite en wachtwoord-hashing met Werkzeug.
- Python Software Foundation. (n.d.). *More control flow tools*. Python documentation. https://docs.python.org/3/tutorial/controlflow.html
- Python Software Foundation. (n.d.). *Data structures*. Python documentation. https://docs.python.org/3/tutorial/datastructures.html
- Python Software Foundation. (n.d.). *Classes*. Python documentation. https://docs.python.org/3/tutorial/classes.html
- Python Software Foundation. (n.d.). *Errors and exceptions*. Python documentation. https://docs.python.org/3/tutorial/errors.html
- Python Software Foundation. (n.d.). *Input and output*. Python documentation. https://docs.python.org/3/tutorial/inputoutput.html
- Python Software Foundation. (n.d.). *collections - Container datatypes*. Python documentation. https://docs.python.org/3/library/collections.html
- Pallets Projects. (n.d.). *Quickstart*. Flask documentation. https://flask.palletsprojects.com/en/stable/quickstart/
- Pallets Projects. (n.d.). *API*. Flask documentation. https://flask.palletsprojects.com/en/stable/api/
- Pallets Projects. (n.d.). *Modular applications with blueprints*. Flask documentation. https://flask.palletsprojects.com/en/stable/blueprints/
- Pallets Projects. (n.d.). *Command line interface*. Flask documentation. https://flask.palletsprojects.com/en/stable/cli/
- Pallets Projects. (n.d.). *Message flashing*. Flask documentation. https://flask.palletsprojects.com/en/stable/patterns/flashing/
- Pallets Projects. (n.d.). *Custom error pages*. Flask documentation. https://flask.palletsprojects.com/en/stable/patterns/errorpages/
- Pallets Projects. (n.d.). *Models and tables*. Flask-SQLAlchemy documentation. https://flask-sqlalchemy.palletsprojects.com/en/stable/models/
- SQLAlchemy. (n.d.). *Legacy query API*. SQLAlchemy 2.0 documentation. https://docs.sqlalchemy.org/en/20/orm/queryguide/query.html
- Pallets Projects. (n.d.). *Utilities*. Werkzeug documentation. https://werkzeug.palletsprojects.com/en/stable/utils/#werkzeug.security.generate_password_hash
- SQLite Consortium. (n.d.). *SQLite documentation*. https://www.sqlite.org/docs.html
- Stack Overflow. (2013). *How do you track the current user in flask-login?* van https://stackoverflow.com/questions/19274226/how-do-you-track-the-current-user-in-flask-login
- Stack Overflow. (2014). *Flask-SQLAlchemy filters and operators*. https://stackoverflow.com/questions/21674303/flask-sqlalchemy-filters-and-operators
- Stack Overflow. (2017). *Flask: getting url_prefix for blueprint in view*. https://stackoverflow.com/questions/41599500/flask-getting-url-prefix-for-blueprint-in-view

### JavaScript, DOM, AJAX en grafieken
- Gebruikte technieken: IIFE, `"use strict"`, variabelen, functies, conditionals, loops, `forEach()`, `map()`, `reduce()`, `sort()`, `slice()`, `Object.keys()`, `Array.isArray()`, `parseInt()`, `Math.round()`, template-opbouw met strings, DOM-selectie, `dataset`, `getElementById()`, `querySelectorAll()`, `createElement()`, `appendChild()`, `textContent`, `innerHTML`, event listeners, form submit handling, `preventDefault()`, Fetch API, promises, `.then()`, `.catch()`, `.finally()`, JSON requests, `JSON.stringify()`, `encodeURIComponent()`, loading/error states, HTML escaping en Chart.js lijn-, radar- en staafgrafieken.
- W3Schools.com. (n.d.). *JavaScript for loop*. https://www.w3schools.com/js/js_loop_for.asp
- W3Schools.com. (n.d.). *JavaScript array iteration*. https://www.w3schools.com/js/js_array_iteration.asp
- W3Schools.com. (n.d.). *JavaScript fetch API*. https://www.w3schools.com/js/js_api_fetch.asp
- W3Schools.com. (n.d.). *AJAX introduction*. https://www.w3schools.com/js/js_ajax_intro.asp
- W3Schools.com. (n.d.). *HTML DOM document createElement() method*. https://www.w3schools.com/jsref/met_document_createelement.asp
- W3Schools.com. (n.d.). *HTML DOM element appendChild() method*. https://www.w3schools.com/jsref/met_node_appendchild.asp
- W3Schools.com. (n.d.). *HTML DOM element addEventListener() method*. https://www.w3schools.com/jsref/met_element_addeventlistener.asp
- W3Schools.com. (n.d.). *HTML DOM element innerHTML property*. https://www.w3schools.com/jsref/prop_html_innerhtml.asp
- W3Schools.com. (n.d.). *JSON.stringify()*. https://www.w3schools.com/js/js_json_stringify.asp
- Chart.js. (n.d.). *Chart.js documentation*. https://www.chartjs.org/docs/latest/
- Stack Overflow. (2011). *What is AJAX and how does it work?* van https://stackoverflow.com/questions/6009206/what-is-ajax-and-how-does-it-work
- Stack Overflow. (2020). *How to get the average value of array in JavaScript*. https://stackoverflow.com/questions/60065105/how-to-get-the-average-value-of-array-in-javascript

### HTML, Jinja templates en formulieren
- Gebruikte technieken: template inheritance met `extends`/`block`, Jinja `if`/`elif`/`else`, Jinja `for`, `url_for()`, formulieren, inputvelden, submitknoppen, labels, `data-*` attributen, semantische layout, navigatie, flash-messages, foutmeldingen, toegankelijkheidsattributen zoals `role`, `aria-label` en `alt`.
- Pallets Projects. (n.d.). *Templates*. Flask documentation. https://flask.palletsprojects.com/en/stable/quickstart/#rendering-templates
- Jinja. (n.d.). *Template designer documentation*. https://jinja.palletsprojects.com/en/stable/templates/
- W3Schools.com. (n.d.). *HTML forms*. https://www.w3schools.com/html/html_forms.asp
- W3Schools.com. (n.d.). *HTML semantic elements*. https://www.w3schools.com/html/html5_semantic_elements.asp
- W3Schools.com. (n.d.). *HTML data-* attribute*. https://www.w3schools.com/tags/att_data-.asp
- W3Schools.com. (n.d.). *ARIA*. https://www.w3schools.com/accessibility/accessibility_aria.asp

### CSS, layout, responsive design en UI-states
- Gebruikte technieken: CSS selectors, classes, pseudo-classes, flexbox, grid, media queries, responsive layout, spacing, cards, buttons, forms, focus-states, hover-states, progress bars, status badges, tables, kleuren, borders, border-radius, shadows, typography, `hidden`, loading/no-data states en dashboard styling.
- W3Schools.com. (n.d.). *CSS tutorial*. https://www.w3schools.com/css/
- W3Schools.com. (n.d.). *CSS flexbox*. https://www.w3schools.com/css/css3_flexbox.asp
- W3Schools.com. (n.d.). *CSS grid layout*. https://www.w3schools.com/css/css_grid.asp
- W3Schools.com. (n.d.). *CSS responsive web design*. https://www.w3schools.com/css/css_rwd_intro.asp
- W3Schools.com. (n.d.). *CSS media queries*. https://www.w3schools.com/css/css3_mediaqueries.asp
- W3Schools.com. (n.d.). *CSS forms*. https://www.w3schools.com/css/css_form.asp
- W3Schools.com. (n.d.). *CSS pseudo-classes*. https://www.w3schools.com/css/css_pseudo_classes.asp
- W3Schools.com. (n.d.). *CSS variables - The var() function*. https://www.w3schools.com/css/css3_variables.asp
- W3Schools.com. (n.d.). *CSS rounded corners*. https://www.w3schools.com/css/css3_borders.asp
- W3Schools.com. (n.d.). *CSS position property*. https://www.w3schools.com/css/css_position.asp

### Documentatie, installatie en screenshots
- Gebruikte technieken: README-structuur, installatie-instructies, PowerShell-commando's, virtual environment, `pip install -r requirements.txt`, Flask CLI import, seed-data, ERD-afbeelding, screenshotverwijzingen en gebruikersinstructies voor docent-, leerling-, login- en klasbeheerflows.
- Python Software Foundation. (n.d.). *Installing Python modules*. Python documentation. https://docs.python.org/3/installing/index.html
- Python Software Foundation. (n.d.). *venv - Creation of virtual environments*. Python documentation. https://docs.python.org/3/library/venv.html
- PyPA. (n.d.). *pip documentation*. https://pip.pypa.io/en/stable/
- Microsoft. (n.d.). *PowerShell documentation*. https://learn.microsoft.com/en-us/powershell/

-----------------------------------------------

## Gebruikte bronnen (Slava)

### JavaScript / Animaties
- Werkplaats jaar 2 (eigen opgebouwde kennis uit voorgaande projecten)
- [Anime.js](https://animejs.com/) — gebruikt voor UI-animaties en visuele overgangen

### CSS / Design
- Eigen mockups als ontwerpleidraad
- [Claude (Anthropic)](https://claude.ai) — AI-tool ingezet voor het genereren en verfijnen van CSS-code op basis van zelfgemaakte mockups; code telkens handmatig beoordeeld en aangepast

### Beveiliging
- [Snyk AI](https://snyk.io) — gebruikt voor statische code-analyse en het opsporen van beveiligingskwetsbaarheden

### Overig
- Diverse AI-tools ingezet ter ondersteuning van het ontwikkelproces, met als doel inzicht te krijgen in de mogelijkheden en werkwijze van AI bij softwareontwikkeling
- Wat hierboven niet expliciet is benoemd, is gebaseerd op kennis en ervaring opgedaan tijdens de opleiding — als tweedejaars student kon ik voor veel onderdelen terugvallen op eerder geleerde stof en eigen inzicht
