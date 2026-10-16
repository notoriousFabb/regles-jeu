# Livret seulement consultable en ligne (Google Drive, téléchargement bloqué)

Essayer d'abord un PDF téléchargeable (site de l'éditeur, BoardGameGeek « Files »). Sinon, avec l'accord de
l'utilisateur, récupérer les pages en images : le résultat est un livret **scanné** (`scan.md`). Méthode testée
en 2026 ; elle dépend de détails internes de Drive qui peuvent changer.

1. Ouvrir le lien dans Chrome (outils navigateur), attendre l'affichage des pages.
2. Dans la page (JavaScript) : l'image d'une page est `drive.google.com/viewer/img?…&page=N&w=…`
   (source d'un `<img>` de la visionneuse). Changer `page` (0, 1…) et `w` (largeur en pixels, 2400 suffit) ;
   `fetch` depuis la page (les cookies de session sont nécessaires). La taille réelle des pages en points est
   la réponse de `viewer/presspage?id=…` (dans `performance.getEntriesByType('resource')`) : `[72, largeur, hauteur]`.
3. Enregistrer chaque image : lien `<a download="p1.png">` sur un `URL.createObjectURL(blob)`, cliqué. Chrome
   peut demander confirmation sans que la fenêtre soit visible : le fichier complet reste alors
   `<Téléchargements>/<uuid>.tmp` (même taille que le blob) — le copier sous son vrai nom. Ne pas envoyer les
   images vers un serveur local : Chrome bloque sur une demande d'accès au réseau local.
4. Assembler dans `A traduire/` (pages à la taille de `presspage`) :
   `python -X utf8 -c "import pymupdf,sys; d=pymupdf.open(); [d.new_page(width=W,height=H).insert_image(pymupdf.Rect(0,0,W,H),filename=f) for f in sys.argv[2:]]; d.save(sys.argv[1])" sortie.pdf p1.png p2.png`
   (remplacer W et H), puis `preparer.py` comme d'habitude.
5. Dire à l'utilisateur quels fichiers temporaires effacer (`.tmp`, téléchargements restés en attente) et noter
   la source (lien, nom du fichier Drive) dans `NOTES.md`.
