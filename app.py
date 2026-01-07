import streamlit as st
import pandas as pd

# --- CONFIGURAZIONE DATI DAL PDF ---

# 1. DATABASE CALORIE (Valori per 100g estratti dal documento - Pagg. 32-36)
db_alimenti = {
    "Latte e Derivati": {
        "Latte intero": 62, "Latte parz. scremato": 41, "Yogurt magro": 37, "Yogurt intero": 64,
        "Mozzarella": 244, "Parmigiano": 374, "Stracchino": 300, "Ricotta": 173, 
        "Gorgonzola": 358, "Emmenthal": 404, "Asiago": 356, "Squacquerone": 250 # stima standard
    },
    "Carni": {
        "Manzo magro": 129, "Vitello magro": 113, "Pollo (petto)": 97, "Pollo intero": 175,
        "Tacchino": 134, "Maiale magro": 131, "Cavallo": 111, 
        "Prosciutto crudo": 370, "Prosciutto cotto": 412, "Bresaola/Crudo magro": 218,
        "Speck": 300, "Salame nostrano": 463, "Salsiccia": 334, "Hamburger manzo": 250 # stima
    },
    "Pesce": {
        "Merluzzo": 71, "Sogliola": 86, "Tonno fresco": 158, "Tonno scatola (sgocc.)": 190,
        "Orata/Branzino": 82, "Salmone": 185, "Trota": 96, "Nasello": 75, "Gamberi": 71
    },
    "Cereali e Carboidrati": {
        "Pane comune": 260, "Pane integrale": 243, "Pasta/Riso": 377, 
        "Patate": 89, "Fette biscottate": 431, "Crackers": 464, 
        "Biscotti Oro Saiwa": 430, "Cereali Special K": 370, "Gnocchi": 160
    },
    "Verdure e Legumi": {
        "Insalata/Lattuga/Valeriana": 20, "Pomodori": 25, "Fagiolini": 19, "Spinaci": 32,
        "Piselli freschi/lessi": 79, "Fagioli": 109, "Lenticchie": 339, 
        "Zucchine": 12, "Carote": 35, "Finocchi": 31, "Cavolfiore": 25, "Broccoli": 27, "Peperoni": 22
    },
    "Frutta e Dolci": {
        "Mela": 48, "Banana": 70, "Arancia/Succo": 40, "Marmellata": 250, "Miele": 304,
        "Cioccolata spalmabile": 530, "Tiramisù": 367, "Crostata": 350, "Barretta cereali": 400
    },
    "Condimenti": {
        "Olio d'oliva": 900, "Burro": 758, "Margarina": 760
    }
}

