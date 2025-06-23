import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet
from prophet.plot import plot_plotly
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime


 
st.set_page_config(page_title="NetView : Analyse des Logs Windows", layout="wide")

# --- Injecter CSS personnalisé pour style pro ---
st.markdown(
    """
    <style>
    /* Palette pro */
    :root {
        --primary-color:   #1a4f6a;  /* Bleu foncé profond, proche de la teinte la plus sombre du logo */
        --primary-light:   #5eb0e6;  /* Bleu clair ciel, pour les accents et hover */
        --secondary-color: #5dade2;  /* Bleu très clair, pour les fonds secondaires */
        --background-color:#f7fafc;  /* Blanc très légèrement bleuté */
        --card-bg:         #ffffff;  /* Blanc pur pour les cartes */
        --text-color:      #0f2c3f;  /* Bleu très sombre presque noir, pour le texte */
        --accent-color:    #3da4f7;  /* Bleu vif et dynamique, pour les boutons et highlights */
    }


    /* Fond et typo générale */
    .main {
        background-color: var(--background-color);
        color: var(--text-color);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        padding: 20px 40px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: var(--secondary-color);
        color: white;
        padding-top: 20px;
        font-weight: 600;
        font-size: 18px;
        border-top-right-radius: 20px;
        border-bottom-right-radius: 20px;
    }

    /* Sidebar titles */
    .sidebar .block-container h1, 
    .sidebar .block-container h2, 
    .sidebar .block-container h3 {
        color: white !important;
    }

    /* Sidebar radio buttons */
    .stRadio > div > label {
        font-weight: 600;
        font-size: 16px;
        padding: 6px 12px;
        border-radius: 10px;
        margin-bottom: 8px;
        transition: background-color 0.3s ease;
        cursor: pointer;
    }
    .stRadio > div > label:hover {
        background-color: var(--primary-color);
        color: white;
    }
    /* Radio selected */
    input[type="radio"]:checked + label {
        background-color: var(--primary-color) !important;
        color: white !important;
        font-weight: 700;
    }

    /* Upload file button */
    .stFileUploader > label {
        font-weight: 700;
        font-size: 16px;
        color: var(--primary-color);
    }

    /* Cards styles */
    .card {
        background-color: var(--card-bg);
        box-shadow: 0 4px 12px rgb(0 0 0 / 0.1);
        border-radius: 18px;
        padding: 24px;
        margin-bottom: 24px;
        transition: transform 0.3s ease;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgb(0 0 0 / 0.15);
    }

    /* Metrics */
    .stMetric > div > div {
        font-weight: 700;
        font-size: 28px;
        color: var(--primary-color);
    }

    /* Headers */
    h1, h2, h3 {
        font-weight: 700;
        color: var(--secondary-color);
        margin-bottom: 12px;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        font-weight: 700 !important;
        font-size: 18px !important;
        color: var(--secondary-color) !important;
    }

    /* Dataframe style */
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden;
    }

    /* Sliders */
    div[data-baseweb="slider"] > div > div > div {
        background-color: var(--primary-color);
    }

    /* Plotly charts background */
    .js-plotly-plot .plotly {
        background: var(--card-bg) !important;
        border-radius: 16px !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

 
# Charger les données CSV avec cache
@st.cache_data(show_spinner="Chargement des données CSV...")
def charger_donnees(csv_file):
    df = pd.read_csv(csv_file, encoding='cp1252')
    df['TimeCreated'] = pd.to_datetime(df['TimeCreated'], errors='coerce', dayfirst=True)
    df = df.dropna(subset=['TimeCreated'])
    return df

# Initialisation de la variable globale df_logs vide
df_logs = pd.DataFrame()

 

# Sidebar content with expander and better spacing
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color: white; margin-bottom: 12px;'>NetView by NetVirtSys</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color: #a0cfc6;'>Supervision & gestion proactive des systèmes informatiques</p>", unsafe_allow_html=True)
    st.title("Menu")
    page = st.radio("Navigation", ["📊 Statistiques Logs", "🔮 Prédictions","💬 Chat intelligent"], index=0, label_visibility="collapsed")

    with st.expander("📁 Téléversement des logs", expanded=True):
        uploaded_file = st.file_uploader("Téléversez un fichier CSV de logs", type=["csv"])

# Charger les données CSV avec cache
@st.cache_data(show_spinner="Chargement des données CSV...")
def charger_donnees(csv_file):
    df = pd.read_csv(csv_file, encoding='cp1252')
    df['TimeCreated'] = pd.to_datetime(df['TimeCreated'], errors='coerce',dayfirst=True)
    df = df.dropna(subset=['TimeCreated'])
    return df

if uploaded_file:
    df = charger_donnees(uploaded_file)

    if page == "📊 Statistiques Logs":
        st.title("📊 Statistiques des Logs Windows")
        st.markdown("---")

        # Section statistiques générales
        with st.container():
            st.subheader("📌 Statistiques générales")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Nombre total de logs", len(df))
            with col2:
                st.metric("Période couverte", f"{df['TimeCreated'].min().date()} → {df['TimeCreated'].max().date()}")

        st.markdown("---")


        # Événements par niveau et catégorie avec cards
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                with st.container():
                    st.subheader("📊 Événements par type")
                    niveau_counts = df['LevelDisplayName'].value_counts()
                    with st.container():
                        st.bar_chart(niveau_counts)
            with col2:
                with st.container():
                    st.subheader("📋 Événements par catégorie de logs")
                    log_counts = df['LogName'].value_counts()
                    with st.container():
                        st.bar_chart(log_counts)

        st.markdown("---")

        # Top Providers erreurs dans card
        with st.container():
            st.subheader("🚨 Top 10 Providers en cas d'erreurs")
            errors_df = df[df['LevelDisplayName'].str.contains("Erreur", case=False, na=False)]
            top_providers = errors_df['ProviderName'].value_counts().head(10)
            top_providers_df = top_providers.reset_index()
            top_providers_df.columns = ['ProviderName', 'Erreurs']
            st.dataframe(top_providers_df, use_container_width=True)
            fig_providers = px.bar(top_providers_df, x='ProviderName', y='Erreurs', 
                                labels={'ProviderName': 'ProviderName', 'Erreurs': 'Erreurs'},
                                title="Top 10 des sources d'erreurs",
                                template="plotly_white",
                                color_discrete_sequence=["#2a9d8f"])
            st.plotly_chart(fig_providers, use_container_width=True)

        st.markdown("---")

        # Fréquence événements par mois et type
        with st.container():
            st.subheader("📆 Événements par mois et type")
            df['Mois'] = df['TimeCreated'].dt.to_period('M').astype(str)
            freq_mois = df.groupby(['Mois', 'LevelDisplayName']).size().unstack(fill_value=0)
            st.line_chart(freq_mois)

        st.markdown("---")

        # Occurrences par type dans un expander
        with st.expander("📊 Détails : occurrences par type"):
            level_counts = df['LevelDisplayName'].value_counts()
            st.dataframe(level_counts.rename_axis("Type").reset_index(name="Occurrences"))
            fig_level = px.bar(level_counts, x=level_counts.index, y=level_counts.values, 
                               labels={'x': 'Type', 'y': "Occurrences"}, 
                               title="Événements par catégorie",
                               template="plotly_white",
                               color_discrete_sequence=["#264653"])
            st.plotly_chart(fig_level, use_container_width=True)

        st.markdown("---")

        # Répartition logs par catégorie système
        with st.expander("📋 Répartition des logs par catégorie système (LogName)"):
            log_counts = df['LogName'].value_counts()
            st.dataframe(log_counts.rename_axis("LogName").reset_index(name="Occurrences"))
            fig_log = px.pie(names=log_counts.index, values=log_counts.values, title="Logs par catégorie",
                             template="plotly_white",
                             color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig_log, use_container_width=True)

        st.markdown("---")

        # Top Providers erreurs (redondance volontaire)
        with st.expander("🚨 Détails : ProviderName les plus fréquents lors d'erreurs"):
            errors_df = df[df['LevelDisplayName'].str.contains("Erreur", case=False, na=False)]
            top_providers = errors_df['ProviderName'].value_counts().head(10)
            st.dataframe(top_providers.rename_axis("ProviderName").reset_index(name="Erreurs"))
            fig_providers = px.bar(top_providers, x=top_providers.index, y=top_providers.values, 
                                  labels={'x': 'ProviderName', 'y': 'Erreurs'}, 
                                  title="Top 10 des sources d'erreurs",
                                  template="plotly_white",
                                  color_discrete_sequence=["#e76f51"])
            st.plotly_chart(fig_providers, use_container_width=True)

        st.markdown("---")

        # Événements par mois et type en table et graphique
        with st.expander("📅 Évolution mensuelle des événements"):
            df['MonthStr'] = df['TimeCreated'].dt.strftime('%Y-%m')
            events_by_month = df.groupby(['MonthStr', 'LevelDisplayName']).size().unstack(fill_value=0)
            st.dataframe(events_by_month)
            fig_month = px.line(events_by_month, labels={'value': 'Nombre d\'événements', 'Month': 'Mois'}, 
                                title="Évolution mensuelle des événements",
                                template="plotly_white",
                                color_discrete_sequence=px.colors.qualitative.T10)
            st.plotly_chart(fig_month, use_container_width=True)

        # --- Carte de chaleur : fréquence des logs par jour et heure ---
        with st.expander("🔥 Carte de chaleur : Fréquence des logs par jour/heure"):
            st.subheader("📆 Analyse temporelle des événements")
            
            df['Heure'] = df['TimeCreated'].dt.hour
            df['Date'] = df['TimeCreated'].dt.date

            heatmap_data = df.groupby(['Date', 'Heure']).size().unstack(fill_value=0)

            fig_heatmap = px.imshow(
                heatmap_data.T,
                labels=dict(x="Date", y="Heure", color="Nombre d'événements"),
                aspect="auto",
                color_continuous_scale="YlOrRd",
                title="Intensité des événements par heure et par jour"
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)

    elif page == "🔮 Prédictions":
        st.title("🔮 Prédiction d'événements futurs avec Prophet")
        st.markdown("---")

        # Sélection du type d'événement à prédire dans un expander
        with st.expander("📌 Sélection du type d'événement à prédire", expanded=True):
            categorie = st.selectbox("Type d'événement", df['LevelDisplayName'].unique())

        horizon = st.slider("Nombre de jours à prédire", 7, 90, 30)

        df_categorie = df[df['LevelDisplayName'] == categorie].copy()

        df_prophet = df_categorie.resample('D', on='TimeCreated').size().reset_index(name='y')
        df_prophet.rename(columns={'TimeCreated': 'ds'}, inplace=True)

        if len(df_prophet) < 2:
            st.warning("Pas assez de données pour effectuer une prédiction.")
        else:
            last_date = df['TimeCreated'].max()
            model = Prophet()
            model.fit(df_prophet)
            start_date = last_date + pd.Timedelta(days=1)
            futur = pd.DataFrame({'ds': pd.date_range(start=start_date, periods=horizon)})
            forecast = model.predict(futur)
            forecast['yhat'] = forecast['yhat'].clip(lower=0).round(0).astype(int)

            st.subheader("📈 Prévision avec Prophet")

            # Graphique complet historique + prédictions
            full_forecast = model.predict(model.make_future_dataframe(periods=horizon))
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_prophet['ds'], y=df_prophet['y'],
                mode='markers+lines', name='Données historiques', line=dict(color='#264653')))
            fig.add_trace(go.Scatter(
                x=forecast['ds'], y=forecast['yhat'],
                mode='lines', name='Prédictions', line=dict(color='#e76f51', dash='dash')))
            fig.add_trace(go.Scatter(
                x=forecast['ds'].tolist() + forecast['ds'].tolist()[::-1],
                y=forecast['yhat_upper'].tolist() + forecast['yhat_lower'].tolist()[::-1],
                fill='toself', fillcolor='rgba(231, 111, 81,0.15)', line=dict(color='rgba(0,0,0,0)'),
                name='Intervalle de confiance'))

            fig.add_shape(type="line", x0=last_date, y0=0, x1=last_date,
                          y1=max(max(df_prophet['y']), forecast['yhat'].max()) * 1.1,
                          line=dict(color="#2a9d8f", width=3, dash="dash"))

            fig.add_annotation(x=last_date,
                               y=max(max(df_prophet['y']), forecast['yhat'].max()) * 1.05,
                               text="Dernière date des logs", showarrow=True, arrowhead=1)

            fig.update_layout(
                title="Prévision des événements",
                xaxis_title="Date",
                yaxis_title="Nombre d'événements",
                legend_title="Légende",
                hovermode="x unified",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
            

            st.subheader("📋 Données de prévision")
            forecast_display = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
            forecast_display.columns = ['Date', 'Prédiction', 'Limite inférieure', 'Limite supérieure']
            st.dataframe(forecast_display)

        # --- Prévision par fournisseur ---
        with st.expander("🔎 Prévision par fournisseur"):
            categorie_f = st.selectbox("Type d'événement (fournisseur)", df['LevelDisplayName'].unique(), key="categorie_selectbox")
            fournisseur = st.selectbox("Fournisseur", df['ProviderName'].unique(), key="fournisseur_selectbox")
            horizon_f = st.slider("Nombre de jours à prédire (fournisseur)", 7, 90, 30, key="horizon_slider")

            df_fournisseur = df[df['ProviderName'] == fournisseur]
            df_cat_fourn = df_fournisseur[df_fournisseur['LevelDisplayName'] == categorie_f].copy()
            df_cat_fourn['TimeCreated'] = pd.to_datetime(df_cat_fourn['TimeCreated'])
            df_cat_fourn.set_index('TimeCreated', inplace=True)

            df_prophet_f = df_cat_fourn.resample('D').size().reset_index(name='y')
            df_prophet_f.rename(columns={'TimeCreated': 'ds'}, inplace=True)

            if len(df_prophet_f) < 2:
                st.warning("Pas assez de données pour effectuer une prédiction.")
            else:
                last_date = df['TimeCreated'].max()
                model_f = Prophet()
                model_f.fit(df_prophet_f)
                start_date_f = last_date + pd.Timedelta(days=1)
                futur_f = pd.DataFrame({'ds': pd.date_range(start=start_date_f, periods=horizon_f)})
                forecast_f = model_f.predict(futur_f)
                forecast_f['yhat'] = forecast_f['yhat'].clip(lower=0).round(0).astype(int)

                st.subheader(f"📈 Prévision des événements pour le fournisseur : {fournisseur}")

                fig_f = go.Figure()
                fig_f.add_trace(go.Scatter(
                    x=df_prophet_f['ds'], y=df_prophet_f['y'],
                    mode='markers+lines', name='Données historiques', line=dict(color='#264653')))
                fig_f.add_trace(go.Scatter(
                    x=forecast_f['ds'], y=forecast_f['yhat'],
                    mode='lines', name='Prédictions', line=dict(color='#e76f51', dash='dash')))
                fig_f.add_trace(go.Scatter(
                    x=forecast_f['ds'].tolist() + forecast_f['ds'].tolist()[::-1],
                    y=forecast_f['yhat_upper'].tolist() + forecast_f['yhat_lower'].tolist()[::-1],
                    fill='toself', fillcolor='rgba(231, 111, 81,0.15)', line=dict(color='rgba(0,0,0,0)'),
                    name='Intervalle de confiance'))

                fig_f.add_shape(type="line", x0=last_date, y0=0, x1=last_date,
                                y1=max(max(df_prophet_f['y']), forecast_f['yhat'].max()) * 1.1,
                                line=dict(color="#2a9d8f", width=3, dash="dash"))

                fig_f.add_annotation(x=last_date,
                                     y=max(max(df_prophet_f['y']), forecast_f['yhat'].max()) * 1.05,
                                     text="Dernière date des logs", showarrow=True, arrowhead=1)

                fig_f.update_layout(
                    title=f"Prévision des événements - {fournisseur}",
                    xaxis_title="Date",
                    yaxis_title="Nombre d'événements",
                    legend_title="Légende",
                    hovermode="x unified",
                    template="plotly_white"
                )
                st.plotly_chart(fig_f, use_container_width=True)

                st.subheader("📋 Données de prévision")
                forecast_f_display = forecast_f[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
                forecast_f_display.columns = ['Date', 'Prédiction', 'Limite inférieure', 'Limite supérieure']
                st.dataframe(forecast_f_display)

        with st.expander("🔎 Prévision et détection de pics par fournisseur"):
            # Sélection de la catégorie
            categorie_f = st.selectbox("Type d'événement (fournisseur)", df['LevelDisplayName'].unique(), key="categorie_selectbox_anomaly")

            # Filtrer les fournisseurs liés à cette catégorie
            filtered_providers = df[df['LevelDisplayName'] == categorie_f]['ProviderName'].unique()
            fournisseur = st.selectbox("Fournisseur", filtered_providers, key="fournisseur_selectbox_anomaly")

            df_fournisseur = df[df['ProviderName'] == fournisseur]
            df_cat_fourn = df_fournisseur[df_fournisseur['LevelDisplayName'] == categorie_f].copy()
            df_cat_fourn['TimeCreated'] = pd.to_datetime(df_cat_fourn['TimeCreated'])
            df_cat_fourn.set_index('TimeCreated', inplace=True)

            df_prophet_f = df_cat_fourn.resample('D').size().reset_index(name='y')
            df_prophet_f.rename(columns={'TimeCreated': 'ds'}, inplace=True)

            if len(df_prophet_f) < 2:
                st.warning("Pas assez de données pour effectuer une prédiction.")
            else:
                last_date = df['TimeCreated'].max()
                model_f = Prophet()
                model_f.fit(df_prophet_f)

                # Prédiction sur l'historique pour détecter des anomalies passées
                df_history = model_f.predict(df_prophet_f[['ds']])
                df_prophet_f['yhat'] = df_history['yhat']
                df_prophet_f['yhat_upper'] = df_history['yhat_upper']
                df_prophet_f['yhat_lower'] = df_history['yhat_lower']
                df_prophet_f['anomaly'] = df_prophet_f['y'] > df_prophet_f['yhat_upper']

                # Prédiction future
                horizon_f = st.slider("Nombre de jours à prédire (fournisseur)", 7, 90, 30, key="horizon_slider_anomaly")
                start_date_f = last_date + pd.Timedelta(days=1)
                futur_f = pd.DataFrame({'ds': pd.date_range(start=start_date_f, periods=horizon_f)})
                forecast_f = model_f.predict(futur_f)
                forecast_f['yhat'] = forecast_f['yhat'].clip(lower=0).round(0).astype(int)
                forecast_f['anomaly'] = forecast_f['yhat'] > forecast_f['yhat_upper']

                # Graphique
                fig_f = go.Figure()
                fig_f.add_trace(go.Scatter(x=df_prophet_f['ds'], y=df_prophet_f['y'],
                                        mode='markers+lines', name='Données historiques', line=dict(color='#264653')))
                fig_f.add_trace(go.Scatter(x=df_prophet_f.loc[df_prophet_f['anomaly'], 'ds'],
                                        y=df_prophet_f.loc[df_prophet_f['anomaly'], 'y'],
                                        mode='markers', name='Anomalies historiques',
                                        marker=dict(color='red', size=10, symbol='x')))
                fig_f.add_trace(go.Scatter(x=forecast_f['ds'], y=forecast_f['yhat'],
                                        mode='lines', name='Prédictions', line=dict(color='#e76f51', dash='dash')))
                fig_f.add_trace(go.Scatter(x=forecast_f['ds'].tolist() + forecast_f['ds'].tolist()[::-1],
                                        y=forecast_f['yhat_upper'].tolist() + forecast_f['yhat_lower'].tolist()[::-1],
                                        fill='toself', fillcolor='rgba(231, 111, 81,0.15)', line=dict(color='rgba(0,0,0,0)'),
                                        name='Intervalle de confiance'))
                fig_f.add_trace(go.Scatter(x=forecast_f.loc[forecast_f['anomaly'], 'ds'],
                                        y=forecast_f.loc[forecast_f['anomaly'], 'yhat'],
                                        mode='markers', name='Anomalies futures',
                                        marker=dict(color='orange', size=10, symbol='star')))

                fig_f.add_shape(type="line", x0=last_date, y0=0, x1=last_date,
                                y1=max(max(df_prophet_f['y']), forecast_f['yhat'].max()) * 1.1,
                                line=dict(color="#2a9d8f", width=3, dash="dash"))
                fig_f.add_annotation(x=last_date,
                                    y=max(max(df_prophet_f['y']), forecast_f['yhat'].max()) * 1.05,
                                    text="Dernière date des logs", showarrow=True, arrowhead=1)

                fig_f.update_layout(
                    title=f"Prévision & détection de pics - {fournisseur}",
                    xaxis_title="Date",
                    yaxis_title="Nombre d'événements",
                    legend_title="Légende",
                    hovermode="x unified",
                    template="plotly_white"
                )
                st.plotly_chart(fig_f, use_container_width=True)

                # 📊 Tableau + Alerte
                forecast_f_display = forecast_f[['ds', 'yhat', 'yhat_lower', 'yhat_upper', 'anomaly']].copy()
                forecast_f_display.columns = ['Date', 'Prédiction', 'Limite inférieure', 'Limite supérieure', 'Anomalie']

                anomalies_future = forecast_f_display[forecast_f_display['Anomalie']]
                if not anomalies_future.empty:
                    st.warning(f"🚨 {len(anomalies_future)} anomalies prévues dans les {horizon_f} prochains jours !")
                else:
                    st.success("✅ Aucune anomalie prévue dans les jours à venir.")

                # 💡 Affichage stylé avec mise en évidence
                st.subheader("📋 Données de prévision avec détection d'anomalies")
                st.dataframe(
                    forecast_f_display.style.apply(
                        lambda row: ['background-color: orange' if row['Anomalie'] else '' for _ in row],
                        axis=1
                    )
                )

    

        
else:
    st.info("Veuillez téléverser un fichier CSV contenant les logs Windows pour commencer.")

