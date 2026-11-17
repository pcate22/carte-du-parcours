#!/usr/bin/env python3
"""Mesure les contrastes des couleurs de la carte, en clair et en sombre.

Usage :
    python3 scripts/contrastes.py [fichier.html]      (défaut : modele/carte.html)

Lit les jetons de couleur de la feuille de style (bloc :root pour le clair, les deux blocs sombres pour le sombre),
vérifie que les deux blocs sombres sont identiques, puis calcule le rapport de contraste WCAG de chaque paire utile.
Seuils : 4,5 pour le texte, 3 pour les bordures, les icônes et l'anneau de focus (RGAA 3.2 et 3.3, WCAG 1.4.3 et 1.4.11).
Code de sortie : 1 si une paire échoue. Python 3.8 ou plus, aucune dépendance.
"""
import os
import re
import sys

ICI = os.path.dirname(os.path.abspath(__file__))

# (texte ou trait, fond, seuil, ce que c'est)
PAIRES = [
    ("texte", "fond", 4.5, "texte courant sur la page"),
    ("texte", "surface", 4.5, "texte dans les cartes et la fiche"),
    ("texte", "alerte-fond", 4.5, "texte dans un cadre de doublon"),
    ("texte", "erreur-fond", 4.5, "texte dans un cadre d'orpheline"),
    ("texte-2", "fond", 4.5, "texte secondaire sur la page"),
    ("texte-2", "surface", 4.5, "texte secondaire dans les cartes"),
    ("texte-2", "teinte", 4.5, "texte secondaire sur une carte d'où l'on vient"),
    ("marque", "fond", 4.5, "titres et boutons"),
    ("marque", "surface", 4.5, "titres dans la fiche"),
    ("marque", "teinte", 4.5, "étiquette d'étape"),
    ("marque", "surligne", 4.5, "puce d'étape choisie"),
    ("action", "fond", 4.5, "étiquette « vers »"),
    ("action", "teinte", 4.5, "étiquette « vers » sur une carte"),
    ("attention", "alerte-fond", 4.5, "badge et bouton « doublon »"),
    ("attention", "surface", 4.5, "bordure des cartes en doublon"),
    ("erreur", "erreur-fond", 4.5, "badge « orpheline »"),
    ("surface", "marque", 4.5, "numéro d'étape (blanc sur couleur de marque)"),
    ("fond", "marque", 4.5, "lien d'évitement"),
    ("bord", "surface", 3.0, "bordure des cartes et des champs"),
    ("bord", "fond", 3.0, "bordure du filtre et des puces"),
    ("action", "surface", 3.0, "bordure d'une page où l'on peut aller, flèche pleine"),
    ("texte-2", "fond", 3.0, "flèche en pointillé"),
    ("focus", "fond", 3.0, "anneau de focus sur la page"),
    ("focus", "surface", 3.0, "anneau de focus dans les cartes"),
    ("attention", "fond", 4.5, "étiquette « même fonction »"),
]


def lire_jetons(bloc):
    return {m.group(1): m.group(2).upper() for m in re.finditer(r"--([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})\b", bloc)}


def blocs(css):
    clair = re.search(r"^:root\s*\{(.*?)^\}", css, re.S | re.M)
    sombre_media = re.search(r":root:not\(\[data-theme=\"light\"\]\)\s*\{(.*?)\}", css, re.S)
    sombre_attr = re.search(r":root\[data-theme=\"dark\"\]\s*\{(.*?)\}", css, re.S)
    if not (clair and sombre_media and sombre_attr):
        raise SystemExit("Les trois blocs de jetons (clair, sombre automatique, sombre choisi) sont introuvables.")
    return lire_jetons(clair.group(1)), lire_jetons(sombre_media.group(1)), lire_jetons(sombre_attr.group(1))


def luminance(hexa):
    canaux = [int(hexa[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canaux]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def rapport(a, b):
    la, lb = luminance(a), luminance(b)
    haut, bas = max(la, lb), min(la, lb)
    return (haut + 0.05) / (bas + 0.05)


def main():
    chemin = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ICI, "..", "modele", "carte.html")
    with open(chemin, encoding="utf-8") as f:
        css = f.read()
    clair, sombre_media, sombre_attr = blocs(css)
    echecs = 0
    if sombre_media != sombre_attr:
        diff = sorted(k for k in set(sombre_media) | set(sombre_attr) if sombre_media.get(k) != sombre_attr.get(k))
        print("ERREUR : les deux blocs sombres diffèrent (jetons : %s). Le thème choisi et le thème du système doivent être identiques." % ", ".join(diff))
        echecs += 1
    sombre = dict(clair)
    sombre.update(sombre_attr)
    print("%-12s %-12s %7s %7s %6s  %s" % ("texte/trait", "fond", "clair", "sombre", "seuil", "usage"))
    for avant, fond, seuil, usage in PAIRES:
        res = []
        for jetons in (clair, sombre):
            if avant not in jetons or fond not in jetons:
                res.append(None)
            else:
                res.append(rapport(jetons[avant], jetons[fond]))
        if None in res:
            print("%-12s %-12s  jeton introuvable (%s)" % (avant, fond, usage))
            echecs += 1
            continue
        ok = all(r >= seuil for r in res)
        if not ok:
            echecs += 1
        print("%-12s %-12s %7.2f %7.2f %6.1f  %s%s" % (avant, fond, res[0], res[1], seuil, usage, "" if ok else "   <-- ÉCHEC"))
    print("Résultat : %s" % ("tout passe" if not echecs else "%d paire(s) à corriger" % echecs))
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
