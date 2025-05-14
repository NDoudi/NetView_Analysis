import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet
from prophet.plot import plot_plotly
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="NetView : Analyse des Logs Windows", layout="wide")

# Ajouter une section dans la sidebar
st.sidebar.markdown("<h4 style='text-align: center;'>NetView by NetVirtSys</h4>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center;'>NetView est une solution de supervision et de gestion proactive des systèmes informatiques, conçue pour aider à maintenir la performance et la sécurité des infrastructures.</p>", unsafe_allow_html=True)

st.sidebar.title("Menu")
page = st.sidebar.radio("Aller à", ["📊 Statistiques Logs", "🔮 Prédictions"])

@st.cache_data(show_spinner="Chargement des données CSV...")
def charger_donnees(csv_file):
    #df = pd.read_csv(csv_file, encoding='utf-8-sig')
    df = pd.read_csv(csv_file, encoding='cp1252')
    df['TimeCreated'] = pd.to_datetime(df['TimeCreated'], errors='coerce')
    df = df.dropna(subset=['TimeCreated'])
    return df

uploaded_file = st.sidebar.file_uploader("Téléversez un fichier CSV de logs", type=["csv"])

if uploaded_file:
    df = charger_donnees(uploaded_file)

    if page == "📊 Statistiques Logs":
        st.title("📊 Statistiques des Logs")

        # Nombre total de logs et période
        st.subheader("📌 Statistiques générales")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Nombre total de logs", len(df))
        with col2:
            st.metric("Période couverte", f"{df['TimeCreated'].min().date()} → {df['TimeCreated'].max().date()}")

        # Nombre d'événements par niveau (erreur, information, etc.)
        niveau_counts = df['LevelDisplayName'].value_counts()
        log_counts = df['LogName'].value_counts()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Nombre d'événements par type")
            st.bar_chart(niveau_counts)

        with col2:
            st.subheader("📋 Nombre d'événements par catégorie de logs")
            st.bar_chart(log_counts)

        # ProviderName les plus fréquents lors des erreurs
        st.subheader("🚨 ProviderName les plus fréquents en cas d'erreurs")
        errors_df = df[df['LevelDisplayName'].str.contains("Erreurs", case=False, na=False)]
        top_providers = errors_df['ProviderName'].value_counts().head(10)

        # Crée un DataFrame à partir de top_providers
        top_providers_df = top_providers.reset_index()
        top_providers_df.columns = ['ProviderName', 'Erreurs']

        # Affiche la table
        st.dataframe(top_providers_df)

        # Graphique des providers d'erreurs
        fig_providers = px.bar(top_providers_df, x='ProviderName', y='Erreurs', 
                            labels={'ProviderName': 'ProviderName', 'Erreurs': 'Erreurs'},
                            title="Top 10 des sources d'erreurs")
        st.plotly_chart(fig_providers, use_container_width=True)

        # Fréquence des événements par mois et par type
        df['Mois'] = df['TimeCreated'].dt.to_period('M').astype(str)
        freq_mois = df.groupby(['Mois', 'LevelDisplayName']).size().unstack(fill_value=0)

        st.subheader("📆 Nombre d'événements par mois et type")
        st.line_chart(freq_mois)

        # Occurrences par LevelDisplayName (détails supplémentaires)
        st.subheader("📊 Occurrences par type")
        level_counts = df['LevelDisplayName'].value_counts()
        st.dataframe(level_counts.rename_axis("Type").reset_index(name="Occurrences"))
        fig_level = px.bar(level_counts, x=level_counts.index, y=level_counts.values, labels={'x': 'Type', 'y': "Occurrences"}, title="Événements par catégorie")
        st.plotly_chart(fig_level, use_container_width=True)

        # Logs par LogName (catégories système)
        st.subheader("📋 Répartition des logs par catégorie système (LogName)")
        log_counts = df['LogName'].value_counts()
        st.dataframe(log_counts.rename_axis("LogName").reset_index(name="Occurrences"))
        fig_log = px.pie(names=log_counts.index, values=log_counts.values, title="Logs par catégorie")
        st.plotly_chart(fig_log, use_container_width=True)

        # ProviderName les plus fréquents lors des erreurs
        st.subheader("🚨 ProviderName les plus fréquents en cas d'erreurs")
        errors_df = df[df['LevelDisplayName'].str.contains("Erreur", case=False, na=False)]
        top_providers = errors_df['ProviderName'].value_counts().head(10)
        st.dataframe(top_providers.rename_axis("ProviderName").reset_index(name="Erreurs"))
        fig_providers = px.bar(top_providers, x=top_providers.index, y=top_providers.values, labels={'x': 'ProviderName', 'y': 'Erreurs'}, title="Top 10 des sources d'erreurs")
        st.plotly_chart(fig_providers, use_container_width=True)

        # Événements par mois et type
        st.subheader("📅 Nombre d'événements par mois et par type")
        df['MonthStr'] = df['TimeCreated'].dt.strftime('%Y-%m')
        events_by_month = df.groupby(['MonthStr', 'LevelDisplayName']).size().unstack(fill_value=0)
        st.dataframe(events_by_month)
        fig_month = px.line(events_by_month, labels={'value': 'Nombre d\'événements', 'Month': 'Mois'}, title="Évolution mensuelle des événements")
        st.plotly_chart(fig_month, use_container_width=True)

    elif page == "🔮 Prédictions":
        st.title("🔮 Prédiction d'événements futurs avec Prophet")

        # Sélection de la catégorie à prédire
        categorie = st.selectbox("Sélectionnez le type d'événement à prédire", df['LevelDisplayName'].unique())

        horizon = st.slider("Nombre de jours à prédire", 7, 90, 30)

        df_categorie = df[df['LevelDisplayName'] == categorie]
        df_categorie = df_categorie.copy()

        # Préparer les données pour Prophet
        df_prophet = df_categorie.resample('D', on='TimeCreated').size().reset_index(name='y')
        df_prophet.rename(columns={'TimeCreated': 'ds'}, inplace=True)

        if len(df_prophet) < 2:
            st.warning("Pas assez de données pour effectuer une prédiction.")
        else:
            # Obtenir la dernière date des données
            last_date = df['TimeCreated'].max()
            
            model = Prophet()

            model.fit(df_prophet)

            # Créer le dataframe futur en commençant au lendemain de la dernière date
            start_date = last_date + pd.Timedelta(days=1)
            futur = pd.DataFrame({'ds': pd.date_range(start=start_date, periods=horizon)})
            
            forecast = model.predict(futur)

            # Ajouter la protection contre les valeurs négatives et arrondir les prédictions
            forecast['yhat'] = forecast['yhat'].clip(lower=0)  # Empêche les valeurs négatives
            forecast['yhat'] = forecast['yhat'].round(0).astype(int)  # Arrondir les valeurs à des entiers

            st.subheader("📈 Prévision avec Prophet")
            
            # Pour le graphique, nous devons inclure l'historique pour la visualisation
            full_forecast = model.predict(model.make_future_dataframe(periods=horizon))
            
            # Créer un graphique personnalisé avec Plotly
            fig = go.Figure()
            
            # Ajouter les données historiques
            hist_dates = df_prophet['ds']
            hist_values = df_prophet['y']
            fig.add_trace(go.Scatter(
                x=hist_dates, 
                y=hist_values,
                mode='markers+lines',
                name='Données historiques',
                line=dict(color='blue')
            ))
            
            # Ajouter les prédictions futures
            future_dates = forecast['ds']
            future_values = forecast['yhat']
            fig.add_trace(go.Scatter(
                x=future_dates, 
                y=future_values,
                mode='lines',
                name='Prédictions',
                line=dict(color='red', dash='dash')
            ))
            
            # Ajouter l'intervalle de confiance
            fig.add_trace(go.Scatter(
                x=forecast['ds'].tolist() + forecast['ds'].tolist()[::-1],
                y=forecast['yhat_upper'].tolist() + forecast['yhat_lower'].tolist()[::-1],
                fill='toself',
                fillcolor='rgba(255,0,0,0.1)',
                line=dict(color='rgba(255,0,0,0)'),
                name='Intervalle de confiance'
            ))
            
            # Ajouter une ligne verticale à la date actuelle
            fig.add_shape(
                type="line",
                x0=last_date,
                y0=0,
                x1=last_date,
                y1=max(max(hist_values), forecast['yhat'].max()) * 1.1,
                line=dict(color="green", width=2, dash="dash"),
            )
            
            fig.add_annotation(
                x=last_date,
                y=max(max(hist_values), forecast['yhat'].max()) * 1.05,
                text="Dernière date des logs",
                showarrow=True,
                arrowhead=1,
            )
            
            fig.update_layout(
                title="Prévision des événements",
                xaxis_title="Date",
                yaxis_title="Nombre d'événements",
                legend_title="Légende",
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("📋 Données de prévision")
            forecast_display = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
            forecast_display.columns = ['Date', 'Prédiction', 'Limite inférieure', 'Limite supérieure']
            st.dataframe(forecast_display)

#Prévision des événements pour le fournisseur
######################################################################

          # Sélection de la catégorie à prédire
            categorie = st.selectbox("Sélectionnez le type d'événement à prédire", df['LevelDisplayName'].unique(), key="categorie_selectbox")

            # Sélection du fournisseur spécifique
            fournisseur = st.selectbox("Sélectionnez un fournisseur", df['ProviderName'].unique(), key="fournisseur_selectbox")


            horizon = st.slider("Nombre de jours à prédire", 7, 90, 30, key="horizon_slider")

            df_fournisseur = df[df['ProviderName'] == fournisseur]
            df_categorie = df_fournisseur[df_fournisseur['LevelDisplayName'] == categorie]
            df_categorie = df_categorie.copy()
            df_categorie['TimeCreated'] = pd.to_datetime(df_categorie['TimeCreated'])

            df_categorie.set_index('TimeCreated', inplace=True)
            # Préparer les données pour Prophet
            df_prophet = df_categorie.resample('D').size().reset_index(name='y')
            df_prophet.rename(columns={'TimeCreated': 'ds'}, inplace=True)

            if len(df_prophet) < 2:
                st.warning("Pas assez de données pour effectuer une prédiction.")
            else:
                # Obtenir la dernière date des données
                last_date = df['TimeCreated'].max()
                
                model = Prophet()

                model.fit(df_prophet)

                # Créer le dataframe futur en commençant au lendemain de la dernière date
                start_date = last_date + pd.Timedelta(days=1)
                futur = pd.DataFrame({'ds': pd.date_range(start=start_date, periods=horizon)})
                
                forecast = model.predict(futur)

                # Ajouter la protection contre les valeurs négatives et arrondir les prédictions
                forecast['yhat'] = forecast['yhat'].clip(lower=0)  # Empêche les valeurs négatives
                forecast['yhat'] = forecast['yhat'].round(0).astype(int)  # Arrondir les valeurs à des entiers

                st.subheader(f"📈 Prévision des événements pour le fournisseur : {fournisseur}")
                
                # Pour le graphique, nous devons inclure l'historique pour la visualisation
                full_forecast = model.predict(model.make_future_dataframe(periods=horizon))
                
                # Créer un graphique personnalisé avec Plotly
                fig = go.Figure()
                
                # Ajouter les données historiques
                hist_dates = df_prophet['ds']
                hist_values = df_prophet['y']
                fig.add_trace(go.Scatter(
                    x=hist_dates, 
                    y=hist_values,
                    mode='markers+lines',
                    name='Données historiques',
                    line=dict(color='blue')
                ))
                
                # Ajouter les prédictions futures
                future_dates = forecast['ds']
                future_values = forecast['yhat']
                fig.add_trace(go.Scatter(
                    x=future_dates, 
                    y=future_values,
                    mode='lines',
                    name='Prédictions',
                    line=dict(color='red', dash='dash')
                ))
                
                # Ajouter l'intervalle de confiance
                fig.add_trace(go.Scatter(
                    x=forecast['ds'].tolist() + forecast['ds'].tolist()[::-1],
                    y=forecast['yhat_upper'].tolist() + forecast['yhat_lower'].tolist()[::-1],
                    fill='toself',
                    fillcolor='rgba(255,0,0,0.1)',
                    line=dict(color='rgba(255,0,0,0)'),
                    name='Intervalle de confiance'
                ))
                
                # Ajouter une ligne verticale à la date actuelle
                fig.add_shape(
                    type="line",
                    x0=last_date,
                    y0=0,
                    x1=last_date,
                    y1=max(max(hist_values), forecast['yhat'].max()) * 1.1,
                    line=dict(color="green", width=2, dash="dash"),
                )
                
                fig.add_annotation(
                    x=last_date,
                    y=max(max(hist_values), forecast['yhat'].max()) * 1.05,
                    text="Dernière date des logs",
                    showarrow=True,
                    arrowhead=1,
                )
                
                fig.update_layout(
                    title=f"Prévision des événements pour {fournisseur}",
                    xaxis_title="Date",
                    yaxis_title="Nombre d'événements",
                    legend_title="Légende",
                    hovermode="x unified"
                )
                
                st.plotly_chart(fig, use_container_width=True)

                st.subheader("📋 Données de prévision")
                forecast_display = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
                forecast_display.columns = ['Date', 'Prédiction', 'Limite inférieure', 'Limite supérieure']
                st.dataframe(forecast_display)

else:
    st.warning("📁 Veuillez téléverser un fichier CSV contenant des logs pour commencer.")
