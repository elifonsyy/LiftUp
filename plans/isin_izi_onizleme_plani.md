# Işın İzi Sekmesi - Önizleme Modu Planı

## 📋 Genel Bakış

**Amaç:** "Işın İzi" sekmesini simülasyon olmadan çalışacak şekilde değiştirmek - önizleme gibi mesh + ışın yönlerini göstermek.

**Mevcut Durum:** 
- Işın İzi simülasyon sonrası çalışıyor
- `bounce_paths` ve `hit_counts` gerektiriyor
- Simülasyon olmadan çalışmıyor

**Hedef Durum:**
- Önizleme gibi çalışsın (simülasyon gerekmeden)
- Mesh + ışın yönlerini göstersin
- Ayarlar sayfasındaki parametreleri kullansın

---

## 🎯 Çözüm Stratejisi

### Seçenek 1: Işın İzi'ni Önizleme Moduna Çevir
**Avantaj:** Kullanıcı simülasyon öncesi ışınları görebilir
**Dezavantaj:** Simülasyon sonrası veri kaybolur

### Seçenek 2: İki Mod Ekle (Önizleme + Simülasyon)
**Avantaj:** Her iki modu da kullanabilir
**Dezavantaj:** Daha karmaşık

### ✅ Seçilen: Seçenek 1 - Basit ve Kullanışlı

---

## 📝 Uygulama Planı

### Adım 1: `create_ray_trace_figure()` Fonksiyonunu Güncelle

**Dosya:** [`simulation_core.py`](../simulation_core.py:750)

**Değişiklik:**
```python
def create_ray_trace_figure(A, B, C, bounce_paths=None, hit_counts=None, origin=None,
                           rays_o=None, rays_d=None,  # YENİ: Önizleme için
                           cam_elev=20, cam_azim=45,
                           bg_color="#FFFFFF", text_color="#333333"):
    """
    Işın izi figure oluştur.
    
    İki mod:
    1. Önizleme Modu: rays_o ve rays_d verilirse, simülasyon olmadan ışınları göster
    2. Simülasyon Modu: bounce_paths ve hit_counts verilirse, simülasyon sonuçlarını göster
    """
    
    # Hangi modda çalışıyoruz?
    preview_mode = (rays_o is not None and rays_d is not None)
    simulation_mode = (bounce_paths is not None and hit_counts is not None)
    
    if preview_mode:
        # ÖNİZLEME MODU: Sadece mesh + ışın yönleri
        # Mesh'i transparan göster
        # Işınları basit çizgiler olarak göster (önizleme gibi)
        pass
    elif simulation_mode:
        # SİMÜLASYON MODU: Mevcut davranış (sekme bazlı renklendirme)
        pass
    else:
        # Hata: Hiçbir veri yok
        pass
```

**Önizleme Modu Detayları:**
```python
if preview_mode:
    # Mesh'i hafif göster
    step = max(1, len(A) // 1000)
    pts = np.concatenate([A[::step], B[::step], C[::step]], axis=0)
    ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2],
               c='#5A7399', s=0.2, alpha=0.1, linewidths=0, rasterized=True)
    
    # Işınları çiz (önizleme gibi - basit)
    max_rays = 100  # Daha fazla ışın göster (önizleme için)
    step = max(1, len(rays_o) // max_rays)
    
    for i in range(0, len(rays_o), step):
        start = rays_o[i]
        direction = rays_d[i]
        # Mesh ölçeğine göre uzunluk
        end = start + direction * mesh_scale * 0.6
        
        ax.plot([start[0], end[0]], 
               [start[1], end[1]], 
               [start[2], end[2]],
               color='#4D9EFF', alpha=0.5, linewidth=0.6, 
               rasterized=True)
    
    # Kaynak noktayı göster
    if origin is not None:
        ax.scatter(*origin, color='#2ECC71', s=200, marker='X',
                   label='Işın Kaynağı', depthshade=False)
    
    fig.suptitle('Işın Yönleri Önizlemesi', ...)
```

