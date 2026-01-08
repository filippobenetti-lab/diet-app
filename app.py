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
        "Prosciutto crudo": {"kcal": 218, "prot": 26, "carb": 0},
        "Prosciutto cotto": {"kcal": 215, "prot": 19, "carb": 0.9},
        "Bresaola": {"kcal": 151, "prot": 32, "carb": 0},
        "Speck": {"kcal": 300, "prot": 28, "carb": 0.5},
        "Salame nostrano": {"kcal": 463, "prot": 20, "carb": 1},
        "Salsiccia": {"kcal": 334, "prot": 14, "carb": 0},
        "Hamburger manzo": {"kcal": 250, "prot": 18, "carb": 0}
    },
    "Pesce": {
        "Merluzzo": {"kcal": 71, "prot": 17, "carb": 0},
        "Sogliola": {"kcal": 86, "prot": 16, "carb": 0},
        "Tonno fresco": {"kcal": 158, "prot": 21, "carb": 0},
        "Tonno scatola (sgocc.)": {"kcal": 190, "prot": 25, "carb": 0},
        "Orata/Branzino": {"kcal": 82, "prot": 18, "carb": 0},
        "Salmone": {"kcal": 185, "prot": 19, "carb": 0},
        "Trota": {"kcal": 96, "prot": 19, "carb": 0},
        "Nasello": {"kcal": 75, "prot": 16, "carb": 0},
        "Gamberi": {"kcal": 71, "prot": 13, "carb": 2.9}
    },
    "Cereali e Carboidrati": {
        "Pane comune": {"kcal": 260, "prot": 8, "carb": 50},
        "Pane integrale": {"kcal": 243, "prot": 9, "carb": 45},
        "Pasta/Riso": {"kcal": 377, "prot": 11, "carb": 73},
        "Patate": {"kcal": 89, "prot": 2, "carb": 18},
        "Fette biscottate": {"kcal": 431, "prot": 11, "carb": 72},
        "Crackers": {"kcal": 464, "prot": 10, "carb": 75},
        "Biscotti Oro Saiwa": {"kcal": 430, "prot": 7, "carb": 77},
        "Cereali Special K": {"kcal": 370, "prot": 14, "carb": 75},
        "Gnocchi": {"kcal": 160, "prot": 5, "carb": 36}
    },
    "Verdure e Legumi": {
        "Insalata/Lattuga": {"kcal": 20, "prot": 1.5, "carb": 2},
        "Pomodori": {"kcal": 25, "prot": 1, "carb": 3.5},
        "Fagiolini": {"kcal": 19, "prot": 2, "carb": 2.5},
        "Spinaci": {"kcal": 32, "prot": 3.5, "carb": 3},
        "Piselli freschi": {"kcal": 79, "prot": 6, "carb": 10},
        "Fagioli secchi": {"kcal": 324, "prot": 23, "carb": 47},
        "Lenticchie secche": {"kcal": 339, "prot": 25, "carb": 54},
        "Zucchine": {"kcal": 12, "prot": 1, "carb": 1.5},
        "Carote": {"kcal": 35, "prot": 1, "carb": 7},
        "Finocchi": {"kcal": 31, "prot": 1, "carb": 1},
        "Cavolfiore": {"kcal": 25, "prot": 3, "carb": 2.5},
        "Broccoli": {"kcal": 27, "prot": 3, "carb": 1.5},
        "Peperoni": {"kcal": 22, "prot": 1, "carb": 4}
    },
    "Frutta e Dolci": {
        "Mela": {"kcal": 48, "prot": 0.2, "carb": 11},
        "Banana": {"kcal": 70, "prot": 1, "carb": 16},
        "Arancia": {"kcal": 40, "prot": 0.7, "carb": 8},
        "Marmellata": {"kcal": 250, "prot": 0.5, "carb": 60},
        "Miele": {"kcal": 304, "prot": 0.6, "carb": 80},
        "Cioccolata spalmabile": {"kcal": 530, "prot": 6, "carb": 55},
        "Tiramisù": {"kcal": 367, "prot": 6, "carb": 35},
        "Crostata": {"kcal": 350, "prot": 5, "carb
