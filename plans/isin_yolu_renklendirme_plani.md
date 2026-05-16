# Işın Yolu Grafiği Renklendirme Planı

## 📋 Genel Bakış

**Amaç:** Işın yolu grafiğinde kaviteye giren ışınları kırmızı, girmeyenleri mavi renkte göstermek.

**Etkilenen Dosyalar:**
- [`simulation_core.py`](../simulation_core.py) - `create_ray_path_figure()` fonksiyonu
- [`simulation_core.py`](../simulation_core.py) - `run_simulation()` fonksiyonu (veri saklama)
- [`test.py`](../test.py) - `_sim_worker()` ve `_render_simulation_graph()` fonksiyonları

---

## 🔍 Mevcut Durum Analizi

### Veri Akışı
1. **Işın Üretimi:** [`generate_beam_from_counts()`](../simulation_core.py:104) → `rays_o`, `rays_d` üretir
2. **Simülasyon:** [`run_simulation()`](../simulation_core.py:261) → İlk çarpışmayı tespit eder
3. **Sonuç Saklama:** [`_sim_worker()`](../test.py:923) → Sonuçları dictionary'de saklar
4. **Görselleştirme:** [`create_ray_path_figure()`](../simulation_core.py:523) → Grafiği çizer

### Sorun
- `create_ray_path_figure()` sadece `bounce_paths` alıyor (çarpan ışınlar)
- Çarpmayan ışınların bilgisi yok
- Tüm ışınlar aynı renkte (`#4D9EFF` - mavi)

---

## 🎯 Çözüm Stratejisi

### Adım 1: İlk Çarpışma Bilgisini Sakla
**Dosya:** [`simulation_core.py`](../simulation_core.py:261) - `run_simulation()`

**Değişiklik:**
```python
# İlk sekmedeki çarpışma bilgisini sakla
first_hit_ids = None  # Hangi ışınlar çarptı
initial_rays_o = rays_o.copy()  # Başlangıç noktaları
initial_rays_d = rays_d.copy()  # Başlangıç yönleri

bounce = 0
while bounce < max_safety_limit:
    bounce += 1
    # ...
    hit_ids, hit_dists = plucker_bvh_tracer(...)
    
    # İlk sekmede hangi ışınların çarptığını kaydet
    if bounce == 1:
        first_hit_ids = hit_ids.copy()  # -1 = çarpmadı, >=0 = çarptı
    # ...
```

**Return değerine ekle:**
```python
return hit_counts, avg_angles, bounce_paths, resource_data, first_hit_ids, initial_rays_o, initial_rays_d
```

---

### Adım 2: create_ray_path_figure() Fonksiyonunu Güncelle
**Dosya:** [`simulation_core.py`](../simulation_core.py:523)

**Yeni Parametre İmzası:**
```python
def create_ray_path_figure(A, B, C, bounce_paths, origin,
                           rays_o, rays_d, first_hit_ids,  # YENİ PARAMETRELER
                           cam_elev=20, cam_azim=45,
                           bg_color="#FFFFFF", text_color="#333333"):
```

