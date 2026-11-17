# La méthode de la carte du parcours

Ce texte explique pourquoi la carte est faite ainsi, et ce que chaque règle protège. Le déroulé pas à pas est dans `SKILL.md`.

## En trois lignes

1. On compte **toutes** les pages, y compris les erreurs, les attentes et les pages que personne ne trouve.
2. On dit à quoi sert chaque page **avec les mots de la personne**, en une phrase.
3. On montre ce qui est fait **deux fois**. On ne tranche pas : la décision est celle de l'équipe.

## Ce qu'il faut demander avant de commencer

Une carte sans cadre devient vite un inventaire sans fin. Quatre réponses suffisent, à demander une par une :

| Question | Pourquoi | Si la personne ne sait pas |
|---|---|---|
| **Périmètre** : quel produit, quelle partie, quelle version du code ? | La carte n'est vraie que pour un morceau de produit à un moment. | Proposer le dépôt lu et la branche courante. |
| **Rôle** : qui est « je » ? | Les phrases de fonction changent selon qui parle. Un seul rôle par carte lisible. | Le rôle qui paie ou qui utilise le plus. L'autre rôle va dans un espace replié. |
| **Étapes officielles** : comment l'équipe découpe-t-elle le parcours ? | Les étapes sont l'ossature du ruban. Les inventer sans l'équipe fabrique une carte que personne ne reconnaît. | Proposer 4 à 7 étapes d'après le chemin réel, les faire valider, et le dire dans `meta.perimetre`. |
| **Date de l'état** | La carte vieillit dès le prochain commit. | La date du dernier commit lu. |

Demander aussi : « Y a-t-il des mots à ne jamais mettre dans la carte ? » (noms de clientes, de personnes, de contenus). Ils vont dans un fichier lu par `verifier.py --interdits`.

## La phrase de fonction

> **Quand** [situation de la personne], **je veux** [ce qu'elle veut faire], **pour** [ce qu'elle y gagne].

Règles :

- **Toujours du côté de la personne.** Le « je » est celle qui utilise le produit. La phrase dit ce qu'elle veut, pas ce que la page contient ni comment le code est fait.
- **Jamais de nom de fonction, de route, de table, de composant, ni de jargon** (« endpoint », « gabarit », « session », « API »). Si le mot n'est pas dans la bouche d'une utilisatrice, il n'est pas dans la phrase.
- **Une seule phrase**, qui finit par un point. Si deux phrases sont nécessaires, la page fait sans doute deux choses : deux pages, ou un doublon.
- **Le « pour » est le but, pas la conséquence technique.** « …pour garantir ma place » et non « …pour enregistrer la réservation ».
- **Sans accord quand c'est possible.** « Quand j'ai réservé » plutôt que « Quand je suis inscrit(e) ».
- Une page d'erreur ou d'attente a une fonction aussi : « Quand le paiement est refusé, je veux comprendre pourquoi et réessayer, pour ne pas perdre ma réservation. »

| À écrire | Pourquoi |
|---|---|
| Quand je veux réserver, je veux voir les dates avec les places qui restent, pour choisir celle qui me va. | La situation, l'action, le but. |
| ~~Affiche la liste des créneaux depuis la table `slots`.~~ | Parle du code. |
| ~~Page de paiement.~~ | C'est un nom, pas une fonction. |
| ~~Quand l'utilisateur est authentifié, le système redirige vers le tableau de bord.~~ | Le système est le sujet, pas la personne. |

Si la phrase est impossible à écrire, c'est une information : la page n'a pas de but clair. Écrire la phrase que la page *devrait* porter dans `fonction`, et ce qui cloche dans `note`.

## Le nombre d'actions

Une **action** est ce que la personne peut faire sur la page : un lien, un bouton, un champ, un choix dans une liste, un onglet. On compte ce qui se trouve **dans la page**, sans le menu ni le pied de page communs (ils sont dits une fois dans `meta.perimetre`).

- Une liste de dix lignes identiques compte comme une ligne : « 1 + 1 par atelier ». Écrire alors la forme en toutes lettres : `"1 + 2 par atelier"`.
- Un groupe de cases à cocher compte pour autant d'actions que de cases.
- Une page d'attente compte 0 si la personne ne peut rien faire.

Le **menu et le pied de page** ne comptent dans les actions d'aucune page, l'accueil compris. Leurs cibles figurent dans le `vers` de l'accueil, pour que les pages qu'on ne trouve que par le pied de page ne paraissent pas orphelines.

Pourquoi compter : une page à 22 actions fait trop de choses, une page à 0 est une impasse. Le chiffre aide à comparer deux écrans qui font la même chose. Le brouillon donne un ordre de grandeur, à recompter à la main sur les pages importantes.

## Les constats

Un **constat** est un défaut observé qui n'est ni un doublon ni une page orpheline : une impasse, un formulaire dont on ne voit pas où part le message, une information absente, une page sans suite. Il s'écrit du côté de la personne, avec les noms des écrans, et renvoie aux pages concernées. Huit au plus. Ils sont dans la fiche d'accueil de la carte.

## Une carte pour l'ordinateur d'abord

La carte sert à **lire et discuter un parcours à plusieurs**, le plus souvent sur un écran d'ordinateur ou projetée. Elle est donc pensée pour environ 1 440 x 760 pixels :

- le **ruban** des étapes en haut, toujours visible, cliquable ;
- les pages en **cartes par étape**, à gauche ;
- la **fiche** de la page choisie à droite, toujours visible sans défilement de la page ;
- les **flèches** du schéma relient la page choisie à ses voisines.

