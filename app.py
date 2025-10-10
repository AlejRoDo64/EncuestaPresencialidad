from flask import Flask, render_template, request, redirect, session
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import datetime as dt

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
gc = gspread.authorize(credentials)

ID_USERS = "1UUaq4_qWEXvaV8jnEXvWk_kKQQ-d-Xkvly1hyMZVGMI"       
ID_RESPUESTAS = "1c9NX6Tc9f2mLTD5jf_902lo6ibn6JIAb7JS9g8WF_Ms" 

def load_excel_from_drive(file_id):
    sh = gc.open_by_key(file_id)
    ws = sh.sheet1
    data = ws.get_all_records()
    return pd.DataFrame(data)

def append_to_excel(file_id, fila, headers):
    sh = gc.open_by_key(file_id)
    ws = sh.sheet1
    if len(ws.get_all_values()) == 0:
        ws.append_row(headers)
    ws.append_row(fila)


app = Flask(__name__)
app.secret_key = "my_secret_key"


df_users = load_excel_from_drive(ID_USERS)

@app.route("/", methods=["GET", "POST"])
def login():
    mensaje = ""
    if request.method == "POST":
        identificacion = request.form.get("identificacion")
        clave = request.form.get("clave")
        if (identificacion in df_users["usuario"].astype(str).values and
            clave == identificacion):
            session["usuario"] = identificacion
            return redirect("/formulario")
        else:
            mensaje = "❌ Usuario o clave incorrectos"
    return render_template("Login.html", mensaje=mensaje)

@app.route("/formulario", methods=["GET", "POST"])
def formulario():
    if "usuario" not in session:
        return redirect("/")

    if request.method == "POST":
        seleccionados_extra = request.form.getlist("valor_presencial_extra")
        otro_texto = request.form.get("otro_valor2", "").strip()
        if otro_texto:
            seleccionados_extra.append(otro_texto)

        respuestas = {
            "fecha": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "anios_empresa": request.form.get("anios_empresa"),
            "justicia": request.form.get("justicia"),
            "productividad": request.form.get("productividad"),
            "valor_presencial_extra": ", ".join(seleccionados_extra),
            "alineacion": request.form.get("alineacion"),
            "tiempo_total": request.form.get("tiempo_total"),
            "balance": request.form.get("balance"),
            "salud": request.form.get("salud"),
            "motivacion": request.form.get("motivacion"),
            "mejoras": request.form.get("mejoras"),
            "riesgos": request.form.get("riesgos"),
            "permanencia_empresa": request.form.get("permanencia_empresa"),
            "recomendaciones": request.form.get("recomendaciones"),
            "oportunidades": request.form.get("oportunidades"),
        }

        headers = list(respuestas.keys())
        fila = list(respuestas.values())
        append_to_excel(ID_RESPUESTAS, fila, headers)

        session.clear()
        return render_template("Base.html", mensaje="✅ Tu encuesta ha sido registrada con éxito.", redirigir_login=True)

    return render_template("Formulario.html")

if __name__ == "__main__":
    app.run(debug=True)
