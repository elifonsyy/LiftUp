# Simülasyon Sekmesi - 3 Grafik Yan Yana Tasarımı

## 📋 Genel Bakış

Simülasyon sekmesinde üç farklı grafiğin aynı anda yan yana gösterilmesi için yeniden tasarım planı.

## 🎯 Hedefler

1. **"Gelme Açısı" histogramını kaldır** - Zaten "Gelen Açı" var, tekrar
2. **3 grafik aynı anda göster** - Fotodaki gibi yan yana düzenleme
3. **Alt sekme butonlarını kaldır** - Artık gerek yok
4. **Log/konsol alanı ekle** - Alt kısımda interaktif log

## 📐 Mevcut Yapı Analizi

### Şu Anki Durum
```
┌─────────────────────────────────────────┐
│ Toolbar (Başlat/Durdur/Progress)       │
├─────────────────────────────────────────┤
│                                         │
│         TEK GRAFİK ALANI               │
│         (Seçilen grafiği gösterir)     │
│                                         │
├─────────────────────────────────────────┤
│ Sekme Çubuğu: Üçgen Işın | Histogram   │
├─────────────────────────────────────────┤
│ Alt Seçenekler: [Işın Yolu] [Isı] ...  │
└─────────────────────────────────────────┘
```

### Hedef Durum (Fotodaki Gibi)
```
┌─────────────────────────────────────────────────────────────┐
│ Toolbar (Başlat/Durdur/Progress)                           │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │ Grafik 1 │  │ Grafik 2 │  │ Grafik 3 │                 │
│  │ Işın     │  │ Histogram│  │ CPU/RAM  │                 │
│  │ Grafikleri│  │          │  │ Grafik   │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
├─────────────────────────────────────────────────────────────┤
│ Sekme Çubuğu: [Işın Grafikleri] [Histogram] [Log]         │
├─────────────────────────────────────────────────────────────┤
│ Log/Konsol Alanı (Simülasyon çıktıları)                   │
│ > [MESH] Lift_Up_Model.unv okunuyor...                     │
│ > 240 üçgen yüklendi.                                      │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Değişiklikler

### 1. Histogram Seçeneklerini Güncelle

**Dosya:** [`test.py`](test.py:1084)

**Mevcut:**
```python
"Histogram": [
    ("📊", "Gelme Açısı"),      # ❌ KALDIRILACAK
    ("📈", "Sekme Dağılımı"),
    ("🎯", "Gelen Açı"),
    ("🔄", "Seken Açı")
]
```

**Yeni:**
```python
"Histogram": [
    ("📈", "Sekme Dağılımı"),
    ("🎯", "Gelen Açı"),
    ("🔄", "Seken Açı")
]
```

**Neden:** "Gelme Açısı" ve "Gelen Açı" aynı şeyi gösteriyor, tekrar var.

---

### 2. Simülasyon Sayfası Layout'u

**Dosya:** [`test.py`](test.py:541)

**Mevcut Yapı:**
```python
def _build_page_simulasyon(self):
    page.rowconfigure(0, weight=0)  # Toolbar
    page.rowconfigure(1, weight=1)  # Grafik alanı (TEK)
    page.rowconfigure(2, weight=0)  # Alt sekme çubuğu
    page.rowconfigure(3, weight=0)  # Alt seçenek butonları
```

**Yeni Yapı:**
```python
def _build_page_simulasyon(self):
    page.rowconfigure(0, weight=0)  # Toolbar
    page.rowconfigure(1, weight=1)  # 3 Grafik alanı (YAN YANA)
    page.rowconfigure(2, weight=0)  # Sekme çubuğu (opsiyonel)
    page.rowconfigure(3, weight=0)  # Log/Konsol alanı
    
    # 3 grafik için column yapılandırması
    page.columnconfigure(0, weight=1, uniform="graph")
    page.columnconfigure(1, weight=1, uniform="graph")
    page.columnconfigure(2, weight=1, uniform="graph")
