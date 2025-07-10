import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timezone
import altair as alt
import json
import ast
st.set_page_config(page_title="OSS Security Testing", layout="wide")
st.title("OSS Security Testing")

# Функция для получения данных
@st.cache_data(ttl=60)
def get_vulnerabilities():
    response = requests.get('http://letsgoplaygo.ru:8000/all_purl')
    packages = response.json()
    
    data = []
    for package in packages:
        purl = package['purl']
        status = "pending" if package['status'] == 0 else "checked"
        if package['report'] and package['report'] != "null":
            package['report'] = ast.literal_eval(package['report'])
            status = "error"
        else:
            package['report'] = {}
            package["report"]["high"] = 0
            package["report"]["medium"] = 0
            package["report"]["low"] = 0
        data.append({
            "package": purl.split("/")[1].split("@")[0],
            "purl": purl,
            "language": "python",
            "scanner": "bandit",
            "high": package["report"]["high"],
            "medium": package["report"]["medium"],
            "low": package["report"]["low"],
            "created_at": package['date'],
            "status": status
        })
    return pd.DataFrame(data)

# Функция для отправки PURL на сканирование
def scan_purl(purl):
    try:
        req = requests.get('http://letsgoplaygo.ru:8000/'+purl)
        print(response := req.responce)
        return response
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Загрузка данных
data = get_vulnerabilities()
data["created_at"] = pd.to_datetime(data["created_at"], utc=True)
data["age_days"] = (datetime.now(timezone.utc) - data["created_at"]).dt.days

# Фильтры в сайдбаре
with st.sidebar:
    st.header("Фильтры")
    language_filter = st.selectbox(
        "Язык", 
        ["Все"] + sorted(data["language"].unique().tolist())
    )
    scanner_filter = st.selectbox(
        "Сканер", 
        ["Все"] + sorted(data["scanner"].unique().tolist())
    )
    days_filter = st.slider(
        "Возраст уязвимости (дней)", 
        0, 365, 90
    )

# Применение фильтров
filtered_data = data.copy()
if language_filter != "Все":
    filtered_data = filtered_data[filtered_data["language"] == language_filter]
if scanner_filter != "Все":
    filtered_data = filtered_data[filtered_data["scanner"] == scanner_filter]
filtered_data = filtered_data[filtered_data["age_days"] <= days_filter]

# Вкладки
tab1, tab2, tab3 = st.tabs(["Обзор", "Уязвимости", "Отправка на проверку"])

with tab1:
    st.header("Обзор уязвимостей")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Всего пакетов", filtered_data["package"].nunique())
    col2.metric("Всего уязвимостей", len(filtered_data))
    col3.metric("На сканировании", 
               len(filtered_data[filtered_data["status"] == "pending"]))
    
    st.altair_chart(
        alt.Chart(filtered_data).mark_bar().encode(
            x="count()",
            y=alt.Y("package", sort="-x"),
            tooltip=["package", "count()"]
        ).properties(title="Топ пакетов по запросам"),
        use_container_width=True
    )

with tab2:
    st.header("Список уязвимостей")
    
    search_term = st.text_input("Поиск по таблице (название, PURL, статус):")
    if search_term:
        search_mask = (
            filtered_data["package"].str.contains(search_term, case=False) |
            filtered_data["purl"].str.contains(search_term, case=False) |
            filtered_data["status"].str.contains(search_term, case=False)
        )
        filtered_data = filtered_data[search_mask]
    
    st.dataframe(
        filtered_data,
        use_container_width=True,
        column_config={
            "purl": st.column_config.TextColumn("PURL", width="large"),
            "status": st.column_config.TextColumn("Статус")
        }
    )

with tab3:
    st.header("Отправка PURL на проверку")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Ручной ввод PURL")
        manual_purl = st.text_area(
            "Введите PURL для проверки (по одному на строку)",
            height=150,
            placeholder="pkg:pypi/requests@2.28.1"
        )
        
        if st.button("Отправить"):
            if manual_purl:
                purl_list = [p.strip() for p in manual_purl.split("\n") if p.strip()]
                progress_bar = st.progress(0)
                results = []
                
                for i, purl in enumerate(purl_list):
                    result = scan_purl(purl)
                    results.append((purl, result["status"]))
                    progress_bar.progress((i + 1) / len(purl_list))
                
                st.success("Сканирование запущено!")
                result_df = pd.DataFrame(results, columns=["PURL", "Статус"])
                st.dataframe(result_df)
            else:
                st.warning("Введите хотя бы один PURL")
    
    
    
    st.markdown("---")
    st.subheader("История отправленных PURL")
    if 'sent_purls' not in st.session_state:
        st.session_state.sent_purls = []
    
    if st.session_state.sent_purls:
        history_df = pd.DataFrame(
            st.session_state.sent_purls,
            columns=["PURL", "Статус", "Время отправки"]
        )
        st.dataframe(history_df, use_container_width=True)
    else:
        st.info("Ещё не было отправленных PURL")