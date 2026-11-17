---
name: carte-du-parcours
description: "Faire la carte du parcours d'un produit numérique (application web, site, application mobile) : inventorier toutes les pages ou écrans, écrire pour chacun sa fonction en une phrase « Quand je…, je veux… pour… », compter les actions, relier les pages (d'où l'on vient, où l'on va), repérer les doublons d'écrans et les pages orphelines, puis produire une carte HTML navigable en un seul fichier (ruban des étapes, recherche, filtre des doublons, fiche par page, clair et sombre, ordinateur d'abord) prête à publier comme artefact. À utiliser dès qu'on parle de « carte du parcours », de cartographier un parcours utilisateur, d'inventaire des pages ou des écrans, de plan du site produit, de sitemap, de user journey map, d'audit des écrans, de doublons d'écrans (même réglage sur deux écrans, deux chemins vers la même fonction, deux libellés pour la même chose, page d'état refaite), de pages orphelines, de « à quoi sert chaque page », de « combien d'écrans fait mon appli » ou de refonte d'un parcours, même si la personne ne dit pas « carte »."
---

# Carte du parcours

Un produit grandit page par page et personne n'en voit l'ensemble. La carte répond à trois questions : à quoi sert chaque page (une phrase), d'où l'on y vient et où l'on peut aller, qu'est-ce qui est fait deux fois. Le résultat est un inventaire (`inventaire.json`, la source) et une carte HTML d'un seul fichier, sans dépendance, à ouvrir dans un navigateur ou à publier comme artefact.

Le dossier du skill est celui de ce fichier. Les scripts sont en Python 3.8 ou plus, sans dépendance : `python3 <dossier du skill>/scripts/...`.

## Les étapes, dans l'ordre

### 1. Cadrer, avant de lire le code

Pose ces questions une par une. Propose chaque fois une réponse tirée du projet, la personne n'a qu'à confirmer. Si tu ne peux pas poser de question, prends la réponse la plus raisonnable, écris-la dans `meta.perimetre` et dis-le dans ton compte rendu.

