import streamlit as st
import pandas as pd
import random
import altair as alt
from datetime import datetime, timedelta

st.set_page_config(page_title="OSS Security Testing", layout="wide")
st.title("OSS Security Testing")

@st.cache_data
def generate_mock_vulnerabilities():
    languages = ["Python", "JavaScript", "Java", "Go"]
    scanners = ["Bandit", "Semgrep", "CodeQL", "SonarQube"]
    severities = ["low", "medium", "high", "critical"]
    packages = [
        ("pkg:pypi/requests@2.28.1", "requests"),
        ("pkg:npm/react@18.2.0", "react"),
        ("pkg:maven/org.apache.commons/commons-lang3@3.12.0", "commons-lang3"),
        ("pkg:golang/github.com/gin-gonic/gin@v1.7.7", "gin")
    ]
    data = []
    for i in range(200):
        purl, name = random.choice(packages)
        lang = purl.split("/")[1].split("@")[0]
        created = datetime.now() - timedelta(days=random.randint(1, 120))
        data.append({
            "package": name,
            "purl": purl,
            "language": lang,
            "scanner": random.choice(scanners),
            "file": f"src/module_{random.randint(1,10)}.py",
            "line": random.randint(10, 300),
            "function": f"func_{random.randint(1,20)}",
            "severity": random.choices(severities, weights=[0.2, 0.4, 0.3, 0.1])[0],
            "description": f"Potential security issue detected in {name}",
            "created_at": created
        })
    return pd.DataFrame(data)

data = generate_mock_vulnerabilities()
data["age_days"] = (pd.Timestamp.now() - data["created_at"]).dt.days
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
with filters[2]:
    sev_filter = st.multiselect("Критичность", options=sorted(data["severity"].unique().tolist()), default=data["severity"].unique().tolist())
with filters[3]:
    days_filter = st.slider("Последние N дней", 0, 120, 90)
with filters[4]:
    only_critical = st.checkbox("Только critical", value=False)

filtered = data.copy()
if lang_filter != "Все":
    filtered = filtered[filtered["language"] == lang_filter]
if scan_filter != "Все":
    filtered = filtered[filtered["scanner"] == scan_filter]
if sev_filter:
    filtered = filtered[filtered["severity"].isin(sev_filter)]
if only_critical:
    filtered = filtered[filtered["severity"] == "critical"]
filtered = filtered[filtered["age_days"] <= days_filter]

st.markdown("---")
tabs = st.tabs(["Обзор", "Уязвимости", "Поиск по PURL"])

with tabs[0]:
    st.header("Общие метрики")
    col1, col2, col3 = st.columns(3)
    col1.metric("Уникальные пакеты", filtered["package"].nunique())
    col2.metric("Всего уязвимостей", len(filtered))
    col3.metric("Критические", len(filtered[filtered["severity"] == "critical"]))

    sev_counts = filtered["severity"].value_counts().reset_index()
    sev_counts.columns = ["Severity", "Count"]
    chart1 = alt.Chart(sev_counts).mark_arc(innerRadius=40).encode(
        theta="Count",
        color="Severity",
        tooltip=["Severity", "Count"]
    ).properties(title="Распределение по критичности", height=300)

    age_counts = filtered["age_group"].value_counts().reset_index()
    age_counts.columns = ["Age", "Count"]
    chart2 = alt.Chart(age_counts).mark_arc(innerRadius=40).encode(
        theta="Count",
        color="Age",
        tooltip=["Age", "Count"]
    ).properties(title="Возраст уязвимостей", height=300)

    col4, col5 = st.columns(2)
    col4.altair_chart(chart1, use_container_width=True)
    col5.altair_chart(chart2, use_container_width=True)

    st.subheader("Распределение по языкам")
    lang_counts = filtered["language"].value_counts().reset_index()
    lang_counts.columns = ["Язык", "Количество"]
    st.bar_chart(lang_counts.set_index("Язык"))

with tabs[1]:
    st.header("Все уязвимости")
    st.dataframe(filtered.drop(columns=["age_days"]), use_container_width=True)

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