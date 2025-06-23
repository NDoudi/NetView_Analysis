    elif page == "💬 Chat intelligent":
        st.title("💬 Chat intelligent avec les logs Windows")
        st.markdown("---")

        if 'df' not in locals():
            st.warning("Les données de logs ne sont pas chargées.")
            st.stop()

        df['texte_analysable'] = df[['LevelDisplayName', 'ProviderName', 'Message']].astype(str).agg(' '.join, axis=1)

        from sentence_transformers import SentenceTransformer, util
        import torch

        @st.cache_resource(show_spinner=False)
        def load_model():
            return SentenceTransformer("all-MiniLM-L6-v2")

        model = load_model()

        @st.cache_data(show_spinner=False)
        def get_embeddings(texts):
            return model.encode(texts, convert_to_tensor=True)

        embeddings = get_embeddings(df['texte_analysable'].tolist())

        question = st.text_input("❓ Posez une question sur les événements :")

        if question:
            st.write("🔍 Recherche en cours...")

            question_embedding = model.encode(question, convert_to_tensor=True)
            scores = util.pytorch_cos_sim(question_embedding, embeddings)[0]
            top_k = torch.topk(scores, k=min(5, len(df)))
            indices = top_k.indices.cpu().numpy()
            valeurs = top_k.values.cpu().numpy()

            st.success("Voici les événements les plus pertinents :")

            for i, idx in enumerate(indices):
                ligne = df.iloc[idx]
                st.markdown(f"""
                **🕒 Temps**: {ligne['TimeCreated']}  
                **🔧 Niveau**: {ligne['LevelDisplayName']}  
                **📡 Source**: {ligne['ProviderName']}  
                **📝 Message**: `{ligne['Message']}`  
                **🔗 Similarité**: {valeurs[i]:.2f}
                ---
                """)

    
    