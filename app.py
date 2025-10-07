from flask import Flask, render_template, request, redirect, session
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import datetime as dt

# ---------------- CONFIGURACIÓN GOOGLE SHEETS ----------------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
gc = gspread.authorize(credentials)

# IDs de Google Sheets
ID_USERS = "1UUaq4_qWEXvaV8jnEXvWk_kKQQ-d-Xkvly1hyMZVGMI"        # Usuarios autorizados
ID_RESPUESTAS = "1c9NX6Tc9f2mLTD5jf_902lo6ibn6JIAb7JS9g8WF_Ms" # Respuestas de encuestas

def load_excel_from_drive(file_id):
    sh = gc.open_by_key(file_id)
    ws = sh.sheet1
    data = ws.get_all_records()
    return pd.DataFrame(data)

def append_to_excel(file_id, fila):
    sh = gc.open_by_key(file_id)
    ws = sh.sheet1
    ws.append_row(fila)

# ---------------- FLASK ----------------
app = Flask(__name__)
app.secret_key = "my_secret_key"

# Cargar usuarios válidos
df_users = load_excel_from_drive(ID_USERS)

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    mensaje = ""
    if request.method == "POST":
        identificacion = request.form.get("identificacion")
        clave = request.form.get("clave")

        # Verificar usuario (usuario == clave)
        if (identificacion in df_users["usuario"].astype(str).values and
            clave == identificacion):
            session["usuario"] = identificacion
            return redirect("/formulario")
        else:
            mensaje = "❌ Usuario o clave incorrectos"

    return render_template("Login.html", mensaje=mensaje)

# ---------------- FORMULARIO ----------------
@app.route("/formulario", methods=["GET", "POST"])
def formulario():
    if "usuario" not in session:
        return redirect("/")

    if request.method == "POST":
        # Obtener selección múltiple
        seleccionados = request.form.getlist("valor_presencial")
        otro_texto = request.form.get("otro_valor", "").strip()

        # Si hay texto en "otro", lo añadimos como valor real
        if otro_texto:
            seleccionados.append(otro_texto)

        respuestas = {
            "fecha": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "modalidad": request.form.get("modalidad"),
            "porcentaje_presencial": request.form.get("porcentaje"),
            "valor_presencial": ", ".join(seleccionados),
            "permanencia": request.form.get("permanencia"),
            "desercion": request.form.get("desercion"),
            "beneficios": request.form.get("beneficios"),
            "tiempo_movilidad": request.form.get("tiempo"),
            "impacto_movilidad": request.form.get("impacto"),
            "medidas_movilidad": request.form.get("medidas"),
        }

        append_to_excel(ID_RESPUESTAS, list(respuestas.values()))

        # ✅ cerrar sesión y volver al login
        session.clear()
        return redirect("/")

    return render_template("Formulario.html")

# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(debug=True)
