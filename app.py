import streamlit as st
import pandas as pd
import altair as alt

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="La dieta di AGU", page_icon="🥑", layout="centered")

# --- CSS PERSONALIZZATO E COLORI ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Stile Base Card */
    .meal-card {
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 12px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.08);
        border-left: 6px solid #ccc; /* Default */
    }
    
    /* 🟠 COLAZIONE - Arancione */
    .type-colazione {
        background-color: #FFF3E0;
        border-left-color: #FF9800;
    }
    .type-colazione .meal-title { color: #EF6C00; }
    
    /* 🔵 SPUNTINO/MERENDA - Azzurro */
    .type-spuntino {
        background-color: #E1F5FE;
        border-left-color: #039BE5;
    }
    .type-spuntino .meal-title { color: #0277BD; }
    
    /* 🟢 PRANZO - Verde */
    .type-pranzo {
        background-color: #E8F5E9;
        border-left-color: #43A047;
    }
    .type-pranzo .meal-title { color: #2E7D32; }
    
    /* 🟣 CENA - Indaco */
    .type-cena {
        background-color: #E8EAF6;
        border-left-color: #3F51B5;
    }
    .type-cena .meal-title { color: #283593; }

    /* Testo */
    .meal-title {
        font-weight: 800;
        font-size: 1.2em;
        margin-bottom: 5px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .meal-content {
        color: #424242;
        font-size: 1.0em;
        line-height: 1.5;
    }
    
    /* Box Nutrizionali */
    .nutri-box {
        background-color: white;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        text-align: center;
    }
    .warning-box {
        background-color: #fff3e0;
        border-left: 5px solid #ff9800;
        padding: 10px;
        border-radius: 5px;
        font-size: 0.9em;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- DATABASE DATI (Kcal, Proteine, Carboidrati per 100g) ---
db_alimenti = {
    "Latte e Derivati": {
        "Latte intero": {"kcal": 62, "prot": 3.3, "carb": 4.7},
        "Latte parz. scremato": {"kcal": 41, "prot": 3.4, "carb": 5.0},
        "Yogurt magro": {"kcal": 37, "prot": 3.5, "carb": 4.0},
        "Yogurt intero": {"kcal": 64, "prot": 3.8, "carb": 4.3},
        "Mozzarella": {"kcal": 244, "prot": 18, "carb": 2.0},
        "Parmigiano": {"kcal": 374, "prot": 33, "carb": 0.0},
        "Stracchino": {"kcal": 300, "prot": 15, "carb": 1.5},
        "Ricotta": {"kcal": 173, "prot": 11, "carb": 3.5},
        "Gorgonzola": {"kcal": 358, "prot": 19, "carb": 0.0},
        "Emmenthal": {"kcal": 404, "prot": 29, "carb": 0.0},
        "Asiago": {"kcal": 356, "prot": 24, "carb": 0.5},
        "Squacquerone": {"kcal": 250, "prot": 13, "carb": 2.0}
    },
    "Carni": {
        "Manzo magro": {"kcal": 129, "prot": 21, "carb": 0},
        "Vitello magro": {"kcal": 113, "prot": 20, "carb": 0},
        "Pollo (petto)": {"kcal": 97, "prot": 23, "carb": 0},
        "Pollo intero": {"kcal": 175, "prot": 18, "carb": 0},
        "Tacchino": {"kcal": 134, "prot": 24, "carb": 0},
        "Maiale magro": {"kcal": 131, "prot": 20, "carb": 0},
        "Cavallo": {"kcal": 111, "prot": 21, "carb": 0.5},
        "Prosciutto crudo": {"kcal": 218,
