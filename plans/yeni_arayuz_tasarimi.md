# Yeni Arayüz Tasarımı - Detaylı Plan

## 📸 Fotoğraf Analizi

### Tasarım Özellikleri
1. **Analiz Ekranı** (Ana Bölüm - Sol/Merkez)
   - Üstte: "Analiz Ekranı" başlığı
   - Grafik alanı: Büyük, merkezi konumda ısı haritası
   - Alt bölüm: "Sonuçlar / Dışa Aktarma"
     - RL (dB), IL (dB), A (Soğurma dB) değerleri
     - Sayısal Format, Grafik Türü, 2B Işıhartası dropdown'ları
     - SIFIRLA (kırmızı), ANALİZ ET (mavi), NOKTA ANALİZİ (açık mavi) butonları
     - Hazır: log mesajı

2. **Result Navigator** (Sağ Panel)
   - Katman seçici (sayısal input)
   - Özellik seçici (dropdown: d (mm))
   - Min, Max, Adım parametreleri
   - PARAMETRİK TARA butonu (turuncu/sarı)
   - Parametrik liste (scrollable)
   - TEMİZLE butonu (gri)

3. **Alt Tablo**
   - Detaylı sonuç tablosu (f, theta, R, T, A, RL, IL, S11_Re vb.)
   - Satır seçimi (mavi highlight)

### Renk Paleti (Fotoğraftan Çıkarılan)
```
Arka Plan:      #F5F5F5 (açık gri)
Panel Arka:     #FFFFFF (beyaz)
Başlık Arka:    #E8E8E8 (açık gri)
Kenarlık:       #CCCCCC (orta gri)
Metin:          #333333 (koyu gri)
Metin Açık:     #666666 (orta gri)

Buton Kırmızı:  #E74C3C (SIFIRLA)
Buton Mavi:     #3498DB (ANALİZ ET)
Buton Açık Mavi:#5DADE2 (NOKTA ANALİZİ)
Buton Turuncu:  #F39C12 (PARAMETRİK TARA)
Buton Gri:      #95A5A6 (TEMİZLE)

Seçili Satır:   #AED6F1 (açık mavi)
Hover:          #D5DBDB (açık gri)
```

## 🎯 Adaptasyon Stratejisi

### Mevcut Yapı → Yeni Yapı Eşleştirmesi

#### 1. Simülasyon Sekmesi Yeniden Tasarımı
**Mevcut:**
```
[Toolbar: Başlat/Durdur/Progress]
[Grafik Alanı - Tam Genişlik]
[Alt Sekme Çubuğu: Üçgen Işın/Histogram/CPU-RAM]
[Alt Seçenek Butonları]
```

**Yeni:**
```
┌─────────────────────────────────────────────────────────┬──────────────────┐
│ Analiz Ekranı                                           │ Result Navigator │
├─────────────────────────────────────────────────────────┤                  │
│                                                         │  Katman: [1]     │
│                                                         │  Özellik: [▼]    │
│              [GRAFİK ALANI]                             │  Min: [1]        │
│                                                         │  Max: [5]        │
│                                                         │  Adım: [0.5]     │
│                                                         │                  │
│                                                         │ [PARAMETRİK TARA]│
├─────────────────────────────────────────────────────────┤                  │
│ Grafik                                                  │  [Liste]         │
│ [Grafik Türü ▼]                                         │                  │
├─────────────────────────────────────────────────────────┤                  │
│ Sonuçlar / Dışa Aktarma                                 │                  │
│ RL (dB): -5.007    IL (dB): -1.742    A (dB): -18.322   │ [TEMİZLE]        │
│                                                         │                  │
│ Sayısal Format: [▼]  Grafik Türü: [▼]  2B Işıh.: [▼]   │                  │
│ [SIFIRLA] [ANALİZ ET] [NOKTA ANALİZİ]                   │                  │
│ Hazır: [16:39:39] Analiz tamamlandı.                    │                  │
└─────────────────────────────────────────────────────────┴──────────────────┘
```

