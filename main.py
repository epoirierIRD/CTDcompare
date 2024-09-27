#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 14:12:11 2024

@author: epoirier1 with help form ChatGPT
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from datetime import date, time, datetime
import matplotlib.dates as mdates
from fpdf import FPDF
import os

#################################################################################################################################
# Chargement des données
# Assurez-vous que chaque fichier contient au moins deux colonnes : 'date' et 'temperature'
# ce script permet de lire 3 fichiers csv venant d'uen intercomp à ste anne avec 2 RBR et 1 SBE
# Il sort les statistiques pour chaque paramètre qui est représenté dans les 3 instruments, les mets dans un PDF avec le graphique également
# il crée aussi un fichier indépendant avec le graphique
# Bug:
    # Si un paramètre est présent dans 2 fichiers seulement, il n'est pas représenté
#################################################################################################################################

# replace your path by the correct path where you store your files
rbr231853 = '/your_path/rbr_231853.csv'
rbr236135 = '/your_path/rbr_236135.csv'
sbe = '/your_path/sbe_time_corrected.csv'

#################################################################################################################################
#Gestion du format de l'heure
# attention du formatage est nécessaire avant pour fabriquer les fichiers csv d'entrée de ce script à partir des fichiers xlsx bruts de sortie des logiciels fabricants
#################################################################################################################################
# lecteur qui prend en compte les décimales sur le format d'heure
df1 = pd.read_csv(rbr231853, parse_dates=['date'], sep=';', date_parser=lambda x: pd.to_datetime(x, format='%Y-%m-%d %H:%M:%S,%f'))
df2 = pd.read_csv(rbr236135, parse_dates=['date'], sep=';',date_parser=lambda x: pd.to_datetime(x, format='%Y-%m-%d %H:%M:%S,%f'))
# attention ligne ci-dessous adaptée pour SBE
df3 = pd.read_csv(sbe, parse_dates=['date'], sep=',',date_parser=lambda x: pd.to_datetime(x, format='%Y-%m-%d %H:%M:%S.%f'))
# Ajouter le déphasage de 9 secondes à la colonne 'date' car la SBE avançait de 9sec pendant les opérations
df3['date'] = df3['date'] - pd.to_timedelta(9, unit='s')
df3.apply(lambda x: pd.to_numeric(x.str.replace(',', '.'), errors='coerce') if x.dtype == 'object' else x)

#################################################################################################################################
#Creation du dataframe global avec tous les instruments
#################################################################################################################################
# Fusionner les trois DataFrames sur la colonne 'date', ils sont tous à 0.5 sec
# on n'ajoute pas de suffixe car fait avant
# merge accepts only two df
merged_df = pd.merge(df1, df2 ,on='date', suffixes=('_rbr231853', '_rbr236135'))

# on va renommer les colonnes du df de la sbe avant merging sauf la colonne date
# Use rename to add a suffix to all columns except the one you want to exclude
df3 = df3.rename(columns=lambda x: f"{x}_sbeSOMLIT" if x != 'date' else x)

merged_df = pd.merge(merged_df,df3, on='date')

#################################################################################################################################
#Selection de la fenêtre temporelle d'intérêt
#################################################################################################################################
# # #Periode d'intérêt, en monitoring
# start = datetime(2024, 9, 12, 9, 52,40)
# end = datetime(2024, 9, 12, 9, 58,20)
# Periode d'intérêt, stable en monitoring mais courte
start = datetime(2024, 9, 12, 9, 57,00)
end = datetime(2024, 9, 12, 9, 58,20)
# Filtrer le DataFrame entre les deux dates
merged_df = merged_df[(merged_df['date'] >= start) & (merged_df['date'] <= end)]

#################################################################################################################################
#Sélection des paramètres à examiner métrologiquement
#################################################################################################################################
# Liste des paramètres à comparer
# Mettre _ pour comparer seulement le premier capteur de Tempé du RBR l'autre est Temperature.1, on l'exclut
#parameters = ['PAR']
parameters = ['Temperature_','Conductivity','Pressure','Dissolved O2 concentration','PAR','pH','Chlorophyll-a','FDOM','Turbidity','Sea pressure','Depth','Salinity','Speed of sound','Specific conductivity','Dissolved O2 saturation','Density anomaly']

# Définition des unités pour chaque paramètre

# Define units for each parameter
parameter_units = {
    'Temperature_':'°C',
    'Conductivity':'mS/cm',
    'Pressure':'dBar(ou m)',
    'Temperature(Coda T.ODO)':'°C',
    'Dissolved O2 concentration':'µmol/L',
    'PAR':'µMol/m2/s',
    'pH':'pH_units',
    'Chlorophyll-a':'µg/L',
    'FDOM':'ppb',
    'Turbidity':'FTU',
    'Sea pressure':'dBar(ou m)',
    'Depth':'m',
    'Salinity':'PSU',
    'Speed of sound':'m/s',
    'Specific conductivity':'µS/cm',
    'Dissolved O2 saturation':'%',
    'Density anomaly':'kg/m3'
}
# Display accuracy for each parameter from specs
nominal_accuracy_rbr = {
    'Temperature_':'±0.002°C',
    'Conductivity':'±0.003 mS/cm',
    'Pressure':'±0.05% Full Scale = ±0.375 dBar(ou m)',
    'Temperature(Coda T.ODO)':'±0.002 °C',
    'Dissolved O2 concentration':'Maximum of ±8μmol/L ',
    'PAR':'±5% of reading or ±1.4 µMol/m2/s',
    'pH':'Accuracy unknown pH_units',
    'Chlorophyll-a':'±5.0% full scale (±2.5 µg/L). Cal range [0-50] µg/L ',
    'FDOM':'±5.0% full scale (±25.0 ppb)',
    'Turbidity':'±5.0% full scale (±25.00 FTU)',
    'Sea pressure':'±0.05% Full Scale = ±0.375 dBar(ou m)',
    'Depth':'±0.05% Full Scale = ±0.375 dBar(ou m)',
    'Salinity':'estimated 0.01 PSU',
    'Speed of sound':'Calculated parameter m/s',
    'Specific conductivity':'Calculated parameter 3 µS/cm',
    'Dissolved O2 saturation':'±5% | fast%',
    'Density anomaly':'Calculated parameter kg/m3'}


# Remplacer les virgules par des points, puis convertir toutes les colonnes en float
merged_df = merged_df.apply(lambda x: pd.to_numeric(x.str.replace(',', '.'), errors='coerce') if x.dtype == 'object' else x)

################################################################################################################################
#!!!!!!!!!!!!!!!    MAIN au-dessous    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#################################################################################################################################
# This main will call functions from function.py file
# Assuming `merged_df` is the merged DataFrame with all instruments' data
# This command creates the stats csv files
calculate_stats(parameters, merged_df)

# On each parameter this function uses the csv file above and create a pdf 
# report with table, plot inside and independant png plot
for param in parameters:
    csv_file = f"{param}_comparison_stats.csv"
    # Tester si le fichier existe
    if not os.path.exists(csv_file):
        print(f"File {csv_file} not found, skipping {param}.")
        continue  # Revenir au début de la boucle si le fichier n'existe pas
    
    csv_to_pdf(csv_file, param, merged_df)
    
    
################################################################################################################################
#!!!!!!!!!!!!!!!    MAIN au dessus     !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#################################################################################################################################
    
  


