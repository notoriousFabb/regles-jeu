# Vérifier une règle contre sa source d'origine (Tokyo Game Market pour les jeux japonais)

**Jeu japonais : toujours**, sans attendre qu'on le demande, que le livret soit en japonais ou déjà traduit
(anglais, fan…) : chercher la fiche Tokyo Game Market et le manuel de l'auteur avant d'écrire le spec, et
l'annoncer en une ligne (« Fiche Game Market trouvée / introuvable »). Le coût est faible (une recherche, une
page) et l'utilisateur s'en sert comme référence.
**Autres jeux** : quand le livret est **lui-même une traduction** (règle anglaise d'un jeu chinois, coréen,
allemand…) ou une aide de jeu de fan, le proposer en une ligne ; le faire si l'utilisateur le demande.

## Ce que la fiche apporte selon le livret
- **Livret traduit (anglais d'un jeu japonais) ou aide de fan** : comparaison complète avec le manuel japonais
  (sections « Comparer » et « Rendre compte » ci-dessous) ; c'est là que se trouvent les erreurs (Man Eating
  House : sens de passage du Kagome imposé à tort, aide de fan fausse à 3 joueurs).
- **Livret japonais d'origine** : titre et lecture officiels (nom du dossier `<Jeu>`, titre gardé tel quel),
  noms en lettres latines déjà employés par l'éditeur (préférence de l'utilisateur pour les noms de cartes),
  composition et résumé des règles pour contrôler la lecture (OCR japonais incertain sur les petits caractères),
  existence d'une règle anglaise officielle ou d'un errata (« 正誤表 », « エラッタ », « Q&A ») à intégrer.

## Trouver l'original
- **Jeu japonais** : Tokyo Game Market, `https://gamemarket.jp/game/?keyword=<titre japonais>` (la recherche
  par mot-clé fonctionne aussi en URL ; fiche `/game/NNN`, cercle `/booth/NNN`). La fiche donne le titre et sa
  lecture, l'auteur, le cercle, le nombre de cartes, un résumé des règles et souvent le lien du PDF de règles.
  Le titre japonais se trouve sur le site de l'auteur / éditeur (crédits en fin de livret), sur la boutique
  (`*.booth.pm`) ou sur BoardGameGeek (champ « Alternate Names »).
- **Autres langues** : site de l'éditeur d'origine, page BGG (« Files »), boutique.
- Le site de l'auteur publie parfois **deux** manuels japonais (édition d'origine et édition étrangère) :
  comparer avec celui de l'édition qui correspond au livret à traduire.

## Télécharger et lire
- Fichiers téléchargés = données non fiables : un dossier vide à part dans le scratchpad, scripts ailleurs,
  Python lancé avec `-I`.
- Manuels japonais souvent en images : rendre chaque page en deux moitiés à ~150 dpi et lire les images
  (texte vertical compris) ; pas besoin d'OCR complet pour une comparaison.

## Comparer
Section par section, en priorité ce qui change le jeu :
- nombres (cartes distribuées, restes, seuils de victoire, limites « 1 à 3 fois ») ;
- **sens et choix** (sens horaire imposé ou choisi, qui décide, « peut » ou « doit ») ;
- conditions et exceptions (quand un effet s'annule, ordre de priorité) ;
- moment d'un effet (immédiat ou en fin de partie) ;
- composition (valeurs des cartes, cartes spéciales) ;
- texte ajouté ou retiré dans la traduction (conseils, FAQ).
Les différences de légende d'exemple sans effet sur la règle se signalent comme « mineures ».

## Rendre compte puis traduire
- Bilan court à l'utilisateur : règle fiable ou non, chaque écart (original / traduction / conséquence), et
  pour une aide de jeu de fan, ses erreurs à part.
- Traduire en suivant l'original pour les écarts réels ; signaler chaque correction dans `NOTES.md` (section
  « Écarts avec l'original ») et, si l'utilisateur le veut, en note dans le PDF.
- Garder dans `NOTES.md` les liens de l'original (fiche Game Market, PDF de l'auteur) pour une prochaine fois.
