# Résultats des essais du skill

Deux essais, le 17 novembre 2026, chacun par un agent qui ne connaissait pas le skill, avec pour seule consigne de le lire et de le suivre sans poser de question (cas `carte-appli-flask` et `carte-site-statique`). Pas de navigateur disponible dans ces essais : le rendu a été vérifié à part, sur l'exemple.

| Cas | Pages trouvées | Orpheline repérée | Doublon | Fausse alerte évitée | Livrables | Durée |
|---|---|---|---|---|---|---|
| Appli Flask (11 pages avec la 404) | 11 sur 11 | oui (`conseils-arrosage`) | oui : livraison de la commande et adresse du compte, même réglage | | inventaire, carte, fichier artefact | environ 3 min |
| Site statique (12 pages) | 12 sur 12 | oui (`galerie`) | aucun, à raison | inscription et contact non déclarés doublons | inventaire, carte, fichier artefact | environ 3 min |

Les sept énoncés de chaque cas (`graders/`) sont tenus dans les deux essais. Les deux agents ont dit leurs hypothèses (étapes, périmètre, date) et que le rendu n'avait pas été ouvert dans un navigateur.

## Ce que les essais ont fait corriger

- le contrôle plantait si le fichier de mots interdits n'existait pas : il l'ignore désormais ;
- une alerte de doublon examinée et écartée revenait à chaque contrôle : `non_doublons` la consigne ;
- les commandes supposaient d'être dans le dossier du skill : elles utilisent `$SKILL` ;
- le brouillon laissait les adresses à la syntaxe du code (`<int:id>`) et retirait `.html` aux pages statiques : corrigé ; il lit aussi les menus des gabarits de base et compte les actions sans le menu ;
- la règle du menu commun (cibles dans le `vers` de l'accueil, hors du compte d'actions) n'était écrite nulle part : écrite ;
- une flèche suit la redirection d'un formulaire vers la page vue ensuite : écrit dans la recette ;
- rien ne permettait de dire « ce qui ne va pas » hors doublons et orphelines : `constats` ;
- le skill ne disait pas quoi faire sans navigateur : `controler_html.py` contrôle les fichiers produits, et le compte rendu doit dire que le rendu n'est pas vérifié ;
- « zéro doublon » est un résultat valable, et deux pages de confirmation voisines ne sont pas un doublon : écrit dans `recettes/doublons.md` ;
- publier comme artefact demande de charger `artifact-design` : écrit.

Ces corrections n'ont pas été rejouées par un nouvel agent : les deux inventaires produits passent le contrôle et se construisent avec les scripts corrigés.

## Trois essais sur des projets réels (17 novembre 2026)

Le skill a été suivi tel quel, un site après l'autre, par la même personne qui ne pouvait pas poser de question. Les projets ne sont pas nommés ici (ils sont privés) ; les cartes, les inventaires et le journal des problèmes sont dans `essais/` (hors dépôt).

