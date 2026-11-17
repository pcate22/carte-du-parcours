#!/usr/bin/env python3
"""Contrôle un inventaire de pages (inventaire.json) avant de construire la carte.

Usage :
    python3 scripts/verifier.py inventaire.json [--interdits mots.txt] [--strict]

Ce que le script contrôle (voir methode/LISEZ-MOI.md, section « Les contrôles ») :
  - chaque page a un identifiant, un nom, une étape connue et une fonction « Quand je…, je veux…, pour… » ;
  - chaque lien (vers, parent, groupe de doublons) mène à une page qui existe ;
  - les pages orphelines et les pages inaccessibles sont listées ;
  - les doublons probables non signalés sont repérés (même adresse, même nom, fonctions très proches) ;
  - aucune donnée réelle (e-mail, téléphone, adresse web) et aucun mot de votre liste d'interdits.

Code de sortie : 0 si aucune erreur, 1 sinon (les attentions ne bloquent pas, sauf avec --strict).
Python 3.8 ou plus, aucune dépendance.
"""
import argparse
import json
import re
import sys
import unicodedata

ID_OK = re.compile(r"^[a-z0-9-]+$")
FONCTION_OK = re.compile(r"^Quand\b.+,\s+je veux\b.+,\s+pour\b.+\.$", re.S)
TYPES_DOUBLON = {"deux-chemins", "meme-reglage", "deux-noms", "etat-refait"}
JARGON = [
    "api", "endpoint", "route", "requête", "requete", "template", "gabarit", "json", "backend", "frontend",
    "composant", "middleware", "redirection", "handler", "contrôleur", "controller", "payload", "slug",
    "base de données", "token", "jeton", "callback", "webhook", "html", "css",
]
MOTS_VIDES = set("""quand je veux pour le la les l de des du d un une mon ma mes ton ta tes son sa ses et ou a à au aux en que qui
quoi dans sur sous par avec sans ce cet cette ces il elle on nous vous ils elles se s y n ne pas plus tout toute tous
bien faire voir pouvoir peux peut ai suis est sont avoir être etre me m te t lui leur leurs si car mais donc or ni""".split())
RE_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
RE_URL = re.compile(r"https?://([^/\s\"']+)", re.I)
RE_TEL = re.compile(r"(?<![\w/])(?:\+?\d[\d .\-]{8,}\d)(?![\w/])")
HOTES_OK = re.compile(r"(^|\.)(example\.(com|org|net)|[a-z0-9-]+\.test|localhost|invalid|exemple\.test)(:\d+)?$", re.I)


def normaliser(texte):
    texte = unicodedata.normalize("NFD", texte)
    texte = "".join(c for c in texte if unicodedata.category(c) != "Mn")
    return texte.lower()


def mots_cles(texte):
    mots = re.findall(r"[a-zà-ÿ]{3,}", texte.lower())
    return {normaliser(m)[:5] for m in mots if m not in MOTS_VIDES}


def toutes_les_chaines(valeur, chemin=""):
    if isinstance(valeur, str):
        yield chemin, valeur
    elif isinstance(valeur, dict):
        for cle, v in valeur.items():
            yield from toutes_les_chaines(v, chemin + "/" + str(cle))
    elif isinstance(valeur, list):
        for i, v in enumerate(valeur):
            yield from toutes_les_chaines(v, chemin + "[" + str(i) + "]")