### 2. Renk Şeması Güncellemesi
- Koyu tema → Açık tema geçişi
- Mavi vurgular → Çok renkli buton sistemi
- Transparan paneller → Beyaz kartlar

### 3. Bileşen Eşleştirmesi

| Fotoğraf Bileşeni | Mevcut Karşılığı | Yeni İşlev |
|-------------------|------------------|------------|
| Analiz Ekranı | Simülasyon Sekmesi | Ana görüntüleme alanı |
| Result Navigator | - (yok) | Yeni: Parametre tarama paneli |
| Sonuçlar/Dışa Aktarma | Sonuçlar Sekmesi | Alt panel olarak entegre |
| Grafik Türü Dropdown | Alt Seçenek Butonları | Dropdown'a dönüştür |
| PARAMETRİK TARA | - (yok) | Yeni: Batch simülasyon |
| Alt Tablo | - (yok) | Yeni: Detaylı sonuç tablosu |

## 🔧 Teknik Uygulama Adımları

### Adım 1: Renk Paleti Güncelleme
```python
C = {
    # Açık tema renkleri
    "bg":            "#F5F5F5",  # Ana arka plan
    "panel":         "#FFFFFF",  # Panel arka planı
    "panel2":        "#FAFAFA",  # İkincil panel
    "panel3":        "#F0F0F0",  # Üçüncül panel
    "border":        "#CCCCCC",  # Kenarlıklar
    "border2":       "#DDDDDD",  # Açık kenarlıklar
    
    # Metin renkleri
    "text":          "#333333",  # Ana metin
    "text_dim":      "#666666",  # Soluk metin
    "text_mid":      "#555555",  # Orta ton metin
    
    # Buton renkleri
    "btn_red":       "#E74C3C",  # Sıfırla
    "btn_red_hover": "#C0392B",
    "btn_blue":      "#3498DB",  # Analiz Et
    "btn_blue_hover":"#2980B9",
    "btn_cyan":      "#5DADE2",  # Nokta Analizi
    "btn_cyan_hover":"#48A0D7",
    "btn_orange":    "#F39C12",  # Parametrik Tara
    "btn_orange_hover":"#E67E22",
    "btn_gray":      "#95A5A6",  # Temizle
    "btn_gray_hover":"#7F8C8D",
    
    # Vurgular
    "selected":      "#AED6F1",  # Seçili satır
    "hover":         "#D5DBDB",  # Hover efekti
    "accent":        "#3498DB",  # Vurgu rengi
}
```

### Adım 2: Layout Yeniden Yapılandırma
```python
def _build_page_simulasyon(self):
    page = self._pages["Simülasyon"]
    
    # Ana container: Sol (Analiz) + Sağ (Navigator)
    page.columnconfigure(0, weight=4)  # Analiz ekranı
    page.columnconfigure(1, weight=1)  # Result Navigator
    page.rowconfigure(0, weight=1)
    
    # Sol: Analiz Ekranı
    left_panel = self._build_analysis_screen(page)
    left_panel.grid(row=0, column=0, sticky="nsew", padx=(10,5), pady=10)
    
    # Sağ: Result Navigator
    right_panel = self._build_result_navigator(page)
    right_panel.grid(row=0, column=1, sticky="nsew", padx=(5,10), pady=10)
```

### Adım 3: Analiz Ekranı Bileşenleri
```python
def _build_analysis_screen(self, parent):
    frame = ctk.CTkFrame(parent, fg_color=C["panel"], corner_radius=8,
                         border_width=1, border_color=C["border"])
    
    # Başlık
    header = ctk.CTkFrame(frame, fg_color=C["panel3"], height=40)
    header.pack(fill="x", padx=0, pady=0)
    ctk.CTkLabel(header, text="Analiz Ekranı", 
                 font=("Arial", 14, "bold")).pack(side="left", padx=15, pady=10)
    
    # Grafik sekmesi
    graph_tab = ctk.CTkFrame(frame, fg_color=C["panel2"], height=35)
    graph_tab.pack(fill="x", padx=10, pady=(5,0))
    ctk.CTkLabel(graph_tab, text="Grafik").pack(side="left", padx=10, pady=5)
    
    # Grafik alanı
    self._graph_area = ctk.CTkFrame(frame, fg_color=C["bg"])
    self._graph_area.pack(fill="both", expand=True, padx=10, pady=5)
    
    # Alt bölüm: Sonuçlar/Dışa Aktarma
    bottom = self._build_results_export(frame)
    bottom.pack(fill="x", padx=10, pady=(0,10))
    
    return frame
```

