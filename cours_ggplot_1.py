# pip install plotnine
from plotnine import *
from plotnine.data import mtcars
from plotnine.data import mpg

from dfply import *

mpg

# conception d'un graphique : ggplot + geom_xxx
# un geom est une représentation graphique de nos variables :
# ici geom_point pour un nuage de points
# on mappe des variables sur des éléments esthétiques (aes)
# chaque geom possède ses aes, mais certains sont ubiquitaires
# (ex : x et y)
(
        ggplot(data=mpg)
        + geom_point(mapping=aes(x='displ', y='hwy'))
)

# mapping de la couleur
(
        ggplot(data=mpg)
        + geom_point(mapping=aes(
            x='displ',
            y='hwy',
            color='class',
            size='displ'))
)

(
        ggplot(data=mpg)
        + geom_point(mapping=aes(
            x='displ',
            y='class',
            color='class',
            size='displ'))
)

# mapping de la taille des points
(
        ggplot(data=mpg)
        + geom_point(mapping=aes(x='displ', y='hwy', size='class'))
)

# mapping de la transparence
(
        ggplot(data=mpg)
        + geom_point(mapping=aes(
            x='displ',
            y='hwy',
            alpha='class'
        ))
)

# mapping de la forme
(
        ggplot(data=mpg)
        + geom_point(mapping=aes(
            x='displ',
            y='hwy',
            shape='class'
        ))
)

# Question : comment définir manuellement une couleur ?
# Ex : je veux des points bleus
# Ceci ne marche pas :
(
        ggplot(data=mpg)
        + geom_point(mapping=aes(
            x='displ',
            y='hwy',
            color='blue'
        ))
)

# Raison : on essaye de mapper la couleur à une variable nommée blue (qui n'existe pas)
# à la place on pourrait tenter une chaine de caractère : "blue"

(
        ggplot(data=mpg)
        + geom_point(mapping=aes(
            x='displ',
            y='hwy',
            color='"blue"'
        ))
)

# Etrange... tous les points sont rouges !
# Raison : lorsqu'on mappe une variable qualitative, ggplot associe une couleur à chaque classe
# ici il ne trouve qu'une seule classe ("blue"), mais il aurait fait de même avec "dsjfndsf" :
(
        ggplot(data=mpg)
        + geom_point(
            mapping=aes(
                x='displ',
                y='hwy',
                color='"dsjfndsf"'
            )
        )
)

# En réalité on ne cherche pas à mapper, donc la solution ne se trouve pas dans mapping
# le paramètre mapping ne fait que rendre dynamique les autres paramètres du geom
# mais on peut directement utiliser ces paramètres sans passer par le mapping
(
        ggplot(data=mpg)
        + geom_point(
            mapping=aes(
                x='displ',
                y='hwy'
            ),
            color='blue'
        )
)

(
        ggplot(data=mpg)
        + geom_point(
            mapping=aes(
                x='displ',
                y='hwy',
                color='displ',
                fill='hwy'
            ),
            shape='o',
            size=10,
            alpha=0.2
        )
)

# Conclusion : lorsqu'on souhaite définir manuellement un paramètre, il faut le faire hors mapping


# Question : comment mettre une couleur selon si la variable est < ou > à 5 ?
# Réponse :
(
        ggplot(data=mpg)
        + geom_point(mapping=aes(
            x='displ',
            y='hwy',
            color='displ < 5'))
)

# Facetting : permet de découper le plot en plusieurs vignettes selon une variable qualitative
(
        ggplot(data=mpg)
        + geom_point(
            mapping=aes(
                x='displ',
                y='hwy'
            ))
        + facet_wrap('~class', nrow=2)
).save("test.svg")

# Si on a 2 variables, on peut en faire une grille (bug sur version actuelle, en cours de correction)
(
        ggplot(data=mpg)
        + geom_point(mapping=aes(x='displ', y='hwy'))
        + facet_grid('drv ~ cyl')
)

# Il existe de nombreux geom, lorsqu'ils partagent les mêmes aes, il suffit de changer le geom
# pour passer de l'un à l'autre. Ainsi on passe d'un nuage de points :
(
        ggplot(data=mpg)
        + geom_point(mapping=aes(
            x='displ',
            y='hwy'
        ))
)

# à une courbe lissée juste en changeant le nom du geom

(
        ggplot(data=mpg)
        + geom_smooth(
            mapping=aes(
                x='displ',
                y='hwy'
            ))
)

# voir les 2 à la fois si on applique les2 geom :

(
        ggplot(data=mpg)
        + geom_point(mapping=aes(
            x='displ', y='hwy'
        ))
        + geom_smooth(mapping=aes(
            x='displ', y='hwy'
        ))
)

