import streamlit as st
import json
import matplotlib.pyplot as plt

# 1. AYARLAR VE STİL (KÜÇÜK HARF VE PENCERELER) [cite: 21]
st.set_page_config(page_title="SoruRota v5", layout="wide")
st.markdown("""
    <style>
    html, body, [class*="css"] { font-size: 11px !important; }
    .stTextArea textarea { font-size: 11px !important; border-radius: 0 0 5px 5px !important; border-top: none !important; }
    .integrated-toolbar { background-color: #f1f3f4; padding: 2px 8px; border: 1px solid #d1d5db; border-radius: 5px 5px 0 0; display: flex; gap: 4px; font-size: 10px; font-weight: bold; }
    .stButton>button { height: 20px !important; font-size: 10px !important; padding: 0 5px !important; }
    .preview-box { border: 1px solid #dee2e6; padding: 15px; border-radius: 8px; background-color: white; box-shadow: 0 2px 10px rgba(0,0,0,0.05); color: black; }
    </style>
    """, unsafe_allow_html=True)

# 2. VERİ YÖNETİMİ
if 'questions' not in st.session_state:
    st.session_state.questions = [{
        "soruYazari": "", "kazanim": "", "konu": "Yeni Soru", "ustMetin": "", "soruMetni": "", 
        "secenekler": {"A": "", "B": "", "C": "", "D": ""}, "pythonKodu": "", "dogruCevap": "A", "cozum": ""
    }]
if 'curr_idx' not in st.session_state:
    st.session_state.curr_idx = 0

# 3. YAN MENÜ (DARALTILMIŞ)
with st.sidebar:
    st.caption("📂 Soru Havuzu")
    up_json = st.file_uploader("JSON Yükle", type=['json'], label_visibility="collapsed")
    if up_json: 
        st.session_state.questions = json.load(up_json)
    
    st.divider()
    # Soru Listesi
    for i, ques in enumerate(st.session_state.questions):
        label = f"{i+1}. {ques.get('konu', 'Adsız')[:10]}"
        if st.sidebar.button(label, key=f"q_btn_{i}", use_container_width=True):
            st.session_state.curr_idx = i
            st.rerun() # Seçim sonrası ön izlemeyi tetikler
    
    if st.sidebar.button("+ Yeni Soru", type="primary", use_container_width=True):
        st.session_state.questions.append({"soruYazari": "", "kazanim": "", "konu": "Yeni Soru", "ustMetin": "", "soruMetni": "", "secenekler": {"A": "", "B": "", "C": "", "D": ""}, "pythonKodu": "", "dogruCevap": "A", "cozum": ""})
        st.session_state.curr_idx = len(st.session_state.questions) - 1
        st.rerun()

# AKTİF SORU
q = st.session_state.questions[st.session_state.curr_idx]

# 4. ARAÇ ÇUBUĞU FONKSİYONU (METİN KUTUSU İÇİNDE)
def render_toolbar(key_name):
    st.markdown(f'<div class="integrated-toolbar">{key_name} Araçları</div>', unsafe_allow_html=True)
    cols = st.columns([1,1,1,1,1,6])
    if cols[0].button("B", key=f"b_{key_name}"): q[key_name] = q.get(key_name, "") + "<b></b>"
    if cols[1].button("I", key=f"i_{key_name}"): q[key_name] = q.get(key_name, "") + "<i></i>"
    if cols[2].button("U", key=f"u_{key_name}"): q[key_name] = q.get(key_name, "") + "<u></u>"
    if cols[3].button("S", key=f"s_{key_name}"): q[key_name] = q.get(key_name, "") + "<small></small>"
    if cols[4].button("L", key=f"l_{key_name}"): q[key_name] = q.get(key_name, "") + "<h3></h3>"

# 5. ANA PANEL (DÜZENLE VE ÖN İZLEME)
tab_edit, tab_prev = st.tabs(["📝 Soruyu Düzenle", "🔍 Tam Ön İzleme"])

with tab_edit:
    c_edit, c_vis = st.columns([1, 0.7])
    with c_edit:
        # Mini Bilgi Satırı
        c1, c2, c3 = st.columns(3)
        q['soruYazari'] = c1.text_input("Yazar", q.get('soruYazari', ''), key="y_in")
        q['kazanim'] = c2.text_input("Kazanım", q.get('kazanim', ''), key="k_in")
        q['konu'] = c3.text_input("Konu", q.get('konu', ''), key="konu_in")

        # Araç Çubuklu Metin Alanları
        render_toolbar('ustMetin')
        q['ustMetin'] = st.text_area("", q.get('ustMetin', ''), height=60, label_visibility="collapsed", key="ta_ust")
        
        render_toolbar('soruMetni')
        q['soruMetni'] = st.text_area("", q.get('soruMetni', ''), height=80, label_visibility="collapsed", key="ta_kok")
        
        st.caption("Şıklar ve Doğru Cevap")
        s = st.columns([1,1,1,1,1])
        labels = ["A","B","C","D"]
        for i, opt in enumerate(labels):
            q['secenekler'][opt] = s[i].text_input(opt, q['secenekler'].get(opt, ""), label_visibility="collapsed", key=f"opt_{opt}")
        q['dogruCevap'] = s[4].selectbox("", labels, index=labels.index(q.get('dogruCevap', 'A')), label_visibility="collapsed")

    with c_vis:
        st.caption("🖼️ Görsel / Kod")
        v_tab1, v_tab2 = st.tabs(["🐍 Python", "📤 Görsel Ekle"])
        with v_tab1:
            q['pythonKodu'] = st.text_area("Python Kodu", q.get('pythonKodu', ""), height=100, label_visibility="collapsed")
            if q.get('pythonKodu'):
                try:
                    plt.clf()
                    fig, ax = plt.subplots(figsize=(3, 2)) # Daha küçük görsel boyutu [cite: 10]
                    exec(q['pythonKodu'])
                    st.pyplot(plt.gcf())
                except: st.caption("Görsel bekleniyor...")
        with v_tab2:
            up_img = st.file_uploader("Görsel Seç", type=['png','jpg','jpeg'], label_visibility="collapsed")
            if up_img: st.image(up_img, width=150)

with tab_prev:
    # Kesin Ön İzleme Alanı
    st.markdown("<div class='preview-box'>", unsafe_allow_html=True)
    st.caption(f"Yazar: {q.get('soruYazari', '')} | Kazanım: {q.get('kazanim', '')}")
    
    if q.get('ustMetin'):
        st.markdown(q['ustMetin'], unsafe_allow_html=True)
    
    if q.get('pythonKodu'):
        try:
            plt.clf()
            fig_p, ax_p = plt.subplots(figsize=(4, 2.5))
            exec(q['pythonKodu'])
            st.pyplot(plt.gcf())
        except: pass
    
    st.markdown(f"**{q.get('soruMetni', '')}**", unsafe_allow_html=True)
    for k, v in q.get('secenekler', {}).items():
        st.write(f"**{k})** {v}")
    
    st.divider()
    st.success(f"Cevap: {q.get('dogruCevap', '')}")
    st.markdown("</div>", unsafe_allow_html=True)

# 6. KAYDET
final_json = json.dumps(st.session_state.questions, indent=4, ensure_ascii=False)
st.sidebar.download_button("💾 JSON Havuzu İndir", final_json, "havuz.json", use_container_width=True)
