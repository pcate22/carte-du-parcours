#!/usr/bin/env python3
"""Vérifications automatiques des scripts (brouillon, verifier), sans dépendance.

Usage : python3 evals/test_scripts.py

Elles reprennent, en petit, les cas rencontrés sur trois vrais sites (un site à générateur maison et PHP,
une application d'une seule page, une plateforme Next.js) : un projet d'essai est écrit dans un dossier temporaire.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

ICI = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(ICI, "..", "scripts")
sys.path.insert(0, SCRIPTS)
import brouillon  # noqa: E402
import verifier  # noqa: E402


def ecrire(racine, chemin, texte):
    p = os.path.join(racine, chemin)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(texte)


def lancer_brouillon(racine):
    sortie = os.path.join(racine, "_brouillon.json")
    r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "brouillon.py"), racine, "-o", sortie], capture_output=True, text=True)
    with open(sortie, encoding="utf-8") as f:
        return json.load(f), r.stdout


class Actions(unittest.TestCase):
    def test_un_lien_repete_compte_une_fois_et_le_champ_piege_ne_compte_pas(self):
        t = ('<a href="/x">a</a><a href="/x">b</a><link rel="stylesheet" href="/c.css"><button>ok</button>'
             '<input type="text" tabindex="-1"><input name="e"><Link href="/y">y</Link><LienTexte vers="/z">z</LienTexte>'
             '<Button>go</Button><summary>s</summary><abbr>x</abbr>')
        self.assertEqual(brouillon.compter_actions(t), 7)

    def test_deux_liens_jinja_differents_ne_sont_pas_confondus(self):
        t = "<a href=\"{{ url_for('a') }}\">a</a><a href=\"{{ url_for('b') }}\">b</a>"
        self.assertEqual(brouillon.compter_actions(t), 2)


class Identifiants(unittest.TestCase):
    def test_identifiants_lisibles(self):
        self.assertEqual(brouillon.identifiant("/"), "accueil")
        self.assertEqual(brouillon.identifiant("/produits"), "produits")
        self.assertEqual(brouillon.identifiant("/produits/{id}"), "produits-detail")
        self.assertEqual(brouillon.identifiant("/{slug}"), "page-slug")
        self.assertEqual(brouillon.identifiant("/a/{x}/b"), "a-b")


class Next(unittest.TestCase):
    def test_redirections_pages_d_erreur_et_adresse_libre(self):
        with tempfile.TemporaryDirectory() as d:
            ecrire(d, "src/app/page.tsx", "export default function A(){ return <main><Link href=\"/catalogue\">Catalogue</Link></main> }")
            ecrire(d, "src/app/catalogue/page.tsx", "export default function B(){ return <main><h1>Catalogue</h1></main> }")
            ecrire(d, "src/app/articles/page.tsx", "import { redirect } from 'next/navigation'\n/** ancienne liste */\nexport default function C(){ redirect('/catalogue') }")
            ecrire(d, "src/app/[slug]/page.tsx", "export default function D(){ return <main><h1>Page</h1></main> }")
            ecrire(d, "src/app/not-found.tsx", "export default function N(){ return <h1>Page introuvable</h1> }")
            ecrire(d, "src/app/error.tsx", "export default function E(){ return <h1>Oups</h1> }")
            ecrire(d, "src/app/api/x/route.ts", "export async function GET(){ return new Response('ok') }")
            data, _ = lancer_brouillon(d)
            ids = {p["id"] for p in data["pages"]}
            self.assertEqual(ids, {"accueil", "catalogue", "page-slug", "page-introuvable", "page-d-erreur"})
            self.assertEqual([r["adresse"] for r in data["redirections"]], ["/articles"])
            accueil = [p for p in data["pages"] if p["id"] == "accueil"][0]
            self.assertIn("catalogue", accueil["vers"])
            self.assertTrue([p for p in data["pages"] if p["id"] == "page-introuvable"][0]["entree"])


class SitePhp(unittest.TestCase):
    def test_formulaire_vers_php_adresse_propre_et_lien_conditionnel(self):
        with tempfile.TemporaryDirectory() as d:
            menu = '<nav><a href="/">Accueil</a><a href="/contact.html">Contact</a><a href="/fiches.html">Fiches</a></nav>\n' * 1
            for nom in ("a", "b", "c", "d", "e"):
                ecrire(d, nom + ".html", "<html><body>" + "<p>ligne commune assez longue pour compter dans le menu</p>\n" + "<h1>" + nom + "</h1></body></html>")
            ecrire(d, "index.html", "<html><body><h1>Accueil</h1><a href=\"/fiches/ma-fiche\">Ma fiche</a></body></html>")
            ecrire(d, "fiches.html", "<html><body><h1>Fiches</h1></body></html>")
            ecrire(d, "fiche-ma-fiche.html", "<html><body><h1>Ma fiche</h1><form action=\"/contact.php\" method=\"post\"><input name=\"e\"><button>Envoyer</button></form></body></html>")
            ecrire(d, "contact.html", "<html><body><h1>Contact</h1></body></html>")
            ecrire(d, "contact-envoye.html", "<html><body><h1>Envoyé</h1></body></html>")
            ecrire(d, "contact.php", "<?php\nfunction aller($p){ header('Location: /' . $p); }\naller('contact-envoye.html');\n")
            data, sortie = lancer_brouillon(d)
            par_id = {p["id"]: p for p in data["pages"]}
            self.assertIn("fiche-ma-fiche", par_id["accueil"]["vers"])          # /fiches/ma-fiche -> fiche-ma-fiche.html, par ressemblance
            self.assertIn("contact-envoye", par_id["fiche-ma-fiche"]["vers"])   # le script PHP cite la page vue ensuite
            self.assertIn("ressemblance", sortie)
            self.assertEqual(par_id["fiche-ma-fiche"]["actions"], "2")


class Verifier(unittest.TestCase):
    def inventaire(self, fonction, adresse="/x"):
        return {"meta": {"titre": "Carte essai", "etat_au": "2026-11-17", "perimetre": "p", "role": "visiteurs"},
                "etapes": [{"id": "e", "numero": "1", "nom": "Étape"}],
                "pages": [{"id": "x", "nom": "X", "etape": "e", "fonction": fonction, "adresse": adresse, "actions": "2", "entree": True}]}

    def test_feuille_de_route_n_est_pas_du_jargon(self):
        _, attentions, _ = verifier.controler(self.inventaire("Quand je prépare la suite, je veux lire la feuille de route, pour savoir où l'on va."))
        self.assertEqual([a for a in attentions if "jargon" in a], [])

    def test_route_seule_est_du_jargon(self):
        _, attentions, _ = verifier.controler(self.inventaire("Quand je change la route, je veux la lire, pour la suivre."))
        self.assertTrue([a for a in attentions if "jargon" in a])

    def test_un_code_dans_l_adresse_est_signale(self):
        _, attentions, _ = verifier.controler(self.inventaire("Quand j'ai le lien, je veux télécharger le fichier, pour le lire.", "/merci-ccc39a8ece.html"))
        self.assertTrue([a for a in attentions if "code" in a])

    def test_une_adresse_ordinaire_n_est_pas_un_code(self):
        _, attentions, _ = verifier.controler(self.inventaire("Quand j'arrive, je veux lire la page, pour la comprendre.", "/cas-devis-mairie.html"))
        self.assertEqual([a for a in attentions if "code" in a], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
