from flask import Flask, render_template
import psycopg2
import os

app = Flask(__name__)

# Configuration de la base de données
DB_HOST = "localhost"
DB_NAME = "BOAD_Carbone"
DB_USER = "postgres"
DB_PASS = "baba"



def get_engins():
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
    cur = conn.cursor()
    types = ["moto", "voiture", "avion", "bateau", "train"]
    engins = {}
    for t in types:
        cur.execute(f"SELECT nom, emission FROM {t} ORDER BY nom;")
        engins[t] = [{"nom": r[0], "facteur": r[1]} for r in cur.fetchall()]
    cur.close()
    conn.close()
    return engins

# Route de la page d'accueil
@app.route('/')
def index():
    return render_template('index.html')

@app.route("/transport")
def transport():
    engins = get_engins()
    return render_template("transport.html", engins=engins)

@app.route("/resultat", methods=["GET", "POST"])
def resultat():
    return render_template("resultat.html")







@app.route("/energie")
def energie():
    energies = {
        "Électricité": {"facteur": 0.055, "unite": "kWh"},
        "Gaz naturel": {"facteur": 0.202, "unite": "kWh"},
        "Fioul": {"facteur": 2.68, "unite": "L"},
        "Bois": {"facteur": 0.015, "unite": "kg"}
    }
    return render_template("energie.html", energies=energies)

@app.route("/equipements")
def equipements():
    equipements_data = {
        "construction": [{"nom": "Béton", "facteur": 0.12}],
        "papier": [{"nom": "Papier A4", "facteur": 1.25}],
        "plastique": [{"nom": "Bouteille PET", "facteur": 2.5}],
        "metaux": [{"nom": "Acier", "facteur": 1.8}],
        "equipement_electrique_IT": [{"nom": "Ordinateur portable", "facteur": 100}]
    }
    return render_template("equipements.html", equipements=equipements_data)

@app.route("/dechets")
def dechets():
    dechets_data = {
        "construction": [{"nom": "Béton", "facteur": 0.12}],
        "papier": [{"nom": "Papier A4", "facteur": 1.25}],
        "plastique": [{"nom": "Bouteille PET", "facteur": 2.5}],
        "metaux": [{"nom": "Acier", "facteur": 1.8}],
        "equipement_electrique_IT": [{"nom": "Ordinateur portable", "facteur": 100}]
    }
    return render_template("dechets.html", dechets=dechets_data)



if __name__ == "__main__":
    app.run(debug=True)
