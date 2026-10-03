import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Dota 2 Tournament", page_icon="🎮", layout="wide")

# Посилання на ваш репозиторій
JSON_URL = "https://raw.githubusercontent.com/fridayxiii13/dota-tournament-app/main/data.json"

@st.cache_data(ttl=10)
def load_data():
    response = requests.get(JSON_URL)
    response.raise_for_status()
    return response.json()

def calculate_standings(teams, matches, group_name):
    # Ініціалізуємо нульову статистику для кожної команди групи
    stats = {
        team: {"Команда": team, "Ігри": 0, "В": 0, "П": 0, "Карти": "0-0", "Різниця карт": 0, "Бали": 0, "_w_maps": 0, "_l_maps": 0}
        for team in teams
    }
    
    # Проходимо по всіх матчах цієї групи зі статусом "Зіграна"
    for m in matches:
        if m["stage"] == group_name and m["status"] == "Зіграна":
            t1, t2 = m["team1"], m["team2"]
            s1, s2 = m["score1"], m["score2"]
            p1, p2 = m["pts1"], m["pts2"]
            
            if t1 in stats and t2 in stats:
                stats[t1]["Ігри"] += 1
                stats[t2]["Ігри"] += 1
                
                stats[t1]["_w_maps"] += s1
                stats[t1]["_l_maps"] += s2
                stats[t2]["_w_maps"] += s2
                stats[t2]["_l_maps"] += s1
                
                stats[t1]["Бали"] += p1
                stats[t2]["Бали"] += p2
                
                if s1 > s2:
                    stats[t1]["В"] += 1
                    stats[t2]["П"] += 1
                elif s2 > s1:
                    stats[t2]["В"] += 1
                    stats[t1]["П"] += 1

    # Формуємо фінальні колонки для таблиці
    result = []
    for t in stats.values():
        t["Карти"] = f"{t['_w_maps']}-{t['_l_maps']}"
        t["Різниця карт"] = t["_w_maps"] - t["_l_maps"]
        del t["_w_maps"]
        del t["_l_maps"]
        result.append(t)
        
    df = pd.DataFrame(result)
    # Сортуємо: спочатку за балами, потім за різницею виграних карт, потім за перемогами
    df = df.sort_values(by=["Бали", "Різниця карт", "В"], ascending=[False, False, False]).reset_index(drop=True)
    df.index = df.index + 1 # Нумерація місць з 1
    return df

st.title("🏆 Корпоративний турнір Dota 2")

try:
    data = load_data()
    teams_dict = data["teams"]
    matches = data["matches"]

    # Створюємо вкладки для зручної навігації
    tab1, tab2, tab3 = st.tabs(["📊 Таблиці та Плей-оф", "🛡️ Досьє команд", "📅 Всі матчі"])

    # --- ВКЛАДКА 1: ТАБЛИЦІ ТА ПЛЕЙ-ОФ ---
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Група A")
            df_a = calculate_standings(teams_dict["Група A"], matches, "Група A")
            st.dataframe(df_a.drop(columns=["Різниця карт"]), use_container_width=True)
            
        with col2:
            st.subheader("Група B")
            df_b = calculate_standings(teams_dict["Група B"], matches, "Група B")
            st.dataframe(df_b.drop(columns=["Різниця карт"]), use_container_width=True)

        st.divider()
        st.header("🔥 Стадія Плей-оф")

        # Фільтруємо всі матчі, етап яких не є груповим
        playoff_stages = ["Півфінал 1", "Півфінал 2", "Матч за 3-тє місце", "Суперфінал"]
        playoff_matches = [m for m in data['matches'] if m['stage'] in playoff_stages]

        if playoff_matches:
            df_playoffs = pd.DataFrame(playoff_matches)
            # Залишаємо лише найважливіші колонки для глядачів
            df_playoffs = df_playoffs[['stage', 'team1', 'score', 'team2', 'status']]
            df_playoffs = df_playoffs.rename(columns={
                'stage': 'Етап', 
                'team1': 'Команда 1', 
                'score': 'Рахунок', 
                'team2': 'Команда 2', 
                'status': 'Статус'
            })
    
            # Виводимо сітку плей-оф окремою таблицею
            st.dataframe(df_playoffs, hide_index=True, use_container_width=True)
        else:
            st.info("Матчі плей-оф ще не сформовані.")

    # --- ВКЛАДКА 2: СТАТИСТИКА ПО КОМАНДІ ---
    with tab2:
        all_teams = teams_dict["Група A"] + teams_dict["Група B"]
        selected_team = st.selectbox("Оберіть команду для перегляду розкладу та історії:", all_teams)
        
        team_matches = [m for m in matches if m["team1"] == selected_team or m["team2"] == selected_team]
        
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown("### ✅ Зіграні матчі")
            played = [m for m in team_matches if m["status"] == "Зіграна"]
            if not played:
                st.caption("Ще немає зіграних матчів.")
            for m in played:
                is_t1 = m["team1"] == selected_team
                my_score = m["score1"] if is_t1 else m["score2"]
                opp_score = m["score2"] if is_t1 else m["score1"]
                opp_name = m["team2"] if is_t1 else m["team1"]
                my_pts = m["pts1"] if is_t1 else m["pts2"]
                
                icon = "🟢 Перемога" if my_score > opp_score else ("🔴 Поразка" if my_score < opp_score else "🟡 Нічия")
                st.markdown(f"**{icon}** проти **{opp_name}**\nРахунок: `{my_score} : {opp_score}` (+{my_pts} балів)")
                st.divider()

        with c2:
            st.markdown("### 📅 Заплановані")
            scheduled = [m for m in team_matches if m["status"] == "Запланована"]
            if not scheduled:
                st.caption("Немає призначених дат.")
            for m in scheduled:
                opp_name = m["team2"] if m["team1"] == selected_team else m["team1"]
                st.warning(f"Проти **{opp_name}**\n\n🕒 Коли: **{m['date']}** ({m['stage']})")

        with c3:
            st.markdown("### ⏳ Очікують розкладу (TBD)")
            tbd = [m for m in team_matches if m["status"] == "Уточнюється"]
            if not tbd:
                st.caption("Всі ігри заплановані або зіграні!")
            for m in tbd:
                opp_name = m["team2"] if m["team1"] == selected_team else m["team1"]
                st.markdown(f"• Проти **{opp_name}** *(Дата уточнюється)*")

    # --- ВКЛАДКА 3: ПОВНИЙ СПИСОК МАТЧІВ ---
    with tab3:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            stage_filter = st.multiselect("Фільтр за етапом:", ["Група A", "Група B", "Півфінал 1", "Півфінал 2", "Суперфінал"], default=["Група A", "Група B"])
        with col_f2:
            status_filter = st.multiselect("Фільтр за статусом:", ["Зіграна", "Запланована", "Уточнюється"], default=["Зіграна", "Запланована", "Уточнюється"])
            
        filtered_matches = [m for m in matches if m["stage"] in stage_filter and m["status"] in status_filter]
        
        df_matches = pd.DataFrame(filtered_matches)
        if not df_matches.empty:
            df_matches = df_matches.rename(columns={
                "id": "ID", "stage": "Етап", "team1": "Команда 1", "team2": "Команда 2",
                "status": "Статус", "date": "Час", "score1": "Карти К1", "score2": "Карти К2",
                "pts1": "Бали К1", "pts2": "Бали К2"
            })
            st.dataframe(df_matches, hide_index=True, use_container_width=True)
        else:
            st.info("Матчів за вибраними фільтрами не знайдено.")

except Exception as e:
    st.error(f"Помилка завантаження або обробки даних: {e}")
