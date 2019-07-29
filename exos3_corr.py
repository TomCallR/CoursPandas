#%% Start
from dfply import *
# pip install mysql-connector-python
import mysql.connector as sql

conn = sql.connect(host='da.cefim-formation.org', database='cefim_datawarehouse', user='root', password='dadfba16')

pat = pd.read_sql('SELECT * FROM patient', conn)
sej = pd.read_sql('SELECT * FROM sejour', conn)
mvt = pd.read_sql('SELECT * FROM mouvement', conn)
doc = pd.read_sql('SELECT * FROM document', conn)
dat = pd.read_sql('SELECT * FROM data', conn)
srv = pd.read_sql('SELECT * FROM structure', conn)
ths = pd.read_sql('SELECT * FROM thesaurus', conn)





#%% CHALLENGE N°1
# Extraire la liste des patients qui avaient entre 20 et 70 ans à l'admission
# et dont le 1er mouvement était aux urgences

# consignes : SQL interdit ! se contenter des dataframes fournis ci-dessus



 #%% Etape 1 : séjours avec âge à l'admission entre 20 et 70 ans
from dateutil.relativedelta import relativedelta

@dfpipe
def merge(df1, df2, how="left", left_on=None, right_on=None, suffixes=('_x', '_y')):
    return pd.merge(left=df1, right=df2, how=how, left_on=left_on, right_on=right_on, suffixes=suffixes)

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


rs = (pat >>
     mask(~X.date_naissance.isna()) >>
     merge(sej,
           left_on='id',
           right_on='patient_id',
           suffixes=('_patient', '_sejour')) >>
     merge(mvt,
           left_on='id_sejour',
           right_on='sejour_id',
           suffixes=('_sejour', '_mouvement')) >>
     group_by(X.id_sejour) >>
     summarize(
         patient_id=first(X.id_patient),
         date_naissance=first(X.date_naissance),
         date_entree_sejour=first(X.date_entree_sejour),
         date_entree_mouvement=np.min(X.date_entree_mouvement),
         service_id=first(X.service_id),
     ) >>
     mutate(
         date_entree_sejour=if_else(
             X.date_entree_sejour.isna(),
             X.date_entree_mouvement,
             X.date_entree_sejour
         )
     ) >>  # on ne peut pas réutiliser les valeurs calculées au sein d'un même mutate
     mutate(
         age_admission=date_diff_annees(
             X.date_entree_sejour,
             X.date_naissance
         )
     ) >>
     mask(
         X.age_admission >= 20,
         X.age_admission <= 70
     )
 )

# Etape 2 : séjours ayant débuté par les urgences

id_patients = (srv >>
 mask(X.parent_id == 1) >>
 merge(rs, left_on='id', right_on='service_id') >>
 pull('patient_id') >>
 distinct())

pat >> mask(X.id.isin(id_patients))


#%%
