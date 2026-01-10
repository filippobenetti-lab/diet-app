import streamlit as st
import pandas as pd
import altair as alt
import re

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="La dieta di AGU", page_icon="🥑", layout="centered")

# --- CSS PERSONALIZZATO ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .meal-card {
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 12px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.08);
        border-left: 6px solid #ccc;
        background-color: white;
    }
    
    /* Colori Specifici per Pasto */
    .type-colazione { background-color: #FFF3E0; border-left-color: #FF9800; }
    .type-spuntino { background-color: #E1F5FE; border-left-color: #039BE5; }
    .type-pranzo { background-color: #E8F5E9; border-left-color: #43A047; }
    .type-cena { background-color: #E8EAF6; border-left-color: #3F51B5; }

    .meal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
    .meal-title { font-weight: 800; font-size: 1.1em; text-transform: uppercase; color: #333; }
    .meal-content { color: #424242; font-size: 0.95em; line-height: 1.5; }
    
    .kcal-badge {
        background-color: rgba(255,255,255,0.6);
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.8em;
        font-weight: bold;
        color: #555;
        border: 1px solid rgba(0,0,0,0.1);
    }
    
    .daily-total {
        background-color: #263238;
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin-top: 20px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    .total-kcal { font-size: 2.5em; font-weight: bold; color: #4CAF50; }
</style>
""", unsafe_allow_html=True)

# --- DATABASE DATI (AGGIORNATO CON VALORI PDF PAG 32-36) ---
# Valori aggiornati rigorosamente secondo il documento "Adobe Scan 7 gen 2026.pdf"
db_alimenti = {
    "Latte e Derivati": {
        "Latte intero": {"kcal": 62, "prot": 3.3, "carb": 4.7},
        "Latte parz. scremato": {"kcal": 41, "prot": 3.4, "carb": 5.0},
        "Yogurt magro": {"kcal": 37, "prot": 3.5, "carb": 4.0}, # PDF pag 32
        "Mozzarella": {"kcal": 244, "prot": 18, "carb": 2.0},
        "Parmigiano": {"kcal": 374, "prot": 33, "carb": 0.0},
        "Stracchino": {"kcal": 300, "prot": 15, "carb": 1.5},
        "Ricotta": {"kcal": 173, "prot": 11, "carb": 3.5},
        "Gorgonzola": {"kcal": 358, "prot": 19, "carb": 0.0},
        "Emmenthal": {"kcal": 404, "prot": 29, "carb": 0.0}
    },
    "Carni e Salumi": {
        "Manzo magro": {"kcal": 129, "prot": 21, "carb": 0},
        "Vitello magro": {"kcal": 113, "prot": 20, "carb": 0},
        "Pollo (petto)": {"kcal": 97, "prot": 23, "carb": 0},
        "Pollo intero": {"kcal": 175, "prot": 18, "carb": 0},
        "Tacchino": {"kcal": 134, "prot": 24, "carb": 0},
        "Maiale magro": {"kcal": 131, "prot": 20, "carb": 0},
        "Prosciutto crudo": {"kcal": 370, "prot": 26, "carb": 0}, # Valore PDF pag 33
        "Prosciutto cotto": {"kcal": 412, "prot": 19, "carb": 0.9}, # Valore PDF pag 33 (Molto alto)
        "Bresaola": {"kcal": 218, "prot": 32, "carb": 0}, # Indicato come "Crudo magro/Bresaola"
        "Speck": {"kcal": 300, "prot": 28, "carb": 0.5}, # Stima (non presente in tabella, usato media)
        "Salsiccia": {"kcal": 334, "prot": 14, "carb": 0}
    },
    "Pesce": {
        "Merluzzo": {"kcal": 71, "prot": 17, "carb": 0},
        "Sogliola": {"kcal": 86, "prot": 16, "carb": 0},
        "Tonno fresco": {"kcal": 158, "prot": 21, "carb": 0},
        "Tonno scatola (sgocc.)": {"kcal": 190, "prot": 25, "carb": 0}, # Valore PDF pag 34
        "Orata/Branzino": {"kcal": 82, "prot": 18, "carb": 0},
        "Salmone": {"kcal": 185, "prot": 19, "carb": 0}, 
        "Trota": {"kcal": 96, "prot": 19, "carb": 0},
        "Gamberi": {"kcal": 71, "prot": 13, "carb": 2.9}
    },
    "Cereali e Carboidrati": {
        "Pane comune": {"kcal": 260, "prot": 8, "carb": 50}, # PDF pag 35
        "Pane integrale": {"kcal": 243, "prot": 9, "carb": 45},
        "Pasta": {"kcal": 377, "prot": 11, "carb": 73}, # PDF pag 35
        "Riso": {"kcal": 384, "prot": 7, "carb": 80}, # PDF pag 35
        "Patate": {"kcal": 89, "prot": 2, "carb": 18},
        "Fette biscottate": {"kcal": 431, "prot": 11, "carb": 72},
        "Crackers": {"kcal": 464, "prot": 10, "carb": 75},
        "Biscotti": {"kcal": 430, "prot": 7, "carb": 77},
        "Gnocchi": {"kcal": 160, "prot": 5, "carb": 36},
        "Pizza": {"kcal": 270, "prot": 10, "carb": 30}
    },
    "Verdure e Legumi": {
        "Insalata": {"kcal": 20, "prot": 1.5, "carb": 2},
        "Pomodori": {"kcal": 25, "prot": 1, "carb": 3.5},
        "Fagiolini": {"kcal": 19, "prot": 2, "carb": 2.5},
        "Spinaci": {"kcal": 32, "prot": 3.5, "carb": 3},
        "Piselli freschi": {"kcal": 79, "prot": 6, "carb": 10}, # PDF pag 35
        "Fagioli secchi": {"kcal": 324, "prot": 23, "carb": 47},
        "Lenticchie secche": {"kcal": 339, "prot": 25, "carb": 54},
        "Zucchine": {"kcal": 12, "prot": 1, "carb": 1.5},
        "Carote": {"kcal": 35, "prot": 1, "carb": 7},
        "Finocchi": {"kcal": 31, "prot": 1, "carb": 1},
        "Cavolfiore": {"kcal": 25, "prot": 3, "carb": 2.5},
        "Broccoli": {"kcal": 28, "prot": 3, "carb": 1.5},
        "Peperoni": {"kcal": 23, "prot": 1, "carb": 4}
    },
    "Frutta e Dolci": {
        "Mela": {"kcal": 48, "prot": 0.2, "carb": 11},
        "Banana": {"kcal": 70, "prot": 1, "carb": 16}, # PDF pag 36
        "Arancia": {"kcal": 36, "prot": 0.7, "carb": 8}, # PDF pag 36
        "Marmellata": {"kcal": 250, "prot": 0.5, "carb": 60},
        "Miele": {"kcal": 304, "prot": 0.6, "carb": 80},
        "Cioccolata spalmabile": {"kcal": 537, "prot": 6, "carb": 55},
        "Tiramisù": {"kcal": 333, "prot": 6, "carb": 35},
        "Crostata": {"kcal": 350, "prot": 5, "carb": 55}
    },
    "Condimenti": {
        "Olio d'oliva": {"kcal": 900, "prot": 0, "carb": 0},
        "Burro": {"kcal": 758, "prot": 1, "carb": 0},
        "Margarina": {"kcal": 760, "prot": 0, "carb": 0}
    }
}

menu_settimanali = {
    "Settimana A.B.": {
        "Lunedì": {"Colazione": "Tè, Miele (2 cuc.), Fette biscottate (4), Marmellata (4 cuc.)", "Spuntino": "Pane bianco (2 fette), Prosciutto cotto (4 fette)", "Pranzo": "Pasta aglio/olio (120g), Parmigiano (2 cuc.), Pane (60g), Stracchino (100g), Valeriana", "Merenda": "Banana (1 pz)", "Cena": "Passato verdure (150g), Pane (80g), Maiale ai ferri (220g), Olio evo (2 cuc.)"},
        "Martedì": {"Colazione": "Succo ACE (1 bic.), Biscotti Oro Saiwa (8 pz)", "Spuntino": "Pane bianco (2 fette), Speck (5 fette)", "Pranzo": "Risotto zucchine (120g), Parmigiano (2 cuc.), Pane (80g), Speck (5 fet.), Radicchio", "Merenda": "Cracker Doria (1 pz)", "Cena": "Branzino ai ferri (300g), Pane (80g), Piselli lessati (150g), Olio evo (3 cuc.)"},
        "Mercoledì": {"Colazione": "Tè, Miele (2 cuc.), Biscotti Oro Saiwa (8 pz)", "Spuntino": "Pane bianco (2 fette), Prosciutto crudo (6 fette)", "Pranzo": "Tortellini panna (180g), Parmigiano (2 cuc.), Pane (80g), Tonno (1 conf.), Cavolo cappuccio", "Merenda": "Barretta Kellogg's (1 pz)", "Cena": "Manzo ai ferri (200g), Pane (80g), Spinaci lessi (200g), Olio evo (3 cuc.)"},
        "Giovedì": {"Colazione": "Succo ACE, Fette biscottate (4), Cioccolata nocciole (4 cuc.)", "Spuntino": "Pane bianco (2 fette), Salame nostrano (5 fette)", "Pranzo": "Pasta pomodoro (120g), Parmigiano, Cracker (1 pz), Frittata (2 pz/150g albume), Carote (100g)", "Merenda": "Banana (1 pz)", "Cena": "Minestrone verdure (100g), Pane (60g), Petto tacchino (200g), Olio evo (3 cuc.)"},
        "Venerdì": {"Colazione": "Tè, Miele (2 cuc.), Fette biscottate (4), Miele (4 cuc.)", "Spuntino": "Pane bianco (2 fette), Prosciutto cotto (4 fette)", "Pranzo": "Risotto zucca (120g), Parmigiano (2 cuc.), Pane (80g), Mozzarella (100g), Finocchi (100g)", "Merenda": "Mela (1 pz)", "Cena": "Merluzzo forno (250g), Pane (80g), Cavolfiore lesso (200g), Olio evo (3 cuc.)"},
        "Sabato": {"Colazione": "Tè, Miele (2 cuc.), Cereali Special K (40g)", "Spuntino": "Yogurt magro frutta (1 pz)", "Pranzo": "Pollo petto ai ferri (250g), Insalata mista (200g), Olio evo (5 cuc.)", "Merenda": "Tiramisù (1 fetta)", "Cena": "Pizza Margherita (1 pz), Zucca forno (100g), Salsiccia (100g), Sprite (1 bic.)"},
        "Domenica": {"Colazione": "Succo ACE, Croissant marmellata (60g)", "Spuntino": "Yogurt magro frutta (1 pz)", "Pranzo": "Pasta ragù (100g), Parmigiano, Pane (80g), Asiago (100g), Valeriana", "Merenda": "Barretta Kellogg's (1 pz)", "Cena": "Orata forno (250g), Pane (80g), Broccoli lessi (200g), Olio evo (6 cuc.)"}
    },
    "Settimana A.B.1": {
        "Lunedì": {"Colazione": "Tè, Miele, Cereali Special K (40g)", "Spuntino": "Pane bianco (2 fette), Speck (5 fette)", "Pranzo": "Pasta pesto (100g), Hamburger manzo (1 pz), Pane (60g), Valeriana", "Merenda": "Pane (80g), Marmellata (4 cuc.)", "Cena": "Salmone forno (200g), Pane (80g), Piselli lessati (150g), Olio evo"},
        "Martedì": {"Colazione": "Succo ACE, Biscotti Oro Saiwa (8 pz)", "Spuntino": "Pane bianco (2 fette), Prosciutto cotto (4 fette)", "Pranzo": "Risotto piselli (100g), Parmigiano, Pane (80g), Prosciutto cotto (4 fette), Radicchio", "Merenda": "Cracker Doria (1 pz)", "Cena": "Hamburger manzo (2 pz), Pane (80g), Piselli (150g), Olio evo"},
        "Mercoledì": {"Colazione": "Tè, Miele, Biscotti Oro Saiwa (8 pz)", "Spuntino": "Pane bianco (2 fette), Prosciutto crudo (6 fette)", "Pranzo": "Tortellini brodo (100g), Parmigiano, Cracker (1 pz), Frittata semplice (2 pz), Cavolo cappuccio", "Merenda": "Pane (80g), Marmellata (4 cuc.)", "Cena": "Manzo ai ferri (200g), Pane (80g), Fagioli Borlotti (150g), Olio evo"},
        "Giovedì": {"Colazione": "Succo ACE, Fette biscottate (4), Cioccolata nocciole (4 cuc.)", "Spuntino": "Pane bianco (2 fette), Salame nostrano (5 fette)", "Pranzo": "Pasta (100g), Tonno (1 conf.), Cracker (1 pz), Tonno (2° conf.), Carote", "Merenda": "Banana (1 pz)", "Cena": "Tacchino ai ferri (200g), Pane (80g), Patate bollite (200g), Olio evo"},
        "Venerdì": {"Colazione": "Tè, Miele, Fette biscottate (4), Miele (4 cuc.)", "Spuntino": "Pane bianco (2 fette), Prosciutto cotto (4 fette)", "Pranzo": "Riso olio (100g), Parmigiano, Pane (60g), Parmigiano stagionato (100g), Lattuga", "Merenda": "Pane (80g), Marmellata (4 cuc.)", "Cena": "Trota forno (250g), Pane (80g), Cavolfiore (200g), Olio evo"},
        "Sabato": {"Colazione": "Tè, Miele, Cereali Special K (40g)", "Spuntino": "Yogurt magro frutta", "Pranzo": "Gnocchi pomodoro (200g), Parmigiano, Pollo petto (220g), Lattuga", "Merenda": "Torta di mele (1 fetta)", "Cena": "Bruschetta speck/gorgonzola (100g), Coca cola Light (1 bic.)"},
        "Domenica": {"Colazione": "Succo ACE, Croissant marmellata (60g)", "Spuntino": "Yogurt magro frutta", "Pranzo": "Passato verdure (150g), Pasta (30g), Parmigiano, Pane (80g), Nasello (200g), Pomodori", "Merenda": "Barretta Kellogg's", "Cena": "Pollo arrosto (200g), Pane (80g), Patate arrosto (200g), Olio evo"}
    },
    "Settimana A.B.2": {
        "Lunedì": {"Colazione": "Tè, Miele, Fette biscottate (4), Marmellata", "Spuntino": "Pane bianco (2 fette), Prosciutto cotto (4 fette)", "Pranzo": "Minestrone (100g), Pasta (40g), Parmigiano, Pane (60g), Stracchino (100g), Valeriana", "Merenda": "Pane (80g), Marmellata (4 cuc.)", "Cena": "Maiale ai ferri (220g), Pane (80g), Piselli (150g), Olio evo"},
        "Martedì": {"Colazione": "Succo ACE, Biscotti Oro Saiwa (8 pz)", "Spuntino": "Pane bianco (2 fette), Speck (5 fette)", "Pranzo": "Pasta olio (100g), Parmigiano, Pane (80g), Speck (5 fette), Radicchio", "Merenda": "Banana (1 pz)", "Cena": "Branzino ai ferri (300g), Pane (80g), Piselli (150g), Olio evo"},
        "Mercoledì": {"Colazione": "Tè, Miele, Biscotti Oro Saiwa (8 pz)", "Spuntino": "Pane bianco (2 fette), Prosciutto crudo (5 fette)", "Pranzo": "Pasta pomodoro (100g), Parmigiano, Pane (80g), Prosciutto crudo (5 fette), Cavolo", "Merenda": "Banana (1 pz)", "Cena": "Cavallo ai ferri (220g), Pane (80g), Spinaci (200g), Olio evo"},
        "Giovedì": {"Colazione": "Succo ACE, Fette biscottate (4), Cioccolata nocciole (4 cuc.)", "Spuntino": "Pane bianco (2 fette), Salame nostrano (5 fette)", "Pranzo": "Brodo carne, Pasta (40g), Parmigiano, Cracker (1 pz), Parmigiano stagionato (80g), Carote", "Merenda": "Pane (80g), Marmellata (4 cuc.)", "Cena": "Tacchino ai ferri (200g), Pane (60g), Peperoni (200g), Olio evo"},
        "Venerdì": {"Colazione": "Succo ACE, Fette biscottate (4), Miele (4 cuc.)", "Spuntino": "Pane bianco (2 fette), Prosciutto cotto (4 fette)", "Pranzo": "Gnocchi (200g), Ragù (80g), Parmigiano, Pane (80g), Mozzarella (100g), Radicchio", "Merenda": "Mela (1 pz)", "Cena": "Cavallo ai ferri (200g), Pane (80g), Cavolfiore (200g), Olio evo"},
        "Sabato": {"Colazione": "Tè, Miele, Cereali Special K (40g)", "Spuntino": "Yogurt magro frutta", "Pranzo": "Risotto peperoni (100g), Cracker (1 pz), Pollo petto (220g), Insalata mista", "Merenda": "Crostata marmellata (1 fetta)", "Cena": "Piadina (1 pz), Prosciutto crudo (8 fette), Squacquerone (50g), Sprite"},
        "Domenica": {"Colazione": "Tè, Miele, Cereali Special K (40g)", "Spuntino": "Yogurt magro frutta", "Pranzo": "Pasta ragù (100g), Parmigiano, Pane (80g), Asiago (100g), Valeriana", "Merenda": "Barretta Kellogg's", "Cena": "Tonno (2 conf.), Pane (80g), Fagioli Borlotti (150g), Olio evo"}
    }
}

# --- FUNZIONI DI UTILITÀ ---
def normalizza_key(k):
    """Mappa nomi comuni alle chiavi del DB del PDF"""
    k = k.lower()
    mapping = {
        "pasta": "Pasta", "riso": "Riso", "pane": "Pane comune", 
        "olio": "Olio d'oliva", "parmigiano": "Parmigiano", "miele": "Miele",
        "prosciutto cotto": "Prosciutto cotto", "prosciutto crudo": "Prosciutto crudo",
        "speck": "Speck", "banana": "Banana", "mela": "Mela", "tonno": "Tonno scatola (sgocc.)",
        "fette biscottate": "Fette biscottate", "biscotti": "Biscotti",
        "pollo": "Pollo (petto)", "tacchino": "Tacchino", "manzo": "Manzo magro",
        "vitello": "Vitello magro", "maiale": "Maiale magro", "merluzzo": "Merluzzo",
        "orata": "Orata/Branzino", "branzino": "Orata/Branzino", "salmone": "Salmone",
        "piselli": "Piselli freschi", "fagioli": "Fagioli secchi", "spinaci": "Spinaci",
        "carote": "Carote", "zucchine": "Zucchine", "cavolfiore": "Cavolfiore",
        "cioccolata": "Cioccolata spalmabile", "marmellata": "Marmellata",
        "yogurt": "Yogurt magro", "cereali": "Cereali Special K",
        "salame": "Salame", "salsiccia": "Salsiccia", "pizza": "Pizza",
        "gnocchi": "Gnocchi"
    }
    for key, val in mapping.items():
        if key in k: return val
    return None

def stima_calorie(descrizione_pasto):
    """Estima le calorie da una stringa di testo con pesi PDF"""
    tot_kcal = 0
    items = descrizione_pasto.split(',')
    
    flat_db = {}
    for cat in db_alimenti.values():
        for k, v in cat.items():
            flat_db[k] = v
            
    for item in items:
        item = item.strip()
        grams = 0
        
        # 1. Cerca Grammi (es. 120g)
        match_g = re.search(r'(\d+)\s*g', item)
        if match_g:
            grams = int(match_g.group(1))
        
        # 2. Cerca Cucchiai/Cucchiaini (Regole PDF)
        # 1 cucchiaio olio = 12g, 1 cucchiaino = 6g
        if "cuc." in item or "cucchia" in item:
            qta_match = re.search(r'(\d+)', item)
            qta = int(qta_match.group(1)) if qta_match else 1
            
            if "olio" in item.lower() and "cuc.ni" in item.lower(): grams = qta * 6
            elif "olio" in item.lower(): grams = qta * 12
            elif "parmigiano" in item.lower(): grams = qta * 10
            elif "miele" in item.lower() and "cuc.ni" in item.lower(): grams = qta * 6 
            elif "marmellata" in item.lower() and "cuc.ni" in item.lower(): grams = qta * 6
            elif "marmellata" in item.lower(): grams = qta * 15
            else: grams = qta * 10 

        # 3. Cerca Pezzi/Fette
        match_pz = re.search(r'(\d+)\s*(pz|fet)', item)
        if match_pz:
            qta = int(match_pz.group(1))
            if "biscotti" in item.lower(): grams = qta * 6
            elif "fette biscottate" in item.lower(): grams = qta * 8
            elif "prosciutto" in item.lower() or "speck" in item.lower() or "salame" in item.lower(): grams = qta * 15 
            elif "cracker" in item.lower(): grams = qta * 25 
            elif "banana" in item.lower(): grams = 110 # media
            elif "mela" in item.lower(): grams = 160 
            elif "yogurt" in item.lower(): grams = 125
            else: grams = qta * 50 
            
        if grams == 0 and ("pasta" in item.lower() or "riso" in item.lower()): grams = 80
        
        found_key = normalizza_key(item)
        if found_key and found_key in flat_db:
             kcal_100 = flat_db[found_key]['kcal']
             tot_kcal += (grams * kcal_100) / 100
             
    return tot_kcal

# --- HEADER APP ---
st.title("🥑 La dieta di AGU")
st.markdown("**Il tuo assistente nutrizionale personale.**")

# --- NAVIGAZIONE A TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📅 Menu", "⚖️ Sostituzioni", "🔍 Cerca", "📊 Analisi"])

# --- TAB 1: MENU ---
with tab1:
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        settimana = st.selectbox("Seleziona Settimana", list(menu_settimanali.keys()), key="week_select")
    with col_sel2:
        giorno = st.selectbox("Seleziona Giorno", ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"], key="day_select")
    
    st.divider()
    
    if giorno in menu_settimanali[settimana]:
        pasti = menu_settimanali[settimana][giorno]
        totale_giornaliero = 0
        
        icons = {
            "Colazione": "☕", "Spuntino": "🍎", "Pranzo": "🍝", 
            "Merenda": "🥨", "Cena": "🌙"
        }
        
        for pasto, descrizione in pasti.items():
            kcal_pasto = stima_calorie(descrizione)
            totale_giornaliero += kcal_pasto
            
            icona = icons.get(pasto, "🍽️")
            
            css_class = "meal-card"
            if "Colazione" in pasto: css_class += " type-colazione"
            elif "Spuntino" in pasto or "Merenda" in pasto: css_class += " type-spuntino"
            elif "Pranzo" in pasto: css_class += " type-pranzo"
            elif "Cena" in pasto: css_class += " type-cena"
            
            badge_html = f'<div class="kcal-badge">{int(kcal_pasto)} kcal</div>' if kcal_pasto > 0 else ""
            
            html_content = f"""
            <div class="{css_class}">
                <div class="meal-header">
                    <span class="meal-title">{icona} {pasto}</span>
                    {badge_html}
                </div>
                <div class="meal-content">{descrizione}</div>
            </div>
            """
            st.markdown(html_content, unsafe_allow_html=True)
            
        # BOX TOTALE
        st.markdown(f"""
        <div class="daily-total">
            <div style="font-size: 0.9em; opacity: 0.8;">TOTALE GIORNALIERO</div>
            <div class="total-kcal">{int(totale_giornaliero)} Kcal</div>
            <div style="margin-top:10px; font-size:0.8em; color:#ccc;">
                *Calcolo basato su pesi e conversioni del PDF
            </div>
        </div>
        """, unsafe_allow_html=True)
            
    else:
        st.error("Dati non disponibili.")

# --- TAB 2: CALCOLATORE AVANZATO ---
with tab2:
    st.info("💡 **Bilanciamento:** Calcolo isocalorico con monitoraggio proteine e carboidrati.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🔴 Togli")
        categoria = st.selectbox("Categoria", list(db_alimenti.keys()), key="cat_calc")
        cibo_originale = st.selectbox("Alimento", list(db_alimenti[categoria].keys()), key="alimento_orig")
        quantita_originale = st.number_input("Grammi", min_value=10, value=100, step=10, key="q_orig")
        
    with c2:
        st.markdown("### 🟢 Aggiungi")
        tutti_cibi = [c for cat in db_alimenti.values() for c in cat.keys()]
        cibo_sostituto = st.selectbox("Nuovo Alimento", tutti_cibi, index=0, key="alimento_sub")
    
    vals_orig = {}
    vals_new = {}
    for cat in db_alimenti.values():
        if cibo_originale in cat: vals_orig = cat[cibo_originale]
        if cibo_sostituto in cat: vals_new = cat[cibo_sostituto]
    
    if st.button("🧮 Calcola Sostituzione", type="primary", use_container_width=True, key="btn_calc"):
        kcal_tot_orig = (quantita_originale * vals_orig['kcal']) / 100
        prot_tot_orig = (quantita_originale * vals_orig['prot']) / 100
        carb_tot_orig = (quantita_originale * vals_orig['carb']) / 100
        
        quantita_nuova = (kcal_tot_orig * 100) / vals_new['kcal']
        
        prot_tot_new = (quantita_nuova * vals_new['prot']) / 100
        carb_tot_new = (quantita_nuova * vals_new['carb']) / 100
        
        diff_prot = prot_tot_new - prot_tot_orig
        diff_carb = carb_tot_new - carb_tot_orig
        
        st.divider()
        st.markdown(f"<h2 style='text-align: center; color: #2e7d32;'>Mangia {int(quantita_nuova)}g di {cibo_sostituto}</h2>", unsafe_allow_html=True)
        st.caption(f"Sostituisce {quantita_originale}g di {cibo_originale} mantenendo {int(kcal_tot_orig)} Kcal.")
        
        st.markdown("#### ⚖️ Bilancio Nutrizionale")
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            st.markdown("**Proteine**")
            st.progress(min(1.0, prot_tot_new / (max(prot_tot_orig, 1) * 2)))
            st.write(f"{int(prot_tot_orig)}g ➝ **{int(prot_tot_new)}g**")
            if abs(diff_prot) > 5:
                color = "red" if diff_prot < 0 else "orange"
                icon = "🔻" if diff_prot < 0 else "🔺"
                st.markdown(f":{color}[{icon} {int(diff_prot)}g]")
            else:
                st.markdown(":green[✅ Ok]")

        with mc2:
            st.markdown("**Carboidrati**")
            st.progress(min(1.0, carb_tot_new / (max(carb_tot_orig, 1) * 2)))
            st.write(f"{int(carb_tot_orig)}g ➝ **{int(carb_tot_new)}g**")
            if abs(diff_carb) > 10:
                color = "red" if diff_carb > 0 else "orange"
                icon = "🔺" if diff_carb > 0 else "🔻"
                st.markdown(f":{color}[{icon} {int(diff_carb)}g]")
            else:
                st.markdown(":green[✅ Ok]")
                
        with mc3:
            st.markdown("**Grassi/Densità**")
            if quantita_nuova > quantita_originale * 1.5: st.info("Piatto voluminoso 🥗")
            elif quantita_nuova < quantita_originale * 0.7: st.warning("Piatto piccolo 🍰")
            else: st.success("Volume simile 🍽️")

        if diff_prot < -8:
            st.markdown("""<div class="warning-box">⚠️ <b>Attenzione:</b> Stai perdendo proteine. Integra con albume o yogurt.</div>""", unsafe_allow_html=True)
        if diff_carb > 15:
            st.markdown("""<div class="warning-box">⚠️ <b>Attenzione:</b> Carboidrati in aumento. Riduci il pane.</div>""", unsafe_allow_html=True)

# --- TAB 3: RICERCA ---
with tab3:
    st.markdown("### 🔎 Trova piatto")
    search_query = st.text_input("Cosa vuoi mangiare?", placeholder="es. Pizza, Salmone...", key="search_input")
    
    if search_query:
        global_found = False
        for week_name, week_data in menu_settimanali.items():
            for day_name, day_data in week_data.items():
                found_meals = {k:v for k,v in day_data.items() if search_query.lower() in v.lower()}
                
                if found_meals:
                    global_found = True
                    st.divider()
                    st.markdown(f"#### 📅 {week_name} - {day_name}")
                    for m_name, m_desc in found_meals.items():
                         st.markdown(f"**{m_name}:** {m_desc.replace(search_query, f'**{search_query}**')}")
                    
                    with st.expander(f"📖 Menu completo di {day_name}"):
                        for meal, desc in day_data.items():
                            st.write(f"**{meal}:** {desc}")
        if not global_found: st.warning("Nessun risultato.")

# --- TAB 4: GRAFICI ---
with tab4:
    st.markdown("### 📊 Analisi Nutrizionale")
    cat_grafico = st.selectbox("Categoria", list(db_alimenti.keys()), key="cat_graf")
    
    raw_data = []
    for food, vals in db_alimenti[cat_grafico].items():
        raw_data.append({"Alimento": food, "Valore": vals['kcal'], "Tipo": "Calorie (Kcal)"})
        raw_data.append({"Alimento": food, "Valore": vals['prot']*4, "Tipo": "Proteine (Kcal equiv)"})
        raw_data.append({"Alimento": food, "Valore": vals['carb']*4, "Tipo": "Carboidrati (Kcal equiv)"})

    df_chart = pd.DataFrame(raw_data)
    
    chart = alt.Chart(df_chart).mark_bar().encode(
        x=alt.X('Alimento', sort='-y'),
        y='Valore',
        color='Tipo',
        tooltip=['Alimento', 'Valore', 'Tipo']
    ).properties(height=400)
    
    st.altair_chart(chart, use_container_width=True)
    st.caption("*Proteine e carboidrati in Kcal equivalenti (x4) per confronto visivo.")
