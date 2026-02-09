import streamlit as st
import json
import matplotlib.pyplot as plt

# Sayfa Genişliği ve Başlık
st.set_page_config(page_title="SoruRota Pro", layout="wide")

# Stil Dosyası
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 2em; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧪 Fen Bilimleri Soru Geliştirme Merkezi")

# 1. Veri Yönetimi ve JSON Yükleme
if 'questions' not in st.session_state:
    st.session_state.questions = [{
        "soruYazari": "", "kazanim": "6.X.X.X", "konu": "Yeni Konu",
        "ustMetin": "", "soruMetni": "Soru kökü...", 
        "secenekler": {"A": "", "B": "", "C": "", "D": ""},
        "pythonKodu": "# Çizim Kodu\nfig, ax = plt.subplots()\nst.pyplot(fig)",
        "htmlKodu": "", "dogruCevap": "A", "cozum": ""
    }]

# --- JSON YÜKLEME BÖLÜMÜ ---
st.sidebar.header("📁 Veri Yönetimi")
uploaded_file = st.sidebar.file_uploader("Mevcut JSON Havuzunu Yükle", type=['json'])

if uploaded_file is not None:
    try:
        loaded_data = json.load(uploaded_file)
        if isinstance(loaded_data, list):
            st.session_state.questions = loaded_data
            st.sidebar.success("Havuz başarıyla yüklendi!")
        else:
            st.sidebar.error("Geçersiz JSON formatı! Liste olmalı.")
    except Exception as e:
        st.sidebar.error(f"Dosya okuma hatası: {e}")

# 2. Yan Menü: Soru Listesi
st.sidebar.header("📋 Soru Havuzu")
for i, q in enumerate(st.session_state.questions):
    if st.sidebar.button(f"{i+1}. Soru: {q.get('konu', 'Adsız')[:15]}...", key=f"btn_{i}"):
        st.session_state.current_index = i

current_idx = st.session_state.get('current_index', 0)
# İndeks aşımı kontrolü
if current_idx >= len(st.session_state.questions):
    current_idx = 0
q = st.session_state.questions[current_idx]

# 3. Ana Panel: Düzenleme ve Ön İzleme Sekmeleri
tab1, tab2 = st.tabs(["📝 Soruyu Düzenle", "🔍 Tam Ön İzleme"])

with tab1:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Metin Düzenleme")
        q['soruYazari'] = st.text_input("Soru Yazarı", q.get('soruYazari', ''))
        q['kazanim'] = st.text_input("Kazanım No", q.get('kazanim', ''))
        q['konu'] = st.text_input("Konu", q.get('konu', ''))
        
        st.write("Vurgu Ekle:")
        b_col1, b_col2, b_col3 = st.columns(3)
        if b_col1.button("Kalın (<b>)"): q['soruMetni'] += "<b></b>"
        if b_col2.button("İtalik (<i>)"): q['soruMetni'] += "<i></i>"
        if b_col3.button("Altı Çizili (<u>)"): q['soruMetni'] += "<u></u>"
        
        q['ustMetin'] = st.text_area("Üst Metin (Senaryo)", q.get('ustMetin', ''), height=100)
        q['soruMetni'] = st.text_area("Soru Kökü", q.get('soruMetni', ''), height=150)
        
        st.write("Şıklar:")
        c1, c2 = st.columns(2)
        q['secenekler']['A'] = c1.text_input("A", q['secenekler'].get('A', ''))
        q['secenekler']['B'] = c2.text_input("B", q['secenekler'].get('B', ''))
        q['secenekler']['C'] = c1.text_input("C", q['secenekler'].get('C', ''))
        q['secenekler']['D'] = c2.text_input("D", q['secenekler'].get('D', ''))

    with col2:
        st.subheader("Görsel ve Kod")
        q['pythonKodu'] = st.text_area("Python Çizim Kodu", q.get('pythonKodu', ''), height=200)
        if q.get('pythonKodu'):
            try: exec(q['pythonKodu'])
            except Exception as e: st.error(f"Kod Hatası: {e}")

with tab2:
    st.subheader("Öğrenci Gözüyle Soru")
    st.markdown(f"**Yazar:** {q.get('soruYazari', '')} | **Kazanım:** {q.get('kazanim', '')}")
    if q.get('ustMetin'): st.write(q['ustMetin'])
    if q.get('pythonKodu'):
        try: exec(q['pythonKodu'])
        except: pass
    st.markdown(f"### {q.get('soruMetni', '')}", unsafe_allow_html=True)
    for k, v in q.get('secenekler', {}).items():
        st.write(f"**{k})** {v}")

# 4. Kaydet ve Dışa Aktar
st.sidebar.divider()
if st.sidebar.button("➕ Yeni Soru Ekle"):
    new_q = st.session_state.questions[0].copy()
    new_q['konu'] = "Yeni Soru"
    st.session_state.questions.append(new_q)
    st.rerun()

final_json = json.dumps(st.session_state.questions, indent=4, ensure_ascii=False)
st.sidebar.download_button("💾 Havuzu JSON Olarak İndir", final_json, "soru_havuzu.json")