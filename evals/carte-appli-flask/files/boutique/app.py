from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)


@app.route("/")
def accueil():
    return render_template("accueil.html")


@app.route("/catalogue")
def catalogue():
    return render_template("catalogue.html")


@app.route("/plantes/<int:plante_id>")
def plante(plante_id):
    return render_template("plante.html", plante_id=plante_id)


@app.route("/panier", methods=["GET", "POST"])
def panier():
    if request.method == "POST":
        return redirect(url_for("livraison"))
    return render_template("panier.html")


@app.route("/commande/livraison", methods=["GET", "POST"])
def livraison():
    if request.method == "POST":
        return redirect(url_for("paiement"))
    return render_template("livraison.html")


@app.route("/commande/paiement", methods=["GET", "POST"])
def paiement():
    if request.method == "POST":
        return redirect(url_for("merci"))
    return render_template("paiement.html")


@app.route("/commande/merci")
def merci():
    return render_template("merci.html")


@app.route("/compte")
def compte():
    return render_template("compte.html")


@app.route("/compte/adresse", methods=["GET", "POST"])
def compte_adresse():
    if request.method == "POST":
        return redirect(url_for("compte"))
    return render_template("compte_adresse.html")


@app.route("/conseils-arrosage")
def conseils():
    return render_template("conseils.html")


@app.errorhandler(404)
def introuvable(e):
    return render_template("404.html"), 404
