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
#Fonctions pour les stats et le plotting
#################################################################################################################################

def calculate_stats(parameters, df):
    """
    Calcule les statistiques pour chaque paramètre et génère un fichier CSV distinct par paramètre.

    Paramètres :
    - parameters : Liste des paramètres à analyser (e.g., ['temperature', 'conductivity', 'pressure']).
    - df : DataFrame contenant les données des instruments pour chaque paramètre.

    Retour :
    - Un fichier CSV pour chaque paramètre contenant les moyennes, écarts-types, moyennes des différences, et RMSE.
    """
    for param in parameters:
        # Filtrer les colonnes du paramètre pour chaque instrument
        param_cols = [col for col in df.columns if col.startswith(param)]

        # S'assurer qu'il y a au moins trois colonnes
        if len(param_cols) < 3:
            print(f"Skipping {param}: only {len(param_cols)} columns found. Expected at least 3.")
            print(f"Columns found: {param_cols}")
            continue  # Passer au paramètre suivant s'il y a moins de 3 colonnes

        # Calcul des moyennes et écarts-types pour chaque instrument
        stats_summary = {}
        for col in param_cols:
            stats_summary[col] = {
                'mean': df[col].mean(),
                'std': df[col].std()
            }

        # Liste pour stocker les résultats pour ce paramètre
        results = []

        # Ajouter les moyennes et écarts-types à la liste des résultats
        results.append([f"{param} - Instrument Stats", "", ""])
        for col in param_cols:
            results.append([col, "%.4f" % stats_summary[col]['mean'], "%.4f" % stats_summary[col]['std']])

        # Ajouter l'en-tête "Mean of Differences and RMSE" sur une seule ligne avec les colonnes Mean et RMSE
        results.append(["Mean of Differences and RMSE", "Mean of Differences", "RMSE"])

        # Calcul des différences moyennes et RMSE pour chaque paire d'instruments
        instrument_pairs = [(param_cols[0], param_cols[1]), (param_cols[0], param_cols[2]), (param_cols[1], param_cols[2])]

        for inst1, inst2 in instrument_pairs:
            # Calculer les différences entre les deux instruments
            differences = df[inst1] - df[inst2]

            # Calculer la moyenne des différences
            mean_diff = differences.mean()

            # Calculer le RMSE
            rmse = np.sqrt(np.mean(np.square(differences)))

            # Ajouter à la liste des résultats
            results.append([f"{inst1} - {inst2}", '%.4f' % mean_diff, '%.4f' % rmse])

        # Création du DataFrame des résultats
        results_df = pd.DataFrame(results, columns=["Instrument statistics", "Mean", "Standard Deviation"])

        # Générer un fichier CSV distinct pour ce paramètre
        csv_filename = f'{param}_comparison_stats.csv'
        results_df.to_csv(csv_filename, index=False)

        print(f"Results for {param} saved to {csv_filename}")
        
        print(results_df)


# Function to create a plot for the parameter and save it as an image
def plot_instruments(parameter, df, output_file):
    # Select the columns for the parameter
    cols = [col for col in df.columns if parameter in col]
    
    # Plot the data for the three instruments
    plt.figure(figsize=(8, 6))
    for col in cols:
        plt.plot(df['date'], df[col], label=col)
    
    plt.title(f"{parameter.capitalize()} Comparison")
    plt.xlabel("Time")
    plt.ylabel(parameter.capitalize())
    plt.legend()
    plt.grid(True)
    # Format the x-axis to show date and time. Ligne importante sinon les heures affichees sont fausses
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    #plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    #plt.gcf().autofmt_xdate()  # Automatically format date labels to avoid overlap
    # Save the plot to a file
    plt.savefig(output_file)
    plt.close()


# Fonction pour ajouter les statistiques CSV dans un PDF
def csv_to_pdf(csv_filename, param_name, merged_df):
    """
    Lire un fichier CSV et l'insérer dans un tableau PDF.
    
    - csv_filename : Le fichier CSV contenant les statistiques.
    - pdf_filename : Le fichier PDF à créer.
    - param_name : Le nom du paramètre à utiliser pour le titre du tableau.
    """
    
    # Lire les données du CSV avec pandas
    df = pd.read_csv(csv_filename, skiprows=[1])
    
    
    # Créer un objet PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Titre du PDF (le nom du paramètre étudié)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, f"Statistiques de comparaison pour {param_name}", ln=True, align="C")
    
    # Add units for the parameter
    unit = parameter_units.get(param_name, '')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Units: {unit}", ln=True, align='C')
    
    # Add nominal accuracy from specs for the parameter
    accuracy = nominal_accuracy_rbr.get(param_name, 'N/A')
    pdf.cell(200, 10, f"Nominal accuracy from specs: {accuracy}", ln=True, align='C')

    # Ajouter un espace
    pdf.ln(10)

    # Créer un tableau avec les données du CSV
    pdf.set_font("Arial", size=10)
    
    # Largeurs des colonnes
    col_widths = [100, 40, 40]

    # En-têtes du tableau (colonnes du CSV)
    for i, col in enumerate(df.columns):
        pdf.cell(col_widths[i], 10, col, border=1, align='C')
    pdf.ln()

    # Ajouter les lignes de données
    for _, row in df.iterrows():
        for i, col in enumerate(df.columns):
            pdf.cell(col_widths[i], 10, str(row[col]), border=1, align='C')
        pdf.ln()

    # # Add some space before the plot
    # pdf.ln(10)
    
    # Generate and save the plot
    plot_filename = f"{param_name}_plot.png"
    plot_instruments(param_name, merged_df, plot_filename)
    
    # Insert the plot image into the PDF
    pdf.image(plot_filename, x=10, y=None, w=190)  # Adjust size and position as necessary
   
    # Save the PDF to file with the parameter as the filename
    pdf_output = f"{param_name}_comparison_stats.pdf"
    pdf.output(pdf_output)
    print(f"PDF saved as {pdf_output}")
   
    # Save the PDF to file with the parameter as the filename
    pdf_output = f"{param_name}_comparison_stats.pdf"
    pdf.output(pdf_output)
    print(f"PDF saved as {pdf_output}")

