import streamlit as st
import json
import matplotlib.pyplot as plt

# 1. SAYFA AYARLARI VE WORD-STYLE CSS
st.set_page_config(page_title="SoruRota Studio", layout="wide")

st.markdown("""
    <style>
    /* Word benzeri araç çubuğu stili */
    .toolbar-container {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px 5px 0 0;
        border: 1px solid #d1d5db;
        display: flex;
        gap: 5px;
    }
    .stTextArea textarea {
        border-radius: 0 0 10px 10px !important;
        border-top: none !important;
    }
    .preview-container {
        border: 1px solid #dee2e6;
        padding: 40px;
        border-radius: 10px;
        background-color: white;
        min-height: 600px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. SESSION STATE YÖNETİMİ
if 'questions' not in st.session_state:
    st.session_state.questions = [{
        "soruYazari": "", "kazanim": "", "konu": "Yeni Soru",
        "ustMetin": "", "soruMetni": "", 
        "secenekler": {"A": "", "B": "", "C": "", "D": ""},
        "pythonKodu": "", "dogruCevap": "A", "cozum": ""
    }]
if 'current_idx' not in st.session_state:
    st.session_state.current_idx = 0

# 3. YAN MENÜ (HAVUZ YÖNETİMİ)
with st.sidebar:
    st.title("📂 Soru Havuzu")
    uploaded = st.file_uploader("JSON Yükle", type=['json'])
    if uploaded: st.session_state.questions = json.load(uploaded)
    
    st.divider()
    for i, q in enumerate(st.session_state.questions):
        if st.button(f"{i+1}. {q.get('konu', 'Adsız')[:15]}", key=f"q_{i}", use_container_width=True):
            st.session_state.current_idx = i
    
    if st.button("➕ Yeni Soru Ekle", type="primary", use_container_width=True):
        st.session_state.questions.append({
            "soruYazari": "", "kazanim": "", "konu": "Yeni Soru", "ustMetin": "", "soruMetni": "",
            "secenekler": {"A": "", "B": "", "C": "", "D": ""}, "pythonKodu": "", "dogruCevap": "A", "cozum": ""
        })
        st.rerun()

# Aktif Soru Verisi
q = st.session_state.questions[st.session_state.current_idx]

# 4. ANA PANELLER (SEKMELER)
tab_edit, tab_preview = st.tabs(["📝 Soru Düzenleme Paneli", "🔍 Sınav Ön İzleme (Tam Sayfa)"])

with tab_edit:
    col_input, col_visual = st.columns([1, 1])
    
    with col_input:
        st.subheader("Metin İçeriği")
        
        # Word Benzeri Araç Çubuğu Fonksiyonu
        def tool_bar(target_key):
            cols = st.columns([1,1,1,1,1,3])
            if cols[0].button("B", key=f"b_{target_key}"): q[target_key] += "<b></b>"
            if cols[1].button("I", key=f"i_{target_key}"): q[target_key] += "<i></i>"
            if cols[2].button("U", key=f"u_{target_key}"): q[target_key] += "<u></u>"
            if cols[3].button("S", key=f"s_{target_key}"): q[target_key] += "<small></small>"
            if cols[4].button("L", key=f"l_{target_key}"): q[target_key] += "<h3></h3>"

        st.markdown('<div class="toolbar-container">Üst Metin Araçları</div>', unsafe_allow_html=True)
        tool_bar('ustMetin')
        q['ustMetin'] = st.text_area("", q['ustMetin'], height=100, label_visibility="collapsed", key="ta_ust")
        
        st.markdown('<div class="toolbar-container">Soru Kökü Araçları</div>', unsafe_allow_html=True)
        tool_bar('soruMetni')
        q['soruMetni'] = st.text_area("", q['soruMetni'], height=150, label_visibility="collapsed", key="ta_kok")
        
        st.write("Seçenekler:")
        c1, c2 = st.columns(2)
        q['secenekler']['A'] = c1.text_input("A", q['secenekler']['A'])
        q['secenekler']['B'] = c2.text_input("B", q['secenekler']['B'])
        q['secenekler']['C'] = c1.text_input("C", q['secenekler']['C'])
        q['secenekler']['D'] = c2.text_input("D", q['secenekler']['D'])

    with col_visual:
        st.subheader("Görsel Tasarım [cite: 59, 60]")
        q['pythonKodu'] = st.text_area("Python Çizim Kodu", q['pythonKodu'], height=300, 
                                     placeholder="import matplotlib.pyplot as plt\nfig, ax = plt.subplots()\n...")
        
        st.info("🖼️ Görsel Çıktısı (Orta Boyut)")
        if q['pythonKodu']:
            try:
                plt.clf()
                fig, ax = plt.subplots(figsize=(5, 4))
                exec(q['pythonKodu'])
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Çizim Hatası: {e}")

with tab_preview:
    st.markdown("<div class='preview-container'>", unsafe_allow_html=True)
    
    # Başlık Bilgisi
    st.markdown(f"**Yazar:** {q['soruYazari']} | **Kazanım:** {q['kazanim']} [cite: 129, 156]")
    st.divider()
    
    # Senaryo ve Görsel
    if q['ustMetin']:
        st.markdown(q['ustMetin'], unsafe_allow_html=True)
    
    if q['pythonKodu']:
        try:
            plt.clf()
            fig, ax = plt.subplots(figsize=(6, 4))
            exec(q['pythonKodu'])
            st.pyplot(fig)
        except: pass
        
    # Soru ve Şıklar
    st.markdown(f"### {q['soruMetni']}", unsafe_allow_html=True)
    st.write(f"**A)** {q['secenekler']['A']}")
    st.write(f"**B)** {q['secenekler']['B']}")
    st.write(f"**C)** {q['secenekler']['C']}")
    st.write(f"**D)** {q['secenekler']['D']}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    with st.expander("Çözüm ve Yanıt Anahtarı"):
        st.success(f"Doğru Cevap: {q['dogruCevap']} [cite: 22]")
        st.write(q['cozum'] if q['cozum'] else "Çözüm belirtilmedi.")

# 5. DIŞA AKTARIM
final_json = json.dumps(st.session_state.questions, indent=4, ensure_ascii=False)
st.sidebar.download_button("💾 Havuzu JSON İndir", final_json, "havuz.json", use_container_width=True)