# mais on répète les aes (principe DRY...) heureusement les aes communs peuvent être
# remontés dans le ggplot :

(
        ggplot(
            data=mpg,
            mapping=aes(
                x='displ',
                y='hwy'
            )
        )
        + geom_point()
        + geom_smooth()
)

# on peut ajouter des aes spécifiques au sein des geom
(
        ggplot(data=mpg,
               mapping=aes(
                   x='displ',
                   y='hwy'
               )
        )
        + geom_point(
            mapping=aes(color='class'))
        + geom_smooth()
)

# si un aes est défini dans ggplot et le geom, c'est le geom qui l'emporte
(
        ggplot(data=mpg,
               mapping=aes(
                   x='displ',
                   y='hwy',
                   color='hwy'
               )
        )
        + geom_point(
            mapping=aes(color='class')
        )
        + geom_smooth()
)

# Tout comme le mapping, l'élément data peut être placé dans les geom ou dans ggplot
# si les geoms concernent différents jeux de données, on peut donc appliquer un geom
# par dataframe
# Exemple :
data1 = pd.DataFrame({
    'poids': [10, 20, 30, 40, 50],
    'taille': [1, 2, 4, 8, 16]
})

data2 = pd.DataFrame({
    'poids': [10, 20, 30, 40, 50],
    'taille': [1, 2, 3, 4, 5]
})

(
        ggplot()
        + geom_smooth(data=data1,
                      mapping=aes(
                          x='poids',
                          y='taille'
                      ), color="blue")
        + geom_smooth(data=data2,
                      mapping=aes(
                          x='poids',
                          y='taille'
                      ), color="red")
)

# Attention ! cela sous nécessite tout de même que x et y mappent la même variable,
# quelque soit le dataframe (sinon les axes n'auraient aucun sens !)

# Exercice : au sein du dataframe mpg,
# tracez une courbe pour chaque classe de drv
# avec displ en x
# et hwy en y
# Les 3 courbes doivent avoir une couleur différente
from dfply import *

data_r = (
    mpg >>
    mask(X.drv == 'r')
)

data_f = (
    mpg >>
    mask(X.drv == 'f')
)

data_4 = (
    mpg >>
    mask(X.drv == '4')
)

(
    ggplot(mapping=aes(x='displ', y='hwy'))
    + geom_smooth(data=data_r, color="blue")
    + geom_smooth(data=data_f, color="red")
    + geom_smooth(data=data_4, color="green")
)



# Solution :
# On découpe notre jeu de données mpg en 3 dataframes (1 pour chaque classe)

mpg.drv.unique()

data_f = (
        mpg >>
        mask(X.drv == 'f')
)

data_4 = (
        mpg >>
        mask(X.drv == '4')
)

data_r = (
        mpg >>
        mask(X.drv == 'r')
)

# Puis on applique nos 3 geoms :
(
        ggplot()
        + geom_smooth(data=data_f, mapping=aes(x='displ', y='hwy'), color='red')
        + geom_smooth(data=data_4, mapping=aes(x='displ', y='hwy'), color='green')
        + geom_smooth(data=data_r, mapping=aes(x='displ', y='hwy'), color='blue')
)

# Ca fonctionne, mais on a perdu la légende (car la couleur a été définie à la main, et non via un mapping)
# et c'est très labvorieux...

# Solution plus efficiente : utiliser le mapping
(
        ggplot(data=mpg)
        + geom_smooth(mapping=aes(
            x='displ',
            y='hwy',
            linetype='drv'
        ))
)
mpg.axes
# en précisant ce mapping, ggplot va automatiquement en déduire qu'il n'est pas possible
# de mapper la couleur tout en ne conservant qu'une seule courbe et fera le découpage automatiquement

# d'autres aes suivent ce même principe :

(
        ggplot(data=mpg)
        + geom_smooth(mapping=aes(x='displ', y='hwy', linetype='drv'))
)

# Notez l'évolution de la légende : en mappant 2 aes sur la même variable,
# ggplot ne crée pas 2 légendes pour autant : il les fusionne !

(
        ggplot(data=mpg)
        + geom_smooth(mapping=aes(x='displ', y='hwy', linetype='drv', color='drv'))
)

# Passons au geom_bar :
(
        ggplot(data=diamonds)
        + geom_bar(
            mapping=aes(x='cut')
        )
)

# geom_bar a calculé pour nous la valeur de x, comment ?
# Chaque geom a une stat par défaut
# ainsi geom_bar transforme nos données via un stat='count'

