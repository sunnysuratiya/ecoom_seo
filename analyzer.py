import pandas as pd
import re
from sklearn.feature_extraction.text import CountVectorizer

def load_and_clean_multiple_csvs(uploaded_files):
    all_dfs = []
    for file in uploaded_files:
        df = pd.read_csv(file, on_bad_lines='skip').dropna(how='all')
        rating_col = None
        for col in df.columns:
            numeric_vals = pd.to_numeric(df[col], errors='coerce')
            if len(numeric_vals[(numeric_vals >= 1) & (numeric_vals <= 5)]) >= 3:
                rating_col = col
                df['clean_rating'] = numeric_vals
                break
        if rating_col:
            df = df[df['clean_rating'].between(1, 5)].copy()
        else:
            df['clean_rating'] = 5.0

        text_col, max_len = None, 0
        for col in df.columns:
            if col in [rating_col, 'clean_rating']:
                continue
            avg_len = df[col].astype(str).str.len().mean()
            if avg_len > max_len:
                max_len, text_col = avg_len, col

        if text_col:
            df['clean_review'] = df[text_col].astype(str).apply(
                lambda x: re.sub(r'http\S+|[^a-zA-Z0-9\s]', ' ', x).strip()
            )
            df = df[df['clean_review'].str.len() > 3]
            all_dfs.append(df[['clean_rating', 'clean_review']])
            
    return pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame(columns=['clean_rating', 'clean_review'])

def extract_keywords(texts, ngram=(1, 1), top_n=25):
    if len(texts) == 0:
        return []
    stops = ['product', 'good', 'nice', 'best', 'flipkart', 'meesho', 'amazon', 'purchase', 'verified', 'review', 'color', 'colour', 'buy', 'money', 'worth', 'super', 'awesome', 'excellent', 'really', 'using']
    vec = CountVectorizer(stop_words='english', ngram_range=ngram, max_features=300)
    try:
        bag = vec.fit_transform(texts)
        sums = bag.sum(axis=0)
        freqs = [(w, int(sums[0, i])) for w, i in vec.vocabulary_.items() if not any(s in w.split() for s in stops)]
        return sorted(freqs, key=lambda x: x[1], reverse=True)[:top_n]
    except ValueError:
        return []

def detect_categories(texts, category_dict):
    results = {}
    for cat, words in category_dict.items():
        pattern = "|".join(words)
        count = texts.str.lower().str.contains(pattern, na=False).sum()
        if count > 0:
            results[cat] = int(count)
    return dict(sorted(results.items(), key=lambda x: x[1], reverse=True))

def analyze_reviews_v2(uploaded_files):
    df = load_and_clean_multiple_csvs(uploaded_files)
    total = len(df)
    if total == 0:
        return None

    avg_rating = round(df['clean_rating'].mean(), 2)
    pos_df = df[df['clean_rating'] >= 4]
    neg_df = df[df['clean_rating'] <= 3]

    single_kw = extract_keywords(pos_df['clean_review'], ngram=(1, 1), top_n=25)
    phrase_kw = extract_keywords(pos_df['clean_review'], ngram=(2, 2), top_n=25)

    complaint_dict = {
        "Battery & Charging": ["battery", "charge", "charging", "backup", "dead", "power", "adapter", "cable", "mins", "minutes"],
        "Motor & Performance": ["weak", "vibration", "speed", "pressure", "stop", "stuck", "motor", "heat", "heating", "working"],
        "Build & Material Quality": ["plastic", "cheap", "quality", "broken", "damage", "damaged", "heavy", "loose"],
        "Noise & Sound": ["noise", "sound", "loud"],
        "Wrong Item / Missing Parts": ["different", "wrong", "old", "used", "missing", "attachment", "head"]
    }
    persona_dict = {
        "Gym & Workout Users": ["gym", "workout", "muscle", "exercise", "fitness", "athlete", "recovery"],
        "Pain Relief & Therapy": ["pain", "relief", "relax", "relaxation", "stiff", "neck", "back", "leg", "shoulder", "joint"],
        "Elderly & Family Use": ["mother", "father", "parents", "mom", "dad", "old", "family", "elderly"],
        "Office & Travel Use": ["office", "travel", "portable", "lightweight", "handy", "desk"]
    }

    complaints = detect_categories(neg_df['clean_review'], complaint_dict)
    personas = detect_categories(df['clean_review'], persona_dict)

    summary_lines = [
        f"FILES ANALYZED: {len(uploaded_files)} | TOTAL CLEAN REVIEWS: {total} | AVG RATING: {avg_rating}/5",
        f"Positive (4-5★): {len(pos_df)} ({round(len(pos_df)/total*100)}%) | Negative/Neutral (1-3★): {len(neg_df)} ({round(len(neg_df)/total*100)}%)",
        "\n1. TOP SINGLE SEO KEYWORDS:",
        ", ".join([f"{k} ({v})" for k, v in single_kw[:15]]),
        "\n2. TOP 2-WORD LONG-TAIL PHRASES:",
        ", ".join([f"{k} ({v})" for k, v in phrase_kw[:15]]),
        "\n3. BUYER PERSONAS & USE-CASES:",
        ", ".join([f"{k}: {v}" for k, v in personas.items()]) if personas else "General daily use",
        "\n4. TOP COMPLAINTS / RETURN RISKS:",
        ", ".join([f"{k}: {v} mentions" for k, v in complaints.items()]) if complaints else "No major defects found",
        "\n5. TOP NEGATIVE REVIEW SAMPLES:",
        *[f"- {r[:140]}" for r in neg_df['clean_review'].head(5).tolist()],
        "\n6. TOP POSITIVE REVIEW SAMPLES:",
        *[f"- {r[:140]}" for r in pos_df['clean_review'].head(5).tolist()]
    ]

    return {
        "total": total, "avg_rating": avg_rating,
        "pos_count": len(pos_df), "neg_count": len(neg_df),
        "single_kw": single_kw, "phrase_kw": phrase_kw,
        "complaints": complaints, "personas": personas,
        "clean_df": df, "ai_prompt_text": "\n".join(summary_lines)
    }
