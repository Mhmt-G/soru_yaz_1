import streamlit as st
import json
import matplotlib.pyplot as plt
from PIL import Image
import io

# ==========================================
# 1. & 2. PROFESYONEL ARAYÜZ AYARLARI
# ==========================================
st.set_page_config(
    page_title="SoruRota Studio",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS ile Modern ve Profesyonel Görünüm
st.markdown("""
    <style>
    /* Genel Font ve Renkler */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', 'Roboto', sans-serif;
        font-size: 14px;
        color: #333;
    }
    
    /* 4. DÜZENLEME BARLARI İÇİN STİL */
    .editor-toolbar {
        background-color: #f8f9fa;
        border: 1px solid #ced4da;
        border-bottom: none;
        border-radius: 5px 5px 0 0;
        padding: 5px;
        display: flex;
        gap: 5px;
        align-items: center;
    }
    
    /* Metin Kutularını Toolbar ile Birleştirme */
    .stTextArea textarea {
        border-top-left-radius: 0 !important;
        border-top-right-radius: 0 !important;
        border-color: #ced4da !important;
        font-family: 'Consolas', monospace !important; /* Kodlama hissi için */
    }
    
    /* Toolbar Butonları */
    .stButton button {
        border: 1px solid transparent;
        background: transparent;
        padding: 2px 8px !important;
        font-size: 13px !important;
        font-weight: bold;
        color: #495057;
    }
    .stButton button:hover {
        background-color: #e9ecef;
        border-radius: 4px;
        color: #000;
    }

    /* 1. & 8. ÖN İZLEME KAĞIDI (A4 Görünümü) */
    .preview-paper {
        background-color: white;
        padding: 40px;
        border: 1px solid #ddd;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        max-width: 800px;
        margin: 0 auto;
        min-height: 800px;
        color: black;
        line-height: 1.6;
    }
    
    /* Seçenekler Kutusu */
    .option-box {
        margin-bottom: 8px;
        padding: 5px;
        border-bottom: 1px solid #eee;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# VERİ YÖNETİMİ (Session State)
# ==========================================
DEFAULT_SORU = {
    "yazar": "", "kazanim": "", "konu": "Yeni Soru", 
    "ustMetin": "", "soruMetni": "", 
    "secenekler": {"A": "", "B": "", "C": "", "D": ""}, 
    "dogruCevap": "A", "cozum": "", "pythonKodu": ""
}

if 'questions' not in st.session_state:
    st.session_state.questions = [DEFAULT_SORU.copy()]
if 'curr_idx' not in st.session_state:
    st.session_state.curr_idx = 0

def get_current_q():
    if st.session_state.curr_idx >= len(st.session_state.questions):
        st.session_state.curr_idx = 0
    return st.session_state.questions[st.session_state.curr_idx]

# ==========================================
# 4. DÜZENLEME BARLARI (FONKSİYON)
# ==========================================
def render_toolbar(key):
    """Metin kutuları için HTML etiket butonları oluşturur."""
    st.markdown('<div class="editor-toolbar">', unsafe_allow_html=True)
    cols = st.columns([1,1,1,1,1,1,1,6]) # Butonlar ve boşluk
    
    q = get_current_q()
    current_text = q.get(key, "")
    
    # HTML Etiketlerini Ekleyen Butonlar
    if cols[0].button("𝐁", key=f"b_{key}", help="Kalın"): q[key] = current_text + "<b></b>"
    if cols[1].button("𝐼", key=f"i_{key}", help="İtalik"): q[key] = current_text + "<i></i>"
    if cols[2].button("U̲", key=f"u_{key}", help="Altı Çizili"): q[key] = current_text + "<u></u>"
    if cols[3].button("x₂", key=f"sub_{key}", help="Alt Simge"): q[key] = current_text + "<sub></sub>"
    if cols[4].button("x²", key=f"sup_{key}", help="Üst Simge"): q[key] = current_text + "<sup></sup>"
    if cols[5].button("🎨", key=f"col_{key}", help="Kırmızı"): q[key] = current_text + "<span style='color:red'></span>"
    if cols[6].button("A+", key=f"sz_{key}", help="Büyük"): q[key] = current_text + "<span style='font-size:16px'></span>"
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 3. GÖRSEL ÇİZİM MOTORU
# ==========================================
def render_visual(code, high_quality=False):
    """Python kodunu çalıştırıp grafik çizer."""
    if not code or len(code.strip()) < 5: return
    try:
        plt.clf()
        dpi = 150 if high_quality else 80
        figsize = (5, 3) if high_quality else (3, 2)
        
        local_vars = {}
        exec_code = f"import matplotlib.pyplot as plt\nfig, ax = plt.subplots(figsize={figsize}, dpi={dpi})\n" + code
        exec(exec_code, {}, local_vars)
        
        if 'fig' in local_vars:
            st.pyplot(local_vars['fig'], use_container_width=False)
    except Exception as e:
        if not high_quality: st.error(f"Kod Hatası: {e}")

# ==========================================
# ARAYÜZ: YAN MENÜ (5. JSON & 8. LİSTE)
# ==========================================
with st.sidebar:
    st.title("🗂️ Soru Havuzu")
    
    # 5. JSON Yükleme
    uploaded_file = st.file_uploader("📂 JSON Yükle", type=['json'])
    if uploaded_file:
        try:
            st.session_state.questions = json.load(uploaded_file)
            st.success("Havuz yüklendi!")
        except: st.error("Hatalı dosya.")
    
    st.divider()
    
    # 8. Soruların Önizlemesi (Liste)
    st.markdown("**📋 Soru Listesi**")
    for i, q in enumerate(st.session_state.questions):
        label = f"{i+1}. {q.get('konu', 'Konusuz')[:15]}"
        if st.sidebar.button(label, key=f"nav_{i}", use_container_width=True):
            st.session_state.curr_idx = i
            st.rerun()
            
    st.divider()
    if st.sidebar.button("➕ Yeni Soru Ekle", type="primary", use_container_width=True):
        st.session_state.questions.append(DEFAULT_SORU.copy())
        st.session_state.curr_idx = len(st.session_state.questions) - 1
        st.rerun()
        
    # İndirme
    json_str = json.dumps(st.session_state.questions, indent=4, ensure_ascii=False)
    st.download_button("💾 Kaydet (JSON)", json_str, "sorular.json", "application/json")

# ==========================================
# ANA EKRAN (SEKMELER)
# ==========================================
q = get_current_q()
tab_edit, tab_prev = st.tabs(["✏️ Düzenleme Modu", "📄 Baskı Ön İzleme"])

# --- SEKME 1: EDİTÖR ---
with tab_edit:
    col_text, col_vis = st.columns([1.2, 0.8], gap="medium")
    
    with col_text:
        st.subheader("📝 Metin ve Seçenekler")
        c1, c2, c3 = st.columns(3)
        q['yazar'] = c1.text_input("Yazar", q.get('yazar',''))
        q['kazanim'] = c2.text_input("Kazanım", q.get('kazanim',''))
        q['konu'] = c3.text_input("Konu", q.get('konu',''))
        
        # 4. Düzenleme Barları Entegrasyonu
        st.caption("Üst Metin / Senaryo")
        render_toolbar('ustMetin')
        q['ustMetin'] = st.text_area("u_txt", q.get('ustMetin',''), height=80, label_visibility="collapsed", key="ta_ust")
        
        st.caption("Soru Kökü")
        render_toolbar('soruMetni')
        q['soruMetni'] = st.text_area("s_txt", q.get('soruMetni',''), height=100, label_visibility="collapsed", key="ta_kok")
        
        st.markdown("**Seçenekler**")
        sc1, sc2 = st.columns(2)
        q['secenekler']['A'] = sc1.text_input("A)", q['secenekler'].get('A',''))
        q['secenekler']['B'] = sc2.text_input("B)", q['secenekler'].get('B',''))
        q['secenekler']['C'] = sc1.text_input("C)", q['secenekler'].get('C',''))
        q['secenekler']['D'] = sc2.text_input("D)", q['secenekler'].get('D',''))
        q['dogruCevap'] = st.selectbox("Doğru Cevap", ["A","B","C","D"], index=["A","B","C","D"].index(q.get('dogruCevap','A')))
        
        # 7. Çözüm Alanı
        st.markdown("**Çözüm Açıklaması**")
        q['cozum'] = st.text_area("Çözüm", q.get('cozum',''), height=80)

    with col_vis:
        st.subheader("🖼️ Görsel Stüdyosu")
        
        # 3. & 6. Görsel Bölümü (Kod veya Upload)
        vis_type = st.radio("Görsel Tipi", ["🐍 Python Çizimi", "📤 Resim Yükle"], horizontal=True)
        
        if vis_type == "🐍 Python Çizimi":
            st.info("Matplotlib kodu yazın:")
            q['pythonKodu'] = st.text_area("kod", q.get('pythonKodu',''), height=200, label_visibility="collapsed")
            if q.get('pythonKodu'):
                st.caption("Canlı Ön İzleme:")
                render_visual(q['pythonKodu'], high_quality=False)
        else:
            # 6. Soruya Görsel Ekleme
            uploaded_img = st.file_uploader("Resim Seç", type=['png','jpg','jpeg'])
            if uploaded_img:
                st.image(uploaded_img, width=250)

# --- SEKME 2: 1. SORUNUN ÖN İZLEMESİ ---
with tab_prev:
    st.markdown('<div class="preview-paper">', unsafe_allow_html=True)
    
    # Başlık
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; border-bottom:2px solid #333; padding-bottom:10px; margin-bottom:20px;">
        <b>FEN BİLİMLERİ TESTİ</b>
        <i>{q.get('kazanim','')}</i>
    </div>
    """, unsafe_allow_html=True)
    
    # Üst Metin
    if q.get('ustMetin'):
        st.markdown(f"<div style='margin-bottom:15px;'>{q['ustMetin']}</div>", unsafe_allow_html=True)
    
    # Görsel Render (Ortalanmış)
    if vis_type == "🐍 Python Çizimi" and q.get('pythonKodu'):
        col_l, col_c, col_r = st.columns([1,3,1])
        with col_c: render_visual(q['pythonKodu'], high_quality=True)
    elif vis_type == "📤 Resim Yükle" and uploaded_img:
        col_l, col_c, col_r = st.columns([1,3,1])
        with col_c: st.image(uploaded_img, width=350)

    # Soru Kökü
    st.markdown(f"<div style='font-weight:bold; margin:20px 0; font-size:15px;'>{q.get('soruMetni','')}</div>", unsafe_allow_html=True)
    
    # Seçenekler
    for opt in ["A", "B", "C", "D"]:
        st.markdown(f"""
        <div class="option-box">
            <b>{opt})</b> {q['secenekler'].get(opt,'')}
        </div>
        """, unsafe_allow_html=True)
        
    # 7. Çözüm (Expandable)
    st.markdown("---")
    with st.expander("🔑 Cevap Anahtarı ve Çözüm"):
        st.success(f"Doğru Cevap: {q.get('dogruCevap')}")
        st.info(f"Çözüm: {q.get('cozum')}")
        
    st.markdown('</div>', unsafe_allow_html=True)
