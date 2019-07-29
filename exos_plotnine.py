#%% modules
from plotnine import *
from plotnine.data import mtcars
from plotnine.data import mpg

from dfply import *

# Référence : livre "The grammar of graphics" (Leland Wilkinson)
# conception d'un graphique : ggplot + geom_xxx
# un geom est une représentation graphique de nos variables
#%% cas geom_point pour un nuage de points
(
    ggplot(data=mpg)
    + geom_point(mapping=aes(x='displ', y='hwy'))
)

#%% mapping de la couleur
(
    ggplot(data=mpg)
    + geom_point(mapping=aes(x='displ', y='hwy', color='class'))
)

#%% en faisant varier la taille pour une variable
(
    ggplot(data=mpg)
    + geom_point(mapping=aes(x='displ', y='hwy', color='class', size='displ'))
)

#%% avec des classes en y
(
    ggplot(data=mpg)
    + geom_point(mapping=aes(x='displ', y='class', color='class', size='displ'))
)

#%% avec de la transparence
(
    ggplot(data=mpg)
    + geom_point(mapping=aes(x='displ', y='hwy', alpha='class'))
)

#%% la forme des points
(
    ggplot(data=mpg)
    + geom_point(mapping=aes(x='displ', y='hwy', shape='class'))
)

#%% couleur bleue : ne marche pas comme ça car il mappe une couleur de son choix
# (rouge) à une catégorie toujours égale à bleue
(
    ggplot(data=mpg)
    + geom_point(mapping=aes(x='displ', y='hwy', color='"blue"'))
)

#%% couleur bleue : sortir la couleur du mapping
(
    ggplot(data=mpg)
    + geom_point(mapping=aes(x='displ', y='hwy'), color='blue')
)

#%%
(
    ggplot(data=mpg)
    + geom_point(mapping=aes(x='displ', y='hwy', color='displ', fill='hwy'),
     shape='o', size=10, alpha=0.2)
)

#%% couleur variant selon que hwy est sup ou inf à 5
(
    ggplot(data=mpg)
    + geom_point(mapping=aes(x='displ', y='hwy', color='displ>5'))
)

#%% Facetting (vignettage)
(
    ggplot(data=mpg)
    + geom_point(mapping=aes(x='displ', y='hwy'))
    + facet_wrap('~class', nrow=2)
)

# pour sauvegarder (par exemple en format vectoriel)
(
    ggplot(data=mpg)
    + geom_point(mapping=aes(x='displ', y='hwy'))
    + facet_wrap('~class', nrow=2)
).save(test.svg)

#%% avec deux varaibles
(
    ggplot(data=mpg)
    + geom_point(mapping=aes(x='displ', y='hwy'))
    + facet_grid('drv ~ cyl')
)

#%% courbe approchée
(
    ggplot(data=mpg)
    + geom_smooth(mapping=aes(x='displ', y='hwy'))
)

#%% en faisant aussi apparaître les points
(
    ggplot(data=mpg)
    + geom_point(mapping=aes(x='displ', y='hwy'))
    + geom_smooth(mapping=aes(x='displ', y='hwy'))
)

# que l'on peut simplifier en
(
    ggplot(data=mpg, mapping=aes(x='displ', y='hwy'))
    + geom_point()
    + geom_smooth()
)

# inversement on pourrait descendre le data dans les geom et ainsi avoir
# des data distincts

#%% avec des points de couleur
(
    ggplot(data=mpg, mapping=aes(x='displ', y='hwy'))
    + geom_point(mapping=aes(color='class'))
    + geom_smooth()
)

#%% au sein du dataframe mpg, tracer une courbe pour chaque classe de drv
# avec displ en x et hwy en y
# les 3 courbes doivent avoir une couleur différente
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

#%% Mais beaucoup plus simple et avec les légendes en plus
(
    ggplot(data=mpg, mapping=aes(x='displ', y='hwy', color='drv'))
    + geom_smooth()
)

# fonctionne aussi en remplaçant color par linetype : fait des courbes avec
# des pointillés, des tirets, ...

#%% Histogramme
(
    ggplot(data=diamonds)
    + geom_bar(mapping=aes(x='cut'))
)

# équivalent à
(
    ggplot(data=diamonds)
    + stat_count(mapping=aes(x='cut'))
)

# lui-même équivalent à
(
    ggplot(data=diamonds)
    + stat_count(mapping=aes(x='cut'),
    geom='bar')
)

#%% stat_summary
(
    ggplot(data=diamonds)
    + stat_summary(mapping=aes(x='cut', y='depth'),
        fun_ymin=np.min,
        fun_ymax=np.max,
        fun_y=np.median)
)

#%% clarity par cut
(
    ggplot(data=diamonds)
    + geom_bar(mapping=aes(x='cut', fill='clarity'),
    position='dodge')
)

# autre présentation
(
    ggplot(data=diamonds)
    + geom_bar(mapping=aes(x='cut', fill='clarity'),
    position='fill')
)
#%%
