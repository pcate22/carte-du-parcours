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
  - React Router (<Route path="...">, routes en objets), pages d'erreur de Next (not-found, error) ;
  - adresses qui ne font que rediriger (Next : redirect, permanentRedirect) : listées à part, ce ne sont pas des pages.
Pour chaque page : adresse, fichier source, gabarit lié, nombre d'actions compté dans le gabarit (un lien répété compte une fois),
liens trouvés vers d'autres pages (aussi les adresses écrites entre guillemets dans le code React et les pages citées par un script PHP
vers lequel mène un formulaire).

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
RE_ACTION = re.compile(r"<(?:a|button|select|textarea|summary)\b|<input\b(?![^>]*(?:type=[\"']hidden|tabindex=[\"']-1))|(?-i:<(?=\w*(?:Button|Link|Lien|Bouton))[A-Z]\w*)|role=[\"']button[\"']", re.I)
RE_BALISE_LIEN = re.compile(r"<(?:a|(?-i:(?=\w*(?:Link|Lien))[A-Z]\w*))\b([^>]*)>", re.I)
RE_LIEN_CIBLE = re.compile(r"(?:href|to|vers)\s*=\s*(?:\{\s*)?([\"'`])(.*?)\1")
RE_CHAINE_ADRESSE = re.compile(r"[\"'`]((?:/[\w\-.${}]+)+/?(?:\?[^\"'`\s]*)?)[\"'`]")
RE_CHAINE_FICHIER = re.compile(r"[\"']/?([\w\-./]+\.html?)[\"']|Location:\s*/?([\w\-./]+)")
RE_LIGNE_A_IGNORER = re.compile(r"canonical|revalidatePath|openGraph|alternates|sitemap|\burl:|permanentRedirect|^\s*import\s", re.I)
RE_REACT_ROUTE = re.compile(r"<Route\b[^>]*?\bpath=[\"'{`]+([^\"'`}]+)")
RE_OBJ_ROUTE = re.compile(r"\{\s*path:\s*[\"']([^\"']*)[\"']\s*,\s*(?:element|Component|lazy|component)\b")
RE_NEXT_REDIRECT = re.compile(r"\b(?:permanentRedirect|redirect)\(\s*[\"'`]([^\"'`]+)")
SPECIALES_NEXT = {"not-found": ("page introuvable", "Page introuvable"), "error": ("page d'erreur", "Une erreur est survenue"), "global-error": ("page d'erreur", "Une erreur est survenue")}
RE_TITLE = re.compile(r"<(?:h1|title)[^>]*>(.*?)</(?:h1|title)>", re.I | re.S)


def slug(texte):
    texte = re.sub(r"\.html?$", "", texte)
    texte = unicodedata.normalize("NFD", texte)
    texte = "".join(c for c in texte if unicodedata.category(c) != "Mn").lower()
    texte = re.sub(r"\{[^}]*\}|<[^>]*>|\[[^\]]*\]", " ", texte)
    texte = re.sub(r"[^a-z0-9]+", "-", texte).strip("-")
    return texte or "accueil"


def identifiant(adresse):
    """Identifiant lisible : /produits -> produits, /produits/{id} -> produits-detail, /{slug} -> page-slug."""
    base = slug(adresse)
    if not adresse.startswith("/") or adresse == "/":
        return base
    derniers = [x for x in re.split(r"/+", adresse.strip("/")) if x]
    if base == "accueil" and derniers:
        return "page-" + (re.sub(r"[^a-z0-9]+", "-", derniers[-1].lower()).strip("-") or "libre")
    if derniers and re.fullmatch(r"\{[^}]*\}|<[^>]*>|:\w+|\[+[^\]]*\]+", derniers[-1]):
        return base + "-detail"
    return base


def compter_actions(texte):
    """Liens distincts + autres contrôles (boutons, champs visibles, volets). Un lien répété compte une fois."""
    cibles, anonymes = set(), 0
    for m in RE_BALISE_LIEN.finditer(texte):
        c = RE_LIEN_CIBLE.search(m.group(1))
        if c:
            cibles.add(c.group(2))
        else:
            anonymes += 1
    return len(cibles) + anonymes + len(RE_ACTION.findall(texte)) - len(RE_BALISE_LIEN.findall(texte))


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
    if "/api/" in "/" + p or nom.startswith("_") or nom.startswith("+layout") or nom in ("layout.tsx", "layout.jsx", "loading.tsx", "error.tsx", "global-error.tsx", "not-found.tsx", "route.ts", "route.js"):
        return False
    if re.search(r"(^|/)(src/)?(pages|routes)/", p) and p.endswith((".vue", ".svelte", ".astro", ".jsx", ".tsx", ".js", ".ts", ".md", ".mdx")):
        return "+page" in nom or "/pages/" in "/" + p or "routes/" not in p
    if re.search(r"(^|/)(src/)?app/.*page\.(jsx|tsx|js|ts)$", p):
        return True
    if p.endswith((".html", ".htm")) and "/templates/" not in "/" + p:
        return True
    return False


