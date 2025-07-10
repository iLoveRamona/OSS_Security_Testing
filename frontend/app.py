import streamlit as st
import pandas as pd
import random
import altair as alt
from datetime import datetime, timedelta, timezone
import requests
import json
import ast

st.set_page_config(page_title="OSS Security Testing", layout="wide")
st.title("OSS Security Testing")

@st.cache_data(ttl=60)
def generate_mock_vulnerabilities():
    scanners = ["Bandit", "Semgrep"]
    severities = ["low", "medium", "high", "critical"]
    packages = requests.get('http://letsgoplaygo.ru:8000/all_purl').json()
    #packages[0] = packages[0]['report'].replace('\\n', '').replace("\\", "")
    #print(packages[0])
    data = []
    for package in packages:
        print(package.keys())
        purl = package['purl']
        try:
            package['report'] = json.loads(ast.literal_eval(package['report']))
            severities_package = package["report"]['metrics']['_totals']
        except:
            severities_package = {}
            severities_package["SEVERITY.HIGH"] = 0
            severities_package["SEVERITY.MEDIUM"] = 0
            severities_package["SEVERITY.LOW"] = 0
        name = purl.split("/")[1].split("@")[0]
        created = package['date']
        status = "pending" if package['status'] == 0 else "checked"
        
        print(severities_package.keys())
        data.append({
            "package": name,
            "purl": purl,
            "language": "python",
            "scanner": "bandit",
            "high": severities_package["SEVERITY.HIGH"],
            "medium": severities_package["SEVERITY.MEDIUM"],
            "low": severities_package["SEVERITY.LOW"],
            "created_at": created,
            "status": status
        })
    return pd.DataFrame(data)

data = generate_mock_vulnerabilities()
data["created_at"] = pd.to_datetime(data["created_at"], utc=True)

# 2. Текущая дата ДОЛЖНА БЫТЬ tz-aware (иначе будет ошибка)
current_date = datetime.now(timezone.utc)

# 3. Вычисляем возраст уязвимости в днях
data["age_days"] = (current_date - data["created_at"]).dt.days

# 4. Группируем по возрастным категориям (pd.cut работает с числами)
data["age_group"] = pd.cut(
    data["age_days"],
    bins=[-1, 7, 30, 90, 10000],
    labels=["< 7 дней", "7–30 дней", "30–90 дней", "> 90 дней"]
)

filters = st.columns(5)
with filters[0]:
    lang_filter = st.selectbox("Язык", options=["Все"] + sorted(data["language"].unique().tolist()))
with filters[1]:
    scan_filter = st.selectbox("Сканер", options=["Все"] + sorted(data["scanner"].unique().tolist()))
#with filters[2]:
 #   sev_filter = st.multiselect("Критичность", options=sorted(data["severity"].unique().tolist()), default=data["severity"].unique().tolist())
with filters[2]:
    days_filter = st.slider("Последние N дней", 0, 120, 90)

filtered = data.copy()
if lang_filter != "Все":
    filtered = filtered[filtered["language"] == lang_filter]
if scan_filter != "Все":
    filtered = filtered[filtered["scanner"] == scan_filter]
#if sev_filter:
#    filtered = filtered[filtered["severity"].isin(sev_filter)]
filtered = filtered[filtered["age_days"] <= days_filter]

st.markdown("---")
tabs = st.tabs(["Обзор", "Уязвимости", "Поиск по PURL"])

with tabs[0]:
    st.header("Общие метрики")
    col1, col2, col3 = st.columns(3)
    pak = filtered["package"]
    col1.metric("Уникальные пакеты", pak.nunique())
    col2.metric("Всего уязвимостей", len(filtered))
    
    # Создаем данные для круговой диаграммы критичности
    sev_data = pd.DataFrame({
        'severity': ['high', 'medium', 'low'],
        'count': [
            filtered['high'].sum(),
            filtered['medium'].sum(),
            filtered['low'].sum()
        ]
    })
    
    # Диаграмма критичности
    chart1 = alt.Chart(sev_data).mark_arc(innerRadius=40).encode(
        theta=alt.Theta('count:Q', title="Количество"),
        color=alt.Color('severity:N', title="Критичность", 
                       scale=alt.Scale(domain=['high', 'medium', 'low'],
                                      range=['#ff4b4b', '#ffa421', '#21c9ff'])),
        tooltip=['severity', 'count']
    ).properties(
        title="Распределение по критичности",
        height=300
    )
    
    # Диаграмма возраста уязвимостей
    age_counts = filtered["age_group"].value_counts().reset_index()
    age_counts.columns = ["Age", "Count"]
    chart2 = alt.Chart(age_counts).mark_arc(innerRadius=40).encode(
        theta="Count",
        color=alt.Color("Age", title="Возрастная группа"),
        tooltip=["Age", "Count"]
    ).properties(
        title="Возраст уязвимостей", 
        height=300
    )
    
    col4, col5 = st.columns(2)
    col4.altair_chart(chart1, use_container_width=True)
    col5.altair_chart(chart2, use_container_width=True)
    
    # Распределение по языкам
    st.subheader("Распределение по пакетам")
    lang_counts = pak.value_counts().reset_index()
    lang_counts.columns = ["Язык", "Количество"]
    st.bar_chart(lang_counts.set_index("Язык"))
    
with tabs[1]:
    st.header("Все уязвимости")
    def style_status(val):
        color = 'blue' if val == 'pending' else 'green'
        return f'color: {color}; font-weight: bold'
    
    filtered = filtered.style.applymap(style_status, subset=['status'])
    st.dataframe(filtered, use_container_width=True)

with tabs[2]:
    st.header("Поиск по PURL")
    purl_input = st.text_input("Введите PURL (например, pkg:pypi/requests@2.28.1):")
    if purl_input:
        matched = data[data["purl"] == purl_input]
        if not matched.empty:
            st.success(f"Найдено уязвимостей: {len(matched)}")
            st.dataframe(matched, use_container_width=True)
        else:
            st.warning("Уязвимости не найдены для указанного PURL")