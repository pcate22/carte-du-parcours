# Inventaire d'une application d'une seule page (React, Vue, Svelte, Angular)

Valable quand tous les écrans sont servis par un seul fichier HTML (`index.html`) et qu'un routeur, dans le navigateur, choisit l'écran d'après l'adresse. Les écrans sont des composants, pas des gabarits : le brouillon ne les voit pas, sauf React Router écrit en JSX (`<Route path=...>`) ou en objets (`{ path: "/x", element: ... }`).

## 0. Le premier jet

```
python3 <skill>/scripts/brouillon.py <racine du projet> -o inventaire.json
```

S'il écrit « ATTENTION : application d'une seule page », il n'a rien trouvé d'utile (en général 1 à 3 « pages » : l'index et des maquettes de `docs/`). Ne les garde pas : lis la table des écrans, ci-dessous.

## 1. Trouver la table des écrans

Il y en a une, en un seul endroit dans la plupart des projets. Cherche :

```
# React Router, Vue Router
grep -rnE "<Route|createBrowserRouter|createRouter|routes\s*[:=]" src
# routeur maison : ce qui lit l'adresse, puis choisit un écran
grep -rnE "location\.pathname|useLocation|pushState|ecranDe|screenFor" src
# un type qui liste les écrans, et le switch qui les rend
grep -rnE "case '[a-z-]+':" src | head
```

Une application à routeur maison a souvent un fichier d'adresses (une fonction par écran), un type `Ecran` ou `Screen`, et un fichier de routes avec un `switch (ecran.nom)`. La table qui range chaque écran dans son onglet (`PLACES`, `tabs`, `screens`) est la meilleure source : une ligne par écran.

- Une adresse avec un identifiant (`/carte/{pizza}`) est **une page par modèle d'écran**, pas une par valeur.
- Les adresses déplacées qui renvoient vers une nouvelle adresse (`deplacee`, `redirect`) ne sont pas des pages.

## 2. Les écrans qui ne sont pas des adresses

Un écran peut remplacer tous les autres sans changer l'adresse : saisie d'un code d'accès, connexion, « l'app doit se mettre à jour », première installation. Cherche dans le composant racine (`App.tsx`) les `return <Ecran... />` placés **avant** le routeur. Ce sont des pages : dis dans `adresse` quand elles s'affichent (« toute adresse, tant que l'accès n'est pas accordé »), marque-les `entree: true`.

## 3. Un écran, deux versions

Un interrupteur (nouveauté, essai A/B, réglage) peut faire afficher, à la même adresse, deux écrans différents. Ce sont **deux pages** et un groupe de doublons (`deux-chemins`) : « deux versions d'un même écran à maintenir ». Dis dans `note` à quelle condition chacune s'affiche. L'alerte « même adresse » du contrôle se tait dès que les deux sont dans un groupe.

## 4. Relier

Les routes disent où mène chaque bouton : cherche `naviguer(`, `navigate(`, `router.push(`, `<Link to=...>`, et les fonctions passées en propriétés (`ouvrirPizza={(id) => naviguer(adresses.produit(id))}`). Le retour (`useRetour(adresses.liste())`) donne la page parente. Une adresse construite par une fonction (`adresses.produit(id)`) se relit dans le fichier des adresses.

La **barre d'onglets** (ou le menu latéral) est le menu commun : dis-la une fois dans `meta.perimetre`, mets ses cibles sur la page d'arrivée, pas sur chaque écran. Elle n'est souvent présente que sur les écrans de liste : dis-le.

## 5. Les étapes d'une application à onglets

Une application de pilotage n'a pas de parcours dans le temps : les onglets sont ses rubriques. Prends les onglets comme étapes. Numérote ceux qui se suivent dans la barre (1, 2, 3…), laisse sans numéro l'aide, les réglages et les écrans d'accès. Écris-le comme une hypothèse (`meta.hypotheses`) : l'équipe a peut-être un autre découpage (par métier plutôt que par onglet).

## 6. Compter les actions

Le rendu est dans les composants et leurs sous-composants : un compte exact demande de lancer l'application avec **des données inventées** (jamais un vrai code d'accès ni des données de production). Sans cela, lis chaque écran et ses sous-composants (boutons, champs, choix, onglets, volets) et écris `"environ 8"` ou `"3 + 1 par pizza"`. Ne mets pas un chiffre précis que tu n'as pas compté : la carte affiche le texte tel quel.

## 7. Les doublons d'une application d'une seule page

Les gestes de `recettes/doublons.md` valent ici, avec trois habitudes du genre :

- **le même texte d'état écrit plusieurs fois** (« cette pizza n'existe plus », « cet ingrédient n'existe plus »…) : `etat-refait` ;
- **le même titre pour deux écrans** (deux « Quel ingrédient ? », deux « Ma carte ») : `deux-noms` ;
- **un composant partagé** par deux écrans (la même liste, le même formulaire) n'est pas un doublon ; deux écrans qui montrent le même composant à deux moments (première ouverture, puis plus tard) vont dans `non_doublons`, avec la raison.

## 8. Écrire, contrôler, construire

Revenir à `SKILL.md`, étapes 3 à 8.
