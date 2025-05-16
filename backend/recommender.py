from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from data_loader import load_all_jobs


_model = None
_embeddings = None
_df_merged = None

def load_and_prepare_recommender():
    global _model, _embeddings, _df_merged

    if _model is not None and _embeddings is not None:
        print("✅ Using cached model and embeddings")
        return _model, _df_merged, _embeddings

    df_merged = load_all_jobs()
    df_merged["description"] = df_merged["description"].fillna("").astype(str)
    df_merged["tags"] = df_merged["tags"].fillna("").astype(str)
    df_merged["content"] = df_merged["description"] + " Tags: " + df_merged["tags"]
    df_merged = df_merged[df_merged["content"].str.strip() != ""]

    print(f"🔄 Encoding {len(df_merged)} jobs...")

    _model = SentenceTransformer("all-MiniLM-L6-v2")
    _embeddings = _model.encode(df_merged["content"].tolist(), show_progress_bar=True, batch_size=32)
    _df_merged = df_merged

    return _model, _df_merged, _embeddings

def recommend_jobs_from_input(job_title, preferences, top_n=5):
    print("📥 Received input:")
    print(f"job_title: {job_title}")
    print(f"preferences: {preferences}")
    
    try:
        model, df_merged, job_embeddings = load_and_prepare_recommender()
        print("✅ Model and embeddings loaded successfully.")
    except Exception as e:
        print(f"❌ Error in loading model/embeddings: {e}")
        raise

    try:
        user_query = f"{job_title} in a {preferences} company"
        print(f"🧠 User query: {user_query}")
        user_embedding = model.encode([user_query])
    except Exception as e:
        print(f"❌ Error in encoding user query: {e}")
        raise

    try:
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity(user_embedding, job_embeddings)[0]
        print(f"📊 Similarity scores calculated. Example: {similarities[:5]}")
    except Exception as e:
        print(f"❌ Error in cosine similarity: {e}")
        raise

    try:
        df_merged["similarity"] = similarities
        top_jobs = df_merged.sort_values(by="similarity", ascending=False).head(top_n)

        results = []
        for _, row in top_jobs.iterrows():
            results.append({
                "job_title": row["job_title"],
                "company": row["company"],
                "url": row.get("url", ""),
                "source": row.get("source", ""),
                "similarity_score": round(row["similarity"] * 100, 1),
                "snippet": row["description"][:250].replace("\n", " ").strip() + "..."
            })

        print(f"✅ Returning {len(results)} results.")
        return results

    except Exception as e:
        print(f"❌ Error in generating results: {e}")
        raise

def recommend_jobs_dummy(top_n=5):
    df = load_all_jobs()
    df = df.fillna("")  # clean up NaNs for safe JSON

    results = []
    for _, row in df.head(top_n).iterrows():
        results.append({
            "job_title": row["job_title"],
            "company": row["company"],
            "url": row.get("url", ""),
            "source": row.get("source", ""),
            "similarity_score": 100.0,  # fake it
            "snippet": row["description"][:250].replace("\n", " ").strip() + "..."
        })
    return results
