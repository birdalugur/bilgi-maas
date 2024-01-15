import pandas as pd
import streamlit as st
import altair as alt

from io import StringIO

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    # Can be used wherever a "file-like" object is accepted:
    df = pd.read_excel(uploaded_file)

else:
    st.stop()

method = st.sidebar.radio('Method', (1, 2))

if method == 1:
    score = st.sidebar.radio('Score: ', ('score_1', 'score_2'))

elif method == 2:
    score = None
    oran_pr = st.sidebar.slider('Oran: Pr', 0.01, 2.0)
    oran_dc = st.sidebar.slider('Oran: Dc', 0.01, 2.0)
    oran_dr = st.sidebar.slider('Oran: Dr', 0.01, 2.0)

oran_1 = st.sidebar.slider('Oran: 1', 0.01, 2.0)
oran_2 = st.sidebar.slider('Oran: 2', 0.01, 2.0)
oran_3 = st.sidebar.slider('Oran: 3', 0.01, 2.0)
oran_4 = st.sidebar.slider('Oran: 4', 0.01, 2.0)

brut, net = st.sidebar.columns(2)

lower_pr_b = brut.number_input('lower_pr_b', value=100.0, step=5.0)
lower_dc_b = brut.number_input('lower_dc_b', value=100.0, step=5.0)
lower_dr_b = brut.number_input('lower_dr_b', value=100.0, step=5.0)

initial_dc_b = brut.number_input('initial_dc_b', value=100.0, step=5.0)
initial_dr_b = brut.number_input('initial_dr_b', value=100.0, step=5.0)
initial_pr_b = brut.number_input('initial_pr_b', value=100.0, step=5.0)

lower_pr_n = net.number_input('lower_pr_n', value=100.0, step=5.0)
lower_dc_n = net.number_input('lower_dc_n', value=100.0, step=5.0)
lower_dr_n = net.number_input('lower_dr_n', value=100.0, step=5.0)

initial_pr_n = net.number_input('initial_pr_n', value=100.0, step=5.0)
initial_dc_n = net.number_input('initial_dc_n', value=100.0, step=5.0)
initial_dr_n = net.number_input('initial_dr_n', value=100.0, step=5.0)

print(oran_1, oran_2, oran_3, oran_4)



# file_path = 'Akademisyen 2024-Çalışma_2.xlsx'


# @st.cache_data
def load_data(path: str) -> pd.DataFrame:
    data = pd.read_excel(path)
    return data


# df = load_data(file_path)

df["Puan"] = pd.to_numeric(df['Puan'], errors='coerce')
median = df[df["Status"] == "Hesaplanacak"]["Puan"].median()
mask = df['Status'] == 'Hesaplanacak'
df.loc[mask, 'score_1'] = df.loc[mask, 'Puan'] / df.loc[mask, 'Puan'].median()
median_departman = (df[df["Status"]=="Hesaplanacak"]
                    .groupby('Departman Fakulte')
                    .apply(lambda x: x['Puan'].median()))
df['score_2'] = df['Puan'] / df['Departman Fakulte'].map(median_departman)


st.write("Departmanlara Göre Median Puanlar:")
st.bar_chart(median_departman)




def get_params(record):
    position = record['Pozisyon']
    net_brut = record['Net-Brüt']

    lower = None
    initial = None

    if net_brut == 'Brüt':
        if position == 'PROF. DR.':
            lower = lower_pr_b
            initial = initial_pr_b
        elif position == 'DOÇ. DR.':
            lower = lower_dc_b
            initial = initial_dc_b
        elif position == 'DR. ÖĞR. ÜYESİ':
            lower = lower_dr_b
            initial = initial_dr_b
    elif net_brut == 'Net':
        if position == 'PROF. DR.':
            lower = lower_pr_n
            initial = initial_pr_n
        elif position == 'DOÇ. DR.':
            lower = lower_dc_n
            initial = initial_dc_n
        elif position == 'DR. ÖĞR. ÜYESİ':
            lower = lower_dr_n
            initial = initial_dr_n

    return {'lower': lower, 'initial': initial}