| Projet | Pages | Ajoutées à la main (que le brouillon n'avait pas) | Groupes de doublons (pages) | Orphelines | Minutes | Problèmes du skill |
|---|---|---|---|---|---|---|
| Site vitrine : générateur Python maison, 4 scripts PHP, adresses réécrites | 26 | 0 (26 sur 26 trouvées, mais 25 liens « non résolus » et des comptes d'actions faux) | 2 (4) | 1, voulue | 8, dont 2 d'attente de charge machine | 11 |
| Application React à routeur maison (écrans choisis par du code) | 40 | 40 (le brouillon n'a rien vu : 3 « pages » fausses, dont 2 maquettes) | 4 (12) | 0 | 5 | 7 |
| Plateforme Next.js, 3 rôles (App Router) | 119 | 2 (page introuvable, page d'erreur ; 5 fausses pages écartées : 4 redirections, 1 maquette) | 5 (17) | 0 | 7 | 10 |

Minutes à l'horloge de la machine, de la première lecture à la carte publiée. Le temps va à l'écriture des phrases de fonction et à la relecture des liens, pas au brouillon.

### Ce que ces essais ont fait corriger

- le brouillon écarte les adresses qui ne font que rediriger (Next : `redirect`, `permanentRedirect`), ajoute `not-found` et `error` comme pages d'entrée, lit React Router, et dit quand l'application est d'une seule page et qu'il n'a rien vu ;
- le brouillon compte un lien répété une fois, ignore un champ piège invisible (`tabindex="-1"`), reconnaît les composants dont le nom contient Button, Link, Lien ou Bouton, et lit les adresses écrites entre guillemets dans le code React (liens conditionnels, tableaux de menus) : sur la plateforme Next, les pages sans aucune flèche passent de 53 à 10, et la somme des actions de 73 à 231 ; sur le site vitrine, le brouillon retrouve 108 des 110 liens relevés à la main (83 avant) ;
- il résout par ressemblance de nom les liens que des règles de réécriture d'adresses rendent introuvables (`/talks/x` pour `talk-x.html`) et les dit, et il suit un formulaire vers un script PHP pour y relever les pages citées ;
- ses identifiants ne se télescopent plus (`speakeuses` et `speakeuses-detail` au lieu de `speakeuses` et `speakeuses-2`, `page-slug` au lieu de `accueil` pour une adresse libre) ; une adresse fixe passe avant `/{slug}` quand il relie ;
- `verifier.py` ne refuse plus « feuille de route », et signale un code dans l'identifiant ou l'adresse (un lien privé reçu par e-mail serait sinon publié dans la carte) ;
- la carte : le compteur de « Seulement les doublons » compte les pages de l'espace replié comme le message qui l'annonce, le filtre ouvre l'espace replié, la fiche d'accueil dit qu'un espace replié existe, `meta.hypotheses` s'y affiche (« à valider ») ;
- recettes ajoutées : Next.js, application d'une seule page, site statique avec générateur maison / scripts PHP / adresses réécrites / pages à lien secret / page cachée / sorties vers un autre outil ; `recettes/doublons.md` : deux écrans à la même adresse, pages de suppression, classement des groupes ; `SKILL.md` : comparer les copies d'un projet avant de lire, hypothèses, constat = fait affiché, serveur local pour regarder la carte ;
- vérifications automatiques de ces cas dans `evals/test_scripts.py` (`python3 evals/test_scripts.py`).

### Ce qui reste non résolu

- le nombre d'actions d'une page ne se compte bien qu'au rendu ; sans lancer l'application, la carte affiche « environ N » ou « au moins N » ;
- les écrans d'un routeur maison se trouvent à la main (la recette dit où chercher) ;
- les sorties vers un autre outil (agenda en ligne, paiement) ne sont pas des pages : la carte ne montre pas cette partie du parcours ;
- écrire une centaine de phrases de fonction reste l'essentiel du temps ; le brouillon pourrait recopier le commentaire d'en-tête des pages comme indice.

### Rejeu des deux cas d'essai avec le skill corrigé

Chaque cas est rejoué par un agent neuf qui lit `SKILL.md` du dossier corrigé et le suit sans poser de question (aucune publication, aucun navigateur).

| Cas | Énoncés tenus | Pages | Orpheline repérée | Doublon | Durée de l'agent |
|---|---|---|---|---|---|
| Appli Flask | 7 sur 7 | 11 sur 11 avec la 404 | oui (`conseils-arrosage`) | oui (livraison de la commande et adresse du compte, même réglage) | 3 min 18 s |
| Site statique | 7 sur 7 | 12 sur 12 | oui (`galerie`) | aucun, à raison (inscription et contact non déclarés doublons) | environ 3 min |

Chaque rejeu a écrit ses hypothèses (affichées dans la carte), dit que le rendu n'a pas été ouvert dans un navigateur et n'a rien publié. Les rejeux ont aussi fait écrire ceci (tiré de leurs retours) : une page d'entrée n'est pas une page du menu commun ; le lien « Accueil » du menu n'est pas une flèche de l'accueil ; sans dépôt git, la date du jour ; sans pouvoir lancer le produit, compter dans le code et le dire ; `nom` d'une page à titre variable dit le modèle (« Fiche d'une plante ») ; un écran qui manque est un constat, pas une page `absente` ; le message du contrôle sur une orpheline ne pousse plus à ajouter `entree` ; l'accueil s'écrit `/` ; une liste déroulante compte pour 1 ; inutile de consigner dans `non_doublons` une paire que le contrôle ne soupçonnait pas.