---

### Adım 2: `test.py` - Işın İzi Çağrısını Güncelle

**Dosya:** [`test.py`](../test.py:1196)

**Değişiklik:**
```python
elif option == "Işın İzi":
    # Önizleme modu: Simülasyon verisi olsa bile önizleme göster
    # Parametreleri al
    try:
        t0 = float(self._t_start.get())
        t1 = float(self._t_end.get())
        p0 = float(self._p_start.get())
        p1 = float(self._p_end.get())
        nt = int(self._n_theta.get())
        np_ = int(self._n_phi.get())
        
        # Kaynak noktası
        origin = [float(self._origin_x.get()),
                 float(self._origin_y.get()),
                 float(self._origin_z.get())]
        
        # Işınları oluştur (önizleme için)
        from simulation_core import generate_beam_from_counts
        rays_o, rays_d = generate_beam_from_counts(
            origin, (t0, t1), (p0, p1), nt, np_)
        
        # Önizleme modunda çağır
        fig = create_ray_trace_figure(
            d["_A"], d["_B"], d["_Cv"],
            rays_o=rays_o, rays_d=rays_d, origin=origin,
            cam_elev=d["_elev"], cam_azim=d["_azim"],
            bg_color=C["panel2"], text_color=C["text"])
    except Exception as e:
        # Hata durumunda boş grafik
        print(f"Işın İzi önizleme hatası: {e}")
        fig = None
```

**Sorun:** Simülasyon çalışmadan `d["_A"]` mevcut olmayabilir!

**Çözüm:** Mesh'i ayrı yükle:
```python
elif option == "Işın İzi":
    # Mesh'i kontrol et
    if self._mesh_A is None:
        # Mesh yüklenmemiş, yükle
        try:
            from simulation_core import read_unv_mesh_optimized
            fp = self._file_path.get()
            A, B, C = read_unv_mesh_optimized(fp)
            self._mesh_A, self._mesh_B, self._mesh_C = A, B, C
        except:
            # Mesh yüklenemedi, hata göster
            fig = None
    
    if self._mesh_A is not None:
        # Parametreleri al ve önizleme oluştur
        ...
```

---

### Adım 3: Alternatif Yaklaşım (Daha Basit)

**Işın İzi'ni tamamen önizleme yap:**

1. Simülasyon sekmesinden kaldır
2. Önizleme sayfasına ekle
3. Veya: Ayarlar sayfasında "Işın Yönleri" butonu ekle

**Avantaj:** Daha mantıklı - önizleme önizleme sayfasında olmalı
**Dezavantaj:** UI değişikliği gerekir

---

## 🎨 Görsel Tasarım

### Önizleme Modu
```
┌─────────────────────────────────────────┐
│  Işın Yönleri Önizlemesi                │
├─────────────────────────────────────────┤
│                                         │
│     Mesh (transparan, gri)              │
│                                         │
│        ╲  |  ╱                          │
│         ╲ | ╱                           │
│          ╲|╱                            │
│      ✖️ Kaynak                          │
│          ╱|╲                            │
│         ╱ | ╲                           │
│        ╱  |  ╲                          │
│                                         │
│  Mavi oklar: Işın yönleri               │
│  (Simülasyon olmadan)                   │
└─────────────────────────────────────────┘
```

---

## ✅ Önerilen Uygulama

### Seçenek A: Işın İzi'ni Önizleme Yap (Basit)
1. `create_ray_trace_figure()` önizleme modunu ekle
2. `test.py`'de Işın İzi çağrısını önizleme için güncelle
3. Mesh'i otomatik yükle

### Seçenek B: Işın İzi'ni Kaldır, Önizleme'ye Ekle (Daha İyi)
1. Simülasyon sekmesinden "Işın İzi"ni kaldır
2. Önizleme sayfasına "Işın Yönleri" butonu ekle
3. Aynı görünüm ama önizleme sayfasında

**Hangisini tercih edersiniz?**
