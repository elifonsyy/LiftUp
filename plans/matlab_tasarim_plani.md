# MATLAB Tarzı Tasarım Uygulama Planı

## 📸 Fotoğraf Analizi

### Fotoğraf 1 - Result Navigator (Üst Panel)
**Gözlemlenen Özellikler:**
- **Başlık:** "Result Navigator" - açık gri arka plan
- **Parametreler:** 
  - Katman: 1 (input kutusu)
  - Özellik: d (mm) (dropdown)
  - Min: 1, Max: 5, Adım: 0.5
- **Büyük Sarı Buton:** "PARAMETRİK TARA" - turuncu/sarı (#F5A623 benzeri)
- **Liste Görünümü:** 
  - Beyaz arka plan
  - Seçili satır: açık mavi (#B3D9FF benzeri)
  - Satırlar: [1B] Theta = 46.0°, 47.0°, 48.0°... formatında
  - Scrollbar: sağda, ince gri
- **Alt Buton:** "TEMİZLE" - gri (#E0E0E0)

### Fotoğraf 2 - Analiz Ekranı (Alt Panel)
**Gözlemlenen Özellikler:**
- **Başlık:** "Analiz Ekranı" - açık gri arka plan
- **Grafik Sekmesi:**
  - Büyük grafik alanı (RADOME | TE | N=1 | A (dB) Isı Haritası)
  - Renkli ısı haritası (mavi-yeşil-sarı-kırmızı gradyan)
- **Sağ Panel - Result Navigator:**
  - Katman, Min, Max göstergeleri
  - Sarı buton (parametrik tara)
  - Liste görünümü
- **Alt Panel - Sonuçlar/Dışa Aktarma:**
  - Metrik değerler: RL (dB), IL (dB), A (Soğurma dB)
  - Tasarım Türü: RADOME
  - Dropdown'lar: Sayısal Format, Grafik Türü, 2B Isıhartası
  - **Butonlar:**
    - SIFIRLA (kırmızı, #E74C3C)
    - ANALİZ ET (mavi, #4A90E2)
    - NOKTA ANALİZİ (açık mavi, #5DADE2)
- **Hazır Mesajı:** "[16:39:39] RADOME analizi tamamlandı."

### Fotoğraf 3 - Tablo Görünümü
**Gözlemlenen Özellikler:**
- **Tablo Başlıkları:** f (GHz), theta (deg), R, T, A (dB), RL (dB), IL (dB), S11_Re
- **Satır Renkleri:**
  - Seçili satırlar: açık mavi (#B3D9FF)
  - Normal satırlar: beyaz
  - Alternatif satırlar: çok açık gri (#F9F9F9)
- **Hücre Kenarlıkları:** İnce gri çizgiler
- **Font:** Düzenli, okunabilir (Arial/Segoe UI benzeri)
- **Sayılar:** Sağa hizalı, 4 ondalık basamak

---

## 🎨 MATLAB Renk Şeması

```python
MATLAB_COLORS = {
    # Ana Renkler
    "bg_main":           "#F0F0F0",  # Ana arka plan (açık gri)
    "bg_panel":          "#FFFFFF",  # Panel arka planı (beyaz)
    "bg_header":         "#E8E8E8",  # Başlık arka planı
    "bg_input":          "#FFFFFF",  # Input arka planı
    
    # Buton Renkleri
    "btn_primary":       "#F5A623",  # Sarı/Turuncu (PARAMETRİK TARA)
    "btn_primary_hover": "#E09612",
    "btn_success":       "#4A90E2",  # Mavi (ANALİZ ET)
    "btn_success_hover": "#3A7BC8",
    "btn_info":          "#5DADE2",  # Açık Mavi (NOKTA ANALİZİ)
    "btn_info_hover":    "#4A9DD2",
    "btn_danger":        "#E74C3C",  # Kırmızı (SIFIRLA)
    "btn_danger_hover":  "#D62C1A",
    "btn_default":       "#E0E0E0",  # Gri (TEMİZLE)
    "btn_default_hover": "#D0D0D0",
    
    # Tablo Renkleri
    "table_header":      "#F5F5F5",  # Tablo başlık
    "table_row_even":    "#FFFFFF",  # Çift satırlar
    "table_row_odd":     "#F9F9F9",  # Tek satırlar
    "table_selected":    "#B3D9FF",  # Seçili satır
    "table_border":      "#D0D0D0",  # Tablo kenarlıkları
    
    # Metin Renkleri
    "text_primary":      "#333333",  # Ana metin
    "text_secondary":    "#666666",  # İkincil metin
    "text_disabled":     "#999999",  # Devre dışı metin
    "text_white":        "#FFFFFF",  # Beyaz metin (butonlarda)
    
    # Kenarlık ve Çizgiler
    "border_light":      "#D0D0D0",  # Açık kenarlık
    "border_medium":     "#B0B0B0",  # Orta kenarlık
    "border_dark":       "#808080",  # Koyu kenarlık
    
    # Vurgu Renkleri
    "accent_blue":       "#4A90E2",  # Mavi vurgu
    "accent_orange":     "#F5A623",  # Turuncu vurgu
    "accent_green":      "#2ECC71",  # Yeşil (başarı)
    "accent_red":        "#E74C3C",  # Kırmızı (hata)
}
```

---

## 🏗️ Tasarım Değişiklikleri

### 1. Genel Görünüm
**Mevcut:** Koyu tema (dark mode)
**Yeni:** Açık tema (light mode) - MATLAB tarzı

**Değişiklikler:**
- Appearance mode: `"dark"` → `"light"`
- Ana arka plan: `#080C12` → `#F0F0F0`
- Panel arka planı: `#0E1420` → `#FFFFFF`
- Metin rengi: `#D0DCF0` → `#333333`

### 2. Üst Header (Başlık Çubuğu)
**Mevcut:** Koyu, modern, gradient efektli
**Yeni:** Açık gri, düz, MATLAB tarzı

**Değişiklikler:**
- Arka plan: `#060A10` → `#E8E8E8`
- Logo rengi: Mavi → Turuncu (#F5A623)
- Metin rengi: Açık → Koyu
- Kenarlık: İnce gri çizgi (#D0D0D0)

### 3. Navigasyon Çubuğu
**Mevcut:** Koyu, transparan butonlar
**Yeni:** Açık gri, belirgin butonlar

**Değişiklikler:**
- Arka plan: `#060A10` → `#E8E8E8`
- Aktif sekme: Koyu mavi → Açık mavi (#B3D9FF)
- Hover efekti: Hafif gri (#F0F0F0)
- Kenarlık: Alt kısımda ince çizgi

### 4. Butonlar
**Mevcut:** Yuvarlak köşeli, koyu renkli
**Yeni:** Az yuvarlak köşeli, MATLAB renkleri

**Değişiklikler:**
- Corner radius: `8px` → `4px`
- Birincil buton (Simülasyon Başlat): Yeşil → Turuncu (#F5A623)
- İkincil butonlar: Koyu → Açık gri (#E0E0E0)
- Tehlike butonu (Durdur): Koyu kırmızı → Parlak kırmızı (#E74C3C)
- Font weight: Bold → Normal

### 5. Input Alanları
**Mevcut:** Koyu arka plan, yuvarlak köşeler
**Yeni:** Beyaz arka plan, ince kenarlık

**Değişiklikler:**
- Arka plan: `#1A2233` → `#FFFFFF`
- Kenarlık: `#243352` → `#D0D0D0`
- Corner radius: `6px` → `3px`
- Metin rengi: Açık → Koyu
- Focus border: Mavi (#4A90E2)

### 6. Kartlar (Cards)
**Mevcut:** Koyu panel, yuvarlak köşeler
**Yeni:** Beyaz panel, ince kenarlık

**Değişiklikler:**
- Arka plan: `#0E1420` → `#FFFFFF`
- Kenarlık: `#1E2D45` → `#D0D0D0`
- Corner radius: `10px` → `4px`
- Gölge: Yok → Hafif gölge (optional)

### 7. Tablo Görünümü (Yeni Özellik)
**Eklenecek:** MATLAB tarzı tablo görünümü

**Özellikler:**
- Başlık satırı: Açık gri arka plan (#F5F5F5)
- Alternatif satır renkleri: Beyaz / Çok açık gri
- Seçili satır: Açık mavi (#B3D9FF)
- Kenarlıklar: İnce gri çizgiler
- Scrollbar: İnce, gri

### 8. Liste Görünümü (Result Navigator)
**Eklenecek:** Parametrik tarama sonuçları için liste

**Özellikler:**
- Beyaz arka plan
- Seçili öğe: Açık mavi (#B3D9FF)
- Hover efekti: Çok açık gri (#F9F9F9)
- Format: "[1B] Theta = 46.0°" tarzı

### 9. Büyük Aksiyon Butonları
**Eklenecek:** MATLAB tarzı büyük butonlar

**Özellikler:**
- "PARAMETRİK TARA" butonu: Turuncu (#F5A623)
- "ANALİZ ET" butonu: Mavi (#4A90E2)
- Yükseklik: 44-48px
- Tam genişlik (fill="x")
- Büyük font (14-15px)
- Bold text

### 10. Durum Mesajları
**Eklenecek:** Alt kısımda log/hazır mesajları

**Özellikler:**
- Beyaz arka plan
- Kenarlık: Üstte ince gri çizgi
- Format: "[16:39:39] RADOME analizi tamamlandı."
- Scrollable
- Monospace font

---

## 📋 Implementasyon Adımları

### Adım 1: Renk Paletini Güncelle
**Dosya:** [`test.py`](test.py:26-50)

```python
# Mevcut C dictionary'sini değiştir
C = {
    # Ana Renkler
    "bg":            "#F0F0F0",
    "panel":         "#FFFFFF",
    "panel2":        "#F9F9F9",
    "panel3":        "#F5F5F5",
    "border":        "#D0D0D0",
    "border2":       "#B0B0B0",
    
    # Buton Renkleri
    "accent":        "#F5A623",  # Turuncu (ana)
    "accent_dim":    "#E09612",
    "accent2":       "#4A90E2",  # Mavi
    "accent2_dim":   "#3A7BC8",
    "accent3":       "#E74C3C",  # Kırmızı
    "accent4":       "#5DADE2",  # Açık mavi
    
    # Metin Renkleri
    "text":          "#333333",
    "text_dim":      "#666666",
    "text_mid":      "#999999",
    
    # Navigasyon
    "nav_bg":        "#E8E8E8",
    "nav_active":    "#B3D9FF",
    "nav_hover":     "#F0F0F0",
    
    # Özel Butonlar
    "run_btn":       "#F5A623",  # Turuncu
    "run_hover":     "#E09612",
    "stop_btn":      "#E74C3C",  # Kırmızı
    "preview_btn":   "#4A90E2",  # Mavi
    "preview_hover": "#3A7BC8",
    
    # Tablo
    "table_header":  "#F5F5F5",
    "table_selected":"#B3D9FF",
    "table_border":  "#D0D0D0",
}
```

### Adım 2: Appearance Mode'u Değiştir
**Dosya:** [`test.py`](test.py:20)

```python
# Değiştir
ctk.set_appearance_mode("dark")  # → "light"
```

### Adım 3: Header'ı Güncelle
**Dosya:** [`test.py`](test.py:180-200)

**Değişiklikler:**
- Arka plan rengini açık gri yap
- Logo rengini turuncu yap
- Metin renklerini koyu yap
- Alt kenarlık ekle

### Adım 4: Navigasyon Çubuğunu Güncelle
**Dosya:** [`test.py`](test.py:203-225)

**Değişiklikler:**
- Arka plan rengini açık gri yap
- Aktif sekme rengini açık mavi yap
- Hover efektini hafif gri yap

### Adım 5: Butonları Güncelle
**Dosya:** [`test.py`](test.py:78-83)

**Değişiklikler:**
- Corner radius'u azalt (8 → 4)
- Renkleri MATLAB paletine göre ayarla
- Font weight'i normal yap

### Adım 6: Input Alanlarını Güncelle
**Dosya:** [`test.py`](test.py:68-72)

**Değişiklikler:**
- Arka planı beyaz yap
- Kenarlık rengini açık gri yap
- Corner radius'u azalt (6 → 3)
- Metin rengini koyu yap

### Adım 7: Kartları Güncelle
**Dosya:** [`test.py`](test.py:74-76)

**Değişiklikler:**
- Arka planı beyaz yap
- Kenarlık rengini açık gri yap
- Corner radius'u azalt (10 → 4)

### Adım 8: Büyük Aksiyon Butonları Ekle
**Yeni Fonksiyon:**

```python
def _big_btn(parent, text, cmd, color, hover, **kw):
    """MATLAB tarzı büyük aksiyon butonu"""
    return ctk.CTkButton(
        parent, text=text, command=cmd,
        height=46, corner_radius=4,
        fg_color=color, hover_color=hover,
        font=ctk.CTkFont(size=14, weight="bold"),
        text_color=C["text_white"],
        **kw
    )
```

### Adım 9: Result Navigator Paneli Ekle
**Yeni Bileşen:** Simülasyon sonuçları için liste görünümü

**Özellikler:**
- Üst kısımda parametreler (Katman, Özellik, Min, Max, Adım)
- Büyük turuncu "PARAMETRİK TARA" butonu
- Liste görünümü (scrollable)
- Alt kısımda "TEMİZLE" butonu

### Adım 10: Tablo Görünümü Ekle
**Yeni Bileşen:** Sonuçlar sekmesinde tablo görünümü

**Özellikler:**
- Treeview widget kullan
- MATLAB tarzı renklendirme
- Alternatif satır renkleri
- Seçili satır vurgulama

### Adım 11: Log/Hazır Mesajları Paneli Ekle
**Yeni Bileşen:** Alt kısımda durum mesajları

**Özellikler:**
- Scrollable text widget
- Timestamp ile mesajlar
- Monospace font
- Beyaz arka plan

### Adım 12: Grafik Arka Planlarını Güncelle
**Dosya:** [`simulation_core.py`](simulation_core.py:504-1016)

**Değişiklikler:**
- Grafik arka planlarını beyaz yap
- Metin renklerini koyu yap
- Grid renklerini açık gri yap
- Eksen renklerini koyu gri yap

---

## 🎯 Öncelikli Değişiklikler

### Yüksek Öncelik (Temel Görünüm)
1. ✅ Renk paletini güncelle
2. ✅ Appearance mode'u light yap
3. ✅ Header'ı güncelle
4. ✅ Navigasyon çubuğunu güncelle
5. ✅ Butonları güncelle
6. ✅ Input alanlarını güncelle
7. ✅ Kartları güncelle

### Orta Öncelik (Yeni Bileşenler)
8. ✅ Büyük aksiyon butonları ekle
9. ✅ Result Navigator paneli ekle
10. ✅ Log/Hazır mesajları paneli ekle

### Düşük Öncelik (İyileştirmeler)
11. ✅ Tablo görünümü ekle
12. ✅ Grafik arka planlarını güncelle
13. ✅ Animasyonları ayarla

---

## 📐 Layout Değişiklikleri

### Ayarlar Sayfası
**Mevcut:** Sol parametreler, sağ mesh önizleme
**Yeni:** Aynı düzen, sadece renkler değişecek

### Önizleme Sayfası
**Mevcut:** Üstte toolbar, altta grafik
**Yeni:** Aynı düzen, grafik arka planı beyaz

### Simülasyon Sayfası
**Mevcut:** Üstte toolbar, ortada grafik, altta sekmeler
**Yeni:** Sağda Result Navigator paneli eklenecek

**Yeni Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ Toolbar (Başlat, Durdur, Progress)                     │
├──────────────────────────────────┬──────────────────────┤
│                                  │ Result Navigator     │
│                                  │ ┌──────────────────┐ │
│                                  │ │ Katman: [1]      │ │
│         Grafik Alanı             │ │ Özellik: [d(mm)] │ │
│                                  │ │ Min: 1  Max: 5   │ │
│                                  │ └──────────────────┘ │
│                                  │ [PARAMETRİK TARA]   │
│                                  │ ┌──────────────────┐ │
│                                  │ │ [1B] Theta=46.0° │ │
│                                  │ │ [1B] Theta=47.0° │ │
│                                  │ │ ...              │ │
│                                  │ └──────────────────┘ │
│                                  │ [TEMİZLE]           │
├──────────────────────────────────┴──────────────────────┤
│ Sekmeler (Üçgen Işın, Histogram, CPU/RAM)              │
├─────────────────────────────────────────────────────────┤
│ Alt Seçenekler                                          │
└─────────────────────────────────────────────────────────┘
```

### Sonuçlar Sayfası
**Mevcut:** Grid layout ile kartlar
**Yeni:** Üstte kartlar, altta tablo görünümü

**Yeni Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ Simülasyon Sonuçları                                    │
├───────────────┬───────────────┬─────────────────────────┤
│ Mesh Bilgisi  │ Sekme Sonuç.  │ Çarpış Açıları         │
├───────────────┼───────────────┼─────────────────────────┤
│ Süre          │ CPU           │ RAM                     │
├───────────────┴───────────────┴─────────────────────────┤
│ Detaylı Sonuçlar Tablosu                                │
│ ┌─────┬────────┬────────┬────────┬────────┬──────────┐ │
│ │ ID  │ Vuruş  │ Açı    │ Durum  │ Yoğunluk│ ...     │ │
│ ├─────┼────────┼────────┼────────┼────────┼──────────┤ │
│ │ 1   │ 5      │ 23.5°  │ Dik    │ 45%    │ ...     │ │
│ │ 2   │ 3      │ 45.2°  │ Orta   │ 27%    │ ...     │ │
│ │ ... │ ...    │ ...    │ ...    │ ...    │ ...     │ │
│ └─────┴────────┴────────┴────────┴────────┴──────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Teknik Detaylar

### CustomTkinter Ayarları
```python
# Appearance
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")  # Değişmeyecek

# Widget Stilleri
button_style = {
    "corner_radius": 4,
    "border_width": 1,
    "border_color": C["border"],
}

entry_style = {
    "corner_radius": 3,
    "border_width": 1,
    "border_color": C["border"],
    "fg_color": C["panel"],
}

frame_style = {
    "corner_radius": 4,
    "border_width": 1,
    "border_color": C["border"],
    "fg_color": C["panel"],
}
```

### Matplotlib Ayarları
```python
# Grafik stilleri
plt.style.use('default')  # MATLAB benzeri

# Figure ayarları
fig_style = {
    "facecolor": "#FFFFFF",
    "edgecolor": "#D0D0D0",
}

# Axes ayarları
ax_style = {
    "facecolor": "#FFFFFF",
    "edgecolor": "#333333",
    "labelcolor": "#333333",
    "grid_color": "#E0E0E0",
    "grid_alpha": 0.5,
}
```

### Font Ayarları
```python
# UI Fontları
FONT_UI = "Segoe UI"  # Windows
FONT_MONO = "Consolas"  # Monospace

# Font Boyutları
FONT_SIZE_LARGE = 14   # Büyük butonlar
FONT_SIZE_NORMAL = 11  # Normal metin
FONT_SIZE_SMALL = 9    # Küçük etiketler
```

---

## ⚠️ Dikkat Edilecek Noktalar

### 1. İşlevsellik Korunacak
- **Hiçbir fonksiyon değiştirilmeyecek**
- **Hiçbir özellik kaldırılmayacak**
- **Sadece görsel tasarım değişecek**

### 2. Geriye Dönük Uyumluluk
- Mevcut simülasyon verileri çalışmaya devam edecek
- Grafik fonksiyonları aynı parametreleri alacak
- Dosya kaydetme/yükleme etkilenmeyecek

### 3. Performans
- Grafik render süreleri değişmeyecek
- Simülasyon hızı etkilenmeyecek
- Memory kullanımı aynı kalacak

### 4. Platform Uyumluluğu
- Windows'ta test edilecek
- Font seçimleri platform bağımsız olacak
- Renk kontrastı erişilebilirlik standartlarına uygun

---

## 📊 Değişiklik Özeti

### Değişecek Dosyalar
1. **[`test.py`](test.py)** - Ana GUI dosyası (tüm değişiklikler)
2. **[`simulation_core.py`](simulation_core.py)** - Grafik fonksiyonları (arka plan renkleri)

### Değişmeyecek Dosyalar
1. **[`Lift_Up_Model.unv`](Lift_Up_Model.unv)** - Mesh dosyası
2. **Plans klasörü** - Dokümantasyon

### Yeni Eklenecek Bileşenler
1. Result Navigator paneli
2. Tablo görünümü (Sonuçlar sekmesi)
3. Log/Hazır mesajları paneli
4. Büyük aksiyon butonları

### Kaldırılacak Özellikler
- **Hiçbiri** (sadece görsel değişiklik)

---

## 🚀 Uygulama Sırası

### Faz 1: Temel Görünüm (30 dakika)
1. Renk paletini güncelle
2. Appearance mode'u değiştir
3. Header ve navigasyonu güncelle
4. Buton ve input stillerini güncelle

### Faz 2: Bileşen Güncellemeleri (45 dakika)
5. Kartları güncelle
6. Grafik arka planlarını güncelle
7. Tüm sayfalardaki renkleri ayarla

### Faz 3: Yeni Özellikler (60 dakika)
8. Result Navigator paneli ekle
9. Tablo görünümü ekle
10. Log paneli ekle
11. Büyük aksiyon butonları ekle

### Faz 4: Test ve İyileştirme (30 dakika)
12. Tüm sayfaları test et
13. Renk kontrastlarını kontrol et
14. Responsive davranışı test et
15. Son rötuşlar

**Toplam Tahmini Süre:** 2.5-3 saat

---

## ✅ Başarı Kriterleri

1. ✅ Uygulama MATLAB'a benzer açık tema kullanıyor
2. ✅ Tüm butonlar MATLAB renk paletinde
3. ✅ Tablo görünümü MATLAB tarzında
4. ✅ Result Navigator paneli çalışıyor
5. ✅ Tüm mevcut özellikler çalışıyor
6. ✅ Hiçbir işlevsellik kaybedilmedi
7. ✅ Grafik arka planları beyaz
8. ✅ Metin renkleri okunabilir
9. ✅ Responsive tasarım korundu
10. ✅ Performans etkilenmedi

---

## 📝 Notlar

- Fotoğraflardaki tasarım MATLAB R2020b veya sonrası versiyonuna benziyor
- Renk paleti MATLAB'ın varsayılan UI renklerine çok yakın
- Tablo görünümü için tkinter.ttk.Treeview kullanılacak
- Result Navigator için custom scrollable frame kullanılacak
- Log paneli için scrolled text widget kullanılacak

---

**Plan Hazırlayan:** Roo (Architect Mode)
**Tarih:** 2026-05-15
**Versiyon:** 1.0
