import streamlit as st
import pandas as pd
from analyzer import analyze_reviews

# Page Configuration
st.set_page_config(
    page_title="E-Com SEO Studio Pro",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern SaaS Look
st.markdown("""
<style>
    .hero-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 25px 30px;
        border-radius: 15px;
        border-left: 6px solid #38bdf8;
        margin-bottom: 25px;
        color: white;
    }
    .hero-title { font-size: 32px; font-weight: 800; margin: 0; color: #f8fafc; }
    .hero-sub { font-size: 15px; color: #94a3b8; margin-top: 6px; }
    div[data-testid="stMetric"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Controls
with st.sidebar:
    st.title("⚙️ Studio Controls")
    st.caption("Apne analysis ko customize karein")
    st.divider()
    top_n_slider = st.slider("Top Keywords Count", min_value=5, max_value=15, value=10)
    st.divider()
    st.info("💡 **Pro Tip:** Flipkart par 'Negative First' filter lagakar scrape ki gayi CSV sabse best defects batati hai.")

# Hero Header Banner
st.markdown("""
<div class="hero-box">
    <div class="hero-title">✨ E-Com SEO & Review Intelligence Studio</div>
    <div class="hero-sub">Apni scraped CSV file upload karein aur seconds mein High-Ranking Keywords aur Return Risks nikalein.</div>
</div>
""", unsafe_allow_html=True)

# File Uploader
uploaded_file = st.file_uploader("📂 Drag & Drop Scraped CSV File Here", type=["csv"])

if uploaded_file is not None:
    try:
        with st.spinner("⚡ Data clean aur visual charts taiyar ho rahe hain..."):
            res = analyze_reviews(uploaded_file)

        # KPI Metric Cards
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("💬 Total Clean Reviews", f"{res['total']:,}")
        c2.metric("⭐ Average Rating", f"{res['avg_rating']} / 5.0")
        pos_pct = round(res['pos_count'] / res['total'] * 100) if res['total'] > 0 else 0
        c3.metric("😊 Happy Buyers (4-5★)", f"{pos_pct}%", f"{res['pos_count']} reviews")
        c4.metric("⚠️ Negative/Neutral (1-3★)", f"{res['neg_count']} reviews")

        st.markdown("<br>", unsafe_allow_html=True)

        # Organized 2-Tab Interface
        tab1, tab2 = st.tabs(["📊 Keywords & Defects Charts", "📋 Copy-Paste AI Prompt"])

        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🔑 Top SEO Keywords")
                if res["keywords"]:
                    df_kw = pd.DataFrame(res["keywords"][:top_n_slider], columns=["Keyword / Phrase", "Mentions"])
                    st.bar_chart(df_kw.set_index("Keyword / Phrase"), color="#38bdf8")
                    st.dataframe(df_kw, use_container_width=True, hide_index=True)
                else:
                    st.info("Keywords nikalne ke liye aur zyada positive reviews chahiye.")

            with col2:
                st.subheader("🚨 Return Risks & Product Defects")
                if res["complaints"]:
                    df_comp = pd.DataFrame(list(res["complaints"].items()), columns=["Defect Category", "Mentions"])
                    st.bar_chart(df_comp.set_index("Defect Category"), color="#f87171")
                    st.dataframe(df_comp, use_container_width=True, hide_index=True)
                else:
                    st.success("🎉 Koi bada defect detect nahi hua!")

        with tab2:
            st.subheader("🤖 Copy-Paste AI Prompt (Chat Par Bhejne Ke Liye)")
            st.write("Neeche wale box ke top-right corner par bane **Copy icon** par click karein aur yahan chat mein paste karein:")
            st.code(res["ai_prompt_text"], language="text")

    except Exception as e:
        st.error(f"File padhne mein error aaya: {e}")
