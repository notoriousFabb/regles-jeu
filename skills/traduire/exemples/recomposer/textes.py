# -*- coding: utf-8 -*-
"""Texte du livret CMYK recomposé (fond noir, sans image du scan) — français et anglais. Moteur : noir.py.

Chaque volet (1 à 12, dans l'ordre du dépliant) est une liste de blocs :
    ("h", titre)            titre de section précédé du repère d'impression ⌖
    ("rule", titre)         petit titre entre deux filets (— Les cartes ———)
    ("sub", html)           sous-titre en gras (① Entame…)
    ("p", html)             paragraphe
    ("li", html)            puce ◦ avec retrait
    ("box", titre, html)    encadré à titre sur le cadre
    ("sp", hauteur)         espace vertical (en multiple de la taille du texte)
    ("logo",) / ("fin",)    page de titre (volet 1) / crédits (volet 12)
Un même texte est donné en français et en anglais : T("fr", "en")."""


def T(fr, en):
    return {"fr": fr, "en": en}


N = '<span style="font-family:Sym">{}</span>'  # ①②③④ : absents de Segoe UI

INFO = [T("30 min", "30 min"), T("3–4 joueurs", "3–4 players"), T("10 ans +", "Ages 10+")]
SOUS_TITRE = T("Livret de règles", "Rulebook")