def redirection_seule(chemin, rel):
    """Une page Next qui ne fait que rediriger (redirect, permanentRedirect) : retourne la cible, sinon None."""
    if not re.search(r"(^|/)(src/)?app/.*page\.(jsx|tsx|js|ts)$", rel):
        return None
    code = lire(chemin)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.S)
    code = re.sub(r"^\s*//.*$", "", code, flags=re.M)
    lignes = [l for l in code.splitlines() if l.strip()]
    m = RE_NEXT_REDIRECT.search(code)
    if m and len(lignes) <= 14 and not re.search(r"<[A-Za-z]", code):
        return m.group(1)
    return None


def cibles_du_php(chemin):
    """Fichiers .html et renvois « Location: » cités par un script PHP (où mène un formulaire dont l'action est ce script)."""
    return [a or b for a, b in RE_CHAINE_FICHIER.findall(lire(chemin)) if a or b]


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
    redirections_seules = []  # pages Next qui ne font que rediriger : pas des pages
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
            for rx in (RE_REACT_ROUTE, RE_OBJ_ROUTE):
                for m in rx.finditer(texte):
                    a = m.group(1)
                    if a and a not in ("*", "/*"):
                        a = "/" + a.lstrip("/")
                        ajouter(a, "%s:%d" % (rel, texte.count("\n", 0, m.start()) + 1), None, None, None, None, humaniser(a))
            if f.endswith(".swift"):
                for m in RE_SWIFT.finditer(texte):
                    ajouter("écran " + m.group(1), "%s:%d" % (rel, texte.count("\n", 0, m.start()) + 1), rel, None, m.group(1), None, m.group(1))
        stem = re.sub(r"\.(tsx|jsx|js|ts)$", "", os.path.basename(rel))
        if re.search(r"(^|/)(src/)?app/", rel) and stem in SPECIALES_NEXT and os.path.basename(rel) != stem:
            adr_s, nom_s = SPECIALES_NEXT[stem]
            ajouter(adr_s, rel, rel, nom=nom_s)
        if est_page_fichier(rel):
            cible = redirection_seule(f, rel)
            if cible:
                redirections_seules.append({"adresse": adresse_fichier(rel), "vers": cible, "source": rel})
            else:
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
        chaines = []
        if chemin and chemin.endswith((".tsx", ".jsx", ".ts", ".js")):
            for ligne in texte.splitlines():
                if not RE_LIGNE_A_IGNORER.search(ligne):
                    chaines += [m.group(1) for m in RE_CHAINE_ADRESSE.finditer(ligne)]
        textes_actions[cle] = "\n".join(l for l in texte_complet.splitlines() if l.strip() not in communes)
        liste.append((cle, p, chemin, texte, titre or p["nom"] or humaniser(p["adresse"]), liens_bruts, chaines))
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

    # Les adresses fixes d'abord : /{slug} ressemble à toutes les adresses d'un segment et ne doit passer qu'en dernier.
    motifs = sorted(((cle, adresse_vers_motif(p["adresse"]), p["adresse"]) for cle, p, *_ in liste if p["adresse"].startswith("/")),
                    key=lambda t: (normaliser_adresse(t[2]).count("{p}"), -len(t[2])))
    ids, utilises = {}, set()
    for cle, p, *_ in liste:
        base = identifiant(p["adresse"])
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
            for cle, motif, _ in motifs:
                if any(motif.match(c) for c in candidats):
                    return cle
        return False

    php = {os.path.basename(x): x for x in fichiers if x.endswith(".php")}

    def par_ressemblance(lien):
        """Un lien sans page (adresse propre réécrite : /fiches/x pour fiche-x.html) : la page dont l'adresse finit comme lui, si elle est seule."""
        dernier = normaliser_adresse(lien).rstrip("/").split("/")[-1]
        if not lien.startswith("/") or len(dernier) < 4 or re.search(r"\.\w{2,4}$", dernier):
            return None
        trouvees = [c for c, q in pages.items() if q["adresse"].startswith("/") and re.search(r"(^|[-/])" + re.escape(dernier) + r"(\.html?)?$", q["adresse"])]
        return trouvees[0] if len(trouvees) == 1 else None

    sortie_pages, sans_gabarit, non_resolus = [], 0, 0
    ressemblances, via_php = [], 0
    for cle, p, chemin, texte, nom, liens, chaines in liste:
        vers, inconnus = [], []
        for lien in liens + p["redirections"]:
            script = lien.split("?")[0]
            if script.endswith(".php") and os.path.basename(script) in php:
                for cible in cibles_du_php(php[os.path.basename(script)]):
                    r2 = resoudre(cible if cible.startswith(("/", ".")) else "/" + cible)
                    if r2 not in (None, False) and r2 != cle and ids[r2] not in vers:
                        vers.append(ids[r2])
                        via_php += 1
                continue
            r = resoudre(lien)
            if r is None:
                continue
            if r is False:
                alt = par_ressemblance(lien)
                if alt and alt != cle:
                    if ids[alt] not in vers:
                        vers.append(ids[alt])
                    ressemblances.append("%s -> %s" % (lien, ids[alt]))
                elif lien not in inconnus:
                    inconnus.append(lien)
            elif r != cle and ids[r] not in vers:
                vers.append(ids[r])
        for lien in chaines:
            r = resoudre(lien)
            if r not in (None, False) and r != cle and ids[r] not in vers:
                vers.append(ids[r])
        if not chemin:
            sans_gabarit += 1
        non_resolus += len(inconnus)
        page = {
            "id": ids[cle], "nom": nom, "etape": "A-CHOISIR", "adresse": modeler(p["adresse"]),
            "fonction": "A ECRIRE : Quand je ..., je veux ..., pour ....",
            "actions": str(compter_actions(textes_actions[cle])) if texte else "",
            "vers": vers, "entree": p["adresse"] in ("/", "page introuvable", "page d'erreur") or os.path.basename(p["adresse"]) in ("404", "404.html"),
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
    if redirections_seules:
        sortie["redirections"] = redirections_seules
    if ressemblances:
        sortie["liens_par_ressemblance"] = sorted(set(ressemblances))
    with open(args.sortie, "w", encoding="utf-8") as f:
        json.dump(sortie, f, ensure_ascii=False, indent=2)
    print("%d pages trouvées (%d sans gabarit lisible, %d liens non résolus) -> %s" % (len(sortie_pages), sans_gabarit, non_resolus, args.sortie))
    if sortie.get("liens_communs"):
        print("Menu ou pied de page commun (gabarit de base ou lignes recopiées), vers : %s. Ces liens sont à mettre sur l'accueil seulement ; dites-le dans meta.perimetre. Le champ liens_communs est une aide : supprimez-le de l'inventaire final." % ", ".join(sortie["liens_communs"]))
    if redirections_seules:
        print("%d adresse(s) ne font que rediriger (ce ne sont pas des pages, écartées) : %s. Champ redirections : une aide, à supprimer de l'inventaire final." % (
            len(redirections_seules), ", ".join("%s -> %s" % (r["adresse"], r["vers"]) for r in redirections_seules)))
    if ressemblances:
        print("%d lien(s) résolu(s) par ressemblance de nom, sans règle lue (réécriture d'adresses ? voir .htaccess, vercel.json, next.config) : à vérifier, champ liens_par_ressemblance, à supprimer ensuite." % len(set(ressemblances)))
    if via_php:
        print("%d lien(s) pris dans des scripts PHP (formulaires) : les renvois faits par une fonction ne sont pas lus, relire le script." % via_php)
    pj = os.path.join(racine, "package.json")
    if os.path.isfile(pj) and re.search(r'"(react|vue|svelte|@angular/core|solid-js|preact)"', lire(pj)) and len(sortie_pages) <= 5:
        print("ATTENTION : application d'une seule page (React, Vue, Svelte…) et seulement %d page(s) trouvée(s) : ses écrans viennent d'un routeur que ce script ne lit pas. Voir recettes/application-une-page.md." % len(sortie_pages))
    print("A faire à la main : étapes, fonction de chaque page, sous-pages (parent), pages d'entrée, doublons, relecture des liens.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
