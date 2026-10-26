# Livret seulement consultable en ligne (Google Drive, téléchargement bloqué)

Le blocage du téléchargement est un choix du propriétaire du fichier : ne pas le contourner (pas d'extraction
des images de la visionneuse par JavaScript, pas de récupération par les rouages internes de Drive, pas de
confirmation de téléchargement forcée).

1. Chercher un PDF téléchargeable du même livret : site de l'éditeur ou de l'auteur, BoardGameGeek (« Files »),
   page du jeu sur une boutique ou un salon (Tokyo Game Market pour un jeu japonais, voir `source.md`).
2. Sinon, le dire à l'utilisateur et lui proposer :
   - de demander le PDF au propriétaire (auteur, éditeur) ;
   - ou de faire lui-même des captures d'écran des pages, à la meilleure résolution possible (zoom de la
     visionneuse, une capture par page), et de les déposer dans `A traduire/`.
3. Captures reçues : les assembler en PDF dans `A traduire/` (une page par image, à la taille de l'image) :
   `python -X utf8 -c "import pymupdf,sys; d=pymupdf.open(); [d.new_page(width=p.width,height=p.height).insert_image(pymupdf.Rect(0,0,p.width,p.height),pixmap=p) for p in map(pymupdf.Pixmap,sys.argv[2:])]; d.save(sys.argv[1])" sortie.pdf p1.png p2.png`
   puis `preparer.py` comme d'habitude : le livret est traité comme **scanné** (`scan.md`).
4. Noter la source (lien, nom du fichier, captures de l'utilisateur) dans `NOTES.md`.
