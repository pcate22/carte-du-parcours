# Inventaire d'un site statique

Valable pour un site fait à la main, ou produit par Jekyll, Hugo, Eleventy, Astro, MkDocs, Docusaurus. Ici **un fichier HTML est une page** : l'inventaire est presque complet sans lire de code.

## 0. Le premier jet

```
python3 <skill>/scripts/brouillon.py <dossier du site> -o inventaire.json
```

Si le site est produit par un générateur, **lire le résultat construit** (dossier `_site`, `public`, `dist`, `build`) et non les sources : c'est lui qui contient toutes les pages. Pour le construire sans toucher au projet, le faire dans un dossier temporaire (`hugo -d /tmp/site-carte`, `jekyll build -d /tmp/site-carte`, `npx astro build --outDir /tmp/site-carte`).

**Générateur maison (un `build.py`, un `Makefile`), ou construction qui demande des secrets** : ne la lance pas (elle lirait `.env`, appellerait des services, écrirait dans le projet). Lis le dossier construit **déjà présent** et vérifie qu'il est à jour : sa date doit suivre celle du dernier commit (`git log -1 --format=%ad`), et sa liste de pages doit être celle des sources (`diff <(ls site) <(ls build)`). Sur les sources, le brouillon voit des marqueurs (`__SITE_URL__/...`) et rate le menu que le générateur injecte : 42 liens non résolus sur 26 pages, contre 25 sur le dossier construit. Dis dans tes hypothèses quel dossier tu as lu et sa date.

Le script reconnaît le **menu et le pied de page recopiés dans chaque fichier** (lignes présentes dans 60 % des pages) et les met à part : leurs liens ne sont comptés que sur l'accueil, et ne gonflent pas le nombre d'actions.

## 1. Lister les pages

```
find <dossier> -name "*.html" -not -path "*/node_modules/*" | sort
```

- `index.html` d'un dossier = la page du dossier (`/concerts/index.html` est `/concerts`).
- Le **plan du site** (`sitemap.xml`) liste ce que le site *annonce* : comparer avec les fichiers. Une page présente en fichier mais absente du plan est un candidat orphelin.
- Les pages `404.html` et celles de redirection (`<meta http-equiv="refresh"`) comptent : la première est une entrée, les secondes sont des doublons probables.

## 2. Relier

```
grep -rhoE 'href="[^"#]+"' <dossier> --include=*.html | sort | uniq -c | sort -rn
```

Pour chaque page, noter vers où mènent ses liens **propres** (hors menu et pied de page). Les **formulaires** : `action="..."` mène à une page de remerciement ou à un service extérieur (le dire dans `note`).

Pour trouver les pages que rien ne relie : toute page de la liste qui n'apparaît dans aucun `href` et qui n'est pas dans le menu. Le script de contrôle les marque en orphelines.

## 2 bis. Ce que le code du serveur ajoute

**Adresses propres.** Un fichier `.htaccess`, un `vercel.json`, un `netlify.toml` ou un `next.config` peut réécrire les adresses : `/talks/mon-talk` sert `talk-mon-talk.html`, `/assistant` sert `assistant.html`. Lis les règles (`RewriteRule`, `rewrites`, `redirects`). Le brouillon résout par ressemblance de nom les liens qu'il ne trouve pas (champ `liens_par_ressemblance`) : vérifie chacun contre les règles. L'adresse de la page est celle que la personne voit (`/talks/mon-talk`), pas celle du fichier.

**Formulaires vers un script (PHP, Python, serveur).** Le formulaire `action="/contact.php"` n'est pas une page : la flèche va vers la page que la personne **voit ensuite**, que le script choisit (renvoi `Location:`, appel de fonction, `header(...)`). Lis le script : cherche `Location`, `header(`, `redirect`, `aller(`. Pour un script PHP, le brouillon relève les fichiers `.html` et les `Location:` cités ; les renvois faits par une fonction maison sont à relire. Les pages « merci » et « erreur » sont alors des pages à part entière, en étape « Après l'envoi » et « Erreurs ». Si un champ est un piège contre les robots (invisible, `tabindex="-1"`), ce n'est pas une action.

**Pages à lien secret.** Une page « merci, voici le fichier » dont l'adresse contient un code (`merci-x-9f3a1c27be.html`, lien envoyé par e-mail) est une page d'entrée (`entree: true`). Écris son adresse en modèle (`/merci-x-{code}.html`) et son identifiant sans le code : la carte se publie, le code protège un fichier. `verifier.py` signale un code dans l'identifiant ou l'adresse.

**Page cachée.** Une page sans lien, hors plan du site, interdite aux moteurs (`noindex`) mais bien vivante (un outil en test) est orpheline : laisse la carte le dire, et explique dans `note` que c'est voulu. Ne la marque `entree` que si l'équipe donne son adresse à des personnes précises.

**Sorties vers un autre outil.** Le bouton « Réserver » qui mène à un agenda en ligne, le paiement chez un prestataire, un formulaire hébergé : ce sont des écrans, mais pas ceux du produit. Dis-les dans `meta.perimetre` et dans la `note` de la page de départ (« la réservation se fait sur un agenda externe »). Ils ne sont pas des pages de la carte, qui ne montre donc pas cette partie du parcours : dis-le dans le compte rendu.

## 3. Les étapes d'un site vitrine

Un site de présentation n'a pas de « paiement » ni de « compte ». Les étapes suivent **les deux ou trois buts du visiteur** (écouter, rejoindre, écrire), pas la structure des dossiers. À défaut, proposer, et faire valider :

1. **Découvrir** : accueil, présentation, actualités.
2. **Comprendre l'offre** : pages de service, tarifs, exemples.
3. **Passer à l'action** : contact, inscription, réservation.
4. **Après** : pages de remerciement, confirmations.
5. **Informations** (sans numéro) : mentions légales, accessibilité, plan du site.
6. **Erreurs** (sans numéro) : 404.

## 3 bis. Les constats d'un site statique

Un formulaire sans destination visible (`action` vers une page fixe, ou absent, ou sans `method`) est un constat : le dire, car la personne ne saura pas où part son message. Idem : une page sans aucune suite, une information attendue qui manque (date, lieu, horaire), un parcours qui renvoie vers un formulaire trop général. Les noter dans `constats`.

Les adresses gardent leur extension (`/concerts.html`) quand les liens du site l'écrivent ainsi ; `index.html` est la page de son dossier.

## 4. Les doublons d'un site statique

- Deux pages de même contenu sous deux adresses (`/a-propos` et `/qui-sommes-nous`) : `deux-chemins`.
- Deux formulaires de contact : `meme-reglage` ou `deux-chemins`.
- Une page « Contact » et une page « Nous écrire » : `deux-noms`.
- Les versions de langue (`/fr/`, `/en/`) ne sont **pas** des doublons : une carte par langue, ou une seule en français.

## 5. Compter les actions

Liens, boutons, champs, listes, hors menu et pied de page. Les images cliquables comptent. Un carrousel compte pour ses commandes, pas pour ses images.

## 6. Écrire, contrôler, construire

Revenir à `SKILL.md`, étapes 3 à 8.
