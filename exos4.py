#%% modules
import numpy as np
import pandas as pd
import mysql.connector as sql
from dateutil.relativedelta import relativedelta
import datetime as dt
from dfply import *

#%% tables sql
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
# srv.rename(
#     columns={'id': 'service_id'},
#     inplace=True
# )
# mvt.rename(
#     columns={'id': 'mouvement_id'},
#     inplace=True
# )
# sej.rename(
#     columns={'id': 'sejour_id'},
#     inplace=True    
# )

# #
# srv_urgences = (srv[srv['parent_id']==1])
# mvt_urgences = srv_urgences.merge(
#     mvt,
#     how='inner',
#     left_on='service_id',
#     right_on='service_id'
# )
# mvt_urgences.drop(
#     labels=['service_id', 'parent_id', 'nom', 'categorie', 'service_id'],
#     axis=1,
#     inplace=True
# )

# #
# nb_mvt_by_sej = mvt_urgences.groupby(
#     by='sejour_id',
#     as_index=False
# ).aggregate(
#     {'mouvement_id': 'count'}
# )
# nb_mvt_by_sej.rename(
#     columns={'mouvement_id': 'mouvement_count'},
#     inplace=True
# )

# # print(nb_mvt_by_sej)

# #
# nb_mvt_by_sej = nb_mvt_by_sej[nb_mvt_by_sej['mouvement_count'] > 1]

# #
# sej_avec_urg_et_aval = nb_mvt_by_sej.merge(
#     sej,
#     how='inner',
#     left_on='sejour_id',
#     right_on='sejour_id'
# )
# print(sej_avec_urg_et_aval)
# print(sej_avec_urg_et_aval.shape)
#

# CHALLENGE2 suite en repartant de la correction J. Pasco
# avec dfply

# Etape 1 : liste des séjours avec entrée par les urgences et au moins 1 service d'aval
#%%
@dfpipe
def merge(df1, df2, how="left", left_on=None, right_on=None, suffixes=('_x', '_y')):
   return pd.merge(left=df1, right=df2, how=how, left_on=left_on, right_on=right_on, suffixes=suffixes)

sej_urg = (
       mvt >>
       group_by(X.sejour_id) >>
       mutate(n=n(X.id)) >>
       mask(X.n > 1) >>
       arrange(X.date_entree) >>
       merge(srv, left_on='service_id', right_on='id') >>
       mutate(first_parent_id=first(X.parent_id)) >>
       mask(X.first_parent_id == 1)
)

sej_urg2 = (
    sej_urg >>
    group_by(X.sejour_id) >>
    summarize(
        service_id=first(X.service_id),
        service_aval_id=nth(X.service_id, 2)
   )
)

# Etape 2 : extraire les documents des urgences
#%%
docs_urgence = (
       sej_urg2 >>
       merge(doc) >>  # sous entendu par sejour_id ET service_id
       mask(
           ~X.texte.isna(),
           X.categorie_id == 1
       ) >>
       select(
           X.sejour_id,
           X.service_id,
           X.service_aval_id,
           X.texte
       )
)

# Etape 3 : extraire le diagnostic des comptes rendus des urgences
#%%
diags = (
    docs_urgence >>
    mutate(
        diag_urg=X.texte.str.extract(
            r'\n\nAu total : (.*)\n\n',
            flags=(re.S + re.M)
        )
    ) >>
    mutate(
        ica=X.diag_urg.str.contains(
            pat=r'ICA|OAP|insuffisance cardiaque aig|décompensation cardiaque',
            regex=True
        )
    )
)

# Etape 4 : documents contenant les diagnostiques uniquement
#%%
docs_diag = (
    (
        doc >> rename(
            service_aval_id=X.service_id
        )
    ) >>
    mask(
        X.categorie_id == 5
    ) >>
    rename(
        document_id=X.id
    ) >>
    inner_join(
        diags,
        by=[
            'sejour_id',
            'service_aval_id'
            ]
    )
)

#%% joindre avec les données d'analyse
docs_diag_dat = (
    docs_diag >> 
    inner_join(
        dat,
        by='document_id'
    )
)

#%% joindre avec le thesaurus (sera utile pour lire un code I50)
docs_diag_dat_ths = (
    (
        docs_diag_dat >>
        rename(
            thesaurus_id=X.code_id
        )
    ) >>
    inner_join(
        (
            ths >> rename(
                thesaurus_id=X.id
            )
        ),
        by='thesaurus_id'
    )
)

#%% vérifier si le diagnostique après les urgences est
# une cardiopathie
docs_diag_dat_ths = (
    docs_diag_dat_ths >>
    mutate(
        ica2=(
            X.libelle.str.contains('I50')
        )
    )
)

#%% comparaison des deux diagnostiques (ica et ica2) :
# matrice de confusion
confusion = pd.crosstab(
    docs_diag_dat_ths['ica'],
    docs_diag_dat_ths['ica2']
)
confusion

#%%
