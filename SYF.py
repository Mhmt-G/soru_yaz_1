import streamlit as st
import json
import matplotlib.pyplot as plt

# 1. AYARLAR VE YENİDEN ÖLÇEKLENDİRİLMİŞ STİL
st.set_page_config(page_title="MÜDÜR V1", layout="wide")
st.markdown("""
    <style>
    /* Yazı boyutlarını büyütme (Okunabilirlik için) */
    html, body, [class*="css"] { font-size: 14px !important; } 
    .stTextArea textarea { font-size: 13px !important; border-radius: 0 0 5px 5px !important; border-top: none !important; }
    .stTextInput input { font-size: 13px !important; height: 32px !important; }
    
    /* Araç çubuğu yazı boyutu */
    .integrated-toolbar { 
        background-color: #f1f3f4; 
        padding: 4px 10px; 
        border: 1px solid #d1d5db; 
        border-radius: 5px 5px 0 0; 
        font-size: 12px; 
        font-weight: bold; 
    }
    
    /* Butonları biraz daha belirgin yapma */
    .stButton>button { height: 26px !important; font-size: 12px !important; }
    
    /* Ön izleme kutusu: Yazıları büyütülmüş, genişliği ayarlanmış */
    .preview-box { 
        border: 1px solid #dee2e6; 
        padding: 30px; 
        border-radius: 10px; 
        background-color: white; 
        max-width: 700px; 
        margin: auto; 
        color: #1a1a1a;
        line-height: 1.6;
    }
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

# 3. YAN MENÜ
with st.sidebar:
    st.subheader("📂 Soru Havuzu")
    up_json = st.file_uploader("JSON Yükle", type=['json'], label_visibility="collapsed")
    if up_json: st.session_state.questions = json.load(up_json)
    
    st.divider()
    for i, ques in enumerate(st.session_state.questions):
        label = f"{i+1}. {ques.get('konu', 'Adsız')[:15]}"
        if st.sidebar.button(label, key=f"q_btn_{i}", use_container_width=True):
            st.session_state.curr_idx = i
            st.rerun()
    
    if st.sidebar.button("+ Yeni Soru Ekle", type="primary", use_container_width=True):
        st.session_state.questions.append({"soruYazari": "", "kazanim": "", "konu": "Yeni Soru", "ustMetin": "", "soruMetni": "", "secenekler": {"A": "", "B": "", "C": "", "D": ""}, "pythonKodu": "", "dogruCevap": "A", "cozum": ""})
        st.session_state.curr_idx = len(st.session_state.questions) - 1
        st.rerun()

q = st.session_state.questions[st.session_state.curr_idx]

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
tab_edit, tab_prev = st.tabs(["📝 Soru Tasarımı", "🔍 Sınav Ön İzleme"])

with tab_edit:
    c_edit, c_vis = st.columns([1.1, 0.9])
    with c_edit:
        c1, c2 = st.columns(2)
        q['soruYazari'] = c1.text_input("Soru Yazarı", q.get('soruYazari', ''), key="y_in")
        q['kazanim'] = c2.text_input("Kazanım No", q.get('kazanim', ''), key="k_in")
        
        render_toolbar('ustMetin')
        q['ustMetin'] = st.text_area("", q.get('ustMetin', ''), height=80, label_visibility="collapsed", key="ta_ust")
        
        render_toolbar('soruMetni')
        q['soruMetni'] = st.text_area("", q.get('soruMetni', ''), height=100, label_visibility="collapsed", key="ta_kok")
        
        st.write("**Seçenekler ve Yanıt**")
        s = st.columns([1,1,1,1,1])
        labels = ["A","B","C","D"]
        for i, opt in enumerate(labels):
            q['secenekler'][opt] = s[i].text_input(opt, q['secenekler'].get(opt, ""), key=f"opt_{opt}")
        q['dogruCevap'] = s[4].selectbox("Cevap", labels, index=labels.index(q.get('dogruCevap', 'A')))

    with c_vis:
        st.write("**🖼️ Görsel ve Çizim**")
        v_tab1, v_tab2 = st.tabs(["🐍 Python Kod", "📤 Resim Yükle"])
        with v_tab1:
            q['pythonKodu'] = st.text_area("Çizim Kodu", q.get('pythonKodu', ""), height=120, label_visibility="collapsed")
            if q.get('pythonKodu'):
                try:
                    plt.clf()
                    fig, ax = plt.subplots(figsize=(2.2, 1.5)) # Düzenleme alanında daha küçük
                    exec(q['pythonKodu'])
                    st.pyplot(plt.gcf(), use_container_width=False)
                except: st.caption("Kod hatası veya eksik veri...")
        with v_tab2:
            up_img = st.file_uploader("Görsel Seç", type=['png','jpg','jpeg'], label_visibility="collapsed")
            if up_img: st.image(up_img, width=100)

with tab_prev:
    st.markdown("<div class='preview-box'>", unsafe_allow_html=True)
    st.markdown(f"<span style='font-size:12px; color:gray;'>Yazar: {q.get('soruYazari', '')} | Kazanım: {q.get('kazanim', '')}</span>", unsafe_allow_html=True)
    
    if q.get('ustMetin'):
        st.markdown(f"<div style='margin-bottom:15px;'>{q['ustMetin']}</div>", unsafe_allow_html=True)
    
    # --- KÜÇÜLTÜLMÜŞ GÖRSEL ALANI ---
    if q.get('pythonKodu'):
        try:
            plt.clf()
            # Ön izleme için kompakt boyut (2.8 x 1.8 inç)
            fig_p, ax_p = plt.subplots(figsize=(2.8, 1.8)) 
            exec(q['pythonKodu'])
            # Ortalamak için sütun kullanıyoruz
            _, mid_c, _ = st.columns([1, 2, 1])
            mid_c.pyplot(plt.gcf(), use_container_width=False)
        except: pass
    
    if up_img:
        _, mid_i, _ = st.columns([1, 2, 1])
        mid_i.image(up_img, width=180) # Yüklenen resimler için dar genişlik
    
    st.markdown(f"<div style='font-size:16px; font-weight:bold; margin-top:10px;'>{q.get('soruMetni', '')}</div>", unsafe_allow_html=True)
    
    for k, v in q.get('secenekler', {}).items():
        st.markdown(f"**{k})** {v}")
    
    st.divider()
    st.success(f"**Doğru Cevap: {q.get('dogruCevap', '')}**")
    st.markdown("</div>", unsafe_allow_html=True)

# 6. KAYDET/İNDİR
final_json = json.dumps(st.session_state.questions, indent=4, ensure_ascii=False)
st.sidebar.download_button("💾 JSON Havuzu İndir", final_json, "havuz_v7.json", use_container_width=True)
