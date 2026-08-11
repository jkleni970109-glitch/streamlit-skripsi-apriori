import streamlit as st

def load_css():
    st.markdown("""
     <style>


    /* Judul */
    h1{
       color:#1E3A8A !important; 
       font-weight:800; 
       letter-spacing:1px; 
       margin-bottom:10px;
    }

    h2,h3{
        color:#1E293B;
    }

    /* Tombol */
    .stButton>button{
        background-color:#2563EB;
        color:white;
        border:none;
        border-radius:10px;
        padding:10px 20px;
        font-weight:bold;
    }

    .stButton>button:hover{
        background:#1D4ED8;
    }

    /* Dataframe */
    div[data-testid="stDataFrame"]{
        border-radius:12px;
        border:1px solid #E2E8F0;
    }

    /* File uploader */
    div[data-testid="stFileUploader"]{
    border:1px solid #93C5FD;
    border-radius:12px;
    padding:15px;
    background:#F8FBFF;
    }
    

    </style>
    """, unsafe_allow_html=True)
