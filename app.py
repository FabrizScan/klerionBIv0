import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# Leggi le credenziali dalle variabili d'ambiente
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Le credenziali di Supabase non sono state configurate correttamente.")
    st.stop()

# Crea il client Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Funzione per ottenere i dati da Supabase
def fetch_data(store_id=None):
    query = supabase.table("goods_entries_monthly_summary").select("*")
    if store_id:
        query = query.eq("store_id", store_id)  # Filtra per store_id
    response = query.execute()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame()

# Leggi il parametro store_id dall'URL (per l'iframe)
query_params = st.experimental_get_query_params()
store_id_from_url = query_params.get("store_id", [None])[0]  # Prende il primo valore o None

# Recupera i dati
if store_id_from_url:
    # Se store_id è passato nell'URL, filtra direttamente i dati
    df = fetch_data(store_id_from_url)
    if df.empty:
        st.error(f"Nessun dato trovato per Store ID: {store_id_from_url}")
else:
    # Altrimenti, recupera tutti i dati e lascia scegliere all'utente
    df = fetch_data()
    if df.empty:
        st.error("Errore nella richiesta dei dati o nessun dato disponibile!")
        st.stop()

# Controlla se il DataFrame contiene i campi attesi
required_columns = {"store_id", "month", "total_value"}
if not df.empty and required_columns.issubset(df.columns):
    # Se store_id è passato dall'URL, usa quello, altrimenti mostra il selectbox
    if store_id_from_url:
        store_id_selected = store_id_from_url
    else:
        st.subheader("Tableau de Données")
        st.dataframe(df)
        store_id_selected = st.selectbox("Seleziona Store ID", df["store_id"].unique())

    # Filtra i dati per lo store selezionato e ordinali per mese
    df_store_month = df[df["store_id"] == store_id_selected].sort_values("month")

    # Formatta la colonna 'month' in formato AAAA-MM
    df_store_month['month'] = pd.to_datetime(df_store_month['month']).dt.strftime('%Y-%m')

    # Formatta 'total_value' come decimale con 2 cifre
    df_store_month['total_value'] = df_store_month['total_value'].round(2)

    # Visualizza i dati mensili (senza store_id nella tabella)
    st.subheader(f"Valore mensile per Store {store_id_selected}")
    st.dataframe(df_store_month[['month', 'total_value']])  # Mostra solo month e total_value
    st.line_chart(df_store_month.set_index("month")["total_value"])
else:
    st.write("Nessun dato disponibile o colonne mancanti.")