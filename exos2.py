#%%
import pandas as pd
import numpy as np
import mysql.connector as sql
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

#%% les pipes
pat >> head(10)
pat >> head(5) >> tail(3)

#%%
pat2 = pat
pat2 >> head(5) >> tail(3)
# renvoie le résultat dans pat2 : attention fonctionne en
# tout ou rien et ne mettre un égal qu'au début
pat2 >>= head(5) >> tail(3)

#%% selectionner des colonnes : select, drop
pat >> select(X.nom, X.sexe)
pat >> select(['nom', 'sexe'])
pat >> select(1, 4)
pat >> select(~X.nom, ~X.sexe)
pat >> drop(X.nom, X.sexe)

#%% aides à la sélection (pour select et drop)
pat >> select(starts_with('date_'))
pat >> select(ends_with('nom'))
pat >> select(contains('nom'))
pat >> select(columns_between('nom', X.statut_vital))
pat >> select(columns_to(5))
pat >> select(1, columns_from('statut_vital'))

#%% renommer les colonnes
pat >> rename(
    a=X.nom,
    b=X.prenom
)

#%% réordonner les colonnes
pat >> select(X.nom, X.prenom, everything())

#%% réordonner les lignes
pat >> arrange(X.statut_vital, X.nom)
pat >> arrange(X.statut_vital, X.nom, ascending=False)

#%% filtrer les lignes par position
doc >> row_slice([1, 3, 7])

#%% échantillon aléatoire
doc >> sample(frac=0.01)
doc >> sample(n=50)

#%% valeurs distinctes selon une/des colonnes
doc >> distinct(X.service_id, X.categorie_id)

#%% filtrer les lignes
doc >> mask(
    X.service_id == 72,
    X.categorie_id.isin([1, 3, 5, 7])
    )

#%% filtrer les lignes, avec un ou
doc >> mask(
    (X.service_id == 72) |
    (X.categorie_id.isin([1, 3, 5, 7]))
    )

#%% mask avec comparateur <
doc >> mask(X.service_id < X.sejour_id)

#%% extraire une unique colonne
doc >> pull('patient_id')

#%% modifier des colonnes (ajout / remplacement)
doc >> mutate(
    somme=X.patient_id + X.service_id,
    division=X.patient_id / X.service_id
) >> select (
    X.somme,
    X.division
)

#%% select + mutate = transmute
doc >> transmute(
    somme=X.patient_id + X.service_id,
    division=X.patient_id / X.service_id
)

#%% groupage / aggrégation : sans aggrégation d'abord
doc >> group_by(
    X.categorie_id
    ) >> transmute(
        n_documents=n(X.id),
        n_sejours=n_distinct(X.sejour_id),
        id_doc_suivant=lead(X.id),
        id_doc_precedent=lag(X.id)
    )

#%% groupage / aggrégation : avec aggrégation
doc >> group_by(
    X.categorie_id
    ) >> summarize(
        n_documents=n(X.id),
        n_sejours=n_distinct(X.sejour_id)
    )

#%% group_by force les autres verbes à respecter les regroupements
doc >> group_by(
    X.categorie_id
    ) >> arrange(
        X.titre
    ) >> select(
        X.categorie_id,
        X.titre
    )

#%% slicing au sein d'un groupe
doc >> group_by(
        X.categorie_id
    ) >> arrange(
        X.titre
    ) >> row_slice(2)

#%% si pas de group_by : resume l'ensemble du DFrame
doc >> group_by(
        X.categorie_id
    ) >> summarize(
        n=n(X.id),
        moy=mean(X.sejour_id),
        premier_titre=first(X.titre),
        deuxieme_titre=nth(X.titre, 2),
        avant_dernier_titre=nth(X.titre, -2),
        dernier_titre=last(X.titre)
    )

#%% agrégation via des liste de fonctions d'aggrégation
doc >> group_by(
        X.categorie_id
    ) >> summarize_each(
        [np.mean, np.min, np.max],
        X.sejour_id, X.service_id
    )

#%% table pivot : d'abord 'linéariser' le tableau diamonds
elongated = diamonds >> gather(
        'variable',
        'value',
        ['price', 'depth', 'x', 'y', 'z'],  # si omis, prend tout
        add_id=True
    )
widened = elongated >> spread(
        X.variable, X.value
    )

#%% jointures
pat >> rename(
    patient_id=X.id
    ) >> left_join(sej)

#%% écriture d'une fonction avec une ornementation @defpipe pour pouvoir
# utiliser dans un pipe
@dfpipe
def merge(
        df1,
        df2,
        how="left",
        left_on=None,
        right_on=None):
    return pd.merge(
        left=df1,
        right=df2,
        how=how,
        left_on=left_on,
        right_on=right_on
    )
pat >> merge(
        sej,
        left_on='id',
        right_on='patient_id'
    )

#%%