### Adım 4: Result Navigator
```python
def _build_result_navigator(self, parent):
    frame = ctk.CTkFrame(parent, fg_color=C["panel"], corner_radius=8,
                         border_width=1, border_color=C["border"])
    
    # Başlık
    ctk.CTkLabel(frame, text="Result Navigator",
                 font=("Arial", 12, "bold")).pack(padx=10, pady=(10,5))
    
    # Katman
    row1 = ctk.CTkFrame(frame, fg_color="transparent")
    row1.pack(fill="x", padx=10, pady=5)
    ctk.CTkLabel(row1, text="Katman:").pack(side="left")
    self._layer_entry = ctk.CTkEntry(row1, width=100)
    self._layer_entry.pack(side="right")
    
    # Özellik
    row2 = ctk.CTkFrame(frame, fg_color="transparent")
    row2.pack(fill="x", padx=10, pady=5)
    ctk.CTkLabel(row2, text="Özellik:").pack(side="left")
    self._property_combo = ctk.CTkComboBox(row2, width=100,
                                           values=["d (mm)", "theta (deg)", "phi (deg)"])
    self._property_combo.pack(side="right")
    
    # Min, Max, Adım
    for label, var in [("Min:", self._param_min), 
                       ("Max:", self._param_max),
                       ("Adım:", self._param_step)]:
        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(row, text=label).pack(side="left")
        entry = ctk.CTkEntry(row, width=100, textvariable=var)
        entry.pack(side="right")
    
    # Parametrik Tara butonu
    ctk.CTkButton(frame, text="PARAMETRİK TARA",
                  fg_color=C["btn_orange"], hover_color=C["btn_orange_hover"],
                  font=("Arial", 11, "bold"), height=35,
                  command=self._parametric_scan).pack(fill="x", padx=10, pady=10)
    
    # Liste
    self._param_list = ctk.CTkScrollableFrame(frame, fg_color=C["bg"])
    self._param_list.pack(fill="both", expand=True, padx=10, pady=5)
    
    # Temizle butonu
    ctk.CTkButton(frame, text="TEMİZLE",
                  fg_color=C["btn_gray"], hover_color=C["btn_gray_hover"],
                  height=35, command=self._clear_params).pack(fill="x", padx=10, pady=(5,10))
    
    return frame
```

