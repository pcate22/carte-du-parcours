# Inventaire d'un site statique

Valable pour un site fait à la main, ou produit par Jekyll, Hugo, Eleventy, Astro, MkDocs, Docusaurus. Ici **un fichier HTML est une page** : l'inventaire est presque complet sans lire de code.

## 0. Le premier jet

```
python3 <skill>/scripts/brouillon.py <dossier du site> -o inventaire.json
```

Si le site est produit par un générateur, **lire le résultat construit** (dossier `_site`, `public`, `dist`, `build`) et non les sources : c'est lui qui contient toutes les pages. Pour le construire sans toucher au projet, le faire dans un dossier temporaire (`hugo -d /tmp/site-carte`, `jekyll build -d /tmp/site-carte`, `npx astro build --outDir /tmp/site-carte`).

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
