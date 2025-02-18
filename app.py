import os
from dotenv import load_dotenv  # importa la libreria per caricare le variabili dal file .env
import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# Legge le credenziali dalle variabili d'ambiente
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Le credenziali di Supabase non sono state configurate correttamente.")
    st.stop()

# Crea il client Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Esegui una query sulla vista 'goods_entries_monthly_summary'
response = supabase.table("goods_entries_monthly_summary").select("*").execute()

# Controlla se abbiamo dei dati (l'attributo 'data' viene valorizzato in caso di successo)
if response.data is None:
    st.error("Errore nella richiesta dei dati!")
    df = pd.DataFrame()
else:
    df = pd.DataFrame(response.data)

# Controlla se il DataFrame contiene i campi attesi
required_columns = {"store_id", "month", "total_value"}
if not df.empty and required_columns.issubset(df.columns):
    st.subheader("Table de Données")
    st.dataframe(df)
    
    # Visualizza i dati mensili per un determinato store
    store_id_selected = st.selectbox("Seleziona Store ID", df["store_id"].unique())
    df_store_month = df[df["store_id"] == store_id_selected].sort_values("month")
    
    st.subheader(f"Valore mensile per Store {store_id_selected}")
    st.dataframe(df_store_month)
    st.line_chart(df_store_month.set_index("month")["total_value"])
else:
    st.write("Nessun dato disponibile o colonne mancanti.")