Sur petit écran la carte ne casse pas : une colonne de cartes, et la fiche devient une feuille plein écran avec un bouton « Retour ». C'est utilisable, pas optimisé : ce n'est pas le cas d'usage.

## Pages, sous-pages, entrées, orphelines, absentes

| Cas | Comment le dire | Ce que la carte montre |
|---|---|---|
| Une sous-page (écran ouvert depuis un autre, un réglage de détail) | `parent` | « sous-page de… » sur la carte, liste « Sous-pages » dans la fiche du parent |
| Une page où l'on arrive de l'extérieur (adresse, menu, e-mail, retour d'un prestataire) | `entree: true` | « Page d'entrée » dans la fiche |
| Une page que rien ne relie | rien : c'est calculé | badge **orpheline**, cadre rouge dans la fiche |
| Une page décidée, pas construite | `absente: true` | badge « à construire », bordure en pointillé |
| Ce qui cloche dans une page | `note` | encadré dans la fiche |

Ne pas « réparer » la carte : une page orpheline qui existe vraiment doit apparaître orpheline.

## Les contrôles

La carte n'est livrée qu'après ces sept contrôles. Les quatre premiers sont faits par `scripts/verifier.py`, le cinquième par le navigateur, les deux derniers à la main.

1. **Chaque page a une fonction** au format « Quand je…, je veux…, pour… », sans jargon repérable.
2. **Chaque lien mène à une fiche qui existe** : `vers`, `parent` et les groupes de doublons nomment tous des pages de l'inventaire.
3. **Aucun doublon non signalé** : le script cherche les pages de même adresse, de même nom ou de fonctions très proches qui ne sont pas dans un groupe. Chaque alerte est tranchée : soit un groupe dans `doublons`, soit une entrée dans `non_doublons` avec la raison de ne pas en faire un.
4. **Aucune donnée réelle** : e-mails, numéros, adresses web, et mots de la liste d'interdits.
5. **La carte s'ouvre sans erreur de console** et chaque clic fait ce qu'il dit (ruban, recherche, filtre, fiche, Retour, thème).
6. **Les pages importantes sont comptées à la main** : actions et liens relus sur au moins une page par étape.
7. **Le périmètre et la date sont dits** en haut de la carte, et ce qu'elle ne couvre pas est dans le compte rendu.

## Accessibilité (RGAA)

Le gabarit est écrit pour que la carte soit lisible au clavier, au lecteur d'écran et par une personne qui voit mal. Ce qu'il fait, et comment le vérifier (les numéros sont ceux du RGAA 4.1) :

| Point | Ce que fait le gabarit | Vérification |
|---|---|---|
| **Clavier** (7.3) | Tout est un vrai bouton ou un vrai lien. Tabulation dans l'ordre visuel. Échap ferme la fiche. Le ruban amène le focus sur le titre de l'étape. Un lien d'évitement mène au schéma. | Tout parcourir sans souris. |
| **Focus visible** (10.7) | Anneau de 3 px, d'un contraste d'au moins 3 pour 1 sur la page et sur les cartes. | Tabulation, en clair et en sombre. |
| **Contrastes mesurés** (3.2, 3.3) | Texte à 4,5 pour 1 au moins, bordures et anneaux à 3 pour 1, en **clair et en sombre**. Les deux blocs sombres sont identiques. | `python3 scripts/contrastes.py` : tableau, sortie en erreur si une paire échoue. |
| **Jamais par la seule couleur** (3.1) | Un doublon a un badge « double » et une barre épaisse ; une page où l'on peut aller, une étiquette « vers » et un trait plein ; d'où l'on vient, une étiquette « d'où » et un trait en pointillé ; une orpheline, un badge « orpheline ». | Passer la page en niveaux de gris : tout reste lisible. |
| **Lecteur d'écran** (7.1) | Boutons nommés, `aria-pressed` sur la carte choisie et sur le filtre, fiche annoncée comme boîte de dialogue sur petit écran, résultat du filtre annoncé (`role="status"`), flèches masquées (`aria-hidden`), `<noscript>`. | axe, puis un essai au lecteur d'écran. |
| **Langue, titres** (8.3, 9.1) | `lang="fr"` sur la page, un `h1`, un `h2` par étape, un `h2` par fiche. | axe. |
| **Zoom et petit écran** (10.4) | Rien ne dépasse à 375 px de large ; texte en unités relatives. | Zoom du navigateur à 200 %. |
| **Mouvement** | Défilement doux seulement si la personne ne demande pas moins de mouvement. | Réglage « réduire les animations » du système. |

Avec axe : zéro violation et zéro contrôle incomplet au repos, en clair et en sombre. Quand une page est choisie, `color-contrast` peut ressortir « incomplet » parce que les flèches passent au-dessus des cartes. Pour le mesurer, masquer le calque (`.liens-svg { display: none }`) puis relancer axe, ou faire confiance à `contrastes.py`, qui mesure les couleurs elles-mêmes.

Si vous changez les couleurs : modifier les jetons de `:root` dans les **trois** blocs (clair, sombre automatique, sombre choisi), puis relancer `contrastes.py`.

## Ce que la carte ne dit pas

- Ce qui se passe **dans** une page (états, cas particuliers) : une page, une phrase.
- Le temps, le volume, les clics des vraies personnes : c'est une carte du *possible*, pas du *vécu*.
- Les parcours qui passent par un autre outil (e-mail, prestataire de paiement) : l'entrée de retour est dite, pas le détail de l'autre outil.
