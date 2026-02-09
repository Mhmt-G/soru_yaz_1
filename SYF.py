import streamlit as st
import json
import matplotlib.pyplot as plt

# 1. PROFESYONEL ARAYÜZ VE WORD ŞERİDİ STİLİ
st.set_page_config(page_title="SoruRota Studio v8", layout="wide")

st.markdown("""
    <style>
    /* Genel Yazı Tipi Ayarları */
    html, body, [class*="css"] { font-size: 14px !important; font-family: 'Aptos', sans-serif !important; }
    
    /* Word Stili Araç Çubuğu (Toolbar) */
    .word-toolbar {
        background-color: #f3f3f3;
        padding: 5px 10px;
        border: 1px solid #d2d2d2;
        border-radius: 4px 4px 0 0;
        display: flex;
        gap: 8px;
        align-items: center;
    }
    .stTextArea textarea { border-radius: 0 0 5px 5px !important; border-top: none !important; }
    
    /* Ön İzleme Kağıdı */
    .exam-paper {
        background-color: white;
        padding: 40px;
        border: 1px solid #ccc;
        border-radius: 2px;
        box-shadow: 0 0 15px rgba(0,0,0,0.1);
        max-width: 800px;
        margin: auto;
        color: black;
        min-height: 800px;
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
    st.title("📂 Soru Havuzu")
    up_json = st.file_uploader("JSON Yükle", type=['json'], label_visibility="collapsed")
    if up_json: st.session_state.questions = json.load(up_json)
    
    st.divider()
    for i, ques in enumerate(st.session_state.questions):
        if st.sidebar.button(f"{i+1}. {ques.get('konu', 'Adsız')[:15]}", key=f"q_btn_{i}", use_container_width=True):
            st.session_state.curr_idx = i
            st.rerun()
    
    if st.sidebar.button("+ Yeni Soru Ekle", type="primary", use_container_width=True):
        st.session_state.questions.append({"soruYazari": "", "kazanim": "", "konu": "Yeni Soru", "ustMetin": "", "soruMetni": "", "secenekler": {"A": "", "B": "", "C": "", "D": ""}, "pythonKodu": "", "dogruCevap": "A", "cozum": ""})
        st.session_state.curr_idx = len(st.session_state.questions) - 1
        st.rerun()

q = st.session_state.questions[st.session_state.curr_idx]

# 4. WORD STİLİ ARAÇ ÇUBUĞU FONKSİYONU
def render_word_toolbar(key_name):
    st.markdown(f'<div class="word-toolbar"><b>{key_name} Düzenle</b></div>', unsafe_allow_html=True)
    t_col = st.columns([0.5, 0.5, 0.5, 0.5, 0.5, 0.7, 0.7, 0.7, 4])
    if t_col[0].button("**K**", key=f"k_{key_name}"): q[key_name] += "<b></b>"
    if t_col[1].button("*T*", key=f"t_{key_name}"): q[key_name] += "<i></i>"
    if t_col[2].button("<u>A</u>", key=f"a_{key_name}"): q[key_name] += "<u></u>"
    if t_col[3].button("~~ab~~", key=f"ab_{key_name}"): q[key_name] += "<strike></strike>"
    if t_col[4].button("x₂", key=f"x2_{key_name}"): q[key_name] += "<sub></sub>"
    if t_col[5].button("x²", key=f"xsq_{key_name}"): q[key_name] += "<sup></sup>"
    if t_col[6].button("Boyut", key=f"sz_{key_name}"): q[key_name] += "<span style='font-size:18px;'></span>"
    if t_col[7].button("Renk", key=f"cl_{key_name}"): q[key_name] += "<span style='color:red;'></span>"

# 5. ANA PANEL
tab_edit, tab_prev = st.tabs(["📝 Soru Tasarımı", "🔍 Sınav Kağıdı Ön İzleme"])

with tab_edit:
    c_edit, c_vis = st.columns([1.1, 0.9])
    with c_edit:
        st.subheader("Metin ve Senaryo")
        q['soruYazari'] = st.text_input("Yazar", q.get('soruYazari', ''))
        
        render_word_toolbar('ustMetin')
        q['ustMetin'] = st.text_area("", q.get('ustMetin', ''), height=100, label_visibility="collapsed", key="ta_ust")
        
        render_word_toolbar('soruMetni')
        q['soruMetni'] = st.text_area("", q.get('soruMetni', ''), height=120, label_visibility="collapsed", key="ta_kok")
        
        st.write("**Seçenekler (Alt Alta)**")
        for opt in ["A", "B", "C", "D"]:
            q['secenekler'][opt] = st.text_input(f"{opt} Seçeneği", q['secenekler'].get(opt, ""))
        
        q['dogruCevap'] = st.selectbox("Doğru Cevap", ["A", "B", "C", "D"], index=["A","B","C","D"].index(q.get('dogruCevap', 'A')))

    with c_vis:
        st.subheader("Yüksek Kaliteli Görsel Motoru")
        q['pythonKodu'] = st.text_area("Python Çizim Kodu", q.get('pythonKodu', ""), height=200)
        
        if q.get('pythonKodu'):
            try:
                plt.clf()
                # Yüksek DPI ile daha kaliteli görsel [cite: 10]
                fig, ax = plt.subplots(figsize=(4, 3), dpi=150) 
                exec(q['pythonKodu'])
                st.pyplot(fig, use_container_width=False)
            except Exception as e:
                st.info("Çizim kodu bekleniyor veya hata var.")

with tab_prev:
    st.markdown("<div class='exam-paper'>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:right; font-size:12px;'>Yazar: {q.get('soruYazari', '')}</div>", unsafe_allow_html=True)
    st.markdown("### FEN BİLİMLERİ BAŞARI TESTİ", unsafe_allow_html=True)
    st.divider()
    
    if q.get('ustMetin'):
        st.markdown(f"<div style='margin-bottom:20px;'>{q['ustMetin']}</div>", unsafe_allow_html=True)
    
    # Ön İzlemede Ortalı ve Kaliteli Görsel
    if q.get('pythonKodu'):
        try:
            plt.clf()
            fig_p, ax_p = plt.subplots(figsize=(5, 3.5), dpi=200)
            exec(q['pythonKodu'])
            _, mid_c, _ = st.columns([0.5, 2, 0.5])
            mid_c.pyplot(fig_p, use_container_width=False)
        except: pass
    
    st.markdown(f"<div style='font-size:18px; font-weight:bold; margin:20px 0;'>{q.get('soruMetni', '')}</div>", unsafe_allow_html=True)
    
    # Seçenekler Alt Alta 
    for k, v in q.get('secenekler', {}).items():
        st.markdown(f"<div style='margin-bottom:10px;'><b>{k})</b> {v}</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# 6. KAYDET
final_json = json.dumps(st.session_state.questions, indent=4, ensure_ascii=False)
st.sidebar.download_button("💾 Havuzu JSON Olarak İndir", final_json, "havuz_v8.json", use_container_width=True)
