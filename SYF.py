import streamlit as st
import json
import matplotlib.pyplot as plt
import io

# ==================================================
# 1. AYARLAR VE PROFESYONEL CSS (Hatasız Stil)
# ==================================================
st.set_page_config(
    page_title="SoruRota Ultimate",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Özel CSS: Word benzeri görünüm ve A4 kağıt efekti için
st.markdown("""
    <style>
    /* Genel Font Ayarları */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', 'Roboto', sans-serif;
        font-size: 14px;
    }
    
    /* Word Tarzı Araç Çubuğu */
    .word-toolbar {
        background-color: #f0f2f5;
        border: 1px solid #d1d5db;
        border-bottom: none;
        border-radius: 6px 6px 0 0;
        padding: 5px 10px;
        display: flex;
        gap: 5px;
        align-items: center;
    }
    
    /* Metin Kutusu (Toolbar ile birleşik görünüm) */
    .stTextArea textarea {
        border-top-left-radius: 0 !important;
        border-top-right-radius: 0 !important;
        border-color: #d1d5db !important;
        min-height: 100px;
    }
    
    /* Butonları Küçültme ve Özelleştirme */
    .stButton button {
        border: 1px solid transparent;
        background: transparent;
        color: #333;
        padding: 2px 8px !important;
        height: 28px !important;
        font-size: 14px !important;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #e4e6eb;
        border-radius: 4px;
    }
    
    /* Sınav Kağıdı (A4 Görünümü) */
    .exam-paper {
        background-color: white;
        width: 100%;
        max-width: 800px;
        min-height: 1000px;
        margin: 0 auto;
        padding: 50px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid #ddd;
        color: #000;
        line-height: 1.6;
    }
    </style>
""", unsafe_allow_html=True)

# ==================================================
# 2. VERİ YÖNETİMİ (Session State - Çökme Önleyici)
# ==================================================

# Varsayılan boş soru şablonu
DEFAULT_SORU = {
    "soruYazari": "",
    "kazanim": "",
    "konu": "Yeni Soru",
    "ustMetin": "",
    "soruMetni": "",
    "secenekler": {"A": "", "B": "", "C": "", "D": ""},
    "pythonKodu": "",
    "dogruCevap": "A"
}

# Session State Başlatma (Daha önce yoksa oluştur)
if 'questions' not in st.session_state:
    st.session_state.questions = [DEFAULT_SORU.copy()]

if 'curr_idx' not in st.session_state:
    st.session_state.curr_idx = 0

# Aktif soruyu güvenli şekilde getiren fonksiyon
def get_active_question():
    # Eğer indeks liste dışına çıkarsa sıfırla
    if st.session_state.curr_idx >= len(st.session_state.questions):
        st.session_state.curr_idx = 0
    return st.session_state.questions[st.session_state.curr_idx]

# ==================================================
# 3. YARDIMCI FONKSİYONLAR (Araç Çubuğu & Görsel)
# ==================================================

def render_toolbar(key_target):
    """
    Belirtilen metin alanı için HTML etiket butonlarını çizer.
    """
    st.markdown('<div class="word-toolbar">', unsafe_allow_html=True)
    
    # Butonlar yan yana (Columns kullanarak)
    # [Kalın, İtalik, Altı Çizili, Üstü Çizili, Alt Simge, Üst Simge, Renk, Temizle]
    cols = st.columns([1, 1, 1, 1, 1, 1, 1, 5])
    
    q = get_active_question()
    current_text = q.get(key_target, "")
    
    # Her butona basıldığında ilgili HTML etiketi metne eklenir
    if cols[0].button("𝐁", key=f"b_{key_target}", help="Kalın"): 
        q[key_target] = current_text + "<b></b>"
    if cols[1].button("𝐼", key=f"i_{key_target}", help="İtalik"): 
        q[key_target] = current_text + "<i></i>"
    if cols[2].button("U̲", key=f"u_{key_target}", help="Altı Çizili"): 
        q[key_target] = current_text + "<u></u>"
    if cols[3].button("<s>S</s>", key=f"s_{key_target}", help="Üstü Çizili"): 
        q[key_target] = current_text + "<s></s>"
    if cols[4].button("x₂", key=f"sub_{key_target}", help="Alt Simge"): 
        q[key_target] = current_text + "<sub></sub>"
    if cols[5].button("x²", key=f"sup_{key_target}", help="Üst Simge"): 
        q[key_target] = current_text + "<sup></sup>"
    if cols[6].button("🎨", key=f"col_{key_target}", help="Kırmızı Renk"): 
        q[key_target] = current_text + "<span style='color:red'></span>"

    st.markdown('</div>', unsafe_allow_html=True)

def render_chart(code_str, high_quality=False):
    """
    Python kodunu çalıştırıp grafiği çizer. Hata varsa kullanıcıyı uyarır ama çökmez.
    """
    if not code_str or len(code_str.strip()) < 5:
        return # Kod yoksa hiçbir şey yapma

    try:
        plt.clf() # Önceki grafiği temizle
        
        # Kalite Ayarı
        dpi = 200 if high_quality else 80
        figsize = (5, 3) if high_quality else (3, 2)
        
        # Kodu çalıştırma ortamı
        local_scope = {}
        exec_code = f"import matplotlib.pyplot as plt\nfig, ax = plt.subplots(figsize={figsize}, dpi={dpi})\n" + code_str
        exec(exec_code, {}, local_scope)
        
        if 'fig' in local_scope:
            st.pyplot(local_scope['fig'], use_container_width=False)
            
    except Exception as e:
        if not high_quality: # Sadece editör modunda hatayı göster
            st.error(f"Kod Hatası: {e}")

# ==================================================
# 4. YAN MENÜ (Dosya İşlemleri & Navigasyon)
# ==================================================
with st.sidebar:
    st.header("🗂️ Soru Havuzu")
    
    # Dosya Yükleme
    uploaded_file = st.file_uploader("JSON Yükle", type=['json'], label_visibility="collapsed")
    if uploaded_file:
        try:
            data = json.load(uploaded_file)
            if isinstance(data, list):
                st.session_state.questions = data
                st.success("Yüklendi!")
        except:
            st.error("Hatalı Dosya!")

    st.divider()
    
    # Soru Listesi
    st.subheader("Sorular")
    for i, ques in enumerate(st.session_state.questions):
        # Buton etiketi (Konu adı veya Soru X)
        lbl = f"{i+1}. {ques.get('konu', 'Konusuz')[:15]}"
        if st.sidebar.button(lbl, key=f"btn_nav_{i}", use_container_width=True):
            st.session_state.curr_idx = i
            st.rerun()

    st.divider()
    
    # Yeni Soru Ekleme
    if st.sidebar.button("➕ Yeni Soru Ekle", type="primary", use_container_width=True):
        st.session_state.questions.append(DEFAULT_SORU.copy())
        st.session_state.curr_idx = len(st.session_state.questions) - 1
        st.rerun()

    # İndirme Butonu
    json_data = json.dumps(st.session_state.questions, indent=4, ensure_ascii=False)
    st.download_button("💾 Havuzu İndir (JSON)", json_data, "sorular.json", "application/json", use_container_width=True)

# ==================================================
# 5. ANA EKRAN (Editör ve Ön İzleme)
# ==================================================

# Aktif soruyu al
q = get_active_question()

# İki Sekmeli Yapı
tab1, tab2 = st.tabs(["✏️ Editör (Düzenleme)", "📄 Sınav Kağıdı (Ön İzleme)"])

# --- SEKME 1: EDİTÖR ---
with tab1:
    col_text, col_vis = st.columns([1.2, 0.8], gap="medium")
    
    with col_text:
        st.subheader("Metin İçeriği")
        
        # Meta Veriler
        c1, c2, c3 = st.columns(3)
        q['soruYazari'] = c1.text_input("Yazar", q.get('soruYazari', ''))
        q['kazanim'] = c2.text_input("Kazanım", q.get('kazanim', ''))
        q['konu'] = c3.text_input("Konu", q.get('konu', ''))
        
        # Üst Metin (Toolbar'lı)
        st.caption("Üst Metin / Senaryo")
        render_toolbar('ustMetin')
        q['ustMetin'] = st.text_area("ust_gizli", q.get('ustMetin', ''), label_visibility="collapsed", key="ta_ust")
        
        # Soru Kökü (Toolbar'lı)
        st.caption("Soru Kökü")
        render_toolbar('soruMetni')
        q['soruMetni'] = st.text_area("kok_gizli", q.get('soruMetni', ''), label_visibility="collapsed", key="ta_kok")
        
        # Seçenekler
        st.subheader("Seçenekler")
        opts = st.columns(2)
        q['secenekler']['A'] = opts[0].text_input("A)", q['secenekler'].get('A', ''))
        q['secenekler']['B'] = opts[1].text_input("B)", q['secenekler'].get('B', ''))
        q['secenekler']['C'] = opts[0].text_input("C)", q['secenekler'].get('C', ''))
        q['secenekler']['D'] = opts[1].text_input("D)", q['secenekler'].get('D', ''))
        
        q['dogruCevap'] = st.selectbox("Doğru Cevap", ["A", "B", "C", "D"], index=["A","B","C","D"].index(q.get('dogruCevap', 'A')))

    with col_vis:
        st.subheader("Görsel Motoru")
        # Python Kodu Alanı
        st.info("Aşağıya Python (Matplotlib) kodu yazın:")
        q['pythonKodu'] = st.text_area("kod_alani", q.get('pythonKodu', ''), height=200, label_visibility="collapsed")
        
        # Canlı, küçük ön izleme
        if q.get('pythonKodu'):
            st.markdown("**Hızlı Ön İzleme:**")
            render_chart(q['pythonKodu'], high_quality=False)
        else:
            st.warning("Henüz kod yazılmadı.")

# --- SEKME 2: SINAV KAĞIDI (ÖN İZLEME) ---
with tab2:
    # A4 Kağıt Simülasyonu Başlangıcı
    st.markdown('<div class="exam-paper">', unsafe_allow_html=True)
    
    # 1. Başlık Bölümü
    st.markdown(f"""
    <div style="border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 20px; display: flex; justify-content: space-between;">
        <span style="font-weight: bold; font-size: 16px;">FEN BİLİMLERİ TESTİ</span>
        <span style="font-style: italic;">Kazanım: {q.get('kazanim', '---')}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. Üst Metin
    if q.get('ustMetin'):
        st.markdown(f"<div style='margin-bottom: 15px;'>{q['ustMetin']}</div>", unsafe_allow_html=True)
    
    # 3. Görsel (Varsa ve Kod Doğruysa)
    if q.get('pythonKodu'):
        # Görseli ortalamak için kolon hilesi
        c_left, c_img, c_right = st.columns([1, 3, 1])
        with c_img:
            render_chart(q['pythonKodu'], high_quality=True) # Yüksek Kalite Render
    
    # 4. Soru Kökü
    st.markdown(f"<div style='font-weight: bold; margin: 20px 0;'>{q.get('soruMetni', '')}</div>", unsafe_allow_html=True)
    
    # 5. Seçenekler (Alt alta diziliş)
    for opt in ["A", "B", "C", "D"]:
        val = q['secenekler'].get(opt, "")
        st.markdown(f"""
        <div style="margin-bottom: 8px;">
            <span style="font-weight: bold;">{opt})</span> {val}
        </div>
        """, unsafe_allow_html=True)
    
    # 6. Alt Bilgi (Cevap Anahtarı)
    st.markdown("<hr style='margin-top: 50px;'>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: right; color: #666; font-size: 12px;'>Soru Yazarı: {q.get('soruYazari', 'Anonim')} | Cevap: {q.get('dogruCevap')}</div>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True) # A4 Kapanış