1. **Périmètre** : quel produit, quelle partie (côté utilisatrice seulement ? l'espace admin, replié ?), quelle version du code.
2. **Rôle** : qui est « je » dans les phrases. Une carte raconte un rôle. Un autre rôle (admin, équipe) va dans un espace replié.
3. **Étapes officielles** du parcours : les 4 à 7 étapes que l'équipe nomme. Si elle n'en a pas, propose-les d'après le chemin réel et fais-les valider. Ajoute si besoin « Compte et aide » et « Erreurs et attentes », sans numéro : on y va à tout moment.
4. **Date de l'état** : la carte dit « État au… ». Prends la date du code lu (dernier commit) ou du jour.

Demande aussi s'il y a des mots à ne jamais publier (noms de personnes, de clientes, de textes de contenu) : mets-les dans `mots-interdits.txt`, un par ligne.

### 2. Inventorier les pages

Choisis la recette de la pile : `recettes/application-web.md` (Python, Node, PHP, Ruby), `recettes/site-statique.md`, `recettes/application-mobile.md`.

Pour un premier jet en une minute : `python3 scripts/brouillon.py <racine du projet> -o inventaire.json`. Il liste routes, gabarits, actions et liens trouvés. C'est un brouillon : tu complètes les étapes, les fonctions, les sous-pages, les entrées, les pages qu'il ne voit pas (gestionnaires d'erreur, écrans ouverts par du code), puis tu relis chaque lien.

Une page est un écran que la personne perçoit comme un lieu distinct : une adresse, un titre, un but. Les pages d'erreur, d'attente, de refus et de confirmation comptent. Les états d'un même écran (vide, plein) ne comptent pas, sauf si le code les refait en écrans à part : c'est alors un doublon à signaler.

Le format des fichiers est dans `methode/format-inventaire.md`. Pars de `modele/inventaire-vide.json`.

### 3. Écrire la fonction de chaque page

Une phrase : `Quand [la situation], je veux [ce que je veux faire], pour [ce que j'y gagne].` Du côté de la personne, en mots d'usage : jamais un nom de fonction, de route, de table ou de composant. Exemples et règles dans `methode/LISEZ-MOI.md`. Le contrôle refuse une fonction qui ne suit pas ce format.

Compte aussi les actions de chaque page : ce que la personne peut faire (liens, boutons, champs, choix), sans le menu et le pied de page communs.

### 4. Relier

Pour chaque page, `vers` liste les pages où l'on peut aller. Les pages précédentes se calculent toutes seules. Une sous-page porte `parent`. Les pages où l'on arrive de l'extérieur (adresse, menu, lien d'e-mail) portent `entree: true`. Ne « corrige » pas une page orpheline (aucun lien n'y mène) : la carte la montre, c'est une information.

### 5. Repérer les doublons

Lis `recettes/doublons.md` : quatre sortes de doublon, comment les trouver, comment écrire `pourquoi` et `piste`. Mets chaque groupe dans `doublons`. Un doublon est une décision à prendre pour l'équipe : tu le montres, tu ne l'arbitres pas.

### 6. Contrôler, puis construire

```
python3 scripts/verifier.py inventaire.json --interdits mots-interdits.txt
python3 scripts/construire.py inventaire.json -o sortie/ --nom carte-du-parcours
```

Corrige jusqu'à « Résultat : OK », puis relis les attentions une par une (doublons non signalés, jargon, pages inaccessibles). Le script produit `carte-du-parcours.html` (page complète) et `carte-du-parcours.artefact.html` (sans `<html>` ni `<head>`, pour l'outil Artifact).

### 7. Regarder le résultat

Ouvre le fichier dans un navigateur (en local, par un petit serveur ou `file://`). Vérifie : le ruban saute à l'étape, la recherche filtre, « Seulement les doublons » filtre, une page ouvre sa fiche avec sa fonction, son adresse, ses actions, ses doublons, ses précédentes et ses sous-pages cliquables, « Retour » revient, le thème bascule, rien ne dépasse à 375 px de large. Si tu as changé des couleurs : `python3 scripts/contrastes.py carte-du-parcours.html`. Si axe est disponible, lance-le : il signale `color-contrast` « incomplet » à cause des flèches superposées, c'est normal (masque le calque `.liens-svg` pour le mesurer).

### 8. Livrer

Rends à la personne l'`inventaire.json` (c'est la source : la carte se refait en une commande), les deux HTML, et une liste de ce que la carte ne couvre pas. Ne publie rien sans son accord. Pour publier comme artefact : le fichier `.artefact.html`, avec l'outil Artifact, icône « map », titre = `meta.titre`, une phrase de description.

## Garde-fous

- **Lecture seule** : tu ne modifies pas le code du produit.
- **Aucune donnée réelle dans la carte** : pas de secret, d'e-mail, de numéro, de texte écrit par des utilisateurs ni d'adresse réelle. Les adresses sont des modèles (`/livres/{id}`). Le contrôle cherche les e-mails, numéros et adresses web, et les mots de ta liste d'interdits.
- **Une carte est un état daté** : dis la date et le périmètre, en haut de la carte.
- **Ne retouche pas `modele/carte.html`** sans demande. Pour changer les couleurs : les jetons de `:root`, dans les trois blocs, puis `scripts/contrastes.py`.

## Où est quoi

| Fichier | Contenu |
|---|---|
| `methode/LISEZ-MOI.md` | la méthode : phrase de fonction, actions, contrôles, accessibilité (RGAA) |
| `methode/format-inventaire.md` | tous les champs de `inventaire.json` |
| `recettes/` | extraire l'inventaire selon la pile, et repérer les doublons |
| `modele/carte.html` | le gabarit de la carte (un bloc de données JSON, le reste est générique) |
| `modele/inventaire-vide.json` | un inventaire minimal pour partir |
| `exemple/` | une carte complète d'un produit fictif (30 pages, 6 groupes de doublons) |
| `scripts/` | `brouillon.py`, `verifier.py`, `construire.py`, `contrastes.py` |
