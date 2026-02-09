import streamlit as st
import json
import matplotlib.pyplot as plt
import io
from PIL import Image

# 1. PROFESYONEL SAYFA YAPILANDIRMASI
st.set_page_config(page_title="SoruRota Studio", layout="wide", initial_sidebar_state="expanded")

# CSS ile Arayüzü Modernleştirme [cite: 10-12, 21]
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stTextArea textarea { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; border-radius: 10px; }
    .stButton>button { border-radius: 20px; transition: all 0.3s; background-color: #ffffff; color: #1f77b4; border: 1px solid #1f77b4; }
    .stButton>button:hover { background-color: #1f77b4; color: white; }
    .preview-box { border: 1px solid #d1d5db; padding: 25px; border-radius: 15px; background-color: white; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    .toolbar-btn { display: inline-block; margin-right: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. VERİ YÖNETİMİ
if 'questions' not in st.session_state:
    st.session_state.questions = [{
        "soruYazari": "", "kazanim": "", "konu": "Yeni Soru",
        "ustMetin": "", "soruMetni": "", "secenekler": {"A": "", "B": "", "C": "", "D": ""},
        "pythonKodu": "", "manuelGorsel": None, "dogruCevap": "A", "cozum": ""
    }]

# 3. YAN MENÜ (SIDEBAR) - DOSYA YÖNETİMİ
with st.sidebar:
    st.title("🚀 SoruRota Studio")
    st.subheader("Veri Yönetimi")
    uploaded_json = st.file_uploader("JSON Havuzu Yükle", type=['json'])
    if uploaded_json:
        st.session_state.questions = json.load(uploaded_json)
    
    st.divider()
    st.subheader("📋 Soru Listesi")
    for i, q in enumerate(st.session_state.questions):
        btn_label = f"{i+1}. {q.get('konu', 'Adsız')[:20]}"
        if st.sidebar.button(btn_label, key=f"nav_{i}"):
            st.session_state.current_index = i
    
    st.divider()
    if st.button("➕ Yeni Soru Ekle"):
        st.session_state.questions.append({
            "soruYazari": "", "kazanim": "", "konu": "Yeni Soru", "ustMetin": "", "soruMetni": "",
            "secenekler": {"A": "", "B": "", "C": "", "D": ""}, "pythonKodu": "", "manuelGorsel": None,
            "dogruCevap": "A", "cozum": ""
        })
        st.rerun()

# Mevcut Soruyu Al
idx = st.session_state.get('current_index', 0)
q = st.session_state.questions[idx]

# 4. ANA PANEL (DÜZENLEME VE GÖRSEL)
col_edit, col_prev = st.columns([1.2, 1])

with col_edit:
    st.subheader("📝 Soru Editörü")
    
    # Bilgi Satırı
    r1_c1, r1_c2 = st.columns(2)
    q['soruYazari'] = r1_c1.text_input("Yazar", q.get('soruYazari', ''))
    q['kazanim'] = r1_c2.text_input("Kazanım (Örn: 6.1.1.1)", q.get('kazanim', ''))
    
    # Zengin Metin Araç Çubuğu (Toolbar) 
    st.write("✒️ Metin Ayarları")
    t1, t2, t3, t4, t5 = st.columns([1,1,1.5,1.5,1])
    
    if t1.button("B (Kalın)"): q['soruMetni'] += "<b></b>"
    if t2.button("I (İtalik)"): q['soruMetni'] += "<i></i>"
    if t3.button("Boyut (S)"): q['soruMetni'] += "<span style='font-size:14px;'></span>"
    if t4.button("Boyut (L)"): q['soruMetni'] += "<span style='font-size:20px;'></span>"
    if t5.button("Renk"): q['soruMetni'] += "<span style='color:red;'></span>"

    q['ustMetin'] = st.text_area("Üst Metin", q.get('ustMetin', ''), height=80)
    q['soruMetni'] = st.text_area("Soru Kökü", q.get('soruMetni', ''), height=150)
    
    st.write("📌 Seçenekler")
    s_c1, s_c2 = st.columns(2)
    q['secenekler']['A'] = s_c1.text_input("A", q['secenekler'].get('A', ''))
    q['secenekler']['B'] = s_c2.text_input("B", q['secenekler'].get('B', ''))
    q['secenekler']['C'] = s_c1.text_input("C", q['secenekler'].get('C', ''))
    q['secenekler']['D'] = s_c2.text_input("D", q['secenekler'].get('D', ''))

    st.divider()
    st.subheader("🖼️ Görsel Ekleme Özelliği")
    img_tab1, img_tab2 = st.tabs(["🐍 Python ile Çiz", "📤 Görsel Yükle"])
    
    with img_tab1:
        q['pythonKodu'] = st.text_area("Python Kodu", q.get('pythonKodu', ''), placeholder="fig, ax = plt.subplots()...")
    
    with img_tab2:
        uploaded_img = st.file_uploader("Soru görselini buraya sürükleyin", type=['png', 'jpg', 'jpeg'])
        if uploaded_img:
            q['manuelGorsel'] = uploaded_img.name # Gerçek uygulamada binary saklanmalı

with col_prev:
    st.subheader("🔍 MEB Standart Ön İzleme")
    st.markdown("<div class='preview-box'>", unsafe_allow_html=True)
    
    # Üst Bilgi
    st.caption(f"Yazar: {q['soruYazari']} | Kazanım: {q['kazanim']}")
    
    if q['ustMetin']:
        st.write(q['ustMetin'])
    
    # Görsel Render (Ortalama Büyüklükte) [cite: 10-12, 59]
    if q['pythonKodu']:
        try:
            plt.clf()
            fig, ax = plt.subplots(figsize=(5, 3)) # Ortalama büyüklük ayarı
            exec(q['pythonKodu'])
            st.pyplot(fig)
        except:
            st.info("Çizim kodu bekleniyor...")
    
    if q.get('manuelGorsel'):
        st.image(uploaded_img, width=400) # Ortalama genişlik

    # Soru ve Şıklar [cite: 21, 51]
    st.markdown(f"#### {q['soruMetni']}", unsafe_allow_html=True)
    
    for label, text in q['secenekler'].items():
        st.write(f"**{label})** {text}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Çözüm Bölümü [cite: 37]
    with st.expander("🔑 Doğru Cevap ve Çözümü Gör"):
        st.success(f"Doğru Cevap: {q['dogruCevap']}")
        q['cozum'] = st.text_area("Çözüm Açıklaması", q.get('cozum', ''))

# 5. DIŞA AKTAR
st.sidebar.divider()
final_json = json.dumps(st.session_state.questions, indent=4, ensure_ascii=False)
st.sidebar.download_button("💾 Havuzu JSON İndir", final_json, "soru_havuzu.json")
