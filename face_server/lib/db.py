import sqlite3
from bson.json_util import dumps

dbName = "lib/data/audiosdb.db"

conexion=sqlite3.connect(dbName)

try:
    conexion.execute("""create table audios (
                              id integer primary key autoincrement,
                              Nombre string,
                              Texto string
                        )""")
    print("Se creó la tabla audios")
except sqlite3.OperationalError:
    pass
    # print("La tabla audios ya existe")

conexion=sqlite3.connect(dbName)
try:
    conexion.execute("""create table volume (
                              Name string,
                              Value integer
                        )""")
    print("Se creó la tabla volume")
    conexion.execute("insert into volume (Name, Value) values (?,?)", ("Volume", 63))
    conexion.commit()
except sqlite3.OperationalError:
    pass
    # print("La tabla volume ya existe")

conexion.close()

def get_audios():
    conexion=sqlite3.connect(dbName)
    cursor=conexion.execute("select id, Nombre, Texto from audios")

    data = []

    for fila in cursor:
        a={
            "id":fila[0],
            "Nombre": fila[1],
            "Texto": fila[2]
        }

        data.append(a)
    conexion.commit()
    conexion.close()

    return data #dumps(data)


#CRUD AUDIOS
def post_audio(data):
    conexion=sqlite3.connect(dbName)
    conexion.execute("insert into audios(Nombre, Texto) values (?,?)", (data["Nombre"], data["Texto"]))
    conexion.commit()
    conexion.close()
    return {"Status": True, "Description":"Audio saved"}

def delete_audio(data):
    conexion=sqlite3.connect(dbName)
    conexion.execute('DELETE FROM audios WHERE id=?', (data["id"],))
    conexion.commit()
    conexion.close()
    return {"Status": True, "Description":"Audio deleted"}

#CRUD VOLUMEN
def add_volume(data):
    conexion=sqlite3.connect(dbName)
    conexion.execute("insert into volume(Name, Value) values (?,?)", (data["Nombre"],str(data["Value"])))
    conexion.commit()
    conexion.close()
    return {"Status": True, "Description":"Value saved"}

def update_volume(data):
    conexion=sqlite3.connect(dbName)
    with conexion:
        conexion.execute("UPDATE volume SET Value=(?) WHERE Name = 'Volume'", (str(data["Value"]),))
    conexion.commit()
    conexion.close()
    return {"Status": True, "Description":"Volume updated", "Value": data["Value"]}

def get_volume():
    conexion=sqlite3.connect(dbName)
    cursor=conexion.execute("select Value from volume")

    data = []

    for fila in cursor:
        a={
            "Status": True,
            "Value":fila[0],
            "Description": "Last value saved"
        }

        data.append(a)
    conexion.commit()
    conexion.close()

    return dumps(data[0])
