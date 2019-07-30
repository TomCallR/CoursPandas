#%%
from plotnine import *
from dfply import *
import numpy as np
import pandas as pd
import mysql.connector as sql

#%%
conn = sql.connect(host='da.cefim-formation.org', database='cefim_datawarehouse', user='root', password='dadfba16')
pat = pd.read_sql('SELECT * FROM patient', conn)
sej = pd.read_sql('SELECT * FROM sejour', conn)
mvt = pd.read_sql('SELECT * FROM mouvement', conn)
doc = pd.read_sql('SELECT * FROM document', conn)
dat = pd.read_sql('SELECT * FROM data', conn)
srv = pd.read_sql('SELECT * FROM structure', conn)
ths = pd.read_sql('SELECT * FROM thesaurus', conn)

#%% Représenter la répartition des patients en terme de sexe
(
    ggplot(data=pat)
    + geom_bar(mapping=aes(x='sexe',
    fill='sexe'))
    + coord_flip()
)

#%% Même chose mais avec représentation en porportion
(
    ggplot(data=pat)
    + geom_bar(
        mapping=aes(x='sexe',
        y='..prop..'),
        group='"Group"')
)

#%% Représenter l'évolution du nb de séjours (entrées) dans le temps
(
    ggplot(data=sej)
    + stat_bin(
        binwidth=365,
        boundary=0,
        mapping=aes(
            x='date_entree',
        )
    )
)

#%% 
(
    ggplot(data=sej)
    + geom_histogram(
        binwidth=365,
        boundary=0,
        mapping=aes(
            x='date_entree',
        )
    )
    + geom_smooth(
        mapping=aes(
            x='date_entree'
        ),
        stat='stat_bin',
        binwidth=365
    )
)

#%% Sur le graphique précédent, ajouter une distinction
# en fonction du sexe
patsej = (
    pat >> rename(
        patient_id='id'
    ) >> inner_join(
        sej,
        by='patient_id'
    )
)
# patsej = sej.merge(
#     right=pat,
#     how='inner',
#     left_on='patient_id',
#     right_on='id'
# )

(
    ggplot(data=patsej)
    + geom_histogram(
        mapping=aes(
            x='date_entree',
            fill='sexe'
        ),
        stat='stat_bin',
        binwidth=365        
    )
)

#%% aa
(
    ggplot(data=patsej)
    + geom_histogram(
        mapping=aes(
            x='date_entree'
        )
    )
    + facet_wrap('~sexe')
    # + coord_flip()
    + theme(
        axis_text_x=element_text(
            angle=90,
            hjust=1
        )
    )
)

#%% Comment faire si on voulait représenter l'âge des patients
# plutôt que le sexe ?
from dateutil.relativedelta import relativedelta
@make_symbolic
def date_diff_annees(series1, series2):
   df = pd.DataFrame({
       's1': series1,
       's2': series2
   })
   return df.apply(
       lambda row:
           relativedelta(row[0], row[1]).years, axis=1
   )
patsej = (
   patsej >>
   mask(
       ~X.date_naissance.isna(),
       ~X.date_entree.isna()
   ) >>
   mutate(age=date_diff_annees(X.date_entree, X.date_naissance))
)

(
    ggplot(data=patsej)
    + stat_summary_bin(
        mapping=aes(
            x='date_entree',
            y='age'
        ),
        fun_y=np.mean,
        geom='bar'
    )
)

#%%
