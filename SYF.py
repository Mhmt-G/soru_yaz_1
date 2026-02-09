import streamlit as st
import json
import matplotlib.pyplot as plt

# 1. PROFESYONEL ARAYÜZ VE SEMBOLİK ARAÇ ÇUBUĞU STİLİ
st.set_page_config(page_title="SoruRota Studio v9", layout="wide")

st.markdown("""
    <style>
    /* Genel Tipografi */
    html, body, [class*="css"] { font-size: 14px !important; font-family: 'Segoe UI', sans-serif !important; }
    
    /* Word Stili Sembolik Araç Çubuğu */
    .word-toolbar {
        background-color: #f3f3f3;
        padding: 4px 8px;
        border: 1px solid #c8c8c8;
        border-radius: 4px 4px 0 0;
        display: flex;
        gap: 2px;
        align-items: center;
    }
    .stTextArea textarea { border-radius: 0 0 5px 5px !important; border-top: none !important; font-size: 13px !important; }
    
    /* Sınav Kağıdı Ön İzleme Alanı */
    .exam-paper {
        background-color: white;
        padding: 50px;
        border: 1px solid #b5b5b5;
        border-radius: 0px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        max-width: 750px;
        margin: 20px auto;
        color: #000;
        min-height: 900px;
        line-height: 1.5;
    }
    .stButton>button { border: 1px solid #ccc; padding: 2px 8px !important; height: 28px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. VERİ YÖNETİMİ VE DURUM KONTROLÜ
if 'questions' not in st.session_state:
    st.session_state.questions = [{
        "soruYazari": "", "kazanim": "", "konu": "Yeni Soru", "ustMetin": "", "soruMetni": "", 
        "secenekler": {"A": "", "B": "", "C": "", "D": ""}, "pythonKodu": "", "dogruCevap": "A", "cozum": ""
    }]
if 'curr_idx' not in st.session_state:
    st.session_state.curr_idx = 0

# 3. YAN MENÜ (HAVUZ VE DOSYA)
with st.sidebar:
    st.subheader("📁 Dosya")
    up_json = st.file_uploader("Yükle", type=['json'], label_visibility="collapsed")
    if up_json: st.session_state.questions = json.load(up_json)
    
    st.divider()
    st.caption("📋 Soru Listesi")
    for i, ques in enumerate(st.session_state.questions):
        if st.sidebar.button(f"{i+1}. {ques.get('konu', '')[:12]}", key=f"nav_{i}", use_container_width=True):
            st.session_state.curr_idx = i
            st.rerun()
    
    if st.sidebar.button("➕ Ekle", type="primary", use_container_width=True):
        st.session_state.questions.append({"soruYazari": "", "kazanim": "", "konu": "Yeni Soru", "ustMetin": "", "soruMetni": "", "secenekler": {"A": "", "B": "", "C": "", "D": ""}, "pythonKodu": "", "dogruCevap": "A", "cozum": ""})
        st.session_state.curr_idx = len(st.session_state.questions) - 1
        st.rerun()

q = st.session_state.questions[st.session_state.curr_idx]

# 4. SADECE SEMBOLLERDEN OLUŞAN ARAÇ ÇUBUĞU
def render_symbol_toolbar(key_name):
    st.markdown(f'<div class="word-toolbar"></div>', unsafe_allow_html=True)
    cols = st.columns([0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.6, 0.6, 5])
    if cols[0].button("𝐁", key=f"b_{key_name}"): q[key_name] += "<b></b>"
    if cols[1].button("𝐼", key=f"i_{key_name}"): q[key_name] += "<i></i>"
    if cols[2].button("𝚄", key=f"u_{key_name}"): q[key_name] += "<u></u>"
    if cols[3].button("̶S̶", key=f"s_{key_name}"): q[key_name] += "<strike></strike>"
    if cols[4].button("x₂", key=f"x2_{key_name}"): q[key_name] += "<sub></sub>"
    if cols[5].button("x²", key=f"xsq_{key_name}"): q[key_name] += "<sup></sup>"
    if cols[6].button("A🡩", key=f"sz_{key_name}"): q[key_name] += "<span style='font-size:18px;'></span>"
    if cols[7].button("🎨", key=f"cl_{key_name}"): q[key_name] += "<span style='color:red;'></span>"

# 5. ANA ÇALIŞMA ALANI
tab_edit, tab_prev = st.tabs(["📝 Tasarım", "🔍 Sınav Kağıdı"])

with tab_edit:
    col_l, col_r = st.columns([1, 0.8])
    
    with col_l:
        st.caption("Künye")
        c1, c2, c3 = st.columns(3)
        q['soruYazari'] = c1.text_input("Yazar", q.get('soruYazari', ''), label_visibility="collapsed")
        q['kazanim'] = c2.text_input("Kazanım", q.get('kazanim', ''), label_visibility="collapsed")
        q['konu'] = c3.text_input("Konu", q.get('konu', ''), label_visibility="collapsed")
        
        render_symbol_toolbar('ustMetin')
        q['ustMetin'] = st.text_area("", q.get('ustMetin', ''), height=80, label_visibility="collapsed", key="at_u")
        
        render_symbol_toolbar('soruMetni')
        q['soruMetni'] = st.text_area("", q.get('soruMetni', ''), height=100, label_visibility="collapsed", key="at_s")
        
        st.caption("Seçenekler (A-B-C-D)")
        for char in ["A", "B", "C", "D"]:
            q['secenekler'][char] = st.text_input(char, q['secenekler'].get(char, ""), label_visibility="collapsed")
        
        q['dogruCevap'] = st.selectbox("Cevap", ["A", "B", "C", "D"], index=["A","B","C","D"].index(q.get('dogruCevap', 'A')))

    with col_r:
        st.caption("🖼️ Görsel Kod (High-DPI)")
        q['pythonKodu'] = st.text_area("", q.get('pythonKodu', ""), height=180, label_visibility="collapsed")
        
        if q.get('pythonKodu'):
            try:
                plt.clf()
                fig, ax = plt.subplots(figsize=(4, 2.5), dpi=150) # Kalite artırıldı
                exec(q['pythonKodu'])
                st.pyplot(fig, use_container_width=False)
            except: st.info("Kod bekleniyor...")

with tab_prev:
    st.markdown("<div class='exam-paper'>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:right; font-size:11px;'>Yazar: {q['soruYazari']}</div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>FEN BİLİMLERİ TESTİ</h2>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    
    if q.get('ustMetin'):
        st.markdown(f"<div style='margin-bottom:15px;'>{q['ustMetin']}</div>", unsafe_allow_html=True)
    
    if q.get('pythonKodu'):
        try:
            plt.clf()
            fig_p, ax_p = plt.subplots(figsize=(5, 3), dpi=200) # Ön izlemede maksimum kalite
            exec(q['pythonKodu'])
            _, mid, _ = st.columns([0.5, 2, 0.5])
            mid.pyplot(fig_p, use_container_width=False)
        except: pass
    
    st.markdown(f"<div style='font-size:17px; font-weight:bold; margin:15px 0;'>{q['soruMetni']}</div>", unsafe_allow_html=True)
    
    # Seçenekler Alt Alta
    for k, v in q['secenekler'].items():
        st.markdown(f"<div style='margin-bottom:8px;'><b>{k})</b> {v}</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# 6. DIŞA AKTAR
final_json = json.dumps(st.session_state.questions, indent=4, ensure_ascii=False)
st.sidebar.download_button("💾 JSON İndir", final_json, "havuz_v9.json", use_container_width=True)
