# Inventaire d'une application Next.js

Valable pour l'App Router (`app/`) et le Pages Router (`pages/`). Les pages sont des fichiers : le brouillon en fait presque tout le travail.

## 0. Le premier jet

```
python3 <skill>/scripts/brouillon.py <racine du projet> -o inventaire.json
```

Il lit les `page.tsx` de `app/` (ou `src/app/`), les fichiers de `pages/`, ajoute `not-found.tsx` et `error.tsx` comme pages d'entrée (« page introuvable », « page d'erreur »), liste à part les adresses qui ne font que rediriger, compte les actions (un lien répété compte une fois, les composants dont le nom contient Button, Link, Lien ou Bouton comptent) et relève les adresses écrites entre guillemets dans le code de chaque page.

## 1. Ce qui est une page, et ce qui n'en est pas

| Fichier | Page ? |
|---|---|
| `page.tsx` | oui, une page par adresse ; `[id]` devient `{id}` (une page par modèle d'écran) ; `(groupe)` n'apparaît pas dans l'adresse ; `[...slug]` est un modèle |
| `not-found.tsx`, `error.tsx`, `global-error.tsx` | oui, ce sont des écrans (le brouillon les ajoute, en entrée) |
| `layout.tsx` | non : lis-le, il porte le menu et le pied de page communs |
| `route.ts` | non : une API, un flux, un fichier (`feed.xml`, `agenda.ics`) |
| `loading.tsx`, `middleware.ts` | non |
| une page qui ne fait que `redirect()` ou `permanentRedirect()` | non : une ancienne adresse. Le brouillon la met dans `redirections`, écartée de `pages`. Dis-le dans un constat si l'équipe doit le savoir |

Une page à adresse libre (`app/[slug]/page.tsx`, contenu écrit dans un outil de gestion) est **une page** « page éditoriale » : dis dans `note` d'où viennent ses contenus.

## 2. Les rôles

Les dossiers `admin`, `mon-espace`, `dashboard` et les gardes (`requireAdmin`, `requireUser`, `auth-guards`) dessinent les rôles. Une carte raconte un rôle : garde la visiteuse ou la membre dans la carte principale, et mets l'espace d'équipe dans un espace replié (`espaces`, `espace` sur l'étape). Les pages d'un espace ne comptent pas dans « N pages côté… » mais la carte les montre, repliées. Ne donne pas à l'étape le même nom qu'à l'espace.

## 3. Relier

- Le menu et le pied de page sont dans des composants (`Header`, `Footer`, `BottomNav`, `AccountMenu`) : lis-les une fois, dis-les dans `meta.perimetre`, mets leurs cibles sur l'accueil (ou sur la page d'arrivée de l'espace).
- Le brouillon ne voit que ce qu'il peut lire : `href={cond ? "/a" : "/b"}`, adresses fabriquées par une fonction, liens dans des composants importés. **Relis chaque lien** des pages qui sortent avec 0 ou 1 flèche.
- Beaucoup de projets Next ont des **pages d'une seule fonction** (« sous-page », un rayon par geste, un seul bouton principal) : une édition, ses ateliers, chaque atelier et ses 8 sous-pages. La carte en montre une centaine : c'est normal. Utilise `parent` pour les sous-pages, et mets les pastilles ou onglets d'une page de synthèse dans son `vers`.
- Les flèches « Retour » (fil d'Ariane, `LienRetour`) vont vers la page parente : ne les oublie pas.

## 4. Les fonctions

Une page Next dit souvent son rôle dans un commentaire d'en-tête et dans `metadata.title`. Prends-les comme matière, jamais telles quelles : elles parlent du code (« sous-page mono-fonction du hub d'édition »). La phrase de fonction se dit du côté de la personne (`methode/LISEZ-MOI.md`).

## 5. Les constats : ce qui est affiché, pas ce qui est écrit

Un `console.error("Ressources indisponibles (migration 051 ?)")` n'est pas un message vu par la personne. Avant d'écrire un constat, vérifie que le texte est affiché (dans le JSX, pas dans un journal).

## 6. Compter les actions

Sans lancer l'application, le brouillon donne un ordre de grandeur : écris `"environ N"` ou `"au moins N"` pour les pages où tu ne les as pas relues. Les formulaires qui passent par des composants maison, des listes répétées (`1 par ligne`), des menus ne se comptent bien qu'au rendu.

## 7. Écrire, contrôler, construire

Revenir à `SKILL.md`, étapes 3 à 8.
