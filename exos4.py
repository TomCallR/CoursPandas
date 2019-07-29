# modules
import numpy as np
import pandas as pd
import mysql.connector as sql
from dateutil.relativedelta import relativedelta
import datetime as dt
from dfply import *

# tables sql
conn = sql.connect(host='da.cefim-formation.org', database='cefim_datawarehouse', user='root', password='dadfba16')
pat = pd.read_sql('SELECT * FROM patient', conn)
sej = pd.read_sql('SELECT * FROM sejour', conn)
mvt = pd.read_sql('SELECT * FROM mouvement', conn)
doc = pd.read_sql('SELECT * FROM document', conn)
dat = pd.read_sql('SELECT * FROM data', conn)
srv = pd.read_sql('SELECT * FROM structure', conn)
ths = pd.read_sql('SELECT * FROM thesaurus', conn)

# CHALLENGE N°2
# Extraire la liste des séjours avec une entrée par les urgences
# puis au moins un service d'aval
# Extraire le disgnostic des urgences
# Dire si le diagnostic est une ICA ou non. Synonymes possibles :
# ICA,
# OAP,
# insuffisance cardiaque aigüe (ou aig),
# décompensation cardiaque

# Comparer le diagnostic des urgences (ICA oui/non)
# à celui du service d'aval (ICA oui/non)

# CHALLENGE N°2
srv.rename(
    columns={'id': 'service_id'},
    inplace=True
)
mvt.rename(
    columns={'id': 'mouvement_id'},
    inplace=True
)
sej.rename(
    columns={'id': 'sejour_id'},
    inplace=True    
)

#
srv_urgences = (srv[srv['parent_id']==1])
mvt_urgences = srv_urgences.merge(
    mvt,
    how='inner',
    left_on='service_id',
    right_on='service_id'
)
mvt_urgences.drop(
    labels=['service_id', 'parent_id', 'nom', 'categorie', 'service_id'],
    axis=1,
    inplace=True
)

#
nb_mvt_by_sej = mvt_urgences.groupby(
    by='sejour_id',
    as_index=False
).aggregate(
    {'mouvement_id': 'count'}
)
nb_mvt_by_sej.rename(
    columns={'mouvement_id': 'mouvement_count'},
    inplace=True
)

# print(nb_mvt_by_sej)

#
nb_mvt_by_sej = nb_mvt_by_sej[nb_mvt_by_sej['mouvement_count'] > 1]

#
sej_avec_urg_et_aval = nb_mvt_by_sej.merge(
    sej,
    how='inner',
    left_on='sejour_id',
    right_on='sejour_id'
)
print(sej_avec_urg_et_aval)
print(sej_avec_urg_et_aval.shape)
#