def maas_hesapla(record: dict, score_name: str, method: int) -> dict:
    maas_2 = None

    if record["Status"] == 'Devlet':
        maas_2 = record['lower']

    if record["Status"] == 'Skalaya eşitlenecek-APYS':
        maas_2 = record['initial'] * oran_1

    if record["Status"] == 'Yarım artış-APYS':
        maas_2 = record['Maas_1'] * oran_1 * 0.5

    if record["Status"] == 'Sıfır artış-APYS':
        maas_2 = record['Maas_1']

    if record["Status"] == 'Özel':
        maas_2 = record['Maas_1'] * oran_3

    if record["Status"] == 'Özel2':
        maas_2 = record['Maas_1'] * oran_3

    if record["Status"] == 'Özel3':
        maas_2 = record['Maas_1'] * oran_2

    if record["Status"] == 'Hesaplanacak':
        if method == 1:
            if record[score_name] < 1:
                maas_2 = record['Maas_1'] * oran_1
            elif (record[score_name] >= 1) & (record[score_name] < 1.5):
                maas_2 = record['Maas_1'] * oran_2
            elif (record[score_name] >= 1.5) & (record[score_name] < 2):
                maas_2 = record['Maas_1'] * oran_3
            elif record[score_name] >= 2:
                maas_2 = record['Maas_1'] * oran_4
            else:
                maas_2 = None
                print("Bu Kayıt İçin Maas_2 Hesaplanamadı, değer None ayarlandı !:", record)

        elif method == 2:
            if record["Pozisyon"] == 'PROF. DR.':
                if record["Puan"] < 90:
                    maas_2 = record['Maas_1'] * (oran_pr - 0.02)
                elif (record["Puan"] >= 90) & (record["Puan"] < 150):
                    maas_2 = record['Maas_1'] * oran_pr
                elif record["Puan"] >= 150:
                    maas_2 = record['Maas_1'] * (oran_pr + 0.02)
                else:
                    print("Bu Kayıt İçin Maas_2 Hesaplanamadı, değer None ayarlandı !:", record)

            elif record["Pozisyon"] == 'DOÇ. DR.':
                if record["Puan"] < 90:
                    maas_2 = record['Maas_1'] * (oran_dc - 0.04)
                elif (record["Puan"] >= 90) & (record["Puan"] < 150):
                    maas_2 = record['Maas_1'] * (oran_dc - 0.02)
                elif (record["Puan"] >= 150) & (record["Puan"] < 200):
                    maas_2 = record['Maas_1'] * oran_dc
                elif (record["Puan"] >= 200):
                    maas_2 = record['Maas_1'] * (oran_dc + 0.02)
                else:
                    print("Bu Kayıt İçin Maas_2 Hesaplanamadı, değer None ayarlandı !:", record)

            if record["Pozisyon"] == 'DR. ÖĞR. ÜYESİ':
                if record["Puan"] < 90:
                    maas_2 = record['Maas_1'] * (oran_dr - 0.06)
                elif (record["Puan"] >= 90) & (record["Puan"] < 150):
                    maas_2 = record['Maas_1'] * (oran_dr - 0.02)
                elif (record["Puan"] >= 150) & (record["Puan"] < 200):
                    maas_2 = record['Maas_1'] * oran_dr
                elif record["Puan"] >= 200:
                    maas_2 = record['Maas_1'] * (oran_dr + 0.02)
                else:
                    print("Bu Kayıt İçin Maas_2 Hesaplanamadı, değer None ayarlandı !:", record)

    if maas_2 < record['lower']:
        maas_2 = record['lower']

    zam = (maas_2 / record['Maas_1']) - 1

    return {'maas_2': maas_2, 'zam': zam}


df_dict = df.to_dict(orient='records')

for record in df_dict:
    record.update(get_params(record))
    record.update(maas_hesapla(record, score_name=score, method=method))

df_updated = pd.DataFrame(df_dict)

st.write("Tablo Bilgileri:")
st.write(df_updated)

st.write("Regresyon Bilgileri:")
chart = alt.Chart(df_updated).mark_point().encode(
    x='Puan',
    y='zam'
)

st.altair_chart(chart + chart.transform_regression('Puan', 'zam').mark_line(), use_container_width=True)

# Or even better, call Streamlit functions inside a "with" block:
