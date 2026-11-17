#!/usr/bin/env python3
"""Premier jet d'un inventaire de pages, lu dans le code d'un projet.

Usage :
    python3 scripts/brouillon.py RACINE_DU_PROJET [-o inventaire-brouillon.json] [--inclure-tests]

Ce que le script trouve (par expressions régulières, donc de façon approximative) :
  - routes Python : Flask, FastAPI, Starlette (décorateurs), Django (urls.py) ;
  - routes JavaScript : Express, Koa-router, Fastify (app.get('/x', ...)) ;
  - pages par fichiers : Next.js (pages/, app/**/page.*), Nuxt (pages/), SvelteKit (routes/**/+page.*), Astro (src/pages/) ;
  - pages statiques : tous les fichiers .html hors des dossiers ci-dessus ;
  - écrans mobiles : React Navigation (Stack.Screen), Flutter (GoRoute), Jetpack Compose (composable), SwiftUI (NavigationLink).
Pour chaque page : adresse, fichier source, gabarit lié, nombre d'actions compté dans le gabarit, liens trouvés vers d'autres pages.

Ce que le script NE fait PAS : écrire la fonction de chaque page, choisir les étapes, repérer les doublons, juger.
Il laisse « fonction » et « etape » à remplir : le contrôle (verifier.py) refuse l'inventaire tant que c'est le cas.
Lecture seule : le script ne modifie rien dans le projet. Python 3.8 ou plus, aucune dépendance.
"""
import argparse
import json
import os
import re
import sys
import unicodedata

IGNORES = {"node_modules", ".git", "venv", ".venv", "env", "__pycache__", "dist", "build", ".next", ".nuxt", ".svelte-kit",
           "vendor", "site-packages", ".idea", ".vscode", "coverage", "static", "public", "assets", "migrations"}
