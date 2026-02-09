import streamlit as st
import json
import matplotlib.pyplot as plt
from PIL import Image
import io

# ==========================================
# 1. KONFİGÜRASYON VE CSS MİMARİSİ
# ==========================================
st.set_page_config(
    page_title="SoruRota Enterprise",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Profesyonel UI/UX CSS Enjeksiyonu
st.markdown("""
    <style>
    /* Global Tipografi - Segoe UI / Aptos benzeri modern fontlar */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', 'Roboto', Helvetica, Arial, sans-serif;
        font-size: 13px !important; 
        color: #2c3e50;
    }
    
    /* Word Stili Entegre Araç Çubuğu (Toolbar) */
    .toolbar-container {
        background-color: #f8f9fa;
        border: 1px solid #ced4da;
        border-bottom: none;
        border-radius: 6px 6px 0 0;
        padding: 4px 8px;
        display: flex;
        gap: 4px;
        align-items: center;
    }
    
    /* Metin Kutularının Toolbar ile Birleşimi */
    .stTextArea textarea {
        border-top-left-radius: 0 !important;
        border-top-right-radius: 0 !important;
        border-color: #ced4da !important;
        font-family: 'Consolas', 'Courier New', monospace !important; /* Kod yazımı hissi için */
        font-size: 12px !important;
    }
    
    /* Toolbar Butonları - Minimalist ve İkonik */
    .stButton > button {
        border: 1px solid transparent;
        background-color: transparent;
        color: #495057;
        padding: 2px 8px !important;
        height: 26px !important;
        font-size: 14px !important;
        border-radius: 4px;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background-color: #e9ecef;
        border: 1px solid #dee2e6;
        color: #000;
    }

    /* Sınav Kağıdı Ön İzleme Modülü (A4 Simülasyonu) */
    .exam-paper {
        background-color: #ffffff;
        width: 100%;
        max-width: 210mm; /* A4 Genişliği */
        min-height: 297mm;
        margin: 0 auto;
        padding: 40px;
        border: 1px solid #dcdcdc;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        font-family: 'Times New Roman', Times, serif; /* Akademik Baskı Fontu */
    }
    
    /* Sidebar Düzeni */
    section[data-testid="stSidebar"] {
        background-color: #f1f3f5;
        border-right: 1px solid #dee2e6;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. STATE MANAGEMENT (DURUM YÖNETİMİ)
# ==========================================
# Varsayılan soru şablonu
DEFAULT_QUESTION = {
    "soruYazari": "",
    "kazanim": "",
    "konu": "Yeni Soru",
    "ustMetin": "",
    "soruMetni": "",
    "secenekler": {"A": "", "B": "", "C": "", "D": ""},
    "pythonKodu": "",
    "dogruCevap": "A"
}

if 'questions' not in st.session_state:
    st.session_state.questions = [DEFAULT_QUESTION.copy()]

if 'current_idx' not in st.session_state:
    st.session_state.current_idx = 0

# Aktif soruya güvenli erişim
def get_current_question():
    if st.session_state.current_idx >= len(st.session_state.questions):
        st.session_state.current_idx = 0
    return st.session_state.questions[st.session_state.current_idx]

# ==========================================
# 3. YARDIMCI FONKSİYONLAR (UTIL)
# ==========================================
def render_toolbar(key_target):
    """Metin kutuları için sembolik araç çubuğu oluşturur."""
    st.markdown(f'<div class="toolbar-container">', unsafe_allow_html=True)
    
    # Grid Layout: Semboller için sıkışık sütunlar
    # [Bold, Italic, Underline, Strike, Sub, Super, Size, Color]
    cols = st.columns([0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.1, 0.1, 0.32])
    
    q = get_current_question()
    
    # Callback fonksiyonları kullanılmadığı için state'i manuel güncelliyoruz
    if cols[0].button("𝐁", key=f"b_{key_target}", help="Kalın"): 
        q[key_target] = q.get(key_target, "") + "<b></b>"
    if cols[1].button("𝐼", key=f"i_{key_target}", help="İtalik"): 
        q[key_target] = q.get(key_target, "") + "<i></i>"
    if cols[2].button("𝚄", key=f"u_{key_target}", help="Altı Çizili"): 
        q[key_target] = q.get(key_target, "") + "<u></u>"
    if cols[3].button("<s>S</s>", key=f"s_{key_target}", help="Üstü Çizili"): 
        q[key_target] = q.get(key_target, "") + "<s></s>"
    if cols[4].button("x₂", key=f"sub_{key_target}", help="Alt Simge"): 
        q[key_target] = q.get(key_target, "") + "<sub></sub>"
    if cols[5].button("x²", key=f"sup_{key_target}", help="Üst Simge"): 
        q[key_target] = q.get(key_target, "") + "<sup></sup>"
    if cols[6].button("A⁺", key=f"sz_{key_target}", help="Yazı Büyüt"): 
        q[key_target] = q.get(key_target, "") + "<span style='font-size:16px'></span>"
    if cols[7].button("🎨", key=f"cl_{key_target}", help="Renk"): 
        q[key_target] = q.get(key_target, "") + "<span style='color:#e74c3c'></span>"
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_visual_engine(code, context="editor"):
    """
    Python kodunu çalıştırıp matplotlib figürünü render eder.
    Context: 'editor' (küçük önizleme) veya 'paper' (yüksek kalite baskı)
    """
    if not code or len(code.strip()) < 5:
        return

    try:
        # Belleği temizle
        plt.clf()
        plt.close('all')
        
        # Context'e göre ayarlar
        if context == "editor":
            figsize = (3, 2)
            dpi = 100
        else:
            figsize = (5, 3.5) # Kitapçık standardı
            dpi = 200          # Baskı kalitesi
            
        # Kullanıcı kodunun çalışacağı güvenli alan
        local_vars = {}
        exec_code = f"import matplotlib.pyplot as plt\nfig, ax = plt.subplots(figsize={figsize}, dpi={dpi})\n" + code
        exec(exec_code, {}, local_vars)
        
        # Figürü al ve göster
        if 'fig' in local_vars:
            st.pyplot(local_vars['fig'], use_container_width=False)
            
    except Exception as e:
        if context == "editor":
            st.error(f"Render Hatası: {str(e)}")

# ==========================================
# 4. SIDEBAR (NAVİGASYON VE IO)
# ==========================================
with st.sidebar:
    st.markdown("### 🗂️ Proje Yönetimi")
    
    # JSON Import
    uploaded_file = st.file_uploader("Veri Havuzu Yükle (.json)", type=['json'], label_visibility="collapsed")
    if uploaded_file:
        try:
            st.session_state.questions = json.load(uploaded_file)
            st.success("Havuz güncellendi.")
        except:
            st.error("JSON formatı hatalı.")
            
    st.divider()
    
    # Soru Navigasyonu
    st.markdown("### 📋 Soru Listesi")
    for i, q in enumerate(st.session_state.questions):
        # Konu başlığı yoksa 'Soru X' yaz
        btn_label = f"{i+1}. {q.get('konu', 'İsimsiz')[:16]}"
        if st.sidebar.button(btn_label, key=f"nav_{i}", use_container_width=True):
            st.session_state.current_idx = i
            st.rerun()
            
    # Yeni Soru Ekleme Butonu
    st.markdown("---")
    if st.sidebar.button("➕ Yeni Soru Oluştur", type="primary", use_container_width=True):
        st.session_state.questions.append(DEFAULT_QUESTION.copy())
        st.session_state.current_idx = len(st.session_state.questions) - 1
        st.rerun()

    # JSON Export
    st.markdown("---")
    json_str = json.dumps(st.session_state.questions, indent=4, ensure_ascii=False)
    st.download_button(
        label="💾 Projeyi Kaydet (JSON)",
        data=json_str,
        file_name="soru_havuzu.json",
        mime="application/json",
        use_container_width=True
    )

# ==========================================
# 5. ANA EKRAN (WORKBENCH)
# ==========================================
q = get_current_question()

# Sekme Yapısı
tab_editor, tab_preview = st.tabs(["✏️ Editör ve Tasarım", "📄 Baskı Ön İzleme (A4)"])

# --- TAB 1: EDİTÖR ---
with tab_editor:
    col_left, col_right = st.columns([1.2, 0.8], gap="medium")
    
    with col_left:
        st.markdown("#### Soru İçeriği")
        
        # Meta Veriler (Tek Satırda Kompakt)
        c1, c2, c3 = st.columns(3)
        q['soruYazari'] = c1.text_input("Yazar", q.get('soruYazari', ''), placeholder="Ad Soyad")
        q['kazanim'] = c2.text_input("Kazanım Kodu", q.get('kazanim', ''), placeholder="6.1.1.1")
        q['konu'] = c3.text_input("Konu Başlığı", q.get('konu', ''), placeholder="Hücre")
        
        # Rich Text Editörleri (Toolbar Entegreli)
        st.caption("Üst Metin / Senaryo")
        render_toolbar('ustMetin')
        q['ustMetin'] = st.text_area("ust_gizli", q.get('ustMetin', ''), height=80, label_visibility="collapsed", key="ta_ust")
        
        st.caption("Soru Kökü")
        render_toolbar('soruMetni')
        q['soruMetni'] = st.text_area("kok_gizli", q.get('soruMetni', ''), height=100, label_visibility="collapsed", key="ta_kok")
        
        # Seçenekler (Grid Yapısı)
        st.caption("Seçenekler ve Doğru Cevap")
        opt_cols = st.columns([1, 1, 1, 1, 1])
        for idx, opt in enumerate(["A", "B", "C", "D"]):
            q['secenekler'][opt] = opt_cols[idx].text_input(f"{opt})", q['secenekler'].get(opt, ""), key=f"opt_{opt}")
        
        q['dogruCevap'] = opt_cols[4].selectbox("Cevap", ["A", "B", "C", "D"], index=["A","B","C","D"].index(q.get('dogruCevap', 'A')))

    with col_right:
        st.markdown("#### Görsel Motoru")
        
        # Görsel Modu Seçimi
        vis_mode = st.radio("Görsel Kaynağı", ["Python Çizimi", "Dosya Yükle"], horizontal=True, label_visibility="collapsed")
        
        if vis_mode == "Python Çizimi":
            st.caption("Matplotlib Kodu (Otomatik Render)")
            q['pythonKodu'] = st.text_area("kod_gizli", q.get('pythonKodu', ''), height=200, label_visibility="collapsed", placeholder="ax.plot([1,2], [3,4])")
            
            # Canlı Küçük Ön İzleme
            if q.get('pythonKodu'):
                st.markdown("**Editör Ön İzlemesi:**")
                render_visual_engine(q['pythonKodu'], context="editor")
                
        else:
            st.caption("Görsel Yükle (PNG/JPG)")
            uploaded_img = st.file_uploader("img_up", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
            if uploaded_img:
                image = Image.open(uploaded_img)
                st.image(image, width=200, caption="Yüklenen Görsel")
                # Not: Gerçek uygulamada bu görseli base64'e çevirip JSON'a gömmek gerekir.

# --- TAB 2: BASKI ÖN İZLEME (EXAM PAPER) ---
with tab_preview:
    # A4 Kağıt Simülasyonu
    st.markdown("""<div class="exam-paper">""", unsafe_allow_html=True)
    
    # Header
    st.markdown(f"""
        <div style="display:flex; justify-content:space-between; border-bottom:2px solid #000; padding-bottom:10px; margin-bottom:20px;">
            <div><b>FEN BİLİMLERİ DERSİ</b></div>
            <div><i>Kazanım: {q.get('kazanim', 'Belirtilmedi')}</i></div>
            <div>Yazar: {q.get('soruYazari', 'Anonim')}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Soru Gövdesi
    if q.get('ustMetin'):
        st.markdown(f"<div style='margin-bottom:15px; text-align:justify;'>{q['ustMetin']}</div>", unsafe_allow_html=True)
    
    # Görsel Render Alanı (Ortalanmış ve Kaliteli)
    if vis_mode == "Python Çizimi" and q.get('pythonKodu'):
        col_spacer1, col_img, col_spacer2 = st.columns([1, 2, 1])
        with col_img:
            render_visual_engine(q['pythonKodu'], context="paper")
    elif vis_mode == "Dosya Yükle" and uploaded_img:
        col_spacer1, col_img, col_spacer2 = st.columns([1, 2, 1])
        with col_img:
            st.image(uploaded_img, width=300)

    # Soru Kökü
    st.markdown(f"<div style='margin: 20px 0; font-weight:600;'>{q.get('soruMetni', '')}</div>", unsafe_allow_html=True)
    
    # Seçenekler (Dikey Liste)
    for opt in ["A", "B", "C", "D"]:
        content = q['secenekler'].get(opt, "")
        st.markdown(f"""
            <div style='margin-bottom:8px; display:flex;'>
                <div style='font-weight:bold; width:25px;'>{opt})</div>
                <div>{content}</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Footer (Cevap Anahtarı - Gizlenebilir)
    st.markdown("---")
    st.markdown(f"<div style='text-align:right; font-size:10px; color:#999;'>Doğru Cevap: {q.get('dogruCevap')}</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
