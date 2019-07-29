#%%
import numpy as np
import pandas as pd
import mysql.connector as sql
from dateutil.relativedelta import relativedelta
import datetime as dt
# from dfply import *

#%%
conn = sql.connect(host='da.cefim-formation.org', database='cefim_datawarehouse', user='root', password='dadfba16')
pat = pd.read_sql('SELECT * FROM patient', conn)
sej = pd.read_sql('SELECT * FROM sejour', conn)
mvt = pd.read_sql('SELECT * FROM mouvement', conn)
doc = pd.read_sql('SELECT * FROM document', conn)
dat = pd.read_sql('SELECT * FROM data', conn)
srv = pd.read_sql('SELECT * FROM structure', conn)
ths = pd.read_sql('SELECT * FROM thesaurus', conn)

#%% CHALLENGE N°1
# Extraire la liste des patients qui avaient entre 20 et 70 ans à
# l'admission
patnotnone = (~pat['date_naissance'].isna())
sejnotnone = (
    (~sej['patient_id'].isna())
    & (~sej['date_entree'].isna())
)

patsej = pd.merge(
    left=pat[patnotnone],
    right=sej[sejnotnone],
    how='inner',
    left_on='id',
    right_on='patient_id'
)

patsej.rename(
    columns={
        'id_x': 'id_patient',
        'id_y': 'id_sejour'
    },
    inplace=True
)

patsej['age_admission'] = patsej.apply(
    lambda row: relativedelta(
        row.loc['date_entree'],
        row.loc['date_naissance']
    ).years,
    axis=1
)

patsej = patsej.query(
    'age_admission >= 20 and age_admission <= 70'
)

#%% CHALLENGE N°1 (suite)
# ... et dont le 1er mouvement était aux urgences
mvttodel = (
    (mvt['date_entree'].isna()) &
    (mvt['date_sortie'].isna())
)

sejtodel = (mvt[mvttodel].
            groupby('sejour_id').
            aggregate(
                {'sejour_id': 'first'}
            ))

mvt = mvt[~mvt['sejour_id'].isin(sejtodel)]

datena = mvt['date_entree'].isna()
mvt.loc[datena,'date_entree'] = mvt.loc[datena,'date_sortie'] - dt.timedelta(seconds=1)

mvt.sort_values(by=['sejour_id', 'date_entree'])

firstmvt = mvt.groupby(
    'sejour_id'
    ).first()

id_srv_urgences = srv.query(
    'parent_id == 1'
)['id']

firstmvt = firstmvt[firstmvt['service_id'].isin(id_srv_urgences)]

patsej_res = patsej[patsej['id_sejour'].isin(
    firstmvt.index
)]

res = pat[pat['id'].isin(
    patsej_res['id_patient']
)]


#%%