```

---

### 3. Her Sekme İçin Varsayılan 3 Grafik

#### Seçenek 1: Sabit Grafik Kombinasyonları

| Sekme | Grafik 1 | Grafik 2 | Grafik 3 |
|-------|----------|----------|----------|
| **Üçgen Işın** | Işın Yolu | Isı Haritası | Işın İzi |
| **Histogram** | Sekme Dağılımı | Gelen Açı | Seken Açı |
| **CPU/RAM** | CPU Kullanımı | RAM Kullanımı | Özet İstatistikler |

#### Seçenek 2: Karma Kombinasyon (ÖNERİLEN)

| Sekme | Grafik 1 | Grafik 2 | Grafik 3 |
|-------|----------|----------|----------|
| **Genel Görünüm** | Işın Yolu | Gelen Açı Histogram | CPU Kullanımı |
| **Detaylı Analiz** | Isı Haritası | Sekme Dağılımı | RAM Kullanımı |
| **İleri Seviye** | Işın İzi | Seken Açı | Özet Tablo |

**Tercih:** Seçenek 1 daha basit ve anlaşılır.

---

### 4. Grafik Render Fonksiyonu

**Dosya:** [`test.py`](test.py:1148)

**Mevcut:** `_render_simulation_graph()` - Tek grafik oluşturur

**Yeni:** `_render_three_graphs()` - 3 grafiği aynı anda oluşturur

```python
def _render_three_graphs(self):
    """3 grafiği aynı anda oluştur ve göster"""
    if self._sim_data is None:
        return
    
    tab = self._current_sim_tab.get()
    
    # Sekmeye göre 3 grafik belirle
    graph_configs = {
        "Üçgen Işın": [
            ("ray_path", "Işın Yolu"),
            ("heatmap", "Isı Haritası"),
            ("ray_trace", "Işın İzi")
        ],
        "Histogram": [
            ("bounce", "Sekme Dağılımı"),
            ("incoming", "Gelen Açı"),
            ("reflection", "Seken Açı")
        ],
        "CPU/RAM": [
            ("cpu", "CPU Kullanımı"),
            ("ram", "RAM Kullanımı"),
            ("summary", "Özet")
        ]
    }
    
    # 3 grafiği paralel oluştur (thread pool)
    # Her grafik için ayrı canvas ve frame
```

---

### 5. Alt Sekme Butonlarını Kaldır

**Dosya:** [`test.py`](test.py:616-628)

**Kaldırılacak:**
```python
# ─── Alt Seçenek Butonları Alanı ───
self._sub_option_area = ctk.CTkFrame(...)
self._sub_option_container = ctk.CTkFrame(...)
self._build_sub_options("Üçgen Işın")
```

**Neden:** Artık alt seçenek yok, 3 grafik hep gösteriliyor.

---

### 6. Log/Konsol Alanı Ekle

**Yeni Bileşen:**
```python
# ─── Log/Konsol Alanı ───
log_frame = ctk.CTkFrame(page, fg_color=C["panel3"], 
                         corner_radius=0, height=200)
log_frame.grid(row=3, column=0, columnspan=3, sticky="ew")

# Scrollable text widget
self._log_text = ctk.CTkTextbox(
    log_frame, 
    fg_color=C["bg"],
    text_color=C["text"],
    font=ctk.CTkFont(family=FONT_MONO, size=10),
    height=180
)
self._log_text.pack(fill="both", expand=True, padx=8, pady=8)
```

**Özellikler:**
- Simülasyon çıktılarını gösterir
- Otomatik scroll (en son satır görünür)
- Temizle butonu
- Kaydet butonu (log'u dosyaya kaydet)

---

## 🎨 UI Bileşenleri

### Canvas Yapısı

```python
# Her grafik için ayrı canvas
self._sim_canvas_1 = None  # Sol grafik
self._sim_canvas_2 = None  # Orta grafik
self._sim_canvas_3 = None  # Sağ grafik

self._sim_fig_1 = None
self._sim_fig_2 = None
self._sim_fig_3 = None

# Her grafik için ayrı frame
self._graph_frame_1 = None
self._graph_frame_2 = None
self._graph_frame_3 = None
```

### Toolbar Yapısı

Her grafiğin altında mini toolbar (opsiyonel):
- 🔍 Zoom
- 💾 Kaydet
- 🔄 Yenile

---

## 📊 Performans Optimizasyonu

### 1. Paralel Grafik Oluşturma

```python
from concurrent.futures import ThreadPoolExecutor

def _create_graphs_parallel(self):
    with ThreadPoolExecutor(max_workers=3) as executor:
        future1 = executor.submit(create_graph_1, data)
        future2 = executor.submit(create_graph_2, data)
        future3 = executor.submit(create_graph_3, data)
        
        fig1 = future1.result()
        fig2 = future2.result()
        fig3 = future3.result()
