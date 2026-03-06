from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)

FILE = "musteriler.xlsx"


def dosyayi_oku():
    if os.path.exists(FILE):
        return pd.read_excel(FILE)
    return pd.DataFrame(columns=[
        "Ad Soyad", "Telefon", "Talep", "Bütçe",
        "Mevkii", "Tip", "Kategori", "Durum"
    ])


def dosyaya_yaz(df):
    df.to_excel(FILE, index=False)


@app.route("/")
def index():
    return render_template("form.html", musteri=None, edit_index=None)


@app.route("/kaydet", methods=["POST"])
def form_kaydet():
    data = {
        "Ad Soyad": request.form["ad"],
        "Telefon": request.form["telefon"],
        "Talep": request.form["talep"],
        "Bütçe": request.form["butce"],
        "Mevkii": request.form["mevkii"],
        "Tip": request.form["tip"],
        "Kategori": request.form["kategori"],
        "Durum": request.form["durum"]
    }

    df = dosyayi_oku()
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    dosyaya_yaz(df)

    return redirect("/musteriler")


@app.route("/musteriler")
def musteriler():
    tip = request.args.get("tip", "")

    df = dosyayi_oku()

    toplam = len(df)
    sicak = 0
    ilgili = 0
    pasif = 0

    if not df.empty and "Durum" in df.columns:
        durum_serisi = df["Durum"].fillna("").astype(str)
        sicak = len(df[durum_serisi.str.contains("Sıcak", na=False)])
        ilgili = len(df[durum_serisi.str.contains("İlgileniyor", na=False)])
        pasif = len(df[durum_serisi.str.contains("bakıyor", na=False)])

    if tip:
        df = df[df["Tip"] == tip]

    data = df.reset_index().to_dict(orient="records")

    return render_template(
        "liste.html",
        musteriler=data,
        toplam=toplam,
        sicak=sicak,
        ilgili=ilgili,
        pasif=pasif,
        secili_tip=tip
    )


@app.route("/duzenle/<int:index>")
def duzenle(index):
    df = dosyayi_oku()

    if index < 0 or index >= len(df):
        return redirect("/musteriler")

    musteri = df.iloc[index].to_dict()

    return render_template(
        "form.html",
        musteri=musteri,
        edit_index=index
    )


@app.route("/guncelle/<int:index>", methods=["POST"])
def guncelle(index):
    df = dosyayi_oku()

    if index < 0 or index >= len(df):
        return redirect("/musteriler")

    df.loc[index, "Ad Soyad"] = request.form["ad"]
    df.loc[index, "Telefon"] = request.form["telefon"]
    df.loc[index, "Talep"] = request.form["talep"]
    df.loc[index, "Bütçe"] = request.form["butce"]
    df.loc[index, "Mevkii"] = request.form["mevkii"]
    df.loc[index, "Tip"] = request.form["tip"]
    df.loc[index, "Kategori"] = request.form["kategori"]
    df.loc[index, "Durum"] = request.form["durum"]

    dosyaya_yaz(df)

    return redirect("/musteriler")


@app.route("/sil/<int:index>")
def sil(index):
    df = dosyayi_oku()

    if index < 0 or index >= len(df):
        return redirect("/musteriler")

    df = df.drop(index=index).reset_index(drop=True)
    dosyaya_yaz(df)

    return redirect("/musteriler")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

