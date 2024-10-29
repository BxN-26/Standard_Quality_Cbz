# Standard_Quality_Cbz
Ce Dépôt vise a créer des script python en ligne de commande, pour standardiser la qualité et la définition des fichiers CBZ au sein d'une grosse bibliothèque de Comics, Mangas et BD.

Plus en Détails, chacun de nous rencontre des soucis lors de l'ouverture de fichier CBZ, car tous ne sont pas au format le plus adapté, por nos différents écran (tablette, smatphone, TV, ...)
Ce projet vise à automatiser le traitement des fichiers CBZ, glanés au fil du temps pour proposés la définition et la qualité de lecture la plus optimal qui soit.
Au Cours de ma reflexion, et de différents calculs, il m'a semblé pouvoir établir 2 principaux formats ( les formats spécifiques viendront dans un second temps), les comics et les mangas seront traités 
avec la même définition, ce qui comprend également les comics strip et les romans graphique au format paysage, cela permet un ratio optimal et une visualisation parfaite pleine écran.
Les Bandes Déssinées quant a elle seront traités différemment puisqu le format et le ration hauteur largeur n'est pas semblabe aux formats précedents, mais toujours pour un affichage optimale sans distortions.
Il a fallu concevoir le script pour prendre plusieurs paramètres en compte:
1 - Les fichiers la plupart du temps sont déja au format CBZ
2 - Offrir le choix des formats appropriés à chaque fichier
3 - Être capable de gérer de multiples formats de fichier image.
4 - Appliquer différents traitement à l'image pour leur donner une homogénéité.
5 - Choisir le format de sortie des images le plus approprié
6 - Supprimer les fichiers images sources pour ne garder que les nouveaux fichiers pour eviter de se retrouver avec des doublons de pages
7 - Extraire la première Page pour créer la cover de la BD pour les bibliothèques
8 - Reconstruire le fichier CBZ à partir des nouveaux fichiers
9 - S'assurer de la validité des fichiers CBZ dans les différents clients de lecture
10 - Supprimer les fichiers source en fin de script pour ne garder que les nouveaux fichiers.
11 - Générer un fichier log incluant également des statistiques
 