```

### 2. Cache Stratejisi

```python
# Her sekme için 3 grafiği cache'le
self._graph_cache = {
    "Üçgen Işın": [fig1, fig2, fig3],
    "Histogram": [fig1, fig2, fig3],
    "CPU/RAM": [fig1, fig2, fig3]
}
```

### 3. DPI Optimizasyonu

```python
# 3 grafik yan yana olduğu için DPI'ı düşür
fig = plt.Figure(figsize=(6, 5), dpi=70)  # 80'den 70'e
```

---

## 🔄 Değişiklik Akışı

### Adım 1: Histogram Seçeneklerini Güncelle
- `test.py` satır 1084-1089
- "Gelme Açısı" seçeneğini kaldır

### Adım 2: Layout'u Yeniden Tasarla
- `_build_page_simulasyon()` fonksiyonunu güncelle
- 3 grafik frame'i oluştur
- Alt seçenek alanını kaldır

### Adım 3: Grafik Render Fonksiyonunu Güncelle
- `_render_simulation_graph()` → `_render_three_graphs()`
- 3 grafiği aynı anda oluştur
- Her grafiği kendi frame'ine embed et

### Adım 4: Log Alanını Ekle
- Yeni `_log_text` widget'ı ekle
- `print()` çağrılarını log'a yönlendir
- Temizle ve kaydet butonları ekle

### Adım 5: Gereksiz Fonksiyonları Temizle
- `_build_sub_options()` - Kaldır
- `_on_sim_sub_option_change()` - Kaldır
- İlgili değişkenleri temizle

---

## 🧪 Test Senaryoları

### Test 1: Grafik Yükleme
- [ ] 3 grafik aynı anda yükleniyor mu?
- [ ] Grafik boyutları eşit mi?
- [ ] Toolbar'lar çalışıyor mu?

### Test 2: Sekme Değiştirme
- [ ] Sekme değişince 3 grafik güncelleniyor mu?
- [ ] Cache çalışıyor mu?
- [ ] Performans kabul edilebilir mi?

### Test 3: Log Alanı
- [ ] Simülasyon çıktıları görünüyor mu?
- [ ] Otomatik scroll çalışıyor mu?
- [ ] Temizle butonu çalışıyor mu?

### Test 4: Performans
- [ ] 3 grafik oluşturma süresi < 3 saniye
- [ ] RAM kullanımı < 500 MB artış
- [ ] UI donmuyor

---

## 📝 Kod Değişiklik Özeti

### Değiştirilecek Dosyalar

1. **[`test.py`](test.py)**
   - `_build_page_simulasyon()` - Layout değişikliği
   - `_render_simulation_graph()` → `_render_three_graphs()`
   - `_build_sub_options()` - Kaldır
   - `_on_sim_sub_option_change()` - Kaldır
   - Yeni: `_add_log_message()` - Log mesajı ekle
   - Yeni: `_clear_log()` - Log'u temizle

2. **[`simulation_core.py`](simulation_core.py)**
   - Değişiklik yok (grafik fonksiyonları zaten var)

### Yeni Değişkenler

```python
# Canvas'lar
self._sim_canvas_1 = None
self._sim_canvas_2 = None
self._sim_canvas_3 = None

# Figure'lar
self._sim_fig_1 = None
self._sim_fig_2 = None
self._sim_fig_3 = None

# Frame'ler
self._graph_frame_1 = None
self._graph_frame_2 = None
self._graph_frame_3 = None

# Log
self._log_text = None
```

### Kaldırılacak Değişkenler

```python
# Artık gerek yok
self._current_sub_option = tk.StringVar(value="Işın Yolu")  # ❌
self._sim_sub_option_btns = {}  # ❌
self._sub_option_area = None  # ❌
self._sub_option_container = None  # ❌
```

---

## 🎯 Sonuç

Bu plan ile:
- ✅ "Gelme Açısı" tekrarı kaldırılacak
- ✅ 3 grafik aynı anda gösterilecek
- ✅ Alt sekme butonları kaldırılacak
- ✅ Log/konsol alanı eklenecek
- ✅ Performans optimize edilecek

**Tahmini Değişiklik:** ~200 satır kod değişikliği

**Zorluk:** Orta seviye

**Süre:** Yaklaşık implementasyon süresi (kullanıcı tarafından belirlenecek)