# 2. MENU SETTIMANALI COMPLETI (A.B., A.B.1, A.B.2)
menu_settimanali = {
    "Settimana A.B.": {
        "Lunedì": {
            "Colazione": "Tè, Miele (2 cuc.), Fette biscottate (4), Marmellata (4 cuc.)",
            "Spuntino": "Pane bianco (2 fette), Prosciutto cotto (4 fette)",
            "Pranzo": "Pasta aglio/olio (120g), Parmigiano (2 cuc.), Pane (60g), Stracchino (100g), Valeriana",
            "Merenda": "Banana (1 pz)",
            "Cena": "Passato verdure (150g), Pane (80g), Maiale ai ferri (220g), Olio evo (2 cuc.)"
        },
        "Martedì": {
            "Colazione": "Succo ACE (1 bic.), Biscotti Oro Saiwa (8 pz)",
            "Spuntino": "Pane bianco (2 fette), Speck (5 fette)",
            "Pranzo": "Risotto zucchine (120g), Parmigiano (2 cuc.), Pane (80g), Speck (5 fet.), Radicchio",
            "Merenda": "Cracker Doria (1 pz)",
            "Cena": "Branzino ai ferri (300g), Pane (80g), Piselli lessati (150g), Olio evo (3 cuc.)"
        },
        "Mercoledì": {
            "Colazione": "Tè, Miele (2 cuc.), Biscotti Oro Saiwa (8 pz)",
            "Spuntino": "Pane bianco (2 fette), Prosciutto crudo (6 fette)",
            "Pranzo": "Tortellini panna (180g), Parmigiano (2 cuc.), Pane (80g), Tonno (1 conf.), Cavolo cappuccio",
            "Merenda": "Barretta Kellogg's (1 pz)",
            "Cena": "Manzo ai ferri (200g), Pane (80g), Spinaci lessi (200g), Olio evo (3 cuc.)"
        },
        "Giovedì": {
            "Colazione": "Succo ACE, Fette biscottate (4), Cioccolata nocciole (4 cuc.)",
            "Spuntino": "Pane bianco (2 fette), Salame nostrano (5 fette)",
            "Pranzo": "Pasta pomodoro (120g), Parmigiano, Cracker (1 pz), Frittata (2 pz/150g albume), Carote (100g)",
            "Merenda": "Banana (1 pz)",
            "Cena": "Minestrone verdure (100g), Pane (60g), Petto tacchino (200g), Olio evo (3 cuc.)"
        },
        "Venerdì": {
            "Colazione": "Tè, Miele (2 cuc.), Fette biscottate (4), Miele (4 cuc.)",
            "Spuntino": "Pane bianco (2 fette), Prosciutto cotto (4 fette)",
            "Pranzo": "Risotto zucca (120g), Parmigiano (2 cuc.), Pane (80g), Mozzarella (100g), Finocchi (100g)",
            "Merenda": "Mela (1 pz)",
            "Cena": "Merluzzo forno (250g), Pane (80g), Cavolfiore lesso (200g), Olio evo (3 cuc.)"
        },
        "Sabato": {
            "Colazione": "Tè, Miele (2 cuc.), Cereali Special K (40g)",
            "Spuntino": "Yogurt magro frutta (1 pz)",
            "Pranzo": "Pollo petto ai ferri (250g), Insalata mista (200g), Olio evo (5 cuc.)",
            "Merenda": "Tiramisù (1 fetta)",
            "Cena": "Pizza Margherita (1 pz), Zucca forno (100g), Salsiccia (100g), Sprite (1 bic.)"
        },
        "Domenica": {
            "Colazione": "Succo ACE, Croissant marmellata (60g)",
            "Spuntino": "Yogurt magro frutta (1 pz)",
            "Pranzo": "Pasta ragù (100g), Parmigiano, Pane (80g), Asiago (100g), Valeriana",
            "Merenda": "Barretta Kellogg's (1 pz)",
            "Cena": "Orata forno (250g), Pane (80g), Broccoli lessi (200g), Olio evo (6 cuc.)"
        }
    },
    "Settimana A.B.1": {
        "Lunedì": {
            "Colazione": "Tè, Miele, Cereali Special K (40g)",
            "Spuntino": "Pane bianco (2 fette), Speck (5 fette)",
            "Pranzo": "Pasta pesto (100g), Hamburger manzo (1 pz), Pane (60g), Valeriana",
            "Merenda": "Pane (80g), Marmellata (4 cuc.)",
            "Cena": "Salmone forno (200g), Pane (80g), Piselli lessati (150g), Olio evo"
        },
        "Martedì": {
            "Colazione": "Succo ACE, Biscotti Oro Saiwa (8 pz)",
            "Spuntino": "Pane bianco (2 fette), Prosciutto cotto (4 fette)",
            "Pranzo": "Risotto piselli (100g), Parmigiano, Pane (80g), Prosciutto cotto (4 fette), Radicchio",
            "Merenda": "Cracker Doria (1 pz)",
            "Cena": "Hamburger manzo (2 pz), Pane (80g), Piselli (150g), Olio evo"
        },
        "Mercoledì": {
            "Colazione": "Tè, Miele, Biscotti Oro Saiwa (8 pz)",
            "Spuntino": "Pane bianco (2 fette), Prosciutto crudo (6 fette)",
            "Pranzo": "Tortellini brodo (100g), Parmigiano, Cracker (1 pz), Frittata semplice (2 pz), Cavolo cappuccio",
            "Merenda": "Pane (80g), Marmellata (4 cuc.)",
            "Cena": "Manzo ai ferri (200g), Pane (80g), Fagioli Borlotti (150g), Olio evo"
        },
        "Giovedì": {
            "Colazione": "Succo ACE, Fette biscottate (4), Cioccolata nocciole (4 cuc.)",
            "Spuntino": "Pane bianco (2 fette), Salame nostrano (5 fette)",
            "Pranzo": "Pasta (100g), Tonno (1 conf.), Cracker (1 pz), Tonno (2° conf.), Carote",
            "Merenda": "Banana (1 pz)",
            "Cena": "Tacchino ai ferri (200g), Pane (80g), Patate bollite (200g), Olio evo"
        },
        "Venerdì": {
            "Colazione": "Tè, Miele, Fette biscottate (4), Miele (4 cuc.)",
            "Spuntino": "Pane bianco (2 fette), Prosciutto cotto (4 fette)",
            "Pranzo": "Riso olio (100g), Parmigiano, Pane (60g), Parmigiano stagionato (100g), Lattuga",
            "Merenda": "Pane (80g), Marmellata (4 cuc.)",
            "Cena": "Trota forno (250g), Pane (80g), Cavolfiore (200g), Olio evo"
        },
        "Sabato": {
            "Colazione": "Tè, Miele, Cereali Special K (40g)",
            "Spuntino": "Yogurt magro frutta",
            "Pranzo": "Gnocchi pomodoro (200g), Parmigiano, Pollo petto (220g), Lattuga",
            "Merenda": "Torta di mele (1 fetta)",
            "Cena": "Bruschetta speck/gorgonzola (100g), Coca cola Light (1 bic.)"
        },
        "Domenica": {
            "Colazione": "Succo ACE, Croissant marmellata (60g)",
            "Spuntino": "Yogurt magro frutta",
            "Pranzo": "Passato verdure (150g), Pasta (30g), Parmigiano, Pane (80g), Nasello (200g), Pomodori",
            "Merenda": "Barretta Kellogg's",
            "Cena": "Pollo arrosto (200g), Pane (80g), Patate arrosto (200g), Olio evo"
        }
    },
    "Settimana A.B.2": {
        "Lunedì": {
            "Colazione": "Tè, Miele, Fette biscottate (4), Marmellata",
            "Spuntino": "Pane bianco (2 fette), Prosciutto cotto (4 fette)",
            "Pranzo": "Minestrone (100g), Pasta (40g), Parmigiano, Pane (60g), Stracchino (100g), Valeriana",
            "Merenda": "Pane (80g), Marmellata (4 cuc.)",
            "Cena": "Maiale ai ferri (220g), Pane (80g), Piselli (150g), Olio evo"
        },
        "Martedì": {
            "Colazione": "Succo ACE, Biscotti Oro Saiwa (8 pz)",
            "Spuntino": "Pane bianco (2 fette), Speck (5 fette)",
            "Pranzo": "Pasta olio (100g), Parmigiano, Pane (80g), Speck (5 fette), Radicchio",
            "Merenda": "Banana (1 pz)",
            "Cena": "Branzino ai ferri (300g), Pane (80g), Piselli (150g), Olio evo"
        },
        "Mercoledì": {
            "Colazione": "Tè, Miele, Biscotti Oro Saiwa (8 pz)",
            "Spuntino": "Pane bianco (2 fette), Prosciutto crudo (5 fette)",
            "Pranzo": "Pasta pomodoro (100g), Parmigiano, Pane (80g), Prosciutto crudo (5 fette), Cavolo",
            "Merenda": "Banana (1 pz)",
            "Cena": "Cavallo ai ferri (220g), Pane (80g), Spinaci (200g), Olio evo"
        },
        "Giovedì": {
            "Colazione": "Succo ACE, Fette biscottate (4), Cioccolata nocciole (4 cuc.)",
            "Spuntino": "Pane bianco (2 fette), Salame nostrano (5 fette)",
            "Pranzo": "Brodo carne, Pasta (40g), Parmigiano, Cracker (1 pz), Parmigiano stagionato (80g), Carote",
            "Merenda": "Pane (80g), Marmellata (4 cuc.)",
            "Cena": "Tacchino ai ferri (200g), Pane (60g), Peperoni (200g), Olio evo"
        },
        "Venerdì": {
            "Colazione": "Succo ACE, Fette biscottate (4), Miele (4 cuc.)",
            "Spuntino": "Pane bianco (2 fette), Prosciutto cotto (4 fette)",
            "Pranzo": "Gnocchi (200g), Ragù (80g), Parmigiano, Pane (80g), Mozzarella (100g), Radicchio",
            "Merenda": "Mela (1 pz)",
            "Cena": "Cavallo ai ferri (200g), Pane (80g), Cavolfiore (200g), Olio evo"
        },
        "Sabato": {
            "Colazione": "Tè, Miele, Cereali Special K (40g)",
            "Spuntino": "Yogurt magro frutta",
            "Pranzo": "Risotto peperoni (100g), Cracker (1 pz), Pollo petto (220g), Insalata mista",
            "Merenda": "Crostata marmellata (1 fetta)",
            "Cena": "Piadina (1 pz), Prosciutto crudo (8 fette), Squacquerone (50g), Sprite"
        },
        "Domenica": {
            "Colazione": "Tè, Miele, Cereali Special K (40g)",
            "Spuntino": "Yogurt magro frutta",
            "Pranzo": "Pasta ragù (100g), Parmigiano, Pane (80g), Asiago (100g), Valeriana",
            "Merenda": "Barretta Kellogg's",
            "Cena": "Tonno (2 conf.), Pane (80g), Fagioli Borlotti (150g), Olio evo"
        }
    }
}