(
        ggplot(data=diamonds)
        + geom_bar(mapping=aes(x='cut'),
                   stat='count')
)

# De façon symétrique, on peut appeler des stats au lieu des geom
# Et chaque stat possède un geom apr défaut
# Ainsi stat_count...
(
        ggplot(data=diamonds)
        + stat_count(mapping=aes(x='cut'))
)

# ... utilise par défaut le geom_bar
(
        ggplot(data=diamonds)
        + stat_count(mapping=aes(x='cut'),
                     geom='bar')
)

# Très pratique : pas besoin de calculer nous même les effectifs par classe
# Mais dans certains cas, on ne souhaite pas réaliser de stat_count car on possède déjà
# les stats par catégorie. Ex :

test = pd.DataFrame({
    'categorie': ['A', 'B', 'C', 'D'],
    'effectif': [50, 100, 75, 25]
})

# la stat_identity signifie : conserver la valeur sans transformation

(
        ggplot(data=test)
        + geom_bar(
            mapping=aes(
                x='categorie',
                y='effectif'
            ), stat='stat_identity')
)

# geom_bar place automatiquement en y la variable count calculée par stats_count
# les variables calculées par les stat_xxx peuvent être utilisée via ..var..
# ainsi un geom_bar sous entend :
(
        ggplot(data=diamonds)
        + geom_bar(
            mapping=aes(
                x='cut',
                y='..count..'
            )
        )
)

# mais stat_count calcule également prop : la proportion des classes
(
        ggplot(data=diamonds)
        + geom_bar(
            mapping=aes(
                x='cut',
                y='..prop..'
            )
        )
)

# Problème : ggplot calcule la paroportion par classe de cut
# c'est comme s'il faisait ceci :
(
        ggplot(data=diamonds)
        + geom_bar(
            mapping=aes(
                x='cut',
                y='..prop..',
                group='cut'))
)

# on peut rassember tous les groupes en 1 seul en lui donnant une valeur statique
# ainsi les proportion sont calculée par rapport à l'ensemble des valeurs
(
        ggplot(data=diamonds)
        + geom_bar(mapping=aes(
            x='cut',
            y='..prop..'),
        group='"robert"')
)


# autre statistique : stat_summary
(
        ggplot(data=diamonds)
        + stat_summary(
            mapping=aes(x='cut', y='depth'),
            fun_ymin=np.min,
            fun_ymax=np.max,
            fun_y=np.median
        )
)

# colorer un geom_bar : son countour (peu utile, mais erreur fréquente)
(
        ggplot(data=diamonds)
        + geom_bar(mapping=aes(
            x='cut',
            color='cut'
        ))
)

# et son contenu

(
        ggplot(data=diamonds)
        + geom_bar(
            mapping=aes(
                x='cut',
                fill='cut'
            )
        )
)

# très utile lorsqu'on utilise une variable qui n'est pas celle des barres !
(
        ggplot(data=diamonds)
        + geom_bar(
            mapping=aes(
                x='cut',
                fill='clarity'
            )
        )
)

# geom_bar possède aussi des positions
# par défaut : position='stack' : on empile les rectangles au sein d'une même barre
(
        ggplot(data=diamonds)
        + geom_bar(
            mapping=aes(
                x='cut',
                fill='clarity'
            ),
            position='stack'
        )
)

# fill : remplir la colonne -> utile pour comparer des proportions
(
        ggplot(data=diamonds)
        + geom_bar(
            mapping=aes(
                x='cut',
                fill='clarity'
            ),
            position='fill'
        )
)

# dodge : mettre côte à côte -> utile pour comparer les valeurs au sein d'un groupe
(
        ggplot(data=diamonds)
        + geom_bar(
            mapping=aes(
                x='cut',
                fill='clarity'),
            position='dodge')
)

# identity : ne pas gérer la position des rectangles -> superpose tou, inutile !
(
        ggplot(data=diamonds)
        + geom_bar(
            mapping=aes(
                x='cut',
                fill='clarity'
            ), position='identity')
)

# la position est valable pour tous les geom
# pour le geom point c'est identity qui est utilisé
# mais que se passe-t-il si plusieurs points ont exactmenent les mêmes coordonnées ?
(
        ggplot(data=mpg)
        + geom_point(
            mapping=aes(x='displ', y='hwy'))
)

# -> overplotting : on ne distingue pas 2 points superposés
# -> utiliser la position jitter qui ajoute un déplacement aléatoire pour démarquer les geoms
(
        ggplot(data=mpg)
        + geom_point(
            mapping=aes(
                x='displ',
                y='hwy'
            ), position='jitter')
)