def controler(data, interdits=None):
    """Renvoie (erreurs, attentions, infos) : trois listes de textes."""
    erreurs, attentions, infos = [], [], []
    meta = data.get("meta", {})
    etapes = data.get("etapes", [])
    espaces = data.get("espaces", [])
    pages = data.get("pages", [])
    groupes = data.get("doublons", [])

    # --- Titre : le nom de la page publiée (2 à 4 mots)
    titre = meta.get("titre", "")
    if not titre:
        erreurs.append("meta.titre est vide : donnez un nom à la carte (deux à quatre mots).")
    elif not 2 <= len(titre.split()) <= 4:
        attentions.append("meta.titre « %s » : visez deux à quatre mots, c'est le nom de l'artefact." % titre)
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", meta.get("etat_au", "")):
        erreurs.append("meta.etat_au doit être une date AAAA-MM-JJ (la carte dit à quelle date l'inventaire a été fait) : %r" % meta.get("etat_au", ""))
    if not meta.get("perimetre"):
        attentions.append("meta.perimetre est vide : dites ce que la carte couvre et ce qu'elle laisse de côté.")

    # --- Étapes et espaces
    ids_etapes = {}
    ids_espaces = {e.get("id") for e in espaces}
    for e in etapes:
        if not e.get("id") or not e.get("nom"):
            erreurs.append("une étape n'a pas d'identifiant ou de nom : %r" % e)
            continue
        if e["id"] in ids_etapes:
            erreurs.append("étape « %s » déclarée deux fois." % e["id"])
        ids_etapes[e["id"]] = e
        if e.get("espace") and e["espace"] not in ids_espaces:
            erreurs.append("étape « %s » : l'espace « %s » n'existe pas dans « espaces »." % (e["id"], e["espace"]))

    # --- Pages
    par_id = {}
    for p in pages:
        pid = p.get("id", "")
        if not pid or not ID_OK.match(pid):
            erreurs.append("identifiant « %s » invalide : minuscules, chiffres et tirets seulement." % pid)
            if not pid:
                continue
        if pid in par_id:
            erreurs.append("identifiant « %s » utilisé deux fois." % pid)
            continue
        par_id[pid] = p
    for pid, p in par_id.items():
        if not p.get("nom"):
            erreurs.append("page « %s » : nom manquant." % pid)
        if p.get("etape") not in ids_etapes:
            erreurs.append("page « %s » : étape « %s » inconnue." % (pid, p.get("etape")))
        f = p.get("fonction", "")
        if not f:
            erreurs.append("page « %s » : fonction manquante (chaque page a une fonction)." % pid)
        else:
            if not FONCTION_OK.match(f.strip()):
                erreurs.append("page « %s » : la fonction doit suivre « Quand je…, je veux…, pour… » et finir par un point : %s" % (pid, f))
            if len(f) > 260:
                attentions.append("page « %s » : fonction de %d signes, une phrase plus courte se lit mieux." % (pid, len(f)))
            bas = normaliser(f)
            trouves = [m for m in JARGON if re.search(r"\b" + re.escape(normaliser(m)) + r"\b", bas)]
            if re.search(r"[_()]|\.(py|js|html|jsx|tsx|php|rb)\b", f):
                trouves.append("code ou nom de fonction")
            if trouves:
                attentions.append("page « %s » : jargon possible (%s). La fonction se dit du côté de la personne." % (pid, ", ".join(trouves)))
        if not p.get("adresse"):
            attentions.append("page « %s » : pas d'adresse (route, fichier ou écran)." % pid)
        if p.get("actions") in (None, ""):
            attentions.append("page « %s » : nombre d'actions manquant." % pid)
        for cible in p.get("vers", []):
            if cible not in par_id:
                erreurs.append("page « %s » : « vers » nomme la page inconnue « %s »." % (pid, cible))
            elif cible == pid:
                attentions.append("page « %s » : un lien vers elle-même (inutile sur la carte)." % pid)
        if p.get("parent") and p["parent"] not in par_id:
            erreurs.append("page « %s » : parent « %s » inconnu." % (pid, p["parent"]))
    if not pages:
        erreurs.append("aucune page dans l'inventaire.")

    # --- Entrées, orphelines, inaccessibles
    arrivees = {pid: set() for pid in par_id}
    for pid, p in par_id.items():
        cibles = [c for c in p.get("vers", []) if c in par_id]
        if p.get("parent") in par_id:
            arrivees[pid].add(p["parent"])
            if pid not in cibles:
                cibles.append(pid)
        for c in p.get("vers", []):
            if c in par_id:
                arrivees[c].add(pid)
    entrees = [pid for pid, p in par_id.items() if p.get("entree")]
    if not entrees:
        attentions.append("aucune page marquée « entree »: true. Marquez la ou les pages où l'on arrive de l'extérieur (adresse, menu, lien externe).")
    orphelines = [pid for pid, p in par_id.items() if not arrivees[pid] and not p.get("entree") and not p.get("absente")]
    for pid in orphelines:
        attentions.append("page « %s » orpheline : aucun lien n'y mène. Si c'est une page d'entrée, ajoutez « entree »: true ; sinon la carte la signale." % pid)
    # accessibles depuis une entrée
    vus = set(entrees)
    pile = list(entrees)
    while pile:
        courant = pile.pop()
        suivantes = list(par_id[courant].get("vers", []))
        suivantes += [q for q, pq in par_id.items() if pq.get("parent") == courant]
        for suivante in suivantes:
            if suivante in par_id and suivante not in vus:
                vus.add(suivante)
                pile.append(suivante)
    if entrees:
        for pid, p in par_id.items():
            if pid not in vus and pid not in orphelines and not p.get("absente"):
                attentions.append("page « %s » inaccessible : aucune chaîne de liens ne l'atteint depuis une page d'entrée." % pid)
    pages_par_etape = {}
    for p in par_id.values():
        pages_par_etape.setdefault(p.get("etape"), []).append(p)
    for eid in ids_etapes:
        if eid not in pages_par_etape:
            attentions.append("étape « %s » sans aucune page : retirez-la ou complétez-la." % eid)

    # --- Groupes de doublons
    dans_un_groupe = set()
    paires_signalees = set()
    for g in groupes:
        gid = g.get("id", "?")
        ids = g.get("pages", [])
        if len(ids) < 2:
            erreurs.append("doublon « %s » : il faut au moins deux pages." % gid)
        if len(set(ids)) != len(ids):
            erreurs.append("doublon « %s » : une page est nommée deux fois." % gid)
        for i in ids:
            if i not in par_id:
                erreurs.append("doublon « %s » : la page « %s » n'existe pas." % (gid, i))
        if not g.get("titre"):
            erreurs.append("doublon « %s » : titre manquant (la fonction doublée, en peu de mots)." % gid)
        if not g.get("pourquoi"):
            erreurs.append("doublon « %s » : « pourquoi » manquant (ce qui est fait deux fois)." % gid)
        if g.get("type") and g["type"] not in TYPES_DOUBLON:
            attentions.append("doublon « %s » : type « %s » inconnu (attendus : %s)." % (gid, g["type"], ", ".join(sorted(TYPES_DOUBLON))))
        if not g.get("type"):
            attentions.append("doublon « %s » : pas de « type » (l'un de : %s)." % (gid, ", ".join(sorted(TYPES_DOUBLON))))
        dans_un_groupe.update(ids)
        for a in ids:
            for b in ids:
                if a < b:
                    paires_signalees.add((a, b))

    # --- Paires examinées et écartées : « non_doublons »
    ecartes = set()
    for e in data.get("non_doublons", []):
        ids = e.get("pages", [])
        if len(ids) != 2 or any(i not in par_id for i in ids):
            erreurs.append("non_doublons : il faut deux pages qui existent : %r" % (ids,))
            continue
        if not e.get("raison"):
            erreurs.append("non_doublons %s : « raison » manquante (pourquoi ce ne sont pas deux fois la même chose)." % (ids,))
        ecartes.add(tuple(sorted(ids)))

    # --- Doublons probables non signalés
    liste = list(par_id.values())
    for i, a in enumerate(liste):
        for b in liste[i + 1:]:
            cle = tuple(sorted((a["id"], b["id"])))
            if cle in paires_signalees or cle in ecartes:
                continue
            if a.get("parent") == b["id"] or b.get("parent") == a["id"]:
                continue
            raisons = []
            adr_a = (a.get("adresse") or "").strip().lower().rstrip("/")
            adr_b = (b.get("adresse") or "").strip().lower().rstrip("/")
            if adr_a and adr_a == adr_b:
                raisons.append("même adresse")
            if normaliser(a.get("nom", "")) == normaliser(b.get("nom", "")):
                raisons.append("même nom")
            ka, kb = mots_cles(a.get("fonction", "")), mots_cles(b.get("fonction", ""))
            if ka and kb and len(ka & kb) >= 3 and len(ka & kb) / float(len(ka | kb)) >= 0.5:
                raisons.append("fonctions très proches")
            if raisons:
                attentions.append("doublon non signalé ? « %s » et « %s » : %s. Ajoutez un groupe dans « doublons », ou, si ce sont bien deux fonctions différentes, une entrée dans « non_doublons » avec la raison." % (a["id"], b["id"], ", ".join(raisons)))

    # --- Constats
    for i, c in enumerate(data.get("constats", [])):
        if not c.get("titre") or not c.get("texte"):
            erreurs.append("constat n°%d : « titre » et « texte » sont obligatoires." % (i + 1))
        for pid in c.get("pages", []):
            if pid not in par_id:
                erreurs.append("constat « %s » : la page « %s » n'existe pas." % (c.get("titre", "?"), pid))

    # --- Données réelles et mots interdits
    interdits_n = [normaliser(m.strip()) for m in (interdits or []) if m.strip() and not m.strip().startswith("#")]
    for chemin, texte in toutes_les_chaines(data):
        if RE_EMAIL.search(texte):
            erreurs.append("donnée réelle possible (adresse e-mail) en %s : %s" % (chemin, RE_EMAIL.search(texte).group(0)))
        for hote in RE_URL.findall(texte):
            if not HOTES_OK.search(hote):
                erreurs.append("donnée réelle possible (adresse web) en %s : %s" % (chemin, hote))
        for tel in RE_TEL.findall(texte):
            chiffres = re.sub(r"\D", "", tel)
            if 9 <= len(chiffres) <= 15 and not re.match(r"^\d{4}-\d{2}-\d{2}$", tel):
                erreurs.append("donnée réelle possible (numéro) en %s : %s" % (chemin, tel))
        bas = normaliser(texte)
        for mot in interdits_n:
            if mot and re.search(r"(?<![a-z0-9])" + re.escape(mot) + r"(?![a-z0-9])", bas):
                erreurs.append("mot interdit « %s » en %s." % (mot, chemin))

    n_doubles = len([p for p in dans_un_groupe if p in par_id])
    infos.append("%d pages, %d étapes, %d groupes de doublons (%d pages touchées), %d orphelines, %d entrées."
                 % (len(par_id), len(ids_etapes), len(groupes), n_doubles, len(orphelines), len(entrees)))
    return erreurs, attentions, infos


