import streamlit as st
import json
import matplotlib.pyplot as plt

# Sayfa Genişliği ve Başlık
st.set_page_config(page_title="SoruRota Pro", layout="wide")

# Stil Dosyası (Butonlar ve Görünüm İçin)
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 2em; }
    .preview-box { border: 1px solid #ddd; padding: 15px; border-radius: 10px; background-color: #f9f9f9; }
    </style>
    """, unsafe_allow_name=True)

st.title("🧪 Fen Bilimleri Soru Geliştirme Merkezi")

# 1. Veri Yönetimi (Session State)
if 'questions' not in st.session_state:
    st.session_state.questions = [{
        "soruYazari": "", "kazanim": "6.X.X.X", "konu": "Yeni Konu",
        "ustMetin": "", "soruMetni": "Soru kökü...", 
        "secenekler": {"A": "", "B": "", "C": "", "D": ""},
        "pythonKodu": "# Çizim Kodu\nfig, ax = plt.subplots()\nst.pyplot(fig)",
        "htmlKodu": "", "dogruCevap": "A", "cozum": ""
    }]

# 2. Yan Menü: Soru Listesi ve Ön İzleme
st.sidebar.header("📋 Soru Havuzu")
for i, q in enumerate(st.session_state.questions):
    if st.sidebar.button(f"{i+1}. Soru: {q['konu'][:20]}...", key=f"btn_{i}"):
        st.session_state.current_index = i

current_idx = st.session_state.get('current_index', 0)
q = st.session_state.questions[current_idx]

# 3. Ana Panel: Düzenleme ve Ön İzleme Sekmeleri
tab1, tab2 = st.tabs(["📝 Soruyu Düzenle", "🔍 Tam Ön İzleme"])

with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Metin Düzenleme")
        
        # HTML Yardımcı Butonları
        st.write("Vurgu Ekle:")
        b_col1, b_col2, b_col3 = st.columns(3)
        if b_col1.button("Kalın (<b>)"): q['soruMetni'] += "<b></b>"
        if b_col2.button("İtalik (<i>)"): q['soruMetni'] += "<i></i>"
        if b_col3.button("Altı Çizili (<u>)"): q['soruMetni'] += "<u></u>"
        
        q['ustMetin'] = st.text_area("Üst Metin (Senaryo)", q['ustMetin'], height=100)
        q['soruMetni'] = st.text_area("Soru Kökü", q['soruMetni'], height=150)
        
        st.write("Şıklar:")
        c1, c2 = st.columns(2)
        q['secenekler']['A'] = c1.text_input("A", q['secenekler']['A'])
        q['secenekler']['B'] = c2.text_input("B", q['secenekler']['B'])
        q['secenekler']['C'] = c1.text_input("C", q['secenekler']['C'])
        q['secenekler']['D'] = c2.text_input("D", q['secenekler']['D'])

    with col2:
        st.subheader("Görsel ve Kod")
        q['pythonKodu'] = st.text_area("Python Çizim Kodu", q['pythonKodu'], height=200)
        
        st.info("Canlı Görsel Çıktısı:")
        if q['pythonKodu']:
            try:
                exec(q['pythonKodu'])
            except Exception as e:
                st.error(f"Kod Hatası: {e}")

with tab2:
    st.subheader("Öğrenci Gözüyle Soru")
    st.markdown(f"**Yazar:** {q['soruYazari']} | **Kazanım:** {q['kazanim']}")
    st.write(q['ustMetin'])
    
    # Görseli burada tekrar gösteriyoruz (Ön izleme için)
    if q['pythonKodu']:
        try: exec(q['pythonKodu'])
        except: pass
        
    st.markdown(f"### {q['soruMetni']}", unsafe_allow_name=True)
    for k, v in q['secenekler'].items():
        st.write(f"**{k})** {v}")
    
    with st.expander("Doğru Cevabı ve Çözümü Gör"):
        st.success(f"Doğru Cevap: {q['dogruCevap']}")
        st.write(q['cozum'])

# 4. Kaydet ve Dışa Aktar
st.sidebar.divider()
if st.sidebar.button("➕ Yeni Soru Ekle"):
    st.session_state.questions.append(st.session_state.questions[0].copy())
    st.rerun()

final_json = json.dumps(st.session_state.questions, indent=4, ensure_ascii=False)
st.sidebar.download_button("💾 Havuzu JSON Olarak İndir", final_json, "soru_havuzu.json")