VOLETS = {
    1: [
        ("logo",),
        ("h", T("Aperçu du jeu", "Game Overview")),
        ("p", T("Vous êtes une imprimante. Le papier est là, les données sont arrivées. Il ne manque que l'encre.",
                "You are a printer. The paper is here, the data has arrived. All that's missing is ink.")),
        ("p", T("Cyan, Magenta, Jaune, Noir : réunissez ces 4 couleurs, une de chaque, et retrouvez une "
                "impression parfaite.",
                "Cyan, Magenta, Yellow, Black: collect these 4 colors, one of each, and restore a perfect print.")),
        ("p", T("Mais si vous remettez trop d'une même couleur, l'encre déborde et vous plantez (« crash »).",
                "But refill the same color too much, and the ink overflows and you crash.")),
        ("p", T("Soyez le premier à réunir les 4 couleurs.<br/>— Lancez l'impression !",
                "Be the first to hold all 4 colors.<br/>— Let the printing begin!")),
        ("h", T("Matériel", "Components")),
        ("p", T("Livret de règles : 1<br/>Cartes : 48 (12 de chaque couleur C, M, Y, K)<br/>"
                "Jetons Encre : 16 (4 de chaque couleur C, M, Y, K)",
                "Rulebook: 1<br/>Cards: 48 (12 each of C, M, Y, K)<br/>Ink tokens: 16 (4 each of C, M, Y, K)")),
    ],
    2: [
        ("h", T("Mise en place", "Setup")),
        ("p", T("Mélangez bien toutes les cartes (en mélangeant aussi leur sens : haut et bas au hasard).",
                "Shuffle all the cards thoroughly (mixing their orientation too: top and bottom at random).")),
        ("p", T("Distribuez les cartes selon le nombre de joueurs :<br/>3 joueurs : 9 cartes chacun<br/>"
                "4 joueurs : 10 cartes chacun",
                "Deal cards according to the number of players:<br/>3 players: 9 cards each<br/>"
                "4 players: 10 cards each")),
        ("p", T("Choisissez librement le premier joueur.", "Choose the start player freely.")),
        ("rule", T("Les cartes", "About the cards")),
        ("p", T("Chaque carte porte un nombre en haut et un nombre en bas ; leur somme fait toujours 25.",
                "Each card has a number at the top and a number at the bottom; together they always add up to 25.")),
        ("rule", T("Préparer sa main", "Preparing your hand")),
        ("p", T("Au début de la manche, chaque joueur regarde sa main, puis peut retourner toute sa main d'un "
                "bloc (haut ↔ bas).<br/>C'est l'un ou l'autre : « tout retourner » ou « ne rien changer ».",
                "At the start of the round, each player looks at their hand, then may flip their whole hand "
                "upside down as a block (top ↔ bottom).<br/>It's one or the other: “flip everything” or "
                "“leave it as is”.")),
    ],
    3: [
        ("h", T("Déroulement d'une manche", "Round Flow")),
        ("p", T("La partie compte autant de manches que de joueurs. Chaque manche se joue en une suite de "
                "« plis ».",
                "The game lasts as many rounds as there are players. Each round is played as a series of "
                "“tricks”.")),
        ("box", T("Qu'est-ce qu'un pli ?", "What is a trick?"),
         T("Chacun joue une carte et l'on désigne « le gagnant de cette confrontation » : c'est l'équivalent "
           "d'une confrontation dans un jeu de cartes classique.",
           "Everyone plays one card to decide “the winner of this showdown”, like a single face-off in a "
           "classic card game.")),
        ("sub", T(N.format("①") + " Entame (jouer la première carte)",
                  N.format("①") + " Lead (playing the first card)")),
        ("p", T("Le meneur (en début de manche, le premier joueur) joue une carte de sa main. Sa couleur devient "
                "la « couleur demandée » de ce pli.",
                "The lead player (at the start of a round, the start player) plays a card from their hand. "
                "Its color becomes the “lead color” of this trick.")),
        ("sub", T(N.format("②") + " Suivre (jouer à son tour la couleur demandée)",
                  N.format("②") + " Follow (playing in turn, following the lead color)")),
        ("p", T("Dans le sens horaire, les autres joueurs jouent chacun une carte.",
                "Clockwise, the other players each play one card.")),
        ("li", T("Vous avez en main la couleur demandée<br/>→ vous devez la jouer.",
                 "You have the lead color in hand<br/>→ you must play it.")),
        ("li", T("Vous n'avez pas la couleur demandée<br/>→ vous pouvez jouer une autre couleur.",
                 "You don't have the lead color<br/>→ you may play another color.")),
    ],
    4: [
        ("box", T("Qu'est-ce que la couleur demandée ?", "What is the lead color?"),
         T("C'est la couleur de la première carte jouée dans le pli. Par exemple, si le premier à jouer pose du "
           "Cyan (C), la couleur demandée de ce pli est le Cyan. Le joueur qui joue la première carte d'un pli "
           "s'appelle le meneur.",
           "It is the color of the first card played in the trick. For example, if the first person to play plays "
           "Cyan (C), the lead color of that trick is Cyan. The player who plays the first card of a trick is "
           "called the lead player.")),
        ("sub", T(N.format("③") + " Gagnant du pli", N.format("③") + " Trick winner")),
        ("p", T("Parmi les cartes de la couleur demandée, celui qui a joué le plus grand nombre remporte le pli. "
                "(Une carte d'une autre couleur ne gagne jamais, si grand que soit son nombre.)",
                "Among the cards of the lead color, the player who played the highest number wins the trick. "
                "(A card of another color never wins, however high its number.)")),
        ("sub", T(N.format("④") + " Valeur acquise (inversion)", N.format("④") + " Earned value (flip)")),
        ("p", T("Le gagnant rassemble les cartes du pli, met celle qu'il a jouée sur le dessus et montre devant "
                "lui, comme « valeur acquise », le nombre du côté opposé à celui qui a servi dans le pli.",
                "The winner gathers the cards of the trick, puts the card they played on top, and displays in "
                "front of them, as their “earned value”, the number on the side opposite the one used in the "
                "trick.")),
        ("p", T("Exemple : vous gagnez avec une carte dont le haut est « 15 » → le « 10 » du bas est votre "
                "valeur acquise.<br/>→ Plus vous gagnez avec un petit nombre, plus votre valeur acquise est grande.",
                "Example: you win with a card whose top number is “15” → the “10” at the bottom is your earned "
                "value.<br/>→ The smaller the number you win with, the bigger your earned value.")),
        ("p", T("Le gagnant du pli devient le meneur du pli suivant.",
                "The winner of the trick becomes the lead player of the next trick.")),
    ],
    5: [
        ("h", T("Jetons Encre pendant la manche", "Ink Tokens During the Round")),
        ("p", T("Pour voir facilement qui a la plus haute valeur acquise dans chaque couleur, posez un jeton "
                "Encre sur la carte provisoirement en tête dans sa couleur.",
                "To make it easy to see who has the highest earned value in each color, place an Ink token on "
                "the card currently in the lead for its color.")),
        ("li", T("Si une valeur acquise plus haute apparaît dans la même couleur, déplacez le jeton Encre sur "
                 "cette carte.",
                 "If a higher earned value appears in the same color, move the Ink token onto that card.")),
        ("li", T("À la fin de la manche, le joueur chez qui se trouve le jeton Encre devient le « gagnant du "
                 "jeton Encre » de cette couleur.",
                 "At the end of the round, the player who has the Ink token becomes the “Ink token winner” "
                 "for that color.")),
        ("box", T("Attention", "Note"),
         T("Pendant la manche, les jetons Encre ne sont qu'un « affichage provisoire ». Réunir les 4 couleurs en "
           "cours de manche ne fait pas gagner sur-le-champ.<br/>(Voir « Fin de partie et vainqueur ».)",
           "During the round, Ink tokens are only a “provisional display”. Having all 4 colors in the middle "
           "of a round does not win the game on the spot.<br/>(See “End of the Game and Winner”.)")),
    ],
    6: [
        ("h", T("Calibrage (retourner une carte)", "Calibration (Flipping a Card)")),
        ("p", T("Quand vous jouez une carte, vous pouvez défausser face cachée une autre carte de votre main pour "
                "jouer retournée (haut ↔ bas) la carte que vous allez poser.",
                "When you play a card, you may discard another card from your hand face down to play the card "
                "you are about to play flipped (top ↔ bottom).")),
        ("sp", 0.5),
        ("p", T("Vous ne pouvez calibrer que lorsque vous jouez une carte.<br/>Le nombre de calibrages par manche "
                "n'est pas limité.<br/>Une carte jouée retournée compte pour le nombre qui se retrouve en haut.",
                "You may calibrate only when you play a card.<br/>There is no limit to how many times you may "
                "calibrate in a round.<br/>A card played flipped counts as the number that ends up on top.")),
        ("sp", 0.5),
        ("p", T("C'est le « calibrage » : le réglage fin de l'imprimante.<br/>Optimiser la sortie ou limiter les "
                "risques ? Gardez un œil sur votre réserve d'encre et jugez la situation.",
                "This is “calibration”: fine-tuning the printer's settings.<br/>Optimize the output, or play it "
                "safe? Keep an eye on your ink levels and read the situation.")),
    ],
    7: [
        ("h", T("Participation aux plis", "Trick Participation Rules")),
        ("p", T("Comme on défausse des cartes en calibrant, le nombre de cartes en main varie d'un joueur à "
                "l'autre.",
                "Since cards are discarded when calibrating, the number of cards left in hand varies from "
                "player to player.")),
        ("p", T("Tant que vous avez des cartes en main, vous participez obligatoirement à chaque pli. Un joueur "
                "qui n'a plus de cartes passe (il ne participe pas à ce pli).",
                "As long as you have cards in hand, you must take part in every trick. A player with no cards "
                "left passes (they do not take part in that trick).")),
        ("p", T("Si le meneur n'a plus de cartes, le prochain joueur dans le sens horaire qui peut jouer devient "
                "le nouveau meneur.",
                "If the lead player has no cards, the next player clockwise who can play becomes the new lead "
                "player.")),
        ("p", T("Même s'il ne reste qu'un seul joueur avec des cartes en main, la manche continue. Ce joueur joue "
                "seul les plis jusqu'à épuisement de sa main (une carte à la fois : il remporte automatiquement "
                "le pli et montre sa valeur acquise normalement).",
                "Even if only one player still has cards in hand, the round does not end. That player keeps "
                "playing tricks alone until their hand is empty (one card at a time: they automatically win the "
                "trick and display their earned value as usual).")),
    ],
    8: [
        ("h", T("Fin de manche et gain d'encre", "End of the Round and Ink Collection")),
        ("p", T("La manche se termine quand plus personne n'a de cartes en main.",
                "The round ends when nobody has any cards left in hand.")),
        ("p", T("Pour chaque couleur, comparez les valeurs acquises : le joueur qui a la plus haute dans cette "
                "couleur gagne le jeton Encre de cette couleur.",
                "For each color, compare earned values: the player with the highest earned value in that color "
                "wins that color's Ink token.")),
        ("p", T("Chaque jeton Encre ne peut être gagné que par un seul joueur par manche. Le joueur chez qui se "
                "trouve le jeton Encre (repère provisoire de tête) à la fin de la manche en devient le gagnant.",
                "Each color's Ink token can be won by only one player per round. The player who has the Ink "
                "token (provisional leader marker) at the end of the round becomes its winner.")),
        ("h", T("Crash (trop d'encre)", "Crash (Too Much Ink)")),
        ("p", T("Si vous gagnez à nouveau un jeton Encre d'une couleur que vous avez déjà, vous plantez (crash).<br/>"
                "→ Vous perdez tous vos jetons Encre de cette couleur.",
                "If you win an Ink token of a color you already have, you crash.<br/>"
                "→ You lose all your Ink tokens of that color.")),
        ("p", T("Trop d'une même couleur, c'est interdit. L'encre déborde, l'impression est gâchée…",
                "Never overfill one color. The ink overflows and the print is ruined…")),
    ],
    9: [
        ("h", T("Préparer la manche suivante", "Preparing the Next Round")),
        ("p", T("Une fois la manche terminée, commencez la suivante. Le rôle de premier joueur passe au voisin de "
                "gauche (sens horaire) du premier joueur de la manche précédente.",
                "After a round ends, start the next one. The start player role passes to the player on the left "
                "(clockwise) of the previous round's start player.")),
        ("p", T("Mélangez toutes les cartes, redistribuez-les et jouez de la même façon. (Mélangez aussi leur "
                "sens : haut et bas au hasard.)",
                "Shuffle all the cards, deal them again and play the same way. (Shuffle so that their "
                "orientation is mixed too: top and bottom at random.)")),
    ],
    10: [
        ("h", T("Fin de partie et vainqueur", "End of the Game and Winner")),
        ("p", T("Lors de la vérification de fin de manche, si un joueur possède les jetons Encre des 4 couleurs"
                "<br/>→ il gagne immédiatement.",
                "When checking at the end of a round, if a player holds Ink tokens of all 4 colors"
                "<br/>→ they win immediately.")),
        ("box", T("Précision", "Clarification"),
         T("La victoire ne se vérifie qu'en fin de manche. Réunir provisoirement les 4 couleurs en cours de manche "
           "ne fait pas gagner. Il faut posséder les 4 couleurs une fois réglés tous les gains d'encre et les "
           "crashs de la fin de manche.",
           "Victory is only checked at the end of a round. Provisionally having all 4 colors mid-round does not "
           "win. You must hold all 4 colors after all of the end-of-round ink collection and crashes have been "
           "resolved.")),
        ("p", T("Si, au terme du nombre de manches prévu, personne n'a obtenu les jetons Encre des 4 couleurs<br/>"
                "→ le joueur qui a gagné le plus de jetons Encre l'emporte.",
                "If, after the set number of rounds, nobody has won Ink tokens of all 4 colors<br/>"
                "→ the player who has won the most Ink tokens wins.")),
        ("p", T("4 joueurs : 4 manches<br/>3 joueurs : 3 manches", "4 players: 4 rounds<br/>3 players: 3 rounds")),
    ],
    11: [
        ("h", T("Départage (en cas d'égalité)", "Final Tiebreak (in Case of a Tie)")),
        ("p", T("S'il y a plusieurs vainqueurs possibles, départagez-les dans l'ordre suivant.",
                "If several players qualify as the winner, determine the true winner in the following order.")),
        ("sp", 0.5),
        ("p", T("Le joueur qui a la plus haute valeur acquise de la dernière manche gagne.<br/>"
                "En cas de nouvelle égalité, départagez par la couleur de la carte de cette plus haute valeur "
                "acquise :<br/>C > M > Y > K (le C est le plus fort).",
                "The player with the highest earned value in the last round wins.<br/>"
                "If still tied, compare the color of the card of that highest earned value:<br/>"
                "C > M > Y > K (C is the strongest).")),
    ],
    12: [("fin",)],
}

CREDITS = T(
    "Remerciements : 狐鞭<br/>Conception du jeu : Kohta Nakagawa<br/>Illustrations : Kohta Nakagawa",
    "Special thanks: 狐鞭<br/>Game design: Kohta Nakagawa<br/>Artwork: Kohta Nakagawa")
ADRESSE = T("https://nakagawa-hands.com/<br/>Tenjin N Bldg. 6F, 2-3-7 Tenjin, Chuo-ku, Fukuoka (Japon)",
            "https://nakagawa-hands.com/<br/>Tenjin N Bldg. 6F, 2-3-7 Tenjin, Chuo-ku, Fukuoka, Japan")
