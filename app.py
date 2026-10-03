import streamlit as st
import pandas as pd
import requests
import time # Додано для обходу кешу GitHub

st.set_page_config(page_title="Dota 2 Tournament", page_icon="🎮", layout="wide")

# ВАЖЛИВО: Замініть на ваше посилання
JSON_URL = "https://raw.githubusercontent.com/fridayxiii13/dota-tournament-app/main/data.json"

@st.cache_data(ttl=10)
def load_data():
    # Додаємо параметр часу, щоб GitHub завжди віддавав найсвіжіший файл
    fresh_url = f"{JSON_URL}?t={time.time()}"
    response = requests.get(fresh_url)
    return response.json()

data = load_data()

st.title("🏆 Dota 2 Tournament Dashboard")

# 1. ДИНАМІЧНИЙ ПІДРАХУНОК СТАТИСТИКИ
standings = {}
for group_name, teams_list in data['teams'].items():
    for team in teams_list:
        standings[team] = {
            'Команда': team, 
            'Ігри': 0, 
            'Перемоги': 0, 
            'Поразки': 0, 
            'Очки': 0, 
            'Група': group_name
        }

# Проходимо по матчах
for match in data['matches']:
    if match['status'] == 'Зіграна':
        t1 = match['team1']
        t2 = match['team2']
        pts1 = match.get('pts1', 0)
        pts2 = match.get('pts2', 0)
        
        if t1 in standings and t2 in standings:
            standings[t1]['Ігри'] += 1
            standings[t2]['Ігри'] += 1
            standings[t1]['Очки'] += pts1
            standings[t2]['Очки'] += pts2
            
            s1 = match.get('score1', 0)
            s2 = match.get('score2', 0)
            if s1 > s2:
                standings[t1]['Перемоги'] += 1
                standings[t2]['Поразки'] += 1
            elif s2 > s1:
                standings[t2]['Перемоги'] += 1
                standings[t1]['Поразки'] += 1

df_all = pd.DataFrame(standings.values())

# 2. ВІДОБРАЖЕННЯ ГРУП
col1, col2 = st.columns(2)

with col1:
    st.header("Група A")
    if not df_all.empty:
        df_a = df_all[df_all['Група'] == 'Група A'].drop(columns=['Група'])
        df_a = df_a.sort_values(by=['Очки', 'Перемоги'], ascending=[False, False])
        st.dataframe(df_a, hide_index=True, use_container_width=True)

with col2:
    st.header("Група B")
    if not df_all.empty:
        df_b = df_all[df_all['Група'] == 'Група B'].drop(columns=['Група'])
        df_b = df_b.sort_values(by=['Очки', 'Перемоги'], ascending=[False, False])
        st.dataframe(df_b, hide_index=True, use_container_width=True)

st.divider()

# 3. СТАДІЯ ПЛЕЙ-ОФ
st.header("🔥 Стадія Плей-оф")
playoff_stages = ["Півфінал 1", "Півфінал 2", "Матч за 3-тє місце", "Суперфінал"]
playoff_matches = [m for m in data['matches'] if m['stage'] in playoff_stages]

if playoff_matches:
    df_playoffs = pd.DataFrame(playoff_matches)
    
    # Безпечне створення колонки рахунку (без мутації кешу)
    df_playoffs['Візуальний_рахунок'] = df_playoffs.apply(
        lambda row: f"{row['score1']} : {row['score2']}" if row['status'] == 'Зіграна' else "- : -", 
        axis=1
    )
    
    expected_columns = ['stage', 'date', 'team1', 'Візуальний_рахунок', 'team2', 'status']
    for col in expected_columns:
        if col not in df_playoffs.columns:
            df_playoffs[col] = ""
            
    df_playoffs = df_playoffs[expected_columns]
    df_playoffs = df_playoffs.rename(columns={
        'stage': 'Етап', 
        'date': 'Дата',
        'team1': 'Команда 1', 
        'Візуальний_рахунок': 'Рахунок', 
        'team2': 'Команда 2', 
        'status': 'Статус'
    })
    st.dataframe(df_playoffs, hide_index=True, use_container_width=True)
else:
    st.info("Матчі плей-оф ще не сформовані.")

st.divider()

# 4. СТАТИСТИКА ТА РОЗКЛАД КОНКРЕТНОЇ КОМАНДИ
st.subheader("📊 Розклад та історія команди")

team_names = []
for group_teams in data['teams'].values():
    team_names.extend(group_teams)
    
selected_team = st.selectbox("Оберіть команду для перегляду її матчів:", team_names)

team_matches = [
    m for m in data['matches'] 
    if m['team1'] == selected_team or m['team2'] == selected_team
]

if team_matches:
    df_matches = pd.DataFrame(team_matches)
    
    # Безпечне створення колонки рахунку
    df_matches['Візуальний_рахунок'] = df_matches.apply(
        lambda row: f"{row['score1']} : {row['score2']}" if row['status'] == 'Зіграна' else "- : -", 
        axis=1
    )
    
    df_matches = df_matches[['stage', 'date', 'team1', 'Візуальний_рахунок', 'team2', 'status']]
    df_matches = df_matches.rename(columns={
        'stage': 'Етап',
        'date': 'Дата',
        'team1': 'Команда 1', 
        'Візуальний_рахунок': 'Рахунок', 
        'team2': 'Команда 2', 
        'status': 'Статус'
    })
    st.dataframe(df_matches, hide_index=True, use_container_width=True)
else:
    st.info("Для цієї команди ще не додано жодного матчу в базу.")
