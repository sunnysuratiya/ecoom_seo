import streamlit as st
import pandas as pd
from analyzer import analyze_reviews_v2

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
    top_n_slider = st.slider("Top Keywords Count", min_value=5, max_value=25, value=12)
    show_raw = st.toggle("Show Cleaned Reviews Table", value=False)
    st.divider()
    st.info("💡 **Pro Tip:** Flipkart par 'Negative First' filter lagakar scrape ki gayi CSV sabse best defects batati hai.")

# Hero Header Banner
st.markdown("""
<div class="hero-box">
    <div class="hero-title">✨ E-Com SEO & Review Intelligence Studio</div>
    <div class="hero-sub">Apni scraped CSV files upload karein aur seconds mein High-Ranking Keywords, Buyer Personas, aur Return Risks nikalein.</div>
</div>
""", unsafe_allow_html=True)

# File Uploader
uploaded_files = st.file_uploader("📂 Drag & Drop 1 or More Scraped CSV Files Here", type=["csv"], accept_multiple_files=True)

if uploaded_files:
    with st.spinner("⚡ Data clean aur visual charts taiyar ho rahe hain..."):
        res = analyze_reviews_v2(uploaded_files)

    if res is None:
        st.error("❌ Valid reviews nahi mile. Kripya sahi CSV file upload karein.")
    else:
        # KPI Metric Cards
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📄 Files Merged", f"{len(uploaded_files)} File(s)")
        c2.metric("💬 Total Clean Reviews", f"{res['total']:,}")
        c3.metric("⭐ Average Rating", f"{res['avg_rating']} / 5.0")
        pos_pct = round(res['pos_count'] / res['total'] * 100)
        c4.metric("😊 Happy Buyers (4-5★)", f"{pos_pct}%", f"{res['pos_count']} reviews")

        st.markdown("<br>", unsafe_allow_html=True)

        # Organized 3-Tab Interface
        tab1, tab2, tab3 = st.tabs(["🔑 SEO Keywords & Charts", "⚠️ Defects & Buyer Personas", "📋 AI Prompt & Export"])

        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Top Single Keywords")
                df_single = pd.DataFrame(res["single_kw"][:top_n_slider], columns=["Keyword", "Mentions"])
                if not df_single.empty:
                    st.bar_chart(df_single.set_index("Keyword"), color="#38bdf8")
                    st.dataframe(df_single, use_container_width=True, hide_index=True)

            with col2:
                st.subheader("Top 2-Word Search Phrases")
                df_phrase = pd.DataFrame(res["phrase_kw"][:top_n_slider], columns=["Search Phrase", "Mentions"])
                if not df_phrase.empty:
                    st.bar_chart(df_phrase.set_index("Search Phrase"), color="#818cf8")
                    st.dataframe(df_phrase, use_container_width=True, hide_index=True)

        with tab2:
            col3, col4 = st.columns(2)
            with col3:
                st.subheader("👥 Buyer Personas & Use-Cases")
                if res["personas"]:
                    df_pers = pd.DataFrame(list(res["personas"].items()), columns=["Audience / Use-Case", "Mentions"])
                    st.bar_chart(df_pers.set_index("Audience / Use-Case"), color="#34d399")
                    st.dataframe(df_pers, use_container_width=True, hide_index=True)
                else:
                    st.info("Specific buyer personas detect nahi hue.")

            with col4:
                st.subheader("🚨 Return Risks & Product Defects")
                if res["complaints"]:
                    df_comp = pd.DataFrame(list(res["complaints"].items()), columns=["Defect Category", "Mentions"])
                    st.bar_chart(df_comp.set_index("Defect Category"), color="#f87171")
                    st.dataframe(df_comp, use_container_width=True, hide_index=True)
                else:
                    st.success("🎉 Koi bada defect detect nahi hua!")

        with tab3:
            st.subheader("🤖 Copy-Paste AI Prompt (Chat Par Bhejne Ke Liye)")
            st.write("Neeche wale box ke top-right corner par bane **Copy icon** par click karein aur yahan chat mein paste karein:")
            st.code(res["ai_prompt_text"], language="text")

            csv_data = res["clean_df"].to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Cleaned Master CSV", data=csv_data, file_name="cleaned_master_reviews.csv", mime="text/csv")

        if show_raw:
            st.divider()
            st.subheader("🔍 Cleaned Reviews Preview")
            st.dataframe(res["clean_df"], use_container_width=True)