def main(argv=None):
    ap = argparse.ArgumentParser(description="Contrôle un inventaire de pages avant de construire la carte.")
    ap.add_argument("inventaire", help="fichier inventaire.json")
    ap.add_argument("--interdits", help="fichier texte : un mot à ne jamais publier par ligne (marque, nom, adresse…)")
    ap.add_argument("--strict", action="store_true", help="les attentions comptent comme des erreurs")
    args = ap.parse_args(argv)
    try:
        with open(args.inventaire, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        print("ERREUR : impossible de lire %s : %s" % (args.inventaire, e))
        return 1
    interdits = []
    avant = []
    if args.interdits:
        try:
            with open(args.interdits, encoding="utf-8") as f:
                interdits = f.read().splitlines()
        except OSError:
            avant.append("fichier d'interdits %s introuvable : ignoré (aucun mot interdit contrôlé)." % args.interdits)
    erreurs, attentions, infos = controler(data, interdits)
    infos = avant + infos
    for t in erreurs:
        print("ERREUR    " + t)
    for t in attentions:
        print("ATTENTION " + t)
    for t in infos:
        print("INFO      " + t)
    if erreurs or (args.strict and attentions):
        print("Résultat : à corriger (%d erreur(s), %d attention(s))." % (len(erreurs), len(attentions)))
        return 1
    print("Résultat : OK (%d attention(s) à relire)." % len(attentions))
    return 0


if __name__ == "__main__":
    sys.exit(main())
