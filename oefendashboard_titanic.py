import pandas as pd
import plotly.express as px
import streamlit as st

BESTAND = "../titanic/train.csv"

st.set_page_config(page_title="Titanic oefendashboard", layout="wide")


# --------------------------------------------------------------- data laden ---
@st.cache_data
def laad_data():
    #df_1 = pd.read_csv(BESTAND)

    df = pd.read_csv("train.csv")
    
    # Missende leeftijden opvullen met het gemiddelde.
    df["Age"] = df["Age"].fillna(df["Age"].mean())

    # De twee rijen zonder opstapplaats gooien we weg.
    df = df.dropna(subset=["Embarked"])

    # Klasse als tekst, zodat Plotly er losse categorieen van maakt.
    df["Klasse"] = df["Pclass"].astype(str)

    return df


def laad_havens():
    """Tweede bron: de opstapplaatsen achter de codes S, C en Q."""
    return pd.DataFrame(
        {
            "Embarked": ["S", "C", "Q", "S"],
            "Haven": ["Southampton", "Cherbourg", "Queenstown", "Southampton (dok2)"],
            "Land": ["Engeland", "Frankrijk", "Ierland", "Engeland"],
        }
    )


data = laad_data()
havens = laad_havens()
data = data.merge(havens, on="Embarked", how="left")


# ------------------------------------------------------------------ sidebar ---
st.sidebar.header("Filters")
gekozen_klasse = st.sidebar.selectbox("Klasse", ["Alle", "1", "2", "3"])

# gekozen_klasse = st.sidebar.multiselect("Klasse", ["1", "2", "3"],default=["1", "2", "3"],)

if gekozen_klasse == "Alle":
    selectie = data
else:
    selectie = data[data["Klasse"] == gekozen_klasse]

st.sidebar.subheader("Colors")
gekozen_kleur = st.sidebar.color_picker("Pick A Color", "#00f900")

st.sidebar.subheader("Ruw")
ruw = st.sidebar.checkbox("laat ruwe data zien")

# ------------------------------------------------------------------- pagina ---
st.title("Titanic -- wie overleefde de ramp?")

survived = st.checkbox("Alleen overlevenden")

if survived:
    selectie = selectie[selectie["Survived"] == 1]

st.write(f"Aantal passagiers in de selectie: {len(selectie)}")

st.header("Overlevenden per klasse")

# Let op: dit is een som, geen percentage.
per_klasse = selectie.groupby("Klasse")["Survived"].mean().reset_index()
per_klasse = per_klasse.sort_values("Klasse")

figuur1 = px.bar(
    per_klasse,
    x="Klasse",
    y="Survived",
    title="Overlevenden per klasse",
    color_discrete_sequence=[gekozen_kleur],
)
st.plotly_chart(figuur1, use_container_width=True)


st.header("Overlevenden per opstapplaats")

per_haven = selectie.groupby("Haven")["Survived"].sum().reset_index()
per_haven = per_haven.sort_values(by= per_haven)

figuur2 = px.bar(
    per_haven,
    x="Haven",
    y="Survived",
    title="Overlevenden per opstapplaats",
    color_discrete_sequence=[gekozen_kleur],
)
st.plotly_chart(figuur2, use_container_width=True)

aantal = st.slider("aantal tickets", 5, 50, 10)
st.header(f"Duurste {aantal} tickets")

duurste = selectie.nlargest(aantal, "Fare")[["Name", "Klasse", "Haven", "Fare", "Survived"]]
st.dataframe(duurste, use_container_width=True)


st.header("Leeftijd en ticketprijs")

figuur3 = px.scatter(
    selectie,
    x="Age",
    y="Fare",
    color="Klasse",
    hover_data=["Name"],
    title="Leeftijd tegen ticketprijs",
)
st.plotly_chart(figuur3, use_container_width=True)

st.subheader("Samenhang tussen de getalskolommen")
st.write(selectie[["Age", "Fare", "SibSp", "Parch", "Survived"]].corr())

if ruw:
    selectie
