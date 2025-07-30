from flask import Flask, render_template, jsonify
import psycopg2
import psycopg2.extras
import json

app = Flask(__name__)

DB_HOST = "localhost"
DB_NAME = "BOAD_Carbone"
DB_USER = "postgres"
DB_PASS = "baba"

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn




def get_transport_data():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    base_donnees = {}

    tables_info = {
        "scope_1": {
            "personne": "transportroutierpersonnes1",
            "marchandise": "transportroutiermarchandise1"
        },
        "scope_2": {
            "personne": "transportroutierpersonnes2",
            "marchandise": "transportroutiermarchandise2"
        },
        "scope_3": {
            "personne": "transportroutierpersonnes3",
            "marchandise": "transportroutiermarchandise3"
        }
    }

    for scope, types in tables_info.items():
        base_donnees[scope] = {}
        for type_transport, table in types.items():
            # Initialiser toutes les catégories vides
            base_donnees[scope][type_transport] = {
                "routier": [],
                "aérien": [],
                "maritime": [],
                "ferroviaire": []
            }

            # Remplir uniquement la catégorie "routier" avec les données de la table actuelle
            cur.execute(f"SELECT id, nom, description, emission FROM {table};")
            lignes = cur.fetchall()
            for ligne in lignes:
                base_donnees[scope][type_transport]["routier"].append({
                    "id": ligne["id"],
                    "nom": ligne["nom"],
                    "facteur": float(ligne["emission"]),
                    "description": ligne["description"]
                })

    cur.close()
    conn.close()
    return base_donnees


@app.route("/transport")
def transport():
    data = get_transport_data()
    return render_template("transport.html", engins_json=json.dumps(data))





def get_energie_data():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT id, nom FROM scope ORDER BY id;")
    scopes = cur.fetchall()

    data = {}

    for scope in scopes:
        scope_nom = scope['nom'].lower().replace(" ", "_")

        cur.execute("""
            SELECT nom, emission, description
            FROM energiebioenergie
            WHERE scope_id = %s;
        """, (scope['id'],))
        rows = cur.fetchall()

        data[scope_nom] = {}
        for row in rows:
            data[scope_nom].setdefault("Énergie", []).append({
                "nom": row['nom'],
                "facteur": float(row['emission']),
                "description": row['description'],
                "unite": "U"
            })

    cur.close()
    conn.close()

    return data


@app.route('/energie')
def energie():
    base_donnees_energie = get_energie_data()
    return render_template('energie.html', engins_energie=base_donnees_energie)













def get_equipement_data():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    categories = [
        "agriculture",
        "sante",
        "it",
        "construction",
        "education",
        "industrie"
    ]

    cur.execute("SELECT id, nom FROM scope ORDER BY id;")
    scopes = cur.fetchall()

    data = {}

    for scope in scopes:
        scope_nom = scope["nom"].lower().replace(" ", "_")
        scope_id = scope["id"]
        data[scope_nom] = {}

        for cat in categories:
            table_name = f"equipement_{cat}"
            try:
                cur.execute(f"""
                    SELECT nom, emission, description
                    FROM {table_name}
                    WHERE scope_id = %s;
                """, (scope_id,))
                rows = cur.fetchall()

                if rows:
                    data[scope_nom][cat.capitalize()] = []
                    for row in rows:
                        data[scope_nom][cat.capitalize()].append({
                            "nom": row["nom"],
                            "facteur": float(row["emission"]),
                            "description": row["description"],
                            "unite": "U"
                        })
            except Exception as e:
                print(f"Erreur avec la table {table_name} : {e}")
                continue

    cur.close()
    conn.close()
    return data





@app.route('/equipements')
def equipements():
    engins = {
        'scope_3': {
            'Agriculture': [
                {'nom': 'Tracteur', 'facteur': 123.4, 'description': 'Tracteur agricole', 'unite': 'U'},
                {'nom': 'Moissonneuse', 'facteur': 456.7, 'description': 'Moissonneuse-batteuse', 'unite': 'U'}
            ],
            'Industrie': [
                {'nom': 'Compresseur', 'facteur': 234.5, 'description': 'Compresseur industriel', 'unite': 'U'}
            ],
            'Santé': [
                {'nom': 'Electro-cardiogramme', 'facteur': 56.3, 'description': 'Mesure de l\'activité cardiaque','unite': 'U'}
            ],
            'Contruction': [
                {'nom': 'Bétonier', 'facteur': 156, 'description': 'Outil permettant de faire les bétons', 'unite': 'U'}
            ],

            'IT/Télécom/Electricité': [
                {'nom': 'Ordinateur', 'facteur': 98, 'description': 'Machine élctronique', 'unite': 'U'}
            ],
        }
    }
    return render_template('equipements.html', engins_equipements=engins)



def get_autre_data():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("""
        SELECT nom, emission, description
        FROM autre
        ORDER BY nom;
    """)

    rows = cur.fetchall()

    autres = []
    for row in rows:
        autres.append({
            "nom": row["nom"],
            "facteur": float(row["emission"]),
            "description": row["description"],
            "unite": "U"
        })

    cur.close()
    conn.close()
    return autres


@app.route('/autre')
def autre():
    autres_data = get_autre_data()
    return render_template('autre.html', autres=autres_data)




@app.route("/resultat", methods=["GET", "POST"])
def resultat():
    return render_template("resultat.html")


#
# @app.route('/dechets')
# def dechets():
#     return render_template('dechets.html')







@app.route('/')
def index():
    # tu peux rendre un template réel ou juste une page test
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
