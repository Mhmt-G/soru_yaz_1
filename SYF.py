import streamlit as st
import json
import matplotlib.pyplot as plt
import pandas as pd

# 1. SAYFA VE STİL YAPILANDIRMASI
st.set_page_config(page_title="SoruRota Pro: Fen Bilimleri Editörü", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .main-header { color: #2E86C1; text-align: center; }
    .preview-card { border: 2px solid #EAECEE; padding: 20px; border-radius: 10px; background-color: #FBFCFC; }
    </style>
    """, unsafe_allow_html=True)

# 2. VERİ YÖNETİMİ (SESSION STATE)
if 'questions' not in st.session_state:
    st.session_state.questions = [{
        "soruYazari": "", "sinifDuzeyi": "6. Sınıf", "ders": "Fen Bilimleri",
        "zorluk": 0.70, "kazanim": "", "konu": "Yeni Konu", "unite": "",
        "ustMetin": "", "soruMetni": "Soru kökünü buraya yazın...", 
        "secenekler": {"A": "", "B": "", "C": "", "D": ""}, "dogruCevap": "A",
        "cozum": "", "pythonKodu": "", "htmlKodu": ""
    }]
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0

# 3. YAN MENÜ: VERİ YÖNETİMİ VE HAVUZ ÖNİZLEME
st.sidebar.header("📁 Veri ve Havuz Yönetimi")

# JSON Yükleme Bölümü 
uploaded_file = st.sidebar.file_uploader("Mevcut JSON Havuzunu Yükle", type=['json'])
if uploaded_file is not None:
    try:
        loaded_data = json.load(uploaded_file)
        if isinstance(loaded_data, list):
            st.session_state.questions = loaded_data
            st.sidebar.success("Havuz Başarıyla Yüklendi!")
    except Exception as e:
        st.sidebar.error(f"Yükleme Hatası: {e}")

st.sidebar.divider()

# Soru Listesi ve Seçimi
st.sidebar.subheader("📋 Soru Listesi")
for i, q in enumerate(st.session_state.questions):
    label = f"{i+1}. {q.get('konu', 'Adsız')[:15]}..."
    if st.sidebar.button(label, key=f"nav_{i}"):
        st.session_state.current_index = i

# 4. ANA PANEL: DÜZENLEME VE ÖNİZLEME
idx = st.session_state.current_index
q = st.session_state.questions[idx]

tab1, tab2 = st.tabs(["📝 Soru Tasarımı", "🔍 MEB Standart Ön İzleme"])

with tab1:
    col_edit, col_vis = st.columns([1, 1])
    
    with col_edit:
        st.subheader("📄 Soru Bilgileri")
        q['soruYazari'] = st.text_input("Soru Yazarı", q.get('soruYazari', ''))
        q['kazanim'] = st.text_input("Kazanım (Örn: 6.1.1.1)", q.get('kazanim', '')) 
        q['zorluk'] = st.slider("Zorluk Katsayısı (1.0: Kolay, 0.0: Zor)", 0.0, 1.0, float(q.get('zorluk', 0.7)))
        
        st.subheader("✍️ Metin ve Vurgu Düzenleme")
        # HTML Butonları 
        b1, b2, b3 = st.columns(3)
        if b1.button("Kalın (<b>)"): q['soruMetni'] += "<b></b>"
        if b2.button("İtalik (<i>)"): q['soruMetni'] += "<i></i>"
        if b3.button("Altı Çizili (<u>)"): q['soruMetni'] += "<u></u>"
        
        q['ustMetin'] = st.text_area("Üst Metin / Deney Senaryosu", q.get('ustMetin', ''), height=80)
        q['soruMetni'] = st.text_area("Soru Kökü", q.get('soruMetni', ''), height=120)
        
        st.write("Seçenekler (Çeldiriciler Kaliteli Olmalı) ")
        sc1, sc2 = st.columns(2)
        q['secenekler']['A'] = sc1.text_input("A Şıkkı", q['secenekler'].get('A', ''))
        q['secenekler']['B'] = sc2.text_input("B Şıkkı", q['secenekler'].get('B', ''))
        q['secenekler']['C'] = sc1.text_input("C Şıkkı", q['secenekler'].get('C', ''))
        q['secenekler']['D'] = sc2.text_input("D Şıkkı", q['secenekler'].get('D', ''))
        
        q['dogruCevap'] = st.selectbox("Doğru Cevap", ["A", "B", "C", "D"], index=["A", "B", "C", "D"].index(q.get('dogruCevap', 'A')))
        q['cozum'] = st.text_area("Pedagojik Çözüm (Kısa ve Öz) ", q.get('cozum', ''))

    with col_vis:
        st.subheader("📊 Görsel ve Çizim Motoru ")
        q['pythonKodu'] = st.text_area("Python Çizim Kodu (matplotlib/pandas)", q.get('pythonKodu', ''), height=250)
        
        st.info("🖼️ Canlı Görsel Çıktısı")
        if q['pythonKodu']:
            try:
                plt.clf()
                exec(q['pythonKodu'])
                st.pyplot(plt.gcf())
            except Exception as e:
                st.warning(f"Kod çalıştırılamadı: {e}")
        
        q['htmlKodu'] = st.text_area("Alternatif HTML/SVG Kodu", q.get('htmlKodu', ''), height=100)
        if q['htmlKodu']:
            st.components.v1.html(q['htmlKodu'], height=200)

with tab2:
    st.markdown("<div class='preview-card'>", unsafe_allow_html=True)
    st.markdown(f"**Yazar:** {q['soruYazari']} | **Kazanım:** {q['kazanim']} | **Zorluk:** {q['zorluk']}")
    if q['ustMetin']: st.write(q['ustMetin'])
    
    # Görseli burada tekrar render ediyoruz 
    if q['pythonKodu']:
        try:
            plt.clf()
            exec(q['pythonKodu'])
            st.pyplot(plt.gcf())
        except: pass
    
    st.markdown(f"### {q['soruMetni']}", unsafe_allow_html=True)
    for k, v in q['secenekler'].items():
        st.write(f"**{k})** {v}")
    
    with st.expander("✅ Doğru Cevap ve Çözümü Görüntüle"):
        st.success(f"Cevap: {q['dogruCevap']}")
        st.write(q['cozum'])
    st.markdown("</div>", unsafe_allow_html=True)

# 5. DOSYA DIŞA AKTARMA VE YENİ SORU
st.sidebar.divider()
if st.sidebar.button("➕ Havuza Yeni Soru Ekle"):
    new_q = st.session_state.questions[0].copy()
    new_q['konu'] = "Yeni Soru"
    st.session_state.questions.append(new_q)
    st.rerun()

final_json = json.dumps(st.session_state.questions, indent=4, ensure_ascii=False)
st.sidebar.download_button("💾 Havuzu JSON Olarak İndir", final_json, "soru_havuzu.json", "application/json")

