---
name: carte-du-parcours
description: "Faire la carte du parcours d'un produit numérique (application web, site, application mobile) : inventorier toutes les pages ou écrans, écrire pour chacun sa fonction en une phrase « Quand je…, je veux… pour… », compter les actions, relier les pages (d'où l'on vient, où l'on va), repérer les doublons d'écrans et les pages orphelines, puis produire une carte HTML navigable en un seul fichier (ruban des étapes, recherche, filtre des doublons, fiche par page, clair et sombre, ordinateur d'abord) prête à publier comme artefact. À utiliser dès qu'on parle de « carte du parcours », de cartographier un parcours utilisateur, d'inventaire des pages ou des écrans, de plan du site produit, de sitemap, de user journey map, d'audit des écrans, de doublons d'écrans (même réglage sur deux écrans, deux chemins vers la même fonction, deux libellés pour la même chose, page d'état refaite), de pages orphelines, de « à quoi sert chaque page », de « combien d'écrans fait mon appli » ou de refonte d'un parcours, même si la personne ne dit pas « carte »."
---

# Carte du parcours

Un produit grandit page par page et personne n'en voit l'ensemble. La carte répond à trois questions : à quoi sert chaque page (une phrase), d'où l'on y vient et où l'on peut aller, qu'est-ce qui est fait deux fois. Le résultat est un inventaire (`inventaire.json`, la source) et une carte HTML d'un seul fichier, sans dépendance, à ouvrir dans un navigateur ou à publier comme artefact.

Le dossier du skill est celui de ce fichier : note-le `SKILL`. Les commandes ci-dessous s'écrivent `python3 "$SKILL/scripts/..."` ; les scripts sont en Python 3.8 ou plus, sans dépendance. Travaille dans un dossier à part (par exemple `carte/`), jamais dans le projet à cartographier.

## Les étapes, dans l'ordre

### 1. Cadrer, avant de lire le code

Pose ces questions une par une. Propose chaque fois une réponse tirée du projet, la personne n'a qu'à confirmer. Si tu ne peux pas poser de question, prends la réponse la plus raisonnable, écris-la dans `meta.hypotheses` (la carte les affiche, « à valider ») et dans `meta.perimetre`, et dis-le dans ton compte rendu avec la liste courte des vraies questions à poser.

