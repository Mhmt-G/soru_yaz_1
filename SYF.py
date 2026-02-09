import streamlit as st
import json
import matplotlib.pyplot as plt

# 1. AYARLAR VE STİL
st.set_page_config(page_title="SoruRota Studio v4", layout="wide")
st.markdown("""
    <style>
    html, body, [class*="css"] { font-size: 12px !important; }
    .stTextArea textarea { font-size: 11px !important; border-radius: 0 0 5px 5px !important; border-top: none !important; }
    .integrated-toolbar { background-color: #f1f3f4; padding: 2px 8px; border: 1px solid #d1d5db; border-radius: 5px 5px 0 0; display: flex; gap: 4px; font-size: 10px; font-weight: bold; }
    .stButton>button { height: 22px !important; font-size: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. VERİ YAPISI VE HATA ÖNLEME
if 'questions' not in st.session_state:
    st.session_state.questions = [{
        "soruYazari": "", "kazanim": "", "konu": "Yeni Soru", "ustMetin": "", "soruMetni": "", 
        "secenekler": {"A": "", "B": "", "C": "", "D": ""}, "pythonKodu": "", "manuelGorsel": None,
        "dogruCevap": "A", "cozum": ""
    }]
if 'curr_idx' not in st.session_state:
    st.session_state.curr_idx = 0

# 3. YAN MENÜ
with st.sidebar:
    st.caption("📂 Veri Yönetimi")
    up_json = st.file_uploader("JSON Yükle", type=['json'], label_visibility="collapsed")
    if up_json: 
        st.session_state.questions = json.load(up_json)
    
    for i, q in enumerate(st.session_state.questions):
        if st.sidebar.button(f"{i+1}. {q.get('konu', 'Adsız')[:10]}", key=f"q_{i}", use_container_width=True):
            st.session_state.current_idx = i
    
    if st.sidebar.button("+ Yeni Soru", type="primary", use_container_width=True):
        st.session_state.questions.append({"soruYazari": "", "kazanim": "", "konu": "Yeni Soru", "ustMetin": "", "soruMetni": "", "secenekler": {"A": "", "B": "", "C": "", "D": ""}, "pythonKodu": "", "manuelGorsel": None, "dogruCevap": "A", "cozum": ""})
        st.rerun()

# Aktif soruyu çekme (Hata korumalı)
q = st.session_state.questions[st.session_state.get('current_idx', 0)]

# 4. ARAÇ ÇUBUĞU FONKSİYONU
def render_toolbar(key_name):
    st.markdown(f'<div class="integrated-toolbar">{key_name} Araçları</div>', unsafe_allow_html=True)
    cols = st.columns([1,1,1,1,1,6])
    if cols[0].button("B", key=f"b_{key_name}"): q[key_name] = q.get(key_name, "") + "<b></b>"
    if cols[1].button("I", key=f"i_{key_name}"): q[key_name] = q.get(key_name, "") + "<i></i>"
    if cols[2].button("U", key=f"u_{key_name}"): q[key_name] = q.get(key_name, "") + "<u></u>"
    if cols[3].button("S", key=f"s_{key_name}"): q[key_name] = q.get(key_name, "") + "<small></small>"
    if cols[4].button("L", key=f"l_{key_name}"): q[key_name] = q.get(key_name, "") + "<h3></h3>"

# 5. ANA PANEL
tab_edit, tab_prev = st.tabs(["📝 Düzenle", "🔍 Ön İzleme"])

with tab_edit:
    c_edit, c_vis = st.columns([1, 0.8])
    with c_edit:
        # Metin alanları için entegre araç çubuğu
        render_toolbar('ustMetin')
        q['ustMetin'] = st.text_area("", q.get('ustMetin', ""), height=60, label_visibility="collapsed", key="at_ust")
        
        render_toolbar('soruMetni')
        q['soruMetni'] = st.text_area("", q.get('soruMetni', ""), height=80, label_visibility="collapsed", key="at_kok")
        
        st.caption("Şıklar")
        s = st.columns(4)
        for i, opt in enumerate(["A","B","C","D"]):
            q['secenekler'][opt] = s[i].text_input(opt, q['secenekler'].get(opt, ""), label_visibility="collapsed")

    with c_vis:
        st.caption("🖼️ Görsel")
        v_tab1, v_tab2 = st.tabs(["🐍 Python", "📤 Yükle"])
        with v_tab1:
            # KeyError hatasını önlemek için .get() kullanımı [cite: 107]
            q['pythonKodu'] = st.text_area("Kod", q.get('pythonKodu', ""), height=100, label_visibility="collapsed")
            if q.get('pythonKodu'):
                try:
                    plt.clf()
                    fig, ax = plt.subplots(figsize=(3, 2))
                    exec(q['pythonKodu'])
                    st.pyplot(plt.gcf())
                except: st.caption("Kod bekleniyor...")
        with v_tab2:
            up_img = st.file_uploader("Seç", type=['png','jpg','jpeg'], label_visibility="collapsed")
            if up_img: st.image(up_img, width=150)

# 6. DIŞA AKTAR
f_json = json.dumps(st.session_state.questions, indent=4, ensure_ascii=False)
st.sidebar.download_button("💾 JSON İndir", f_json, "havuz.json", use_container_width=True)
