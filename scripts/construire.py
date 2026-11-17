#!/usr/bin/env python3
"""Construit la carte du parcours à partir d'un inventaire (inventaire.json).

Usage :
    python3 scripts/construire.py inventaire.json [-o DOSSIER] [--nom carte-du-parcours] [--interdits mots.txt] [--forcer]

Produit deux fichiers HTML dans DOSSIER (par défaut, le dossier de l'inventaire) :
  NOM.html            page complète : s'ouvre dans un navigateur ou se met en ligne telle quelle ;
  NOM.artefact.html   même page sans <!doctype>, <html>, <head> ni <body> : à publier avec l'outil Artifact
                      de Claude (qui ajoute lui-même ces balises).

Le script refuse de construire si le contrôle (scripts/verifier.py) trouve des erreurs, sauf avec --forcer.
Python 3.8 ou plus, aucune dépendance.
"""
import argparse
import html
import json
import os
import re
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import verifier  # noqa: E402

DEBUT = "<!--DONNEES:DEBUT-->"
FIN = "<!--DONNEES:FIN-->"


def bloc_donnees(data):
    texte = json.dumps(data, ensure_ascii=False, indent=2)
    # « < » devient < : le JSON ne peut plus fermer la balise <script> ni ouvrir un commentaire.
    texte = texte.replace("<", "\\u003c")
    return DEBUT + '\n<script type="application/json" id="donnees">\n' + texte + "\n</script>\n" + FIN


def injecter(modele, data):
    i, j = modele.find(DEBUT), modele.find(FIN)
    if i < 0 or j < 0 or j < i:
        raise SystemExit("Le modèle ne contient pas les repères %s … %s." % (DEBUT, FIN))
    page = modele[:i] + bloc_donnees(data) + modele[j + len(FIN):]
    titre = data.get("meta", {}).get("titre") or "Carte du parcours"
    page, n = re.subn(r"<title>.*?</title>", lambda m: "<title>" + html.escape(titre) + "</title>", page, count=1, flags=re.S)
    if n != 1:
        raise SystemExit("Le modèle ne contient pas de balise <title>.")
    return page


def fragment_artefact(page):
    """Retire ce que l'outil Artifact ajoute lui-même : doctype, html, head, body, métas de base."""
    avant = page
    for motif in (
        r"<!doctype html>\s*",
        r"<html[^>]*>\s*",
        r"<head>\s*",
        r'<meta charset="utf-8">\s*',
        r'<meta name="viewport"[^>]*>\s*',
        r"</head>\s*",
        r"<body>\s*",
        r"\s*</body>\s*",
        r"\s*</html>\s*",
    ):
        page = re.sub(motif, "", page, count=1, flags=re.I)
    if page == avant or not page.lstrip().startswith("<title>"):
        raise SystemExit("Le fragment pour l'artefact doit commencer par <title> : le modèle a changé ?")
    return page.strip() + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Construit la carte du parcours (HTML) à partir de inventaire.json.")
    ap.add_argument("inventaire", help="fichier inventaire.json")
    ap.add_argument("-o", "--dossier", help="dossier de sortie (défaut : celui de l'inventaire)")
    ap.add_argument("--nom", default="carte-du-parcours", help="nom des fichiers produits, sans extension")
    ap.add_argument("--modele", default=os.path.join(ICI, "..", "modele", "carte.html"), help="gabarit HTML")
    ap.add_argument("--interdits", help="fichier texte : un mot à ne jamais publier par ligne")
    ap.add_argument("--forcer", action="store_true", help="construire même si le contrôle trouve des erreurs")
    args = ap.parse_args(argv)

    with open(args.inventaire, encoding="utf-8") as f:
        data = json.load(f)
    interdits = []
    if args.interdits:
        with open(args.interdits, encoding="utf-8") as f:
            interdits = f.read().splitlines()
    erreurs, attentions, infos = verifier.controler(data, interdits)
    for t in erreurs:
        print("ERREUR    " + t)
    for t in attentions:
        print("ATTENTION " + t)
    for t in infos:
        print("INFO      " + t)
    if erreurs and not args.forcer:
        print("Carte non construite : corrigez les erreurs (ou --forcer).")
        return 2

    with open(args.modele, encoding="utf-8") as f:
        modele = f.read()
    page = injecter(modele, data)
    dossier = args.dossier or os.path.dirname(os.path.abspath(args.inventaire))
    os.makedirs(dossier, exist_ok=True)
    chemin_page = os.path.join(dossier, args.nom + ".html")
    chemin_artefact = os.path.join(dossier, args.nom + ".artefact.html")
    with open(chemin_page, "w", encoding="utf-8") as f:
        f.write(page)
    with open(chemin_artefact, "w", encoding="utf-8") as f:
        f.write(fragment_artefact(page))
    print("Écrit : %s (%d Ko)" % (chemin_page, os.path.getsize(chemin_page) // 1024))
    print("Écrit : %s (%d Ko, pour l'outil Artifact)" % (chemin_artefact, os.path.getsize(chemin_artefact) // 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
