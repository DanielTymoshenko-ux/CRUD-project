# To-Do CRUD Flask App

Mini-aplikacja CRUD  w  **Python + Flask + SQLite**  
Frontend –  HTML + JavaScript.  
Zawiera dwie encje: `Task` i `Category` z relacją jeden-do-wielu.
# Hosted at 
https://crud-project-76vx.onrender.com/

## Uruchomienie lokalne
```bash
pip install -r requirements.txt
python app.py

## Tests & CI

Run tests locally:
```bash
pip install -r requirements.txt
pytest -v


## External endpoints

Weather:
GET /external/weather?city=Warsaw
or GET /external/weather?lat=52.23&lon=21.01

Rates:
GET /external/rates?base=EUR
GET /external/rates?base=EUR&symbols=PLN,USD

Frontend pages:
/weather
/rates