# --- INTERFACCIA STREAMLIT ---

st.title("🍽️ MyDiet Assistant")
st.markdown("""
Questa applicazione ti aiuta a consultare il piano alimentare completo e a calcolare le sostituzioni basandosi sul principio di **equivalenza calorica**.
""")

st.sidebar.header("Navigazione")
scelta_funzione = st.sidebar.radio("Cosa vuoi fare?", ["Consulta Menu", "Calcolatore Sostituzioni", "Tabelle Riferimento"])

# --- FUNZIONE 1: CONSULTA MENU ---
if scelta_funzione == "Consulta Menu":
    st.header("📅 Piano Settimanale")
    
    settimana = st.selectbox("Seleziona la settimana:", list(menu_settimanali.keys()))
    giorno = st.selectbox("Seleziona il giorno:", ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"])
    
    if giorno in menu_settimanali[settimana]:
        pasti = menu_settimanali[settimana][giorno]
        for pasto, descrizione in pasti.items():
            st.subheader(pasto)
            st.info(descrizione)
    else:
        st.warning("Giorno non trovato.")

# --- FUNZIONE 2: CALCOLATORE SOSTITUZIONI ---
elif scelta_funzione == "Calcolatore Sostituzioni":
    st.header("🔄 Calcolatore Isocalorico")
    st.markdown("Calcola quanto mangiare di un cibo alternativo per mantenere le stesse calorie.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        categoria = st.selectbox("Categoria Alimento:", list(db_alimenti.keys()))
        cibo_originale = st.selectbox("Cibo previsto dal menu:", list(db_alimenti[categoria].keys()))
        quantita_originale = st.number_input("Quantità prevista (grammi):", min_value=10, value=100, step=10)
        
    with col2:
        st.markdown("⬇️ **Voglio sostituirlo con:**")
        cibo_sostituto = st.selectbox("Nuovo cibo:", [c for cat in db_alimenti.values() for c in cat.keys()])
        
    # Logica di calcolo
    kcal_orig_per_100 = 0
    kcal_new_per_100 = 0
    
    for cat in db_alimenti.values():
        if cibo_originale in cat: kcal_orig_per_100 = cat[cibo_originale]
        if cibo_sostituto in cat: kcal_new_per_100 = cat[cibo_sostituto]
            
    if st.button("Calcola Sostituzione"):
        calorie_totali = (quantita_originale * kcal_orig_per_100) / 100
        quantita_nuova = (calorie_totali * 100) / kcal_new_per_100
        
        st.success(f"Per sostituire **{quantita_originale}g di {cibo_originale}**...")
        st.metric(label=f"Devi mangiare questa quantità di {cibo_sostituto}:", value=f"{int(quantita_nuova)} gr")
        st.caption(f"Kcal originali: {int(calorie_totali)} | Kcal nuovo cibo/100g: {kcal_new_per_100}")

# --- FUNZIONE 3: TABELLE RIFERIMENTO ---
elif scelta_funzione == "Tabelle Riferimento":
    st.header("📋 Equivalenze Rapide")
    st.table(pd.DataFrame([
        {"Alimento Base": "30g Pane Comune", "Equivale a": "25g Pasta o Riso"},
        {"Alimento Base": "100g Patate", "Equivale a": "30g Pane"},
        {"Alimento Base": "100g Carne Vitello", "Equivale a": "150g Pesce o 2 Uova"},
        {"Alimento Base": "1 Mela", "Equivale a": "1 Arancia o 140g Pompelmo"},
        {"Alimento Base": "1 Cucchiaio Olio", "Equivale a": "12g circa"}
    ]))
    
    st.header("Database Calorie (Kcal/100g)")
    df_db = pd.DataFrame([(k, v) for cat in db_alimenti.values() for k, v in cat.items()], columns=["Alimento", "Kcal/100g"])
    st.dataframe(df_db)