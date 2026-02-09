import streamlit as st
import json
import matplotlib.pyplot as plt
from PIL import Image
import io

# 1. SAYFA VE KOMPAKT TASARIM AYARLARI
st.set_page_config(page_title="SoruRota Studio v3", layout="wide")

st.markdown("""
    <style>
    /* Genel yazı tipi küçültme */
    html, body, [class*="css"] { font-size: 12px !important; }
    .stTextArea textarea { font-size: 11px !important; border-radius: 0 0 5px 5px !important; border-top: none !important; }
    .stTextInput input { font-size: 11px !important; height: 26px !important; }
    
    /* Entegre Araç Çubuğu Tasarımı */
    .integrated-toolbar {
        background-color: #f1f3f4;
        padding: 2px 8px;
        border: 1px solid #d1d5db;
        border-radius: 5px 5px 0 0;
        display: flex;
        gap: 4px;
        font-size: 10px;
        font-weight: bold;
        color: #444;
    }
    
    /* Butonları küçültme */
    .stButton>button { height: 22px !important; padding: 0 5px !important; font-size: 10px !important; border-radius: 3px !important; }
    
    /* Ön izleme kutusu */
    .preview-container { border: 1px solid #eee; padding: 15px; background: white; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# 2. VERİ YÖNETİMİ
if 'questions' not in st.session_state:
    st.session_state.questions = [{
        "soruYazari": "", "kazanim": "", "konu": "Yeni Soru", "ustMetin": "", "soruMetni": "", 
        "secenekler": {"A": "", "B": "", "C": "", "D": ""}, "pythonKodu": "", "manuelGorsel": None,
        "dogruCevap": "A", "cozum": ""
    }]
if 'curr_idx' not in st.session_state:
    st.session_state.curr_idx = 0

# 3. YAN MENÜ (DARALTILMIŞ DOSYA YÖNETİMİ)
with st.sidebar:
    st.caption("📂 Veri Yönetimi")
    up_json = st.file_uploader("JSON Yükle", type=['json'], label_visibility="collapsed")
    if up_json: st.session_state.questions = json.load(up_json)
    
    st.divider()
    for i, q in enumerate(st.session_state.questions):
        if st.button(f"{i+1}. {q.get('konu', 'Adsız')[:10]}", key=f"q_{i}", use_container_width=True):
            st.session_state.curr_idx = i
    
    if st.button("+ Yeni Soru", type="primary", use_container_width=True):
        st.session_state.questions.append({"soruYazari": "", "kazanim": "", "konu": "Yeni Soru", "ustMetin": "", "soruMetni": "", "secenekler": {"A": "", "B": "", "C": "", "D": ""}, "pythonKodu": "", "manuelGorsel": None, "dogruCevap": "A", "cozum": ""})
        st.rerun()

q = st.session_state.questions[st.session_state.curr_idx]

# 4. ANA PANELLER
tab_edit, tab_preview = st.tabs(["📝 Kompakt Düzenle", "🔍 Tam Ön İzleme"])

with tab_edit:
    col_input, col_vis = st.columns([1, 0.8])
    
    with col_input:
        # Mini Bilgi Satırı
        c1, c2, c3 = st.columns([1,1,1])
        q['soruYazari'] = c1.text_input("Yazar", q['soruYazari'], key="yazar")
        q['kazanim'] = c2.text_input("Kazanım", q['kazanim'], key="kaz")
        q['konu'] = c3.text_input("Konu", q['konu'], key="konu_in")

        # Araç Çubuğu Fonksiyonu (Yazı alanının üstüne yapışık)
        def toolbar_integrated(key_name):
            st.markdown(f'<div class="integrated-toolbar">{key_name} Araçları</div>', unsafe_allow_html=True)
            cols = st.columns([1,1,1,1,1,6])
            if cols[0].button("B", key=f"b_{key_name}"): q[key_name] += "<b></b>"
            if cols[1].button("I", key=f"i_{key_name}"): q[key_name] += "<i></i>"
            if cols[2].button("U", key=f"u_{key_name}"): q[key_name] += "<u></u>"
            if cols[3].button("S", key=f"s_{key_name}"): q[key_name] += "<small></small>"
            if cols[4].button("L", key=f"l_{key_name}"): q[key_name] += "<h3></h3>"

        toolbar_integrated('ustMetin')
        q['ustMetin'] = st.text_area("", q['ustMetin'], height=60, label_visibility="collapsed", key="area_ust")
        
        toolbar_integrated('soruMetni')
        q['soruMetni'] = st.text_area("", q['soruMetni'], height=80, label_visibility="collapsed", key="area_kok")
        
        st.caption("Şıklar ve Cevap")
        s1, s2, s3, s4, s5 = st.columns([1,1,1,1,1])
        q['secenekler']['A'] = s1.text_input("A", q['secenekler']['A'], label_visibility="collapsed")
        q['secenekler']['B'] = s2.text_input("B", q['secenekler']['B'], label_visibility="collapsed")
        q['secenekler']['C'] = s3.text_input("C", q['secenekler']['C'], label_visibility="collapsed")
        q['secenekler']['D'] = s4.text_input("D", q['secenekler']['D'], label_visibility="collapsed")
        q['dogruCevap'] = s5.selectbox("", ["A","B","C","D"], index=["A","B","C","D"].index(q['dogruCevap']), label_visibility="collapsed")

    with col_vis:
        st.caption("🖼️ Görsel Bölümü (Küçültülmüş)")
        v_tab1, v_tab2 = st.tabs(["🐍 Python", "📤 Yükle"])
        
        with v_tab1:
            q['pythonKodu'] = st.text_area("Kod", q['pythonKodu'], height=120, label_visibility="collapsed")
            if q['pythonKodu']:
                try:
                    plt.clf()
                    fig, ax = plt.subplots(figsize=(3, 2)) # Görsel boyutunu küçülttük 
                    exec(q['pythonKodu'])
                    st.pyplot(fig)
                except: st.caption("Çizim hatası veya eksik kod.")
        
        with v_tab2:
            up_img = st.file_uploader("Görsel Seç", type=['png','jpg','jpeg'], label_visibility="collapsed")
            if up_img:
                st.image(up_img, width=200) # Görsel ekle bölümü eklendi 

with tab_preview:
    st.markdown("<div class='preview-container'>", unsafe_allow_html=True)
    st.caption(f"Yazar: {q['soruYazari']} | Kazanım: {q['kazanim']}")
    if q['ustMetin']: st.markdown(q['ustMetin'], unsafe_allow_html=True)
    
    # Görsel Ön İzleme (Küçük Boyut)
    if q['pythonKodu']:
        try:
            plt.clf(); fig, ax = plt.subplots(figsize=(4, 2.5))
            exec(q['pythonKodu']); st.pyplot(fig)
        except: pass
    
    st.markdown(f"**{q['soruMetni']}**", unsafe_allow_html=True)
    for k, v in q['secenekler'].items():
        st.write(f"**{k})** {v}")
    st.markdown("</div>", unsafe_allow_html=True)

# 5. DIŞA AKTAR
f_json = json.dumps(st.session_state.questions, indent=4, ensure_ascii=False)
st.sidebar.download_button("💾 JSON İndir", f_json, "soru_havuzu.json", use_container_width=True)
