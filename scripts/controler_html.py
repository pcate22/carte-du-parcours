#!/usr/bin/env python3
"""Contrôle statique d'une carte construite, sans navigateur.

Usage :
    python3 scripts/controler_html.py carte-du-parcours.html [carte-du-parcours.artefact.html]

Ce que le script vérifie : le bloc de données est un JSON lisible, aucun repère à remplir ne reste
(« A REMPLIR », « A ECRIRE », « AAAA-MM-JJ »), le script de la page passe la vérification de syntaxe de Node
(si `node` est installé), le fichier pour l'artefact commence par <title> et ne contient ni doctype, ni <html>,
ni <head>, ni <body>, et la taille reste sous la limite des artefacts (16 Mo).

Ce que le script NE vérifie PAS : le rendu, les clics, les couleurs, la navigation au clavier. Il ne remplace pas
l'ouverture de la carte dans un navigateur (étape 8 de SKILL.md) ; si vous ne l'avez pas ouverte, dites-le.
Code de sortie : 1 si une erreur. Python 3.8 ou plus, aucune dépendance.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

LIMITE = 16 * 1024 * 1024
RESTES = ("A REMPLIR", "A ECRIRE", "AAAA-MM-JJ")


def controler_page(chemin, fragment=False):
    erreurs, infos = [], []
    with open(chemin, encoding="utf-8") as f:
        texte = f.read()
    if len(texte.encode("utf-8")) > LIMITE:
        erreurs.append("%s : plus de 16 Mo." % chemin)
    m = re.search(r'<script type="application/json" id="donnees">(.*?)</script>', texte, re.S)
    if not m:
        erreurs.append("%s : bloc de données introuvable." % chemin)
        return erreurs, infos
    try:
        data = json.loads(m.group(1))
    except ValueError as e:
        erreurs.append("%s : le bloc de données n'est pas du JSON valide (%s)." % (chemin, e))
        return erreurs, infos
    brut = json.dumps(data, ensure_ascii=False)
    for repere in RESTES:
        if repere in brut:
            erreurs.append("%s : il reste « %s » dans les données." % (chemin, repere))
    infos.append("%s : %d pages dans le bloc de données." % (os.path.basename(chemin), len(data.get("pages", []))))
    if fragment:
        if not texte.lstrip().startswith("<title>"):
            erreurs.append("%s : le fragment doit commencer par <title>." % chemin)
        for balise in (r"<!doctype", r"<html[\s>]", r"<head[\s>]", r"<body[\s>]"):
            if re.search(balise, texte, re.I):
                erreurs.append("%s : le fragment ne doit pas contenir %s." % (chemin, balise.replace("[\\s>]", "").replace("\\", "")))
    # Syntaxe du script de la page, par Node.
    scripts = re.findall(r"<script>(.*?)</script>", texte, re.S)
    node = shutil.which("node")
    if not scripts:
        erreurs.append("%s : script de la page introuvable." % chemin)
    elif node:
        with tempfile.TemporaryDirectory() as dossier:
            js = os.path.join(dossier, "carte.js")
            with open(js, "w", encoding="utf-8") as f:
                f.write(scripts[-1])
            r = subprocess.run([node, "--check", js], capture_output=True, text=True)
            if r.returncode != 0:
                lignes = [l for l in r.stderr.splitlines() if "Error" in l] or r.stderr.splitlines() or ["?"]
                erreurs.append("%s : erreur de syntaxe dans le script : %s" % (chemin, lignes[0].strip()))
            else:
                infos.append("%s : syntaxe du script vérifiée par Node." % os.path.basename(chemin))
    else:
        infos.append("Node n'est pas installé : syntaxe du script non vérifiée.")
    return erreurs, infos


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(__doc__)
        return 1
    erreurs, infos = [], []
    for chemin in argv:
        e, i = controler_page(chemin, fragment=chemin.endswith(".artefact.html"))
        erreurs += e
        infos += i
    for t in erreurs:
        print("ERREUR    " + t)
    for t in infos:
        print("INFO      " + t)
    print("Résultat : %s (contrôle statique : le rendu et les clics ne sont pas testés)." % ("à corriger" if erreurs else "OK"))
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