**Işın Çizim Mantığı:**
```python
# 1. Hangi ışınlar çarptı, hangileri çarpmadı?
hit_ray_indices = np.where(first_hit_ids >= 0)[0]  # Çarpan ışınlar
miss_ray_indices = np.where(first_hit_ids == -1)[0]  # Çarpmayan ışınlar

# 2. ÇARPMAYAN IŞINLARI MAVİ ÇİZ (önce, altta kalsın)
max_miss_rays = 50  # Performans için limit
if len(miss_ray_indices) > 0:
    step = max(1, len(miss_ray_indices) // max_miss_rays)
    for idx in miss_ray_indices[::step]:
        start = rays_o[idx]
        direction = rays_d[idx]
        # Mesh dışına uzanan bir çizgi çiz
        end = start + direction * mesh_scale * 0.8
        ax.plot([start[0], end[0]], 
               [start[1], end[1]], 
               [start[2], end[2]],
               color='#4D9EFF', alpha=0.4, linewidth=0.5, 
               rasterized=True, label='Girmeyen' if idx == miss_ray_indices[0] else '')

# 3. ÇARPAN IŞINLARI KIRMIZI ÇİZ (bounce_paths kullanarak)
max_hit_rays = 80
for bounce_idx, (start_pts, end_pts) in enumerate(bounce_paths):
    n = start_pts.shape[0]
    step = max(1, n // max_hit_rays)
    for i in range(0, min(n, max_hit_rays * step), step):
        ax.plot([start_pts[i,0], end_pts[i,0]],
               [start_pts[i,1], end_pts[i,1]],
               [start_pts[i,2], end_pts[i,2]],
               color='#E74C3C', alpha=0.6, linewidth=0.7,  # KIRMIZI
               rasterized=True, label='Giren' if bounce_idx == 0 and i == 0 else '')
```

**Legend Güncelleme:**
```python
# Legend'i manuel oluştur
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], color='#E74C3C', linewidth=2, label='Kaviteye Giren'),
    Line2D([0], [0], color='#4D9EFF', linewidth=2, label='Girmeyen'),
    Line2D([0], [0], marker='X', color='w', markerfacecolor='#2ECC71', 
           markersize=10, label='Işın Kaynağı', linestyle='None')
]
ax.legend(handles=legend_elements, fontsize=9, facecolor='#F5F5F5', 
         labelcolor=text_color, edgecolor='#D0D0D0', loc='upper right')
```

---

### Adım 3: test.py'de Veri Aktarımını Güncelle
**Dosya:** [`test.py`](../test.py:923) - `_sim_worker()`

**run_simulation() çağrısını güncelle:**
```python
# Eski:
hit_counts, avg_angles, bounce_paths, resource_data = run_simulation(...)

# Yeni:
hit_counts, avg_angles, bounce_paths, resource_data, first_hit_ids, initial_rays_o, initial_rays_d = run_simulation(...)
```

**Sonuç dictionary'sine ekle:**
```python
res = dict(
    # ... mevcut alanlar ...
    _first_hit_ids=first_hit_ids,  # YENİ
    _rays_o=initial_rays_o,        # YENİ
    _rays_d=initial_rays_d,        # YENİ
)
```

---

### Adım 4: test.py'de Grafik Çağrısını Güncelle
**Dosya:** [`test.py`](../test.py:1187) - `_render_simulation_graph()`

**create_ray_path_figure() çağrısını güncelle:**
```python
if option == "Işın Yolu":
    fig = create_ray_path_figure(
        d["_A"], d["_B"], d["_Cv"], 
        d["_paths"], d["_orig"],
        d["_rays_o"], d["_rays_d"], d["_first_hit_ids"],  # YENİ PARAMETRELER
        cam_elev=d["_elev"], cam_azim=d["_azim"],
        bg_color=C["panel2"], text_color=C["text"])
```

---

## 📊 Görsel Tasarım

### Renk Şeması
- **Kırmızı (`#E74C3C`)**: Kaviteye giren ışınlar (çarpan)
  - Alpha: 0.6
  - Linewidth: 0.7
  - Üstte görünsün (daha belirgin)

- **Mavi (`#4D9EFF`)**: Kaviteye girmeyen ışınlar
  - Alpha: 0.4
  - Linewidth: 0.5
  - Altta görünsün (daha soluk)

### Performans Optimizasyonu
- Çarpmayan ışınlar: Maksimum 50 adet
- Çarpan ışınlar: Maksimum 80 adet (mevcut)
- `rasterized=True` kullan (daha hızlı render)

---

## ✅ Test Senaryoları

1. **Tüm ışınlar çarpıyor:**
   - Sadece kırmızı ışınlar görünmeli
   - Legend'de her iki renk de olmalı

