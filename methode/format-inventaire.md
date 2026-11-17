# Format de `inventaire.json`

Un seul fichier JSON, en UTF-8. La carte se construit à partir de lui avec `scripts/construire.py`. Les champs inconnus sont ignorés. Le brouillon en ajoute, comme aides de travail à supprimer : `source`, `gabarit`, `liens_non_resolus` sur les pages, et à la racine `liens_communs` (pages citées par le menu ou le pied de page), `redirections` (adresses qui ne font que rediriger : ce ne sont pas des pages) et `liens_par_ressemblance` (liens résolus sans règle de réécriture lue : à vérifier).

Modèle de départ : `modele/inventaire-vide.json`. Exemple complet : `exemple/inventaire-exemple.json`.

## `meta` : la carte elle-même

| Champ | Obligatoire | Rôle |
|---|---|---|
| `titre` | oui | Titre de la page et nom de l'artefact. Deux à quatre mots, un nom plutôt qu'une phrase. |
| `produit` | non | Nom du produit, utilisé dans le texte d'introduction. |
| `role` | oui | Qui est « je », au pluriel : « clientes », « participants ». La carte écrit « 28 pages côté participants ». |
| `etat_au` | oui | Date de l'état, `AAAA-MM-JJ`. Affichée : « État au 17 novembre 2026. » |
| `perimetre` | oui | Une ou deux phrases : ce que la carte couvre, ce qu'elle laisse de côté, ce que le menu commun contient. |
| `introduction` | non | Texte sous le titre. Par défaut : une phrase générique avec `produit` et `role`. |
| `pour_commencer` | non | Identifiants de 1 à 3 pages proposées dans la fiche d'accueil. Par défaut : les premières pages en doublon. |
| `hypotheses` | non | Liste de phrases courtes : ce que tu as choisi faute de pouvoir demander (étapes proposées, version du code lue, ce qui n'est pas compté). Affichées dans la fiche d'accueil, sous le périmètre : une carte construite sans l'équipe doit dire qu'elle est à valider. |

## `etapes` : les étapes du parcours, dans l'ordre

| Champ | Obligatoire | Rôle |
|---|---|---|
| `id` | oui | Identifiant court, en minuscules. |
| `numero` | non | « 1 », « 2 »… Une étape **sans numéro** est une étape « à tout moment » (compte, aide, erreurs) : bordure en pointillé dans le ruban. |
| `nom` | oui | Titre de l'étape. |
| `court` | non | Nom court pour le ruban. |
| `sous_titre` | non | Ce que l'étape contient, en quelques mots. |
| `espace` | non | Identifiant d'un espace replié (voir `espaces`). Les pages de cette étape sont dans l'espace, pas dans le schéma principal. |

## `espaces` : les parties repliées (liste, souvent vide)

`id`, `nom` (titre du bloc replié), `note` (une précision à côté du titre, par exemple « réservé à l'équipe, replié »). Sert à un autre rôle : admin, animateur, support. Les pages d'un espace ne comptent pas dans « N pages côté… ».

## `pages` : une entrée par page ou par écran

| Champ | Obligatoire | Rôle |
|---|---|---|
| `id` | oui | Minuscules, chiffres, tirets. Sert à relier les pages et à l'adresse de la carte (`#p-<id>`). |
| `nom` | oui | Le nom de l'écran, tel que la personne le lit. Quand le titre dépend des données (le nom d'une plante, d'une pizza), `nom` dit le modèle d'écran : « Fiche d'une plante ». |
| `etape` | oui | Identifiant d'une étape. |
| `fonction` | oui | `Quand [situation], je veux [action], pour [but].` Une phrase, qui finit par un point. |
| `adresse` | conseillé | Route, fichier ou nom d'écran. Ce qui identifie une donnée ou une personne s'écrit **en modèle** (`/ateliers/{atelier}`, `/merci-{code}.html`), jamais une valeur réelle. L'adresse d'une page fixe d'un site public (`/talks/mon-talk`) est publique : écris-la telle quelle. |
| `actions` | conseillé | Nombre d'actions sur la page, ou une fourchette : `"6"`, `"4 à 6"`, `"1 + 2 par atelier"`. Un compte non vérifié à l'écran s'écrit tel quel : `"environ 8"`, `"au moins 5"`. Ne mets pas un chiffre précis que tu n'as pas compté. |
| `vers` | non | Identifiants des pages où l'on peut aller depuis celle-ci. |
| `parent` | non | Identifiant de la page dont celle-ci est une sous-page. Le lien parent vers sous-page est ajouté tout seul. |
| `entree` | non | `true` si l'on arrive sur cette page sans être passé par une autre page de la carte : adresse tapée ou donnée, lien d'un e-mail ou d'un autre site, moteur de recherche, erreur 404. Le menu commun ne fait pas des autres pages des entrées : c'est l'accueil qui porte ses cibles. |
| `absente` | non | `true` pour une page décidée et pas encore construite : bordure en pointillé, badge « à construire ». |
| `note` | non | Une remarque : ce qui cloche, ce qui manque, ce que le code fait en vrai. |

**Ce que la carte calcule** (ne l'écrivez pas) :

- les **pages précédentes** : toutes les pages dont `vers` ou `parent` mène ici ;
- les **pages orphelines** : aucune page précédente, pas `entree`, pas `absente` ;
- le **repère de doublon** de chaque page, d'après `doublons`.

## `doublons` : les groupes de pages qui font la même chose

| Champ | Obligatoire | Rôle |
|---|---|---|
| `id` | oui | Identifiant du groupe. |
| `titre` | oui | La fonction faite deux fois, en peu de mots : « Dire ses régimes alimentaires ». |
| `type` | conseillé | `deux-chemins`, `meme-reglage`, `deux-noms` ou `etat-refait` (voir `recettes/doublons.md`). |
| `pages` | oui | Deux identifiants de page ou plus. |
| `pourquoi` | oui | Ce qui est fait deux fois, en une ou deux phrases, avec les mots de l'écran. |
| `piste` | non | Ce que l'équipe pourrait faire. Une piste, pas une décision. |

Une page peut être dans plusieurs groupes : sa carte affiche « double ×2 ».

## `constats` : ce qui ne va pas, en dehors des doublons (liste, facultative)

Les défauts qui ne sont ni un doublon ni une page orpheline : une impasse, un formulaire sans destination visible, une information absente, une étape qui bloque. Ils s'affichent dans la fiche d'accueil de la carte, chacun avec ses pages cliquables. Huit au plus : au-delà, plus personne ne les lit.

| Champ | Obligatoire | Rôle |
|---|---|---|
| `titre` | oui | Le constat, en une phrase courte. |
| `texte` | oui | Ce qui se passe, avec les noms des écrans, du côté de la personne. |
| `pages` | non | Identifiants des pages concernées. |

## `non_doublons` : les paires examinées et écartées (liste, facultative)

Le contrôle soupçonne parfois un doublon (même adresse, même nom, fonctions très proches). Quand vous avez regardé et que ce sont bien deux fonctions différentes, notez-le : l'alerte ne revient plus.

| Champ | Obligatoire | Rôle |
|---|---|---|
| `pages` | oui | Exactement deux identifiants de page. |
| `raison` | oui | Pourquoi ce n'est pas deux fois la même chose : « ajouter un article au panier, et non relire le panier ». |
