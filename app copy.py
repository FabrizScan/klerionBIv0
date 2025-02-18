import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Imposta le credenziali per Supabase
SUPABASE_URL = "https://roousoojawkidfmewghh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJvb3Vzb29qYXdraWRmbWV3Z2hoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzQxMTY0MTgsImV4cCI6MjA0OTY5MjQxOH0.O-k7O19h9d_KVjVNzJ0NBHf1-WPdhY-cicT4R13E6s8"

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
    
    # Raggruppa per store e somma il total_value su tutti i mesi
    df_store = df.groupby("store_id")["total_value"].sum().reset_index()
    
    st.subheader("Valeur pour Magasin")
    st.dataframe(df_store)
    st.bar_chart(df_store.set_index("store_id"))
    
    # Visualizza i dati mensili per un determinato store
    store_id_selected = st.selectbox("Seleziona Store ID", df["store_id"].unique())
    df_store_month = df[df["store_id"] == store_id_selected].sort_values("month")
    
    st.subheader(f"Valore mensile per Store {store_id_selected}")
    st.dataframe(df_store_month)
    st.line_chart(df_store_month.set_index("month")["total_value"])
else:
    st.write("Nessun dato disponibile o colonne mancanti.")
