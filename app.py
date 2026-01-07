import streamlit as st
import pandas as pd
import altair as alt

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="MyDiet Assistant", page_icon="🥗", layout="centered")

# --- CSS PERSONALIZZATO ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Card principale per i pasti */
    .meal-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #4CAF50;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .meal-title {
        color: #2e7d32;
        font-weight: bold;
        font-size: 1.1em;
        margin-bottom: 5px;
    }
    .meal-content {
        color: #424242;
        font-size: 0.95em;
    }

    /* Stile per i risultati di ricerca */
    .search-hit {
        background-color: #e8f5e9; 
        padding: 10px; 
        border-radius: 8px; 
        margin-bottom: 5px; 
        border: 1px solid #c8e6c9;
    }
    
    /* Titoli colorati */
    h1 { color: #2E7D32; }
    h2 { color: #388E3C; }
    h3 { color: #43A047; }
</style>
""", unsafe_allow_html=True)

# --- DATABASE DATI ---
db_alimenti = {
    "Latte e Derivati": {
        "Latte intero": 62, "Latte parz. scremato": 41, "Yogurt magro": 37, "Yogurt intero": 64,
        "Mozzarella": 244, "Parmigiano": 374, "Stracchino": 300, "Ricotta": 173, 
        "Gorgonzola": 358, "Emmenthal": 404, "Asiago": 356, "Squacquerone": 250
    },
    "Carni": {
        "Manzo magro": 129, "Vitello magro": 113, "Pollo (petto)": 97, "Pollo intero": 175,
        "Tacchino": 134, "Maiale magro": 131, "Cavallo": 111, 
        "Prosciutto crudo": 370, "Prosciutto cotto": 412, "Bresaola/Crudo magro": 218,
        "Speck": 300, "Salame nostrano": 463, "Salsiccia": 334, "Hamburger manzo": 250
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

# --- HEADER APP ---
st.title("🥗 MyDiet Assistant")
st.markdown("**Benvenuto nel tuo assistente nutrizionale personale.**")

# --- NAVIGAZIONE A TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📅 Menu Settimanale", "🔄 Calcola Sostituzione", "🔍 Cerca Piatto", "📊 Grafici Nutrienti"])

# --- TAB 1: MENU ---
with tab1:
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        settimana = st.selectbox("Seleziona Settimana", list(menu_settimanali.keys()))
    with col_sel2:
        giorno = st.selectbox("Seleziona Giorno", ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"])
    
    st.divider()
    
    if giorno in menu_settimanali[settimana]:
        pasti = menu_settimanali[settimana][giorno]
        icons = {"Colazione": "☕", "Spuntino": "🍎", "Pranzo": "🍝", "Merenda": "🥨", "Cena": "🌙"}
        
        for pasto, descrizione in pasti.items():
            icona = icons.get(pasto, "🍽️")
            st.markdown(f"""
            <div class="meal-card">
                <div class="meal-title">{icona} {pasto}</div>
                <div class="meal-content">{descrizione}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error("Dati non disponibili per questo giorno.")

# --- TAB 2: CALCOLATORE ---
with tab2:
    st.info("💡 **Principio Isocalorico:** Sostituisci gli alimenti mantenendo le stesse calorie.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🔴 Cibo da togliere")
        categoria = st.selectbox("Categoria", list(db_alimenti.keys()))
        cibo_originale = st.selectbox("Alimento", list(db_alimenti[categoria].keys()))
        quantita_originale = st.number_input("Grammi previsti", min_value=10, value=100, step=10)
        
    with c2:
        st.markdown("### 🟢 Cibo da mettere")
        tutti_cibi = [c for cat in db_alimenti.values() for c in cat.keys()]
        cibo_sostituto = st.selectbox("Nuovo Alimento", tutti_cibi, index=0)
        
    # Calcolo
    kcal_orig = 0
    kcal_new = 0
    for cat in db_alimenti.values():
        if cibo_originale in cat: kcal_orig = cat[cibo_originale]
        if cibo_sostituto in cat: kcal_new = cat[cibo_sostituto]
    
    if st.button("🧮 Calcola Equivalenza", type="primary", use_container_width=True):
        kcal_totali = (quantita_originale * kcal_orig) / 100
        quantita_nuova = (kcal_totali * 100) / kcal_new
        
        st.divider()
        res_col1, res_col2 = st.columns(2)
        with res_col1:
             st.metric(label="Calorie Totali", value=f"{int(kcal_totali)} kcal")
        with res_col2:
             st.metric(label=f"Nuova quantità di {cibo_sostituto}", value=f"{int(quantita_nuova)} g", delta=f"{int(quantita_nuova - quantita_originale)}g diff.")
             
        if quantita_nuova > quantita_originale:
            st.success(f"Puoi mangiare di più! 🎉 ({int(quantita_nuova)}g invece di {quantita_originale}g)")
        else:
            st.warning(f"Attenzione, alimento più calorico. Riduci la porzione a {int(quantita_nuova)}g.")

# --- TAB 3: RICERCA (AGGIORNATA) ---
with tab3:
    st.markdown("### 🔎 Trova il tuo piatto preferito")
    search_query = st.text_input("Cosa vuoi mangiare?", placeholder="es. Pizza, Salmone, Pasta...")
    
    if search_query:
        global_found = False
        
        # Iterazione su Settimane
        for week_name, week_data in menu_settimanali.items():
            # Iterazione su Giorni
            for day_name, day_data in week_data.items():
                
                # Cerco se nel giorno corrente c'è almeno un match
                found_meals_in_day = {}
                for meal_name, meal_desc in day_data.items():
                    if search_query.lower() in meal_desc.lower():
                        found_meals_in_day[meal_name] = meal_desc
                
                # Se ho trovato qualcosa in questo giorno
                if found_meals_in_day:
                    global_found = True
                    st.divider()
                    st.markdown(f"#### 📅 {week_name} - {day_name}")
                    
                    # 1. Mostro i risultati specifici trovati
                    for m_name, m_desc in found_meals_in_day.items():
                        # Evidenzio la parola cercata
                        highlighted_desc = m_desc.replace(search_query, f"**{search_query}**").replace(search_query.lower(), f"**{search_query.lower()}**").replace(search_query.capitalize(), f"**{search_query.capitalize()}**")
                        
                        st.markdown(f"""
                        <div class="search-hit">
                            <b>{m_name}:</b> {highlighted_desc}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # 2. Mostro il pulsante (Expander) per vedere TUTTO il menu di quel giorno
                    with st.expander(f"📖 Apri menu completo di {day_name}"):
                        for meal, desc in day_data.items():
                            if meal in found_meals_in_day:
                                # Evidenzia il pasto trovato anche qui dentro
                                st.markdown(f"✅ **{meal}**: {desc}")
                            else:
                                st.markdown(f"🔹 **{meal}**: {desc}")

        if not global_found:
            st.warning("Nessun piatto trovato con questo nome.")

# --- TAB 4: GRAFICI ---
with tab4:
    st.markdown("### 📊 Densità Calorica Alimenti (Kcal/100g)")
    cat_grafico = st.selectbox("Quale categoria vuoi analizzare?", list(db_alimenti.keys()))
    
    data_chart = pd.DataFrame(list(db_alimenti[cat_grafico].items()), columns=["Alimento", "Kcal"])
    
    chart = alt.Chart(data_chart).mark_bar().encode(
        x=alt.X('Alimento', sort='-y'),
        y='Kcal',
        color=alt.Color('Kcal', scale=alt.Scale(scheme='greens')),
        tooltip=['Alimento', 'Kcal']
    ).properties(height=300)
    
    st.altair_chart(chart, use_container_width=True)
    
    st.markdown("#### Equivalenze Rapide")
    col_eq1, col_eq2 = st.columns(2)
    with col_eq1:
        st.info("🍞 **30g Pane** = 25g Pasta")
        st.info("🥔 **100g Patate** = 30g Pane")
    with col_eq2:
        st.info("🥩 **100g Vitello** = 150g Pesce")
        st.info("🍎 **1 Mela** = 1 Arancia")
