# Repérer les doublons d'écrans

Un **doublon** est un ensemble d'écrans qui permettent à la personne de faire **la même chose**. Ce n'est pas un défaut en soi : c'est une décision à prendre. Le travail est de les montrer avec leurs preuves, pas de les supprimer.

Ce qui n'est **pas** un doublon :

- un composant réutilisé tel quel dans deux écrans (c'est ce qu'on veut) ;
- deux fonctions voisines mais différentes (acheter et offrir) ;
- la version « équipe » et la version « utilisatrice » d'une même liste (deux rôles) ;
- les versions de langue d'une même page.

## Les quatre sortes

| `type` | En clair | Comment le repérer |
|---|---|---|
| `deux-chemins` | La **même fonction** est atteinte par deux chemins, ou par deux écrans. | Deux entrées de menu, deux boutons ou deux adresses qui mènent à des écrans de même fonction. Une même page servie par deux routes. |
| `meme-reglage` | Le **même réglage** se modifie sur deux écrans. | Le même champ, la même colonne ou la même clé écrits par deux formulaires. On le change ici, il n'a pas changé là. |
| `deux-noms` | **Deux libellés** pour la même chose (ou un libellé pour deux choses). | Trier tous les titres et boutons. Synonymes : « Mes réservations » et « Historique » ; « Valider », « Confirmer », « Continuer ». |
| `etat-refait` | Une **page d'état refaite** : vide, plein, erreur, attente, limite atteinte. | Lister toutes les pages d'état de toutes les fonctions, les comparer : texte, mise en page, bouton. Chacune a été refaite à son tour. |

## Les six gestes, dans l'ordre

1. **Trier les pages par objet.** Relire toutes les `fonction` et noter l'objet de chacune : date, adresse, régime, rappel, code, paiement, titre, format… Deux pages du même objet sont candidates.
2. **Comparer les champs.** Chercher les mêmes noms de champ dans les gabarits :
   ```
   grep -rhoE 'name="[a-z_]+"' <gabarits> | sort | uniq -c | sort -rn | head -30
   ```
   Un champ présent dans deux gabarits de pages différentes est un indice fort de `meme-reglage`.
3. **Comparer les noms.** Lister les `h1` ou `<title>` de chaque page, puis les libellés de boutons et de menu. Chercher les synonymes et les titres identiques :
   ```
   grep -rhoE '<h1[^>]*>[^<]+' <gabarits> | sed 's/<[^>]*>//' | sort | uniq -c | sort -rn
   ```
4. **Compter les chemins d'accès.** Une fonction importante atteinte depuis trois menus différents mérite un regard : est-ce le même écran, ou trois écrans ?
5. **Faire la grille des pages d'état.** Un tableau : une ligne par fonction, une colonne par état (vide, erreur, attente, limite, refus). Les cases remplies avec des mises en page différentes sont des candidats `etat-refait`. Mots à chercher dans le code : `empty`, `vide`, `erreur`, `attente`, `introuvable`, `complet`, `limite`, `expire`, `refus`.
6. **Relire les attentions de `scripts/verifier.py`** : il signale les pages de même adresse, de même nom ou de fonctions très proches qui ne sont pas dans un groupe.

## Tester un candidat

Deux questions, la réponse « oui » à l'une des deux confirme :

- *Si la personne fait la chose à l'écran A, retrouve-t-elle son choix à l'écran B ?* Si non : le réglage existe deux fois.
- *Pour changer une règle (un texte, un prix, un champ), faut-il modifier deux endroits ?* Si oui : le code porte deux fois la fonction.

## Écrire un groupe

```json
{
  "id": "regimes",
  "titre": "Dire ses régimes alimentaires",
  "type": "meme-reglage",
  "pages": ["regimes-resa", "compte-regimes"],
  "pourquoi": "Le régime se règle dans la réservation et dans le compte, sans lien entre les deux : on le redit à chaque atelier.",
  "piste": "préremplir la réservation avec le réglage du compte."
}
```

- `titre` : la fonction faite deux fois, avec un verbe (« Dire », « Choisir », « Voir »). Pas « Doublon n°3 ».
- `pourquoi` : ce qui est fait deux fois, avec **les noms des écrans** et ce qui les distingue. Une personne qui n'a pas lu le code doit comprendre.
- `piste` : une phrase au plus, qui ouvre une direction. Pas un ordre, pas un planning.
- Une page dans plusieurs groupes est normale : elle affichera « double ×2 ».

## Deux écrans, même adresse

Quand un interrupteur, un essai ou un réglage fait afficher deux écrans différents à la même adresse (une fiche en une page, ou une fiche puis une page de détail), ce sont deux pages. Mets-les dans un groupe `deux-chemins` : l'alerte « même adresse » se tait, et la carte montre qu'il y a deux versions à maintenir. Écris dans `note` de chacune à quelle condition elle s'affiche.

## Les pages de confirmation, de suppression, d'erreur

Une page « Supprimer X ? » par type d'objet (édition, atelier, compte…) est un `etat-refait` quand chacune a sa mise en page et son bouton. Sept pages de suppression qui n'ont ni le même composant ni la même page sont un bon candidat : un seul gabarit suffirait. Quand elles partagent déjà le même composant, ce sont des voisines : `non_doublons`.

## Classer les groupes par intérêt

Une équipe veut savoir par où commencer. Pour chaque groupe, écris à la fin du compte rendu ce qu'elle gagnerait à le supprimer, du plus au moins utile :

1. **ce qu'on change à deux endroits** : une saisie, un texte, un réglage qu'il faut refaire dans chaque écran (le plus utile : c'est là que ça diverge) ;
2. **le nombre de pages en moins** si on fusionne ;
3. **la confusion pour la personne** (un même nom pour deux choses, deux chemins pour la même fonction) ;
4. **ce qui est voulu** (les écrans d'un composant partagé, deux rôles, une décision documentée dans le code) : en dernier, avec la raison de l'avoir gardé.

## Zéro est un résultat

Sur un petit site ou un produit récent, il n'y a souvent aucun doublon : le dire est un résultat, pas un échec. Ne pas en fabriquer pour « remplir ». Deux pages voisines qu'on a examinées et écartées vont dans `non_doublons`, avec la raison, quand le contrôle les soupçonnait ; inutile de consigner celles qu'il n'a pas relevées (la carte n'affiche pas `non_doublons`, c'est une trace pour le contrôle).

## Les pages de confirmation

Deux pages « merci » pour deux actions différentes (s'inscrire, écrire) sont des **voisines**, pas des doublons. Elles deviennent une page d'état refaite (`etat-refait`) quand le même message, la même mise en page et le même bouton ont été refaits à une variable près : un seul composant « Confirmation » suffirait.

## Combien de doublons ?

Sur un produit qui a grandi sans carte, 15 à 30 % des pages touchées par un doublon est courant. Au-delà de 40 %, vérifier qu'on n'a pas confondu *voisin* et *doublon* : deux pages qui se ressemblent mais n'ont pas la même fonction ne vont pas dans un groupe.
