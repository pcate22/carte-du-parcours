# Inventaire d'une application web

Valable pour Python (Flask, FastAPI, Starlette, Django), Node (Express, Koa, Fastify, Next.js, Nuxt, SvelteKit, Remix, Astro), PHP (Laravel, Symfony) et Ruby (Rails). L'idée est la même partout : **une route = une page candidate, un gabarit = ce que la personne voit, les liens du gabarit = les flèches**.

## 0. Le premier jet

```
python3 <skill>/scripts/brouillon.py <racine du projet> -o inventaire.json
```

Il lit les décorateurs Flask et FastAPI, `urls.py` de Django, les appels `app.get(...)` d'Express, les pages par fichiers de Next, Nuxt, SvelteKit et Astro, rattache chaque route à son gabarit, compte les actions et relève les liens. Il ne voit pas : les gestionnaires d'erreur, les écrans que le code compose à la volée, les routes construites en boucle, les menus hérités d'un gabarit de base. Tout cela est à compléter à la main avec ce qui suit.

## 1. Lister les routes

Si le brouillon ne suffit pas, ou pour vérifier son travail :

```
# Flask, FastAPI, Starlette
grep -rnE "@[a-z_]+\.(route|get|post|put|delete|patch)\(" --include=*.py .

# Django (avec django-extensions : python manage.py show_urls)
grep -rn "path(" --include=urls.py .

# Express, Koa, Fastify
grep -rnE "\b(app|router)\.(get|post|put|delete|all)\(" --include=*.js --include=*.ts .

# Next.js, Nuxt, SvelteKit, Astro, Remix : les fichiers sont les routes
find . -path ./node_modules -prune -o \( -path "*pages/*" -o -name "page.*" -o -name "+page.*" -o -path "*app/routes/*" \) -type f -print

# Laravel, Symfony, Rails
php artisan route:list        # ou : grep -n "Route::" routes/web.php
php bin/console debug:router
bin/rails routes
```

Ne garder que les routes qui **rendent une page** : `GET` qui renvoie du HTML. Un `POST` qui redirige fait partie de la page qui porte le formulaire. Les routes d'API qui renvoient du JSON (`/api/...`) ne sont pas des pages. Les fragments HTML d'un écran (htmx, `hx-get`) non plus, sauf s'ils changent l'écran entier.

## 2. Ne pas oublier ce que les routes ne montrent pas

- **Pages d'erreur et de refus** : `grep -rnE "errorhandler|exception_handler|handler404|handler500|not-found|error\.(tsx|vue)|404\.html"`. Une page par cause distincte (introuvable, refus, session expirée, limite atteinte, paiement refusé).
- **Pages d'attente** : calcul en cours, confirmation de paiement. Chercher `meta refresh`, `setInterval`, `polling`, `EventSource`, `WebSocket` dans les gabarits.
- **Pages construites par paramètre** (`/reglages/{reglage}`) : une page par *modèle d'écran*, pas une par valeur. Écrire l'adresse en modèle et noter combien de variantes dans `note`.
- **Retours d'un prestataire externe** (paiement, connexion sociale) : l'adresse de retour est une **entrée**.
- **Pages ouvertes par un e-mail ou une notification** : lire les gabarits d'e-mail (`grep -rln "mail" --include=*.html .`) ; leurs liens sont des entrées.
- **Étapes d'un formulaire en plusieurs écrans** : chaque écran est une page.

## 3. Choisir les rôles

Les contrôles d'accès dessinent les rôles : `@login_required`, `@admin_required`, `middleware`, `can(`, `guard`. Ne garder dans la carte principale que le rôle choisi ; les autres vont dans un espace replié (`espaces`, et `espace` sur l'étape).

## 4. Relier

Lire chaque gabarit et noter où il mène :

| Ce qu'on cherche | Motif |
|---|---|
| liens | `href="..."`, `<a ` |
| formulaires | `action="..."`, `<form` |
| redirections côté serveur | `redirect(`, `RedirectResponse(`, `res.redirect(`, `redirect_to` |
| noms de routes | `url_for('x')`, `{% url 'x' %}`, `route('x')`, `path('x')` |
| navigation côté client | `router.push(`, `navigate(`, `<Link `, `router-link` |

Le **menu et le pied de page** sont dans le gabarit de base : les lire une fois, les dire dans `meta.perimetre` (« menu présent partout : Accueil, Catalogue, Panier, Mon compte »), et ne mettre leurs liens que sur l'accueil. Sinon chaque page mène à tout et les flèches ne disent plus rien.

**Sous-page** : une page qu'on ouvre depuis une autre pour en régler un détail, avec une adresse qui la prolonge (`/reservations/{id}` puis `/reservations/{id}/date`). Mettre `parent`.

**Entrée** : `/`, les adresses données par e-mail, les retours de prestataire, la 404. Mettre `entree: true`.

## 5. Compter les actions

Dans le **rendu**, pas dans le source : liens, boutons, champs, listes de choix, onglets, sans le menu ni le pied de page. Ouvrir les `include`, `macro` et composants. Si l'application peut tourner en local avec **des données inventées** (jamais celles de la production), la parcourir et compter à l'écran. Une liste répétée compte pour une ligne : écrire `"1 + 2 par atelier"`.

## 6. Écrire, contrôler, construire

Revenir à `SKILL.md`, étapes 3 à 7 : fonctions, doublons, `verifier.py`, `construire.py`.

## Pièges fréquents

- **Compter les routes au lieu des pages.** Une page avec un `GET` et un `POST` sur la même adresse est une page.
- **Compter les routes d'API.** Elles n'ont pas de fonction côté personne.
- **Oublier ce qui n'a pas de lien.** Ce sont justement les pages orphelines qu'on cherche.
- **Lire la documentation au lieu du code.** La carte dit ce que le produit fait aujourd'hui.
- **Mettre une valeur réelle dans `adresse`** (identifiant, jeton, nom). Toujours un modèle.
