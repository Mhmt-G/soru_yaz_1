import streamlit as st
import json
import matplotlib.pyplot as plt

# Sayfa Yapılandırması
st.set_page_config(page_title="SoruRota Pro", layout="wide")

st.title("🧪 Fen Bilimleri Soru Geliştirme Merkezi")

# 1. Veri Yapısı
if 'questions' not in st.session_state:
    st.session_state.questions = [{
        "soruYazari": "", "kazanim": "6.X.X.X", "konu": "Yeni Konu",
        "ustMetin": "", "soruMetni": "Soru kökü...", 
        "secenekler": {"A": "", "B": "", "C": "", "D": ""},
        "pythonKodu": "import matplotlib.pyplot as plt\nfig, ax = plt.subplots()\nax.plot([1, 2, 3], [4, 5, 6])\nst.pyplot(fig)",
        "htmlKodu": "", "dogruCevap": "A", "cozum": ""
    }]

# 2. Yan Menü: Dosya Yükleme ve Liste
st.sidebar.header("📁 Veri Yönetimi")
uploaded_file = st.sidebar.file_uploader("JSON Yükle", type=['json'])
if uploaded_file:
    st.session_state.questions = json.load(uploaded_file)

st.sidebar.header("📋 Soru Havuzu")
for i, q in enumerate(st.session_state.questions):
    if st.sidebar.button(f"{i+1}. {q.get('konu', 'Adsız')[:15]}", key=f"q_{i}"):
        st.session_state.current_index = i

idx = st.session_state.get('current_index', 0)
q = st.session_state.questions[idx]

# --- GÖRSEL OLUŞTURMA FONKSİYONU ---
def render_visual(code):
    if code:
        try:
            # Temiz bir figür oluştur
            plt.clf() 
            # Kodu çalıştır
            exec(code, globals(), locals())
            # Eğer kod içinde st.pyplot kullanılmadıysa biz zorlayalım
            if "plt.show()" in code or "plt.plot" in code:
                st.pyplot(plt.gcf())
        except Exception as e:
            st.error(f"Görsel oluşturma hatası: {e}")

# 3. Sekmeler
tab1, tab2 = st.tabs(["📝 Düzenle", "🔍 Ön İzleme"])

with tab1:
    col1, col2 = st.columns([1, 1])
    with col1:
        q['soruMetni'] = st.text_area("Soru Kökü", q.get('soruMetni', ''), height=150)
        q['pythonKodu'] = st.text_area("Python Çizim Kodu", q.get('pythonKodu', ''), height=200)
    with col2:
        st.info("🖼️ Canlı Görsel:")
        render_visual(q.get('pythonKodu'))

with tab2:
    st.markdown(f"### {q.get('soruMetni', '')}", unsafe_allow_html=True)
    render_visual(q.get('pythonKodu')) # Ön izlemede de göster
    for k, v in q.get('secenekler', {}).items():
        st.write(f"**{k})** {v}")