1. **Périmètre** : quel produit, quelle partie (côté utilisatrice seulement ? l'espace admin, replié ?), quelle version du code. Si le projet existe en plusieurs copies (branches, dossiers de travail), compare-les avant de lire : `git log -1 --format=%ad`, `git branch --contains`. Prends celle qui contient les autres (souvent `main`) et dis-le : une copie de travail ancienne donne une carte fausse. Demande aussi quelle version est en ligne.
2. **Rôle** : qui est « je » dans les phrases. Une carte raconte un rôle. Un autre rôle (admin, équipe) va dans un espace replié.
3. **Étapes officielles** du parcours : les 4 à 7 étapes que l'équipe nomme. Si elle n'en a pas, propose-les d'après le chemin réel et fais-les valider. Ajoute si besoin « Compte et aide » et « Erreurs et attentes », sans numéro : on y va à tout moment. Une application à onglets n'a pas de parcours dans le temps : prends les onglets comme étapes (`recettes/application-une-page.md`).
4. **Date de l'état** : la carte dit « État au… ». Prends la date du code lu (dernier commit) ou du jour.

Demande aussi s'il y a des mots à ne jamais publier (noms de personnes, de clientes, de textes de contenu) : mets-les dans `mots-interdits.txt`, un par ligne. Si tu ne peux pas demander, n'en crée pas : le contrôle ignore un fichier absent.

### 2. Inventorier les pages

Choisis la recette de la pile : `recettes/application-web.md` (Python, Node, PHP, Ruby), `recettes/nextjs.md`, `recettes/application-une-page.md` (React, Vue, Svelte, routeur maison), `recettes/site-statique.md` (aussi : générateur maison, pages PHP, adresses réécrites), `recettes/application-mobile.md`.

Pour un premier jet en une minute : `python3 "$SKILL/scripts/brouillon.py" <racine du projet> -o carte/inventaire.json`. Il liste routes, gabarits, actions et liens trouvés. C'est un brouillon : tu complètes les étapes, les fonctions, les sous-pages, les entrées, les pages qu'il ne voit pas (gestionnaires d'erreur, écrans ouverts par du code), puis tu relis chaque lien : les pages qui sortent avec 0 ou 1 flèche, et les liens « résolus par ressemblance », sont les premières à relire. Ses nombres d'actions sont un ordre de grandeur. S'il annonce « application d'une seule page » ou ne trouve presque rien, il ne lit pas le routeur : passe à la recette. Supprime les champs d'aide du brouillon (`liens_communs`, `source`, `gabarit`, `liens_non_resolus`, `redirections`, `liens_par_ressemblance`) une fois utilisés.

Une page est un écran que la personne perçoit comme un lieu distinct : une adresse, un titre, un but. Les pages d'erreur, d'attente, de refus et de confirmation comptent. Les états d'un même écran (vide, plein) ne comptent pas, sauf si le code les refait en écrans à part : c'est alors un doublon à signaler.

Le format des fichiers est dans `methode/format-inventaire.md`. Pars de `modele/inventaire-vide.json`.

### 3. Écrire la fonction de chaque page

Une phrase : `Quand [la situation], je veux [ce que je veux faire], pour [ce que j'y gagne].` Du côté de la personne, en mots d'usage : jamais un nom de fonction, de route, de table ou de composant. Exemples et règles dans `methode/LISEZ-MOI.md`. Le contrôle refuse une fonction qui ne suit pas ce format.

Compte aussi les actions de chaque page : ce que la personne peut faire (liens, boutons, champs, choix), sans le menu et le pied de page communs.

### 4. Relier

Pour chaque page, `vers` liste les pages où l'on peut aller. Un lien vers un autre outil (agenda en ligne, paiement chez un prestataire) n'est pas une page de la carte : dis-le dans `meta.perimetre` et dans la `note` de la page de départ. Une flèche va vers la page que la personne **voit ensuite** : si un formulaire envoie vers une adresse dont la réponse est une redirection, la flèche va vers la destination de la redirection. Le menu et le pied de page communs se disent une fois dans `meta.perimetre` : leurs cibles vont dans le `vers` de l'accueil (sinon une page qu'on ne trouve que dans le pied de page paraîtrait orpheline), mais ils ne comptent pas dans les actions de l'accueil ni des autres pages. Les pages précédentes se calculent toutes seules. Une sous-page porte `parent`. Les pages où l'on arrive de l'extérieur (adresse, menu, lien d'e-mail) portent `entree: true`. Ne « corrige » pas une page orpheline (aucun lien n'y mène) : la carte la montre, c'est une information.

### 5. Repérer les doublons

Lis `recettes/doublons.md` : quatre sortes de doublon, comment les trouver, comment écrire `pourquoi` et `piste`. Mets chaque groupe dans `doublons`. Un doublon est une décision à prendre pour l'équipe : tu le montres, tu ne l'arbitres pas. Dans le compte rendu, classe les groupes par intérêt pour elle (ce qu'elle gagnerait à les supprimer : `recettes/doublons.md`, section « Classer »). Quand le contrôle soupçonne un doublon que tu as examiné et écarté (deux fonctions voisines mais différentes), note la paire dans `non_doublons` avec la raison : l'alerte ne revient plus.

### 6. Noter ce qui ne va pas

Quand la demande est aussi un audit (« ce qui ne va pas », « les défauts »), ou quand tu as vu autre chose qu'un doublon, ajoute des `constats` : une impasse, un formulaire dont on ne voit pas où part le message, une information absente, une page qui n'offre aucune suite. Huit au plus, chacun avec ses pages. Un constat est un fait observé dans le code, pas une opinion, et c'est un fait **affiché** : vérifie que le texte est vu par la personne (dans l'écran, pas dans un `console.error`).

### 7. Contrôler, puis construire

```
python3 "$SKILL/scripts/verifier.py" carte/inventaire.json --interdits carte/mots-interdits.txt
python3 "$SKILL/scripts/construire.py" carte/inventaire.json --interdits carte/mots-interdits.txt
```

Corrige jusqu'à « Résultat : OK », puis relis les attentions une par une (doublons non signalés, jargon, pages inaccessibles, code dans une adresse). Le script produit, à côté de l'inventaire, `carte-du-parcours.html` (page complète) et `carte-du-parcours.artefact.html` (sans `<html>` ni `<head>`, pour l'outil Artifact), puis les contrôle sans navigateur (`scripts/controler_html.py` : données lisibles, aucun repère « A REMPLIR » oublié, syntaxe du script par Node). Ce contrôle ne remplace pas l'étape 8.

### 8. Regarder le résultat

Si tu n'as pas de navigateur, dis-le dans ton compte rendu : n'écris pas que les clics ou le rendu sont vérifiés. Sinon, ouvre le fichier dans un navigateur, de préférence servi par un petit serveur (`python3 -m http.server 8000 --bind 127.0.0.1 --directory carte`, puis `http://127.0.0.1:8000/carte-du-parcours.html`). Le volet de navigateur de Claude Code charge un `file://` situé hors du projet comme une capture (adresse `data:`) : le `#` du changement de page y produit une erreur de console qui n'est pas celle de la carte. Vérifie : le ruban saute à l'étape, la recherche filtre, « Seulement les doublons » filtre, une page ouvre sa fiche avec sa fonction, son adresse, ses actions, ses doublons, ses précédentes et ses sous-pages cliquables, « Retour » revient, le thème bascule, rien ne dépasse à 375 px de large. Si tu as changé des couleurs : `python3 "$SKILL/scripts/contrastes.py" carte/carte-du-parcours.html`. Si axe est disponible, lance-le en clair et en sombre : zéro violation attendue. Quand une page est choisie, axe peut classer `color-contrast` en « incomplet » parce que les flèches passent au-dessus des cartes ; masque alors le calque (`.liens-svg { display: none }`) pour le mesurer.

Deux pièges de test : un volet de navigateur masqué suspend les animations de la page, donc les flèches ne se tracent pas (ce n'est pas un défaut) ; et `navigate` vers la même adresse avec un `#` identique ne recharge pas la page (recharge-la).

### 9. Livrer

Rends à la personne l'`inventaire.json` (c'est la source : la carte se refait en une commande), les deux HTML, et un compte rendu court : pages trouvées, pages que le brouillon n'avait pas vues, doublons classés, pages orphelines, hypothèses, questions à poser, ce que la carte ne couvre pas. Ne publie rien sans son accord. Pour publier comme artefact : l'outil Artifact demande de charger le skill `artifact-design` avant de publier (fais-le, il se charge en une ligne), puis publie le fichier `.artefact.html` **tel quel** : il respecte déjà le contrat des artefacts (`<title>` d'abord, jetons de couleur clair et sombre, aucun script externe). Icône « map », titre = `meta.titre` (déjà dans le fichier), une phrase de description.

## Garde-fous

- **Lecture seule** : tu ne modifies pas le code du produit.
- **Aucune donnée réelle dans la carte** : pas de secret, d'e-mail, de numéro, de texte écrit par des utilisateurs ni d'adresse réelle. Ce qui identifie une donnée ou une personne est un modèle (`/livres/{id}`, `/merci-{code}.html`) ; l'adresse d'une page fixe d'un site public est publique et s'écrit telle quelle. Le contrôle cherche les e-mails, numéros et adresses web, les codes dans les adresses, et les mots de ta liste d'interdits.
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
| `scripts/` | `brouillon.py`, `verifier.py`, `construire.py`, `controler_html.py`, `contrastes.py` |
