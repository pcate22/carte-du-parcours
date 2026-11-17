# Inventaire d'une application mobile

Un **écran** est une page. La navigation de l'application (pile, onglets, feuilles) joue le rôle des liens. La carte, elle, reste une carte pour ordinateur : on la lit sur grand écran même si le produit est mobile.

## 0. Le premier jet

```
python3 <skill>/scripts/brouillon.py <racine du projet> -o inventaire.json
```

Il repère les écrans de React Navigation (`<Stack.Screen name=...>`), de Flutter (`GoRoute(path: ...)`), de Jetpack Compose (`composable("...")`) et de SwiftUI (`struct XxxView: View`). Il ne trouve ni les liens entre écrans ni les actions : à relever à la main (§ 2 et 3). Il ne voit ni les storyboards, ni les graphes de navigation XML.

## 1. Lister les écrans

```
# React Native (Expo Router : les fichiers du dossier app/ sont les écrans)
grep -rn "Screen name=" src app

# Flutter
grep -rnE "GoRoute\(|routes:|onGenerateRoute|MaterialPageRoute" lib

# SwiftUI
grep -rnE "NavigationLink|\.sheet\(|\.fullScreenCover\(|TabView|NavigationStack" .

# Jetpack Compose
grep -rnE "composable\(|NavHost|navController\.navigate" app/src
```

- **UIKit** : dans `Main.storyboard`, chaque `<viewController` est un écran et chaque `<segue destination=` un lien.
- **Android à vues XML** : `res/navigation/*.xml` (`<fragment`, `<action app:destination=`) et les `<activity` de `AndroidManifest.xml`.
- **React Native** : les liens profonds sont dans la configuration `linking`.

Les **feuilles du bas, fenêtres modales, onglets** sont des écrans : des sous-pages (`parent`) de l'écran qui les ouvre. Les **boîtes de dialogue système** (permissions, partage, sélecteur de photo) ne sont pas des écrans du produit : les citer dans `note` de l'écran qui les déclenche.

## 2. Relier

Chercher les appels de navigation : `navigation.navigate('X')`, `context.go('/x')`, `Navigator.pushNamed`, `NavigationLink(destination:`, `navController.navigate("x")`, les actions des graphes XML. Chaque appel est une flèche de l'écran qui le contient vers l'écran cible.

**Entrées** (`entree: true`) : l'écran de lancement, mais aussi tout ce qui ouvre l'application ailleurs : **liens profonds** (config `linking`, `<intent-filter>`, `applinks`), **notifications**, **widgets**, **raccourcis**. Les chercher : `grep -rnE "intent-filter|applinks|scheme" .`.

## 3. Compter les actions

Boutons, champs, éléments de liste, **gestes qui portent une fonction** (balayer pour supprimer, tirer pour actualiser), onglets. Une liste compte pour une ligne.

## 4. Étapes et rôles

Les onglets du bas donnent souvent l'ossature (Accueil, Recherche, Panier, Profil) mais ce ne sont pas des étapes : une étape est un moment du parcours (Découvrir, Réserver, Payer). Proposer les étapes d'après le chemin et les faire valider. Un seul rôle par carte.

## 5. Spécificités mobiles à ne pas rater

- **Premier lancement** : présentation, demande de permissions, connexion. Ce sont des écrans.
- **États hors ligne**, écrans de chargement, écrans de mise à jour obligatoire : à compter comme pages d'attente et d'erreur.
- **iOS et Android** : si les écrans diffèrent, le dire dans `note` plutôt que de faire deux cartes.

## 6. Écrire, contrôler, construire

Revenir à `SKILL.md`, étapes 3 à 7.