### Adım 5: Sonuçlar/Dışa Aktarma Bölümü
```python
def _build_results_export(self, parent):
    frame = ctk.CTkFrame(parent, fg_color=C["panel2"], corner_radius=6,
                         border_width=1, border_color=C["border"])
    
    # Başlık
    ctk.CTkLabel(frame, text="Sonuçlar / Dışa Aktarma",
                 font=("Arial", 11, "bold")).pack(padx=10, pady=(8,5))
    
    # Sonuç değerleri
    results_row = ctk.CTkFrame(frame, fg_color="transparent")
    results_row.pack(fill="x", padx=10, pady=5)
    
    for label, var in [("RL (dB):", self._rl_value),
                       ("IL (dB):", self._il_value),
                       ("A (Soğurma dB):", self._a_value)]:
        col = ctk.CTkFrame(results_row, fg_color="transparent")
        col.pack(side="left", expand=True, fill="x", padx=5)
        ctk.CTkLabel(col, text=label, font=("Arial", 9)).pack(anchor="w")
        ctk.CTkLabel(col, textvariable=var, font=("Arial", 11, "bold")).pack(anchor="w")
    
    # Dropdown'lar
    dropdown_row = ctk.CTkFrame(frame, fg_color="transparent")
    dropdown_row.pack(fill="x", padx=10, pady=5)
    
    for label, values in [("Sayısal Format:", ["YIS(R,T,A)", "S-Parameters"]),
                          ("Grafik Türü:", ["RL + IL (dB)", "R + T", "A (dB)"]),
                          ("2B Işıhartası:", ["A (dB)", "RL (dB)", "IL (dB)"])]:
        col = ctk.CTkFrame(dropdown_row, fg_color="transparent")
        col.pack(side="left", expand=True, fill="x", padx=5)
        ctk.CTkLabel(col, text=label, font=("Arial", 9)).pack(anchor="w")
        ctk.CTkComboBox(col, values=values, width=150).pack(anchor="w")
    
    # Butonlar
    button_row = ctk.CTkFrame(frame, fg_color="transparent")
    button_row.pack(fill="x", padx=10, pady=8)
    
    ctk.CTkButton(button_row, text="SIFIRLA", width=120, height=35,
                  fg_color=C["btn_red"], hover_color=C["btn_red_hover"],
                  font=("Arial", 11, "bold")).pack(side="left", padx=5)
    
    ctk.CTkButton(button_row, text="ANALİZ ET", width=120, height=35,
                  fg_color=C["btn_blue"], hover_color=C["btn_blue_hover"],
                  font=("Arial", 11, "bold")).pack(side="left", padx=5)
    
    ctk.CTkButton(button_row, text="NOKTA ANALİZİ", width=140, height=35,
                  fg_color=C["btn_cyan"], hover_color=C["btn_cyan_hover"],
                  font=("Arial", 11, "bold")).pack(side="left", padx=5)
    
    # Log mesajı
    self._log_label = ctk.CTkLabel(frame, text="Hazır: Simülasyon bekleniyor...",
                                   font=("Arial", 9), text_color=C["text_dim"])
    self._log_label.pack(padx=10, pady=(0,8))
    
    return frame
```

## 📋 Uygulama Sırası

1. ✅ **Renk paletini güncelle** - C dictionary'sini yeniden yaz
2. ✅ **Tema modunu değiştir** - `ctk.set_appearance_mode("light")`
3. ✅ **Simülasyon sekmesini yeniden yapılandır** - Grid layout ile 2 kolon
4. ✅ **Analiz Ekranı bileşenlerini oluştur** - Grafik + Sonuçlar
5. ✅ **Result Navigator panelini ekle** - Parametrik tarama
6. ✅ **Buton stillerini güncelle** - Renkli butonlar
7. ✅ **Dropdown menüleri ekle** - ComboBox bileşenleri
8. ✅ **Alt tablo ekle** (opsiyonel) - Detaylı sonuçlar için
9. ✅ **Test ve ince ayarlar** - Padding, spacing, fontlar

## 🎨 Tipografi

```python
FONTS = {
    "header": ("Arial", 14, "bold"),
    "subheader": ("Arial", 12, "bold"),
    "body": ("Arial", 10),
    "small": ("Arial", 9),
    "button": ("Arial", 11, "bold"),
}
```

## 📝 Notlar

- Fotoğraftaki tasarım radar/RF analiz yazılımı için tasarlanmış
- Bizim simülasyon: Işın izleme (ray tracing)
- Adaptasyon: Aynı layout ve renk şeması, farklı içerik
- Result Navigator: Parametrik tarama için yeni özellik
- Alt tablo: Detaylı sonuçlar için opsiyonel (yer varsa eklenebilir)

## 🚀 Sonraki Adımlar

1. Önce renk paletini ve temel layout'u uygula
2. Bileşenleri tek tek ekle ve test et
3. Mevcut simülasyon fonksiyonlarını yeni arayüze bağla
4. Parametrik tarama özelliğini implement et
5. Son rötuşlar ve optimizasyon
