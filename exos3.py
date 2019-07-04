#%%
import numpy as np
import pandas as pd
import mysql.connector as sql
from dateutil.relativedelta import relativedelta
from datetime import date, datetime
from dfply import *

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
# l'admission et dont le 1er mouvement était aux urgences
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
mvtnotnone = (
    (~mvt['sejour_id'].isna())
    & (~mvt['service_id'].isna())
)

srvmvt = pd.merge(
    left=srv[srv['parent_id'] == 1],
    right=mvt[mvtnotnone],
    how='left',
    left_on='id',
    right_on='sejour_id'
)

srvmvt.rename(
    columns={
        'id_x': 'id_service',
        'id_y': 'id_mouvement'
    },
    inplace=True
)

# patsejmvt = pd.merge(
#     left=patsej,
#     right=mvt[mvtnotnone],
#     how='left',
#     left_on='id_sejour',
#     right_on='id'
# )



# @dfpipe
# def merge(
#     df1: pd.DataFrame,
#     df2: pd.DataFrame,
#     how: str,
#     left_on: str,
#     right_on: str
#     ):
#     return pd.merge(
#         left=df1,
#         right=df2,
#         how=how,
#         left_on=left_on,
#         right_on=right_on
#     )
# pat2 >>= merge(
#         sej,
#         how='inner',
#         left_on='id',
#         right_on='patient_id'
#     )
    
# pat3 >>= mutate(
#         age_admission=age_admission(
#             X.date_entree,
#             X.date_naissance
#         )
#     )
    
    # >> select(
    #     20 <= X.age_admission <= 70
    # ) >> select(

    # )




#%%