TESTS = {"tests", "test", "__tests__", "spec", "specs", "e2e", "cypress"}
EXT_GABARIT = (".html", ".htm", ".jinja", ".jinja2", ".j2", ".njk", ".erb", ".ejs", ".hbs", ".twig", ".vue", ".svelte", ".astro", ".jsx", ".tsx", ".php")
EXT_CODE = (".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".dart", ".kt", ".swift")
RE_PY_ROUTE = re.compile(r"^[ \t]*@(\w+)\.(route|get|post|put|delete|patch)\(\s*([\"'])(.*?)\3(?:[^)]*?methods\s*=\s*\[([^\]]*)\])?", re.M)
RE_PY_DEF = re.compile(r"^[ \t]*(?:async\s+)?def\s+(\w+)\s*\(", re.M)
RE_DJANGO = re.compile(r"\b(?:re_)?path\(\s*r?([\"'])(.*?)\1\s*,\s*([\w.]+)")
RE_JS_ROUTE = re.compile(r"\b(app|router|server|route|fastify)\.(get|post|put|delete|patch|all)\(\s*([\"'`])(/[^\"'`]*)\3")
RE_RN = re.compile(r"<\w+\.Screen\s+name=[\"'{]+([\w ]+)")
RE_FLUTTER = re.compile(r"GoRoute\(\s*(?:name:\s*[\"'][^\"']*[\"']\s*,\s*)?path:\s*[\"']([^\"']*)")
RE_COMPOSE = re.compile(r"\bcomposable\(\s*(?:route\s*=\s*)?[\"']([^\"']+)")
RE_SWIFT = re.compile(r"\bstruct\s+(\w+)View\s*:\s*View")
RE_TEMPLATE_PY = re.compile(r"(?:render_template|TemplateResponse|render)\(\s*(?:request\s*,\s*)?[\"']([^\"']+)")
RE_REDIRECT_PY = re.compile(r"(?:redirect|RedirectResponse)\(\s*(?:url_for\(\s*[\"']([\w.]+)[\"']|[\"'](/[^\"']*))")
RE_HREF = re.compile(r"(?:href|action|to|routerLink)\s*=\s*(?:\{\s*)?[\"'`]\s*([^\"'`]+)")
RE_URL_FOR = re.compile(r"url_for\(\s*[\"']([\w.]+)[\"']")
RE_DJ_URL = re.compile(r"\{%\s*url\s+[\"']([\w:-]+)[\"']")
RE_PUSH = re.compile(r"(?:router\.push|navigate|navigation\.navigate|context\.go|Navigator\.pushNamed)\(\s*[\"'`]([^\"'`]+)")
RE_ACTION = re.compile(r"<(?:a|button|select|textarea|summary)\b|<input\b(?![^>]*type=[\"']hidden)|role=[\"']button[\"']", re.I)
RE_TITLE = re.compile(r"<(?:h1|title)[^>]*>(.*?)</(?:h1|title)>", re.I | re.S)


def slug(texte):
    texte = re.sub(r"\.html?$", "", texte)
    texte = unicodedata.normalize("NFD", texte)
    texte = "".join(c for c in texte if unicodedata.category(c) != "Mn").lower()
    texte = re.sub(r"\{[^}]*\}|<[^>]*>|\[[^\]]*\]", " ", texte)
    texte = re.sub(r"[^a-z0-9]+", "-", texte).strip("-")
    return texte or "accueil"


def normaliser_adresse(a):
    a = re.sub(r"<(?:\w+:)?(\w+)>|:(\w+)|\[+\.{0,3}(\w+)\]+|\{\{[^}]*\}\}|\{[^}]*\}|\$\{[^}]*\}", "{p}", a)
    a = a.split("?")[0].split("#")[0]
    if len(a) > 1:
        a = a.rstrip("/")
    return a or "/"


def adresse_vers_motif(a):
    parties = re.split(r"(\{p\})", normaliser_adresse(a))
    return re.compile("^" + "".join("[^/]+" if p == "{p}" else re.escape(p) for p in parties) + "$")


def modeler(adresse):
    """/plantes/<int:plante_id> ou /plantes/:id ou /plantes/[id] devient /plantes/{plante_id}."""
    a = re.sub(r"<(?:\w+:)?(\w+)>", r"{\1}", adresse)
    a = re.sub(r"/:(\w+)", r"/{\1}", a)
    a = re.sub(r"\[+\.{0,3}(\w+)\]+", r"{\1}", a)
    return re.sub(r"\$\{[^}]*\}|\{\{[^}]*\}\}", "{id}", a)


def lire(chemin):
    try:
        with open(chemin, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def parcourir(racine, inclure_tests):
    for dossier, sous, fichiers in os.walk(racine):
        sous[:] = [d for d in sous if d not in IGNORES and not d.startswith(".") and (inclure_tests or d not in TESTS)]
        for f in fichiers:
            yield os.path.join(dossier, f)


def humaniser(adresse):
    reste = [p for p in normaliser_adresse(adresse).strip("/").split("/") if p and p != "{p}"]
    return (reste[-1] if reste else "Accueil").replace("-", " ").replace("_", " ").capitalize()


def adresse_fichier(rel):
    """Adresse d'une page définie par son fichier (Next, Nuxt, SvelteKit, Astro, site statique)."""
    p = rel.replace(os.sep, "/")
    for prefixe in ("src/pages/", "pages/", "src/app/", "app/", "src/routes/", "routes/"):
        if p.startswith(prefixe):
            p = p[len(prefixe):]
            break
    if re.search(r"(^|/)index\.html?$", p):
        p = re.sub(r"/?index\.html?$", "", p)   # un index.html est la page de son dossier
    elif not p.endswith((".html", ".htm")):
        p = re.sub(r"\.(vue|svelte|astro|jsx|tsx|js|ts|md|mdx|php)$", "", p)   # un .html garde son extension : les liens l'écrivent
    p = re.sub(r"/?(\+page|page|index)$", "", p)
    p = re.sub(r"\(([^)]*)\)/?", "", p)
    p = re.sub(r"\[+\.{0,3}(\w+)\]+", r"{\1}", p)
    return "/" + p.strip("/")


def est_page_fichier(rel):
    p = rel.replace(os.sep, "/")
    nom = os.path.basename(p)
    if "/api/" in "/" + p or nom.startswith("_") or nom.startswith("+layout") or nom in ("layout.tsx", "layout.jsx", "loading.tsx", "error.tsx", "route.ts", "route.js"):
        return False
    if re.search(r"(^|/)(src/)?(pages|routes)/", p) and p.endswith((".vue", ".svelte", ".astro", ".jsx", ".tsx", ".js", ".ts", ".md", ".mdx")):
        return "+page" in nom or "/pages/" in "/" + p or "routes/" not in p
    if re.search(r"(^|/)(src/)?app/.*page\.(jsx|tsx|js|ts)$", p):
        return True
    if p.endswith((".html", ".htm")) and "/templates/" not in "/" + p:
        return True
    return False


def main(argv=None):
    ap = argparse.ArgumentParser(description="Premier jet d'inventaire de pages, lu dans le code.")
    ap.add_argument("racine", help="dossier du projet à lire")
    ap.add_argument("-o", "--sortie", default="inventaire-brouillon.json")
    ap.add_argument("--inclure-tests", action="store_true", help="lire aussi les dossiers de tests")
    args = ap.parse_args(argv)
    racine = os.path.abspath(args.racine)
    if not os.path.isdir(racine):
        print("ERREUR : %s n'est pas un dossier." % args.racine)
        return 1

    fichiers = sorted(parcourir(racine, args.inclure_tests))
    gabarits = {}  # nom court -> chemin relatif
    for f in fichiers:
        if f.endswith(EXT_GABARIT):
            rel = os.path.relpath(f, racine).replace(os.sep, "/")
            gabarits[rel] = f
            gabarits.setdefault(os.path.basename(f), f)
            if "templates/" in rel:
                gabarits.setdefault(rel.split("templates/", 1)[1], f)

    pages = {}  # adresse normalisée -> dict
    endpoints = {}  # nom de fonction ou de route -> adresse normalisée

    def ajouter(adresse, source, gabarit=None, methode=None, endpoint=None, redirections=None, nom=None):
        cle = normaliser_adresse(adresse) if adresse.startswith("/") else adresse
        p = pages.setdefault(cle, {"adresse": adresse, "sources": [], "gabarit": None, "methodes": set(), "redirections": [], "nom": None})
        if source not in p["sources"]:
            p["sources"].append(source)
        p["gabarit"] = p["gabarit"] or gabarit
        if methode:
            p["methodes"].add(methode.upper())
        p["redirections"] += redirections or []
        p["nom"] = p["nom"] or nom
        if endpoint:
            endpoints[endpoint] = cle
            endpoints[endpoint.split(".")[-1]] = cle
        return p

    for f in fichiers:
        rel = os.path.relpath(f, racine).replace(os.sep, "/")
        if f.endswith(".py"):
            texte = lire(f)
            routes = list(RE_PY_ROUTE.finditer(texte))
            for i, m in enumerate(routes):
                methode = m.group(2) if m.group(2) != "route" else (re.sub(r"[\"'\s]", "", (m.group(5) or "GET")).split(",")[0] or "GET")
                debut = m.end()
                fin = routes[i + 1].start() if i + 1 < len(routes) else len(texte)
                corps = texte[debut:fin]
                d = RE_PY_DEF.search(corps)
                nom_fn = d.group(1) if d else None
                corps_fn = corps[d.end():] if d else corps
                tpl = RE_TEMPLATE_PY.search(corps_fn)
                redirs = [r[0] or r[1] for r in RE_REDIRECT_PY.findall(corps_fn)]
                ligne = texte.count("\n", 0, m.start()) + 1
                ajouter(m.group(4), "%s:%d" % (rel, ligne), tpl.group(1) if tpl else None, methode, nom_fn, redirs)
            if os.path.basename(f) == "urls.py":
                for m in RE_DJANGO.finditer(texte):
                    ajouter("/" + m.group(2).lstrip("^").rstrip("$"), "%s:%d" % (rel, texte.count("\n", 0, m.start()) + 1), None, "GET", m.group(3).split(".")[-1])
        elif f.endswith((".js", ".mjs", ".cjs", ".ts")):
            texte = lire(f)
            for m in RE_JS_ROUTE.finditer(texte):
                suite = texte[m.end():m.end() + 600]
                tpl = re.search(r"\.render\(\s*[\"']([^\"']+)", suite)
                redirs = re.findall(r"\.redirect\(\s*[\"'`](/[^\"'`]*)", suite)
                ajouter(m.group(4), "%s:%d" % (rel, texte.count("\n", 0, m.start()) + 1), tpl.group(1) if tpl else None, m.group(2), None, redirs)
        if f.endswith(EXT_CODE) and not f.endswith(".py"):
            texte = lire(f)
            for rx, prefixe in ((RE_RN, "écran "), (RE_FLUTTER, ""), (RE_COMPOSE, "écran ")):
                for m in rx.finditer(texte):
                    a = m.group(1)
                    ajouter(a if a.startswith("/") else prefixe + a, "%s:%d" % (rel, texte.count("\n", 0, m.start()) + 1), None, None, a.strip("/"), None, a.replace("-", " ").strip())
            if f.endswith(".swift"):
                for m in RE_SWIFT.finditer(texte):
                    ajouter("écran " + m.group(1), "%s:%d" % (rel, texte.count("\n", 0, m.start()) + 1), rel, None, m.group(1), None, m.group(1))
        if est_page_fichier(rel):
            ajouter(adresse_fichier(rel), rel, rel)

    # Lecture des gabarits : titre, actions, liens.
    liste = []
    textes = {}
    textes_actions = {}
    for cle, p in pages.items():
        chemin = None
        if p["gabarit"]:
            chemin = gabarits.get(p["gabarit"]) or gabarits.get(os.path.basename(p["gabarit"]))
        textes[cle] = (chemin, lire(chemin) if chemin else "")
    # Menu et pied de page recopiés dans chaque fichier : les lignes présentes dans 60 % des gabarits (au moins 5) sont « communes ».
    communes = set()
    distincts = {c: t for c, (ch, t) in textes.items() if t}
    if len(distincts) >= 5:
        compte = {}
        for t in distincts.values():
            for ligne in {l.strip() for l in t.splitlines() if len(l.strip()) > 20}:
                compte[ligne] = compte.get(ligne, 0) + 1
        communes = {l for l, n in compte.items() if n >= 0.6 * len(distincts)}
    for cle, p in pages.items():
        chemin, texte_complet = textes[cle]
        texte = texte_complet if p["adresse"] == "/" else "\n".join(l for l in texte_complet.splitlines() if l.strip() not in communes)
        titre = None
        m = RE_TITLE.search(texte_complet)
        if m:
            titre = re.sub(r"\s+", " ", re.sub(r"\{\{.*?\}\}|\{%.*?%\}|<[^>]+>", "", m.group(1))).strip()
        liens_bruts = []
        for rx in (RE_HREF, RE_URL_FOR, RE_DJ_URL, RE_PUSH):
            liens_bruts += [x.strip() for x in rx.findall(texte)]
        liens_bruts = [x for x in liens_bruts if x and not x.startswith("{")]
        textes_actions[cle] = "\n".join(l for l in texte_complet.splitlines() if l.strip() not in communes)
        liste.append((cle, p, chemin, texte, titre or p["nom"] or humaniser(p["adresse"]), liens_bruts))
    liens_communs_bruts = []
    for ligne in communes:
        for rx in (RE_HREF, RE_URL_FOR, RE_DJ_URL, RE_PUSH):
            liens_communs_bruts += [x.strip() for x in rx.findall(ligne)]
    # Gabarits de base (menu, pied de page hérités par les autres) : leurs liens sont communs à toutes les pages.
    for nom_g, chemin_g in {os.path.basename(c): c for c in set(gabarits.values())}.items():
        if re.match(r"^_?(base|layout|application|default|main|root)\b", nom_g, re.I):
            texte_g = lire(chemin_g)
            for rx in (RE_HREF, RE_URL_FOR, RE_DJ_URL, RE_PUSH):
                liens_communs_bruts += [x.strip() for x in rx.findall(texte_g) if x.strip() and not x.strip().startswith("{")]

    motifs = [(cle, adresse_vers_motif(p["adresse"])) for cle, p, *_ in liste if p["adresse"].startswith("/")]
    ids, utilises = {}, set()
    for cle, p, *_ in liste:
        base = slug(p["adresse"]) if p["adresse"].startswith("/") else slug(p["adresse"])
        i, n = base, 2
        while i in utilises:
            i, n = "%s-%d" % (base, n), n + 1
        utilises.add(i)
        ids[cle] = i

    def resoudre(lien):
        if re.match(r"^(https?:|mailto:|tel:|#|javascript:|data:)", lien) or re.search(r"\.(css|js|png|jpe?g|svg|ico|webp|pdf|woff2?)$", lien):
            return None
        if lien in endpoints:
            return endpoints[lien]
        if lien.split(".")[-1] in endpoints and "/" not in lien:
            return endpoints[lien.split(".")[-1]]
        if lien.startswith("/") or lien.startswith("./") or lien.endswith((".html", ".htm")):
            adr = normaliser_adresse(lien[1:] if lien.startswith("./") else lien)
            if not adr.startswith("/"):
                adr = "/" + adr
            adr = re.sub(r"/index(\.html?)?$", "", adr) or "/"
            candidats = {adr, adr + ".html", re.sub(r"\.html?$", "", adr)}
            for cle, motif in motifs:
                if any(motif.match(c) for c in candidats):
                    return cle
        return False

    sortie_pages, sans_gabarit, non_resolus = [], 0, 0
    for cle, p, chemin, texte, nom, liens in liste:
        vers, inconnus = [], []
        for lien in liens + p["redirections"]:
            r = resoudre(lien)
            if r is None:
                continue
            if r is False:
                if lien not in inconnus:
                    inconnus.append(lien)
            elif r != cle and ids[r] not in vers:
                vers.append(ids[r])
        if not chemin:
            sans_gabarit += 1
        non_resolus += len(inconnus)
        page = {
            "id": ids[cle], "nom": nom, "etape": "A-CHOISIR", "adresse": modeler(p["adresse"]),
            "fonction": "A ECRIRE : Quand je ..., je veux ..., pour ....",
            "actions": str(len(RE_ACTION.findall(textes_actions[cle]))) if texte else "",
            "vers": vers, "entree": p["adresse"] == "/" or os.path.basename(p["adresse"]) in ("404", "404.html"),
            "source": ", ".join(p["sources"][:3]),
        }
        if chemin:
            page["gabarit"] = os.path.relpath(chemin, racine).replace(os.sep, "/")
        if inconnus:
            page["liens_non_resolus"] = inconnus[:8]
        sortie_pages.append(page)

    sortie = {
        "meta": {"titre": "Carte du parcours", "produit": "A REMPLIR", "role": "A REMPLIR", "etat_au": "A REMPLIR (AAAA-MM-JJ)", "perimetre": "A REMPLIR", "introduction": ""},
        "etapes": [],
        "espaces": [],
        "pages": sortie_pages,
        "doublons": [],
    }
    communs_ids = sorted({ids[r] for r in (resoudre(x) for x in liens_communs_bruts) if r})
    if communs_ids:
        sortie["liens_communs"] = communs_ids
    with open(args.sortie, "w", encoding="utf-8") as f:
        json.dump(sortie, f, ensure_ascii=False, indent=2)
    print("%d pages trouvées (%d sans gabarit lisible, %d liens non résolus) -> %s" % (len(sortie_pages), sans_gabarit, non_resolus, args.sortie))
    if sortie.get("liens_communs"):
        print("Menu ou pied de page commun (gabarit de base ou lignes recopiées), vers : %s. Ces liens sont à mettre sur l'accueil seulement ; dites-le dans meta.perimetre. Le champ liens_communs est une aide : supprimez-le de l'inventaire final." % ", ".join(sortie["liens_communs"]))
    print("A faire à la main : étapes, fonction de chaque page, sous-pages (parent), pages d'entrée, doublons, relecture des liens.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
