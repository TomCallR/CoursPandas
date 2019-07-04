#%%
import pandas as pd
import numpy as np
import mysql.connector as sql

conn = sql.connect(host='da.cefim-formation.org', database='cefim_datawarehouse', user='root', password='dadfba16')
pat = pd.read_sql('SELECT * FROM patient', conn)
sej = pd.read_sql('SELECT * FROM sejour', conn)
mvt = pd.read_sql('SELECT * FROM mouvement', conn)
doc = pd.read_sql('SELECT * FROM document', conn)
dat = pd.read_sql('SELECT * FROM data', conn)
srv = pd.read_sql('SELECT * FROM structure', conn)
ths = pd.read_sql('SELECT * FROM thesaurus', conn)

#%% Afficher les trois premiers patients
pat.iloc[0:3]

#%% N'affiche que les colonnes id, nom, prenom
pat.loc[:, ['id', 'nom', 'prenom']]


#%% Toutes colonnes sauf le prénom
pat.drop(labels=['prenom'], axis=1)

#%% Afficher les patients vivants
pat.statut_vital == 'V'
pat[pat.statut_vital == 'V']

#%% Ou : 
pat.query('statut_vital == "V"')

#%% Afficher les femmes vivantes
pat[(pat.statut_vital == 'V') & (pat.sexe == 'F')]

#%% Ou
pat.query('statut_vital == "V"').query('sexe == "F"')

#%% Calculer l'âge des patients au décès
from dateutil.relativedelta import relativedelta
from datetime import date, datetime
dcd = pat[pat.statut_vital == 'D']
# créer la nouvelle colonne
dcd = dcd.assign(date_actuelle=datetime.today())

#%% colonne âge : utilisation d'une fonction à la place
def calc_age(row):
    return relativedelta(row.date_deces, row.date_naissance).years
# ne fonctionne pas à cause d'une valeur manquante
# dcd.assign(age=dcd.apply(calc_age, axis=1))
dcd.date_naissance.isna()
dcd = dcd.query('~date_naissance.isna()').query('~date_deces.isna()')
dcd.assign(age=dcd.apply(calc_age, axis=1))

#%% Pour chaque séjour, calculer l'âge à l'admission
df = pat.merge(sej, how='inner', left_on='id',
    right_on='patient_id')\
    .query('~date_naissance.isna()')\
    .query('~date_entree.isna()')
df = df.assign(age_admission=df.apply(
    lambda row:
        relativedelta(row.date_entree, row.date_naissance).years,
    axis=1))

#%% Utiliser la date de premier mouvement si la date d'entrée manque
df = pat\
    .merge(sej, 
            how='left', 
            left_on='id', 
            right_on='patient_id',
            suffixes=('_patient', '_sejour')
    )\
    .merge(mvt,
            how='left',
            left_on='id_sejour',
            right_on='sejour_id',
            suffixes=('_sejour', '_mouvement')
    )
def flat_columns(self):
    self.columns = ['_'.join(col).strip() for col in self.columns.values]
    return self.reset_index()
pd.DataFrame.flat_columns = flat_columns
rs = df\
    .sort_values([
        'sejour_id',
        'date_entree_mouvement'
    ])\
    .groupby('sejour_id').agg({
        'date_naissance': ['first'],
        'date_entree_sejour': ['first'],
        'date_entree_mouvement': ['min']
    }).flat_columns()

#%% Suite : renommer les colonnes
rs.rename(
    columns={
        'date_naissance_first': 'date_naissance',
        'date_entree_mouvement_min': 'date_entree_mouvement',
        'date_entree_sejour_first': 'date_entree_sejour'
    },
    inplace=True
)

#%% Suite : si date entrée manquante, recopier la date mouvement
rs['date_entree_sejour'].fillna(
    rs['date_entree_mouvement'],
    inplace=True
)

#%% On termine et on calcule l'âge à la date d'entrée
rs = rs.query('~date_naissance.isna()')\
    .query('~date_entree_mouvement.isna()')
rs = rs.assign(age_admission=rs.apply(
    lambda row: 
        relativedelta(row.date_entree_sejour, row.date_naissance).years,
    axis=1)
)
rs

#%%
