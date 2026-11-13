import streamlit as st

def apply_theme():
    st.markdown("""
    <style>
      .block-container {padding-top: 1.7rem; padding-bottom: 3rem; max-width: 1500px;}
      h1, h2, h3 {letter-spacing: -0.02em;}
      div[data-testid="stMetric"] {background: white; border: 1px solid #e5eaf2;
        padding: 14px 16px; border-radius: 12px;}
      .stAlert {border-radius: 10px;}
      section[data-testid="stSidebar"] {border-right: 1px solid #e7ebf2;}
    </style>
    """, unsafe_allow_html=True)

def page_header(title, subtitle):
    st.title(title)
    st.caption(subtitle)
    st.divider()
