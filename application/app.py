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



def table_exists(cur, table_name):
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = %s
        );
    """, (table_name,))
    return cur.fetchone()[0]




def get_transport_data():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    base_donnees = {}

    # Tables classées par scope, type de transport, et mode (routier, aérien, etc.)
    tables_info = {
        "scope_1": {
            "personne": {
                "routier": "transportroutierpersonnes1"
                # "aérien": "transportaerienpersonnes1",
                # "maritime": "transportmaritimepersonnes1",
                # "ferroviaire": "transportferroviairepersonnes1"
            },
            "marchandise": {
                "routier": "transportroutiermarchandise1"
                # "aérien": "transportaerienmarchandise1",
                # "maritime": "transportmaritimemarchandise1",
                # "ferroviaire": "transportferroviairemarchandise1"
            }
        },
        "scope_2": {
            "personne": {
                "routier": "transportroutierpersonnes2"
                # "aérien": "transportaerienpersonnes2",
                # "maritime": "transportmaritimepersonnes2",
                # "ferroviaire": "transportferroviairepersonnes2"
            },
            "marchandise": {
                "routier": "transportroutiermarchandise2"
                # "aérien": "transportaerienmarchandise2"
                # "maritime": "transportmaritimemarchandise2",
                # "ferroviaire": "transportferroviairemarchandise2"
            }
        },
        "scope_3": {
            "personne": {
                "routier": "transportroutierpersonnes3",
                "aérien": "transportaerienpersonnes3",
                # "maritime": "transportmaritimepersonnes3",
                "ferroviaire": "transportferroviairepersonnes3"
            },
            "marchandise": {
                "routier": "transportroutiermarchandise3",
                "aérien": "transportaerienmarchandise3",
                # "maritime": "transportmaritimemarchandise3",
                # "ferroviaire": "transportferroviairemarchandise3"
            }
        }
    }

    for scope, types in tables_info.items():
        base_donnees[scope] = {}
        for type_transport, modes in types.items():
            base_donnees[scope][type_transport] = {}
            for mode, table in modes.items():
                base_donnees[scope][type_transport][mode] = []
                if table is not None:
                    cur.execute(f"SELECT id, nom, description, emission FROM {table};")
                    lignes = cur.fetchall()
                    for ligne in lignes:
                        base_donnees[scope][type_transport][mode].append({
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









def safe_value(val, default=""):
    if val is None:
        return default
    try:
        if isinstance(val, (str, int, float)):
            return val
        return str(val)
    except Exception:
        return default



def get_equipements_data():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT id, nom FROM scope ORDER BY id;")
    scopes = cur.fetchall()

    categories = {
        "Construction": "equipementsagriculture3",
        "Plastique": "equipementsplastique3",
        "Papier/Carton": "equipementspapiercarton3",
        "Autre": "equipementsautre3",
        "Électrique/IT": "equipementselectriqueit3"
    }

    data = {}

    for scope in scopes:
        scope_nom = scope['nom'].lower().replace(" ", "_")
        data[scope_nom] = {}

        for categorie_nom, table in categories.items():
            try:
                cur.execute(f"""
                    SELECT nom, emission, description
                    FROM {table}
                    WHERE scope_id = %s;
                """, (scope['id'],))
                rows = cur.fetchall()
            except psycopg2.Error as e:
                conn.rollback()
                print(f"Erreur SQL sur la table {table} : {e}")
                rows = []

            data[scope_nom][categorie_nom] = []
            for row in rows:
                data[scope_nom][categorie_nom].append({
                    "nom": safe_value(row['nom']),
                    "facteur": float(row['emission']) if row['emission'] is not None else 0.0,
                    "description": safe_value(row['description']),
                    "unite": "U"
                })

    cur.close()
    conn.close()
    return data

@app.route('/equipements')
def equipements():
    base_donnees_equipements = get_equipements_data()

    try:
        base_donnees_json = json.dumps(base_donnees_equipements)
    except TypeError as e:
        print("Erreur JSON:", e)
        base_donnees_json = "{}"

    return render_template('equipements.html', engins_equipements=get_equipements_data())






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
