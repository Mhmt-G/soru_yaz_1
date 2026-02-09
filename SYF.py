import streamlit as st
import json
import matplotlib.pyplot as plt

# 1. SAYFA AYARLARI VE MİNİMALİST CSS
st.set_page_config(page_title="SoruRota Studio", layout="wide")

st.markdown("""
    <style>
    /* Yazı tiplerini ve boşlukları küçültme */
    html, body, [class*="css"] { font-size: 13px !important; }
    .stTextArea textarea { font-size: 12px !important; border-radius: 0 0 5px 5px !important; padding: 5px !important; }
    .stTextInput input { font-size: 12px !important; height: 28px !important; }
    .stButton>button { height: 24px !important; font-size: 11px !important; padding: 0px !important; }
    
    /* Word stili daraltılmış araç çubuğu */
    .toolbar-container {
        background-color: #f0f2f6;
        padding: 4px 8px;
        border-radius: 5px 5px 0 0;
        border: 1px solid #d1d5db;
        font-size: 11px;
        font-weight: bold;
        color: #555;
    }
    
    /* Ön izleme penceresi küçültme */
    .preview-container {
        border: 1px solid #dee2e6;
        padding: 20px;
        border-radius: 8px;
        background-color: white;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. VERİ YÖNETİMİ
if 'questions' not in st.session_state:
    st.session_state.questions = [{
        "soruYazari": "", "kazanim": "", "konu": "Yeni Soru",
        "ustMetin": "", "soruMetni": "", 
        "secenekler": {"A": "", "B": "", "C": "", "D": ""},
        "pythonKodu": "", "dogruCevap": "A", "cozum": ""
    }]
if 'current_idx' not in st.session_state:
    st.session_state.current_idx = 0

# 3. YAN MENÜ (DARALTILMIŞ)
with st.sidebar:
    st.caption("📂 Soru Yönetimi")
    uploaded = st.file_uploader("Yükle", type=['json'], label_visibility="collapsed")
    if uploaded: st.session_state.questions = json.load(uploaded)
    
    st.divider()
    for i, q in enumerate(st.session_state.questions):
        if st.button(f"{i+1}. {q.get('konu', 'Adsız')[:12]}", key=f"q_{i}", use_container_width=True):
            st.session_state.current_idx = i
    
    if st.button("+ Yeni Soru", type="primary", use_container_width=True):
        st.session_state.questions.append({
            "soruYazari": "", "kazanim": "", "konu": "Yeni Soru", "ustMetin": "", "soruMetni": "",
            "secenekler": {"A": "", "B": "", "C": "", "D": ""}, "pythonKodu": "", "dogruCevap": "A", "cozum": ""
        })
        st.rerun()

q = st.session_state.questions[st.session_state.current_idx]

# 4. ANA PANELLER
tab_edit, tab_preview = st.tabs(["📝 Düzenle", "🔍 Ön İzleme"])

with tab_edit:
    col_input, col_visual = st.columns([1, 1])
    
    with col_input:
        # Kompakt Bilgi Satırı
        c_y, c_k = st.columns(2)
        q['soruYazari'] = c_y.text_input("Yazar", q['soruYazari'], placeholder="Ad Soyad")
        q['kazanim'] = c_k.text_input("Kazanım", q['kazanim'], placeholder="6.X.X.X")
        
        # Word Tipi Mini Araç Çubuğu
        def mini_toolbar(target_key):
            cols = st.columns([1,1,1,1,5])
            if cols[0].button("B", key=f"b_{target_key}"): q[target_key] += "<b></b>"
            if cols[1].button("I", key=f"i_{target_key}"): q[target_key] += "<i></i>"
            if cols[2].button("U", key=f"u_{target_key}"): q[target_key] += "<u></u>"
            if cols[3].button("S", key=f"s_{target_key}"): q[target_key] += "<small></small>"

        st.markdown('<div class="toolbar-container">Üst Metin Araçları</div>', unsafe_allow_html=True)
        mini_toolbar('ustMetin')
        q['ustMetin'] = st.text_area("", q['ustMetin'], height=70, label_visibility="collapsed", key="ta_ust")
        
        st.markdown('<div class="toolbar-container">Soru Kökü Araçları</div>', unsafe_allow_html=True)
        mini_toolbar('soruMetni')
        q['soruMetni'] = st.text_area("", q['soruMetni'], height=100, label_visibility="collapsed", key="ta_kok")
        
        st.caption("Şıklar")
        c1, c2 = st.columns(2)
        q['secenekler']['A'] = c1.text_input("A", q['secenekler']['A'], label_visibility="collapsed")
        q['secenekler']['B'] = c2.text_input("B", q['secenekler']['B'], label_visibility="collapsed")
        q['secenekler']['C'] = c1.text_input("C", q['secenekler']['C'], label_visibility="collapsed")
        q['secenekler']['D'] = c2.text_input("D", q['secenekler']['D'], label_visibility="collapsed")

    with col_visual:
        st.caption("🐍 Python Çizim Kodu")
        q['pythonKodu'] = st.text_area("", q['pythonKodu'], height=200, label_visibility="collapsed")
        
        if q['pythonKodu']:
            try:
                plt.clf()
                fig, ax = plt.subplots(figsize=(4, 3)) # Daha küçük görsel boyutu
                exec(q['pythonKodu'])
                st.pyplot(fig)
            except: st.caption("Çizim bekleniyor...")

with tab_preview:
    st.markdown("<div class='preview-container'>", unsafe_allow_html=True)
    st.caption(f"Yazar: {q['soruYazari']} | Kazanım: {q['kazanim']}")
    if q['ustMetin']: st.markdown(q['ustMetin'], unsafe_allow_html=True)
    if q['pythonKodu']:
        try:
            plt.clf(); fig, ax = plt.subplots(figsize=(5, 3.5))
            exec(q['pythonKodu']); st.pyplot(fig)
        except: pass
    st.markdown(f"**{q['soruMetni']}**", unsafe_allow_html=True)
    for k, v in q['secenekler'].items():
        st.write(f"**{k})** {v}")
    st.markdown("</div>", unsafe_allow_html=True)

# 5. KAYDET
final_json = json.dumps(st.session_state.questions, indent=4, ensure_ascii=False)
st.sidebar.download_button("💾 JSON İndir", final_json, "havuz.json", use_container_width=True)
