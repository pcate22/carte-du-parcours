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
