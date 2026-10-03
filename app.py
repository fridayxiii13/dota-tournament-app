import streamlit as st
import pandas as pd

# Налаштування сторінки
st.set_page_config(page_title="Dota 2 Tournament", page_icon="🎮", layout="wide")

st.title("🏆 Dota 2 Tournament Dashboard")
st.markdown("Це тестова MVP-версія. Дані поки що тестові, щоб перевірити відображення.")

# Створюємо дві колонки для груп
col1, col2 = st.columns(2)

with col1:
    st.header("Група A (5 команд)")
    # Тестові дані для Групи А
    data_a = {
        "Команда": ["Radiant Legends", "Dire Wolves", "Mid Or Feed", "Support Squad", "Carry Us"],
        "Ігри": [0, 0, 0, 0, 0],
        "Перемоги": [0, 0, 0, 0, 0],
        "Поразки": [0, 0, 0, 0, 0],
        "Очки": [0, 0, 0, 0, 0]
    }
    df_a = pd.DataFrame(data_a)
    st.dataframe(df_a, hide_index=True, use_container_width=True)

with col2:
    st.header("Група B (4 команди)")
    # Тестові дані для Групи B
    data_b = {
        "Команда": ["Techies Enjoyers", "Pudge Hookers", "Rampage", "Roshan Slayers"],
        "Ігри": [0, 0, 0, 0],
        "Перемоги": [0, 0, 0, 0],
        "Поразки": [0, 0, 0, 0],
        "Очки": [0, 0, 0, 0]
    }
    df_b = pd.DataFrame(data_b)
    st.dataframe(df_b, hide_index=True, use_container_width=True)

st.divider()
st.subheader("Останні матчі (Тест)")
st.info("Radiant Legends **2 : 1** Dire Wolves")
st.info("Techies Enjoyers **0 : 2** Pudge Hookers")
