from flask import Flask, render_template
import psycopg2
import psycopg2.extras

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

    cur.execute("SELECT id, nom FROM scope ORDER BY id;")
    scopes = cur.fetchall()

    for scope in scopes:
        scope_id = scope["id"]
        scope_nom = scope["nom"].lower()
        base_donnees[scope_nom] = {}

        cur.execute("""
            SELECT id, nom FROM type_engin
            WHERE scope_id = %s
            ORDER BY nom;
        """, (scope_id,))
        categories = cur.fetchall()

        for cat in categories:
            cat_id = cat["id"]
            cat_nom = cat["nom"]
            base_donnees[scope_nom][cat_nom] = []

            cur.execute("""
                SELECT nom, emission, description
                FROM transportroutierpersonnes1
                WHERE type_engin_id = %s;
            """, (cat_id,))
            engins = cur.fetchall()

            for engin in engins:
                base_donnees[scope_nom][cat_nom].append({
                    "nom": engin["nom"],
                    "facteur": float(engin["emission"]),
                    "description": engin["description"]
                })

    cur.close()
    conn.close()
    return base_donnees

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


@app.route('/transport')
def transport():
    base_donnees_transport = get_transport_data()
    return render_template('transport.html', engins=base_donnees_transport)

@app.route('/energie')
def energie():
    base_donnees_energie = get_energie_data()
    return render_template('energie.html', engins_energie=base_donnees_energie)

@app.route('/')
def index():
    # tu peux rendre un template réel ou juste une page test
    return render_template('index.html')



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



from flask import render_template

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





if __name__ == '__main__':
    app.run(debug=True)