2. **Hiçbir ışın çarpmıyor:**
   - Sadece mavi ışınlar görünmeli
   - Kırmızı ışın olmamalı

3. **Karışık durum:**
   - Hem kırmızı hem mavi ışınlar görünmeli
   - Kırmızılar daha belirgin olmalı

4. **Performans:**
   - Grafik 2-3 saniyede yüklenmeli
   - Zoom/pan sorunsuz çalışmalı

---

## 🔄 Geriye Dönük Uyumluluk

**Sorun:** Eski simülasyon sonuçları yeni parametreleri içermeyebilir.

**Çözüm:** `create_ray_path_figure()` içinde varsayılan değerler:
```python
def create_ray_path_figure(A, B, C, bounce_paths, origin,
                           rays_o=None, rays_d=None, first_hit_ids=None,
                           cam_elev=20, cam_azim=45,
                           bg_color="#FFFFFF", text_color="#333333"):
    # Eğer yeni parametreler yoksa, eski davranışı koru
    if rays_o is None or rays_d is None or first_hit_ids is None:
        # Sadece çarpan ışınları çiz (eski davranış)
        # Renk: mavi (eski)
        pass
    else:
        # Yeni davranış: Renkli ışınlar
        pass
```

---

## 📝 Uygulama Sırası

1. ✅ **Adım 1:** `run_simulation()` fonksiyonunu güncelle
   - İlk çarpışma bilgisini sakla
   - Return değerini genişlet

2. ✅ **Adım 2:** `create_ray_path_figure()` fonksiyonunu güncelle
   - Yeni parametreleri ekle
   - Çarpmayan ışınları mavi çiz
   - Çarpan ışınları kırmızı çiz
   - Legend'i güncelle

3. ✅ **Adım 3:** `_sim_worker()` fonksiyonunu güncelle
   - Yeni return değerlerini al
   - Sonuç dictionary'sine ekle

4. ✅ **Adım 4:** `_render_simulation_graph()` fonksiyonunu güncelle
   - Yeni parametrelerle çağır

5. ✅ **Test:** Simülasyonu çalıştır ve sonuçları kontrol et

---

## 🎨 Örnek Görsel

```
┌─────────────────────────────────────────┐
│  Işın Yolu Görünümü                     │
├─────────────────────────────────────────┤
│                                         │
│     🟦🟦🟦  (Mavi - Girmeyen)           │
│        ╲  ╱                             │
│         ╲╱                              │
│    ✖️ Kaynak                            │
│         ╱╲                              │
│        ╱  ╲                             │
│     🟥🟥🟥  (Kırmızı - Giren)           │
│       ╱╲  ╱╲                            │
│      ╱  ╲╱  ╲  (Sekmeler)              │
│     ╱    ╱╲   ╲                         │
│    ╱    ╱  ╲   ╲                        │
│                                         │
│  Legend:                                │
│  🟥 Kaviteye Giren                      │
│  🟦 Girmeyen                            │
│  ✖️ Işın Kaynağı                        │
└─────────────────────────────────────────┘
```

---

## 💡 Ek İyileştirmeler (Opsiyonel)

1. **İstatistik Gösterimi:**
   - Başlıkta: "Giren: 1,234 / Girmeyen: 791"

2. **Interaktif Filtreleme:**
   - Checkbox: "Giren ışınları göster"
   - Checkbox: "Girmeyen ışınları göster"

3. **Renk Özelleştirme:**
   - Kullanıcı renkleri seçebilsin

4. **Animasyon:**
   - Işınların zamanla ilerlemesi

---

## 🚀 Sonuç

Bu plan uygulandığında:
- ✅ Kaviteye giren ışınlar **kırmızı** olacak
- ✅ Kaviteye girmeyen ışınlar **mavi** olacak
- ✅ Legend açıklayıcı olacak
- ✅ Performans korunacak
- ✅ Geriye dönük uyumlu olacak
