"""
IŞIN SİMÜLASYONU – Profesyonel GUI (customtkinter)
Kurulum: pip install customtkinter psutil numba matplotlib numpy
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, scrolledtext
import threading
import queue
import sys
import time
import os
import numpy as np

from simulation_core_plucker import save_detailed_results_to_excel

# ── Tema ──────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Renk paleti ───────────────────────────────────────────────────────────────
C = {
    "bg":        "#0D1117",
    "panel":     "#161B22",
    "panel2":    "#1C2128",
    "border":    "#30363D",
    "accent":    "#58A6FF",
    "accent2":   "#3FB950",
    "accent3":   "#F78166",
    "accent4":   "#E3B341",
    "text":      "#E6EDF3",
    "text_dim":  "#8B949E",
    "btn":       "#21262D",
    "btn_hover": "#30363D",
    "run_btn":   "#238636",
    "run_hover": "#2EA043",
    "stop_btn":  "#DA3633",
    "stop_hover":"#F85149",
    "header_bg": "#0D1117",
}

# ══════════════════════════════════════════════════════════════════════════════
# YARDIMCI: stdout'u kuyruğa yönlendir
# ══════════════════════════════════════════════════════════════════════════════
class QueueStream:
    def __init__(self, q: queue.Queue):
        self.q = q
    def write(self, text):
        if text:
            self.q.put(text)
    def flush(self):
        pass


# ══════════════════════════════════════════════════════════════════════════════
# ANA PENCERE
# ══════════════════════════════════════════════════════════════════════════════
class SimulationGUI(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("IŞIN SİMÜLASYONU  —  Plücker + Precompute + BVH")
        self.geometry("1280x820")
        self.minsize(1100, 700)
        self.configure(fg_color=C["bg"])

        self._sim_thread   = None
        self._stop_flag    = threading.Event()
        self._log_queue    = queue.Queue()
        self._result_queue = queue.Queue()

        self._file_path = tk.StringVar(value="Kavite_230k.unv")
        self._origin_x  = tk.StringVar(value="0.0")
        self._origin_y  = tk.StringVar(value="-0.05")
        self._origin_z  = tk.StringVar(value="0.2")
        self._t_start   = tk.StringVar(value="75")
        self._t_end     = tk.StringVar(value="105")
        self._n_theta   = tk.StringVar(value="45")
        self._p_start   = tk.StringVar(value="75")
        self._p_end     = tk.StringVar(value="105")
        self._n_phi     = tk.StringVar(value="45")
        self._max_bounce= tk.StringVar(value="100")

        self._stat_vars = {k: tk.StringVar(value="—") for k in [
            "triangles","total_rays","bounces","hit_tris",
            "avg_angle","min_angle","max_angle",
            "sim_time","cpu_avg","cpu_max","ram_avg","ram_max"
        ]}

        self._build_ui()
        self._poll_log()

    # ─────────────────────────────────────────────────────────────────────────
    # UI İNŞASI
    # ─────────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Header ────────────────────────────────────────────────────────────
        hdr = ctk.CTkFrame(self, fg_color=C["panel"], corner_radius=0, height=64)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)

        ctk.CTkLabel(
            hdr, text="⬡  IŞIN SİMÜLASYONU",
            font=ctk.CTkFont(family="Courier New", size=20, weight="bold"),
            text_color=C["accent"]
        ).pack(side="left", padx=24, pady=16)

        ctk.CTkLabel(
            hdr, text="Plücker + Precompute + BVH Multi-Bounce Ray Tracer",
            font=ctk.CTkFont(size=12),
            text_color=C["text_dim"]
        ).pack(side="left", padx=0, pady=16)

        self._status_lbl = ctk.CTkLabel(
            hdr, text="● Hazır",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=C["accent2"]
        )
        self._status_lbl.pack(side="right", padx=24)

        # ── Ana gövde: sol panel + sağ alan ───────────────────────────────────
        body = ctk.CTkFrame(self, fg_color=C["bg"])
        body.pack(fill="both", expand=True, padx=0, pady=0)

        body.columnconfigure(0, weight=0, minsize=320)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        # Sol panel
        left = ctk.CTkFrame(body, fg_color=C["panel"], corner_radius=0, width=320)
        left.grid(row=0, column=0, sticky="nsew")
        left.pack_propagate(False)

        self._build_left(left)

        # Sağ: sekmeler
        right = ctk.CTkFrame(body, fg_color=C["bg"])
        right.grid(row=0, column=1, sticky="nsew", padx=(1,0))

        self._tab = ctk.CTkTabview(
            right,
            fg_color=C["panel"],
            segmented_button_fg_color=C["panel2"],
            segmented_button_selected_color=C["accent"],
            segmented_button_selected_hover_color="#79B8FF",
            segmented_button_unselected_color=C["panel2"],
            segmented_button_unselected_hover_color=C["btn_hover"],
            text_color=C["text"],
            corner_radius=8
        )
        self._tab.pack(fill="both", expand=True, padx=12, pady=12)

        self._tab.add("📊  Sonuçlar")
        self._tab.add("📋  Log")
        self._tab.add("ℹ️  Hakkında")

        self._build_results_tab(self._tab.tab("📊  Sonuçlar"))
        self._build_log_tab(self._tab.tab("📋  Log"))
        self._build_about_tab(self._tab.tab("ℹ️  Hakkında"))

    # ── Sol Panel ─────────────────────────────────────────────────────────────
    def _build_left(self, parent):
        scroll = ctk.CTkScrollableFrame(
            parent, fg_color=C["panel"],
            scrollbar_button_color=C["border"],
            scrollbar_button_hover_color=C["accent"]
        )
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        def section(title):
            f = ctk.CTkFrame(scroll, fg_color=C["panel2"],
                             corner_radius=8, border_width=1,
                             border_color=C["border"])
            f.pack(fill="x", padx=12, pady=(10,0))
            ctk.CTkLabel(
                f, text=title,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=C["accent"]
            ).pack(anchor="w", padx=12, pady=(8,4))
            return f

        def row(parent, label, var, placeholder=""):
            r = ctk.CTkFrame(parent, fg_color="transparent")
            r.pack(fill="x", padx=12, pady=3)
            ctk.CTkLabel(r, text=label, width=130, anchor="w",
                         font=ctk.CTkFont(size=12),
                         text_color=C["text_dim"]).pack(side="left")
            e = ctk.CTkEntry(r, textvariable=var, height=30,
                             fg_color=C["btn"], border_color=C["border"],
                             text_color=C["text"], font=ctk.CTkFont(size=12))
            e.pack(side="left", fill="x", expand=True)
            return e

        # Mesh dosyası
        sf = section("📁  Mesh Dosyası")
        fr = ctk.CTkFrame(sf, fg_color="transparent")
        fr.pack(fill="x", padx=12, pady=(0,8))
        ctk.CTkEntry(fr, textvariable=self._file_path, height=30,
                     fg_color=C["btn"], border_color=C["border"],
                     text_color=C["text"], font=ctk.CTkFont(size=11)
                     ).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(fr, text="...", width=36, height=30,
                      fg_color=C["btn"], hover_color=C["btn_hover"],
                      command=self._browse_file
                      ).pack(side="left", padx=(4,0))

        # Kaynak konumu
        sf2 = section("📡  Radar Kaynağı (m)")
        row(sf2, "X koordinatı", self._origin_x)
        row(sf2, "Y koordinatı", self._origin_y)
        row(sf2, "Z koordinatı", self._origin_z); _pad(sf2)

        # Theta
        sf3 = section("🔻  Theta — Dikey Açı (°)")
        row(sf3, "Başlangıç θ₀", self._t_start)
        row(sf3, "Bitiş θ₁",     self._t_end)
        row(sf3, "Adım sayısı",  self._n_theta); _pad(sf3)

        # Phi
        sf4 = section("🔹  Phi — Yatay Açı (°)")
        row(sf4, "Başlangıç φ₀", self._p_start)
        row(sf4, "Bitiş φ₁",     self._p_end)
        row(sf4, "Adım sayısı",  self._n_phi); _pad(sf4)

        # Sekme limiti
        sf5 = section("⚙️  Gelişmiş")
        row(sf5, "Maks sekme",   self._max_bounce); _pad(sf5)

        # Toplam ışın önizleme
        self._ray_preview = ctk.CTkLabel(
            scroll,
            text="Toplam Işın: 45 × 45 = 2025",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=C["accent4"]
        )
        self._ray_preview.pack(pady=(10,0))
        for v in [self._n_theta, self._n_phi]:
            v.trace_add("write", self._update_ray_preview)

        # Butonlar
        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.pack(fill="x", padx=12, pady=14)

        self._run_btn = ctk.CTkButton(
            btn_frame, text="▶  SİMÜLASYONU BAŞLAT",
            height=42, font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=C["run_btn"], hover_color=C["run_hover"],
            command=self._start_simulation
        )
        self._run_btn.pack(fill="x", pady=(0,6))

        self._stop_btn = ctk.CTkButton(
            btn_frame, text="⏹  DURDUR",
            height=36, font=ctk.CTkFont(size=12),
            fg_color=C["btn"], hover_color=C["stop_hover"],
            text_color=C["text_dim"],
            state="disabled",
            command=self._stop_simulation
        )
        self._stop_btn.pack(fill="x")

        # Progress bar
        self._progress = ctk.CTkProgressBar(
            scroll, mode="indeterminate",
            progress_color=C["accent"],
            fg_color=C["border"]
        )
        self._progress.pack(fill="x", padx=12, pady=(4,12))

    # ── Sonuçlar sekmesi ──────────────────────────────────────────────────────
    def _build_results_tab(self, parent):
        parent.configure(fg_color=C["panel"])

        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=16, pady=16)
        grid.columnconfigure((0,1,2), weight=1, uniform="col")

        def card(parent, col, row, title, keys_labels):
            f = ctk.CTkFrame(parent, fg_color=C["panel2"],
                             corner_radius=10, border_width=1,
                             border_color=C["border"])
            f.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            ctk.CTkLabel(f, text=title,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=C["accent"]
                         ).pack(anchor="w", padx=14, pady=(10,6))
            for key, label in keys_labels:
                r = ctk.CTkFrame(f, fg_color="transparent")
                r.pack(fill="x", padx=14, pady=2)
                ctk.CTkLabel(r, text=label, anchor="w",
                             font=ctk.CTkFont(size=11),
                             text_color=C["text_dim"]
                             ).pack(side="left")
                ctk.CTkLabel(r, textvariable=self._stat_vars[key],
                             font=ctk.CTkFont(size=13, weight="bold"),
                             text_color=C["text"]
                             ).pack(side="right", padx=(0,4))
            ctk.CTkFrame(f, fg_color="transparent", height=8).pack()
            return f

        grid.rowconfigure((0,1), weight=1)

        card(grid, 0, 0, "🔺  Mesh Bilgisi", [
            ("triangles",  "Yüklenen Üçgen"),
            ("total_rays", "Toplam Işın"),
        ])
        card(grid, 1, 0, "🔁  Sekme Sonuçları", [
            ("bounces",   "Toplam Sekme"),
            ("hit_tris",  "Çarpılan Üçgen"),
        ])
        card(grid, 2, 0, "📐  Çarpış Açıları", [
            ("avg_angle", "Ortalama (°)"),
            ("min_angle", "Min (°)"),
            ("max_angle", "Max (°)"),
        ])
        card(grid, 0, 1, "⏱️  Süre", [
            ("sim_time",  "Simülasyon (sn)"),
        ])
        card(grid, 1, 1, "🖥️  CPU", [
            ("cpu_avg",  "Ortalama (%)"),
            ("cpu_max",  "Maksimum (%)"),
        ])
        card(grid, 2, 1, "💾  RAM", [
            ("ram_avg",  "Ortalama (GB)"),
            ("ram_max",  "Maksimum (GB)"),
        ])

    # ── Log sekmesi ───────────────────────────────────────────────────────────
    def _build_log_tab(self, parent):
        parent.configure(fg_color=C["panel"])

        toolbar = ctk.CTkFrame(parent, fg_color="transparent", height=36)
        toolbar.pack(fill="x", padx=12, pady=(8,0))
        toolbar.pack_propagate(False)

        ctk.CTkLabel(toolbar, text="Konsol Çıktısı",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=C["text_dim"]
                     ).pack(side="left")

        ctk.CTkButton(toolbar, text="Temizle", width=80, height=28,
                      fg_color=C["btn"], hover_color=C["btn_hover"],
                      font=ctk.CTkFont(size=11),
                      command=self._clear_log
                      ).pack(side="right")

        self._log_box = ctk.CTkTextbox(
            parent,
            fg_color=C["bg"],
            text_color="#A8D8A8",
            font=ctk.CTkFont(family="Courier New", size=11),
            corner_radius=6,
            border_width=1,
            border_color=C["border"],
            wrap="word",
            state="disabled"
        )
        self._log_box.pack(fill="both", expand=True, padx=12, pady=(6,12))

    # ── Hakkında sekmesi ──────────────────────────────────────────────────────
    def _build_about_tab(self, parent):
        parent.configure(fg_color=C["panel"])
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(expand=True)

        ctk.CTkLabel(f, text="⬡  IŞIN SİMÜLASYONU",
                     font=ctk.CTkFont(family="Courier New", size=28, weight="bold"),
                     text_color=C["accent"]
                     ).pack(pady=(30,4))

        ctk.CTkLabel(f, text="Plücker + Precompute + BVH  Multi-Bounce Ray Tracer",
                     font=ctk.CTkFont(size=14),
                     text_color=C["text_dim"]
                     ).pack()

        info = [
            ("Algoritma",   "Plücker koordinatları + Precomputed edge moments"),
            ("Hızlandırma", "BVH (Bounding Volume Hierarchy) — AABB tabanlı"),
            ("Parallelism", "Numba JIT + prange (çok çekirdekli)"),
            ("Mesh Formatı","I-DEAS Universal (UNV) — Dataset 2411/2412"),
            ("Görselleştirme","Matplotlib 3D ısı haritası + açı histogramı"),
        ]
        ctk.CTkFrame(f, fg_color=C["border"], height=1, width=400
                     ).pack(pady=18)
        for k, v in info:
            r = ctk.CTkFrame(f, fg_color="transparent")
            r.pack(pady=3)
            ctk.CTkLabel(r, text=f"{k}:", width=140, anchor="e",
                         font=ctk.CTkFont(size=12),
                         text_color=C["text_dim"]).pack(side="left")
            ctk.CTkLabel(r, text=v,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=C["text"]).pack(side="left", padx=8)

    # ─────────────────────────────────────────────────────────────────────────
    # OLAYLAR
    # ─────────────────────────────────────────────────────────────────────────
    def _browse_file(self):
        path = filedialog.askopenfilename(
            title="UNV Mesh Dosyası Seç",
            filetypes=[("Universal Mesh", "*.unv"), ("Tüm Dosyalar", "*.*")]
        )
        if path:
            self._file_path.set(path)

    def _update_ray_preview(self, *_):
        try:
            nt = int(self._n_theta.get())
            np_ = int(self._n_phi.get())
            self._ray_preview.configure(
                text=f"Toplam Işın: {nt} × {np_} = {nt*np_:,}"
            )
        except ValueError:
            self._ray_preview.configure(text="Toplam Işın: —")

    def _clear_log(self):
        self._log_box.configure(state="normal")
        self._log_box.delete("0.0", "end")
        self._log_box.configure(state="disabled")

    def _append_log(self, text: str):
        self._log_box.configure(state="normal")
        self._log_box.insert("end", text)
        self._log_box.see("end")
        self._log_box.configure(state="disabled")

    def _set_status(self, text: str, color: str):
        self._status_lbl.configure(text=text, text_color=color)

    # ─────────────────────────────────────────────────────────────────────────
    # POLLING
    # ─────────────────────────────────────────────────────────────────────────
    def _poll_log(self):
        while not self._log_queue.empty():
            text = self._log_queue.get_nowait()
            self._append_log(text)

        while not self._result_queue.empty():
            data = self._result_queue.get_nowait()
            self._apply_results(data)

        self.after(80, self._poll_log)

    # ─────────────────────────────────────────────────────────────────────────
    # SİMÜLASYON BAŞLAT / DURDUR
    # ─────────────────────────────────────────────────────────────────────────
    def _start_simulation(self):
        if self._sim_thread and self._sim_thread.is_alive():
            return

        # Doğrulama
        try:
            t0   = float(self._t_start.get());  t1 = float(self._t_end.get())
            p0   = float(self._p_start.get());  p1 = float(self._p_end.get())
            nt   = int(self._n_theta.get());    np_ = int(self._n_phi.get())
            ox   = float(self._origin_x.get()); oy = float(self._origin_y.get())
            oz   = float(self._origin_z.get())
            maxb = int(self._max_bounce.get())
            assert t0 < t1 and p0 < p1 and nt > 0 and np_ > 0 and maxb > 0
        except Exception:
            self._append_log("[HATA] Geçersiz parametre girişi — lütfen değerleri kontrol edin.\n")
            return

        fp = self._file_path.get()
        if not os.path.isfile(fp):
            self._append_log(f"[HATA] Dosya bulunamadı: {fp}\n")
            return

        # UI güncelle
        self._run_btn.configure(state="disabled", text="⏳  Çalışıyor…")
        self._stop_btn.configure(state="normal", text_color=C["accent3"])
        self._progress.start()
        self._set_status("● Çalışıyor", C["accent4"])

        self._stop_flag.clear()
        self._clear_log()
        self._reset_stats()

        self._tab.set("📋  Log")

        params = dict(
            file_path=fp,
            origin=[ox, oy, oz],
            theta_range=(t0, t1), phi_range=(p0, p1),
            n_theta=nt, n_phi=np_,
            max_bounces=maxb
        )
        self._sim_thread = threading.Thread(
            target=self._simulation_worker,
            args=(params,), daemon=True
        )
        self._sim_thread.start()

    def _stop_simulation(self):
        self._stop_flag.set()
        self._append_log("\n[KULLANICI] Durdurma isteği gönderildi...\n")

    def _simulation_finished(self, results=None):
        self._run_btn.configure(state="normal", text="▶  SİMÜLASYONU BAŞLAT")
        self._stop_btn.configure(state="disabled", text_color=C["text_dim"])
        self._progress.stop()
        if results:
            self._set_status("● Tamamlandı", C["accent2"])
            self._result_queue.put(results)
            self._tab.set("📊  Sonuçlar")
        else:
            self._set_status("● Durduruldu", C["accent3"])

    # ─────────────────────────────────────────────────────────────────────────
    # SİMÜLASYON İŞÇİSİ (arka plan thread)
    # ─────────────────────────────────────────────────────────────────────────
    def _simulation_worker(self, params):
        old_stdout = sys.stdout
        sys.stdout = QueueStream(self._log_queue)

        try:
            # Simülasyon modülünü içe aktar
            from simulation_core_plucker import (
                read_unv_mesh_optimized,
                generate_beam_from_counts,
                plucker_method,
                bvh_tree,
                plucker_bvh_tracer,
                run_simulation,
                visualize
            )

            fp           = params["file_path"]
            origin       = params["origin"]
            theta_range  = params["theta_range"]
            phi_range    = params["phi_range"]
            n_theta      = params["n_theta"]
            n_phi        = params["n_phi"]
            max_bounces  = params["max_bounces"]

            print(f"\n[MESH] {fp} okunuyor...")
            A, B, C_ = read_unv_mesh_optimized(fp)
            num_tris = A.shape[0]
            print(f"  {num_tris:,} üçgen yüklendi.")

            if self._stop_flag.is_set():
                self.after(0, lambda: self._simulation_finished())
                return

            print("\n[PRECOMPUTE] Plücker kenar verileri hesaplanıyor...")
            dAB,mAB,dBC,mBC,dCA,mCA,N_arr,d_plane = plucker_method(A, B_, C_) \
                if False else plucker_method(A, B, C_)

            print("\n[BVH] Ağaç inşa ediliyor...")
            bvh_nodes, bvh_meta, bvh_tids = bvh_tree(A, B, C_)
            print(f"  {len(bvh_nodes)} düğüm oluşturuldu.")

            rays_o, rays_d = generate_beam_from_counts(
                origin, theta_range, phi_range, n_theta, n_phi
            )

            print("\n[WARM-UP] Numba JIT derleniyor...")
            plucker_bvh_tracer(
                rays_o[:2], rays_d[:2],
                dAB[:10], mAB[:10], dBC[:10], mBC[:10], dCA[:10], mCA[:10],
                N_arr[:10], d_plane[:10],
                bvh_nodes, bvh_meta, bvh_tids
            )
            print("[WARM-UP] Tamamlandı.")

            if self._stop_flag.is_set():
                self.after(0, lambda: self._simulation_finished())
                return

            hit_counts, avg_angles, bounce_paths, resource_data = run_simulation(
                rays_o, rays_d, A, B, C_,
                dAB, mAB, dBC, mBC, dCA, mCA,
                N_arr, d_plane,
                bvh_nodes, bvh_meta, bvh_tids,
                max_safety_limit=max_bounces
            )
            try:
                # params sözlüğünden n_theta ve n_phi değerlerini alıyoruz
                save_detailed_results_to_excel(
                    hit_counts, 
                    avg_angles, 
                    params["n_theta"], 
                    params["n_phi"]
                )
            except Exception as e:
                print(f"\n[EXCEL HATASI] Kayıt yapılamadı: {e}")

            active = hit_counts > 0
            results = dict(
                num_tris    = num_tris,
                total_rays  = n_theta * n_phi,
                hit_tris    = int(np.sum(active)),
                bounces     = len(bounce_paths),
                avg_angle   = float(np.mean(avg_angles[active])) if np.sum(active) else 0,
                min_angle   = float(np.min(avg_angles[active])) if np.sum(active) else 0,
                max_angle   = float(np.max(avg_angles[active])) if np.sum(active) else 0,
                sim_time    = resource_data["duration"],
                cpu_avg     = float(np.mean(resource_data["cpu"])) if resource_data["cpu"] else 0,
                cpu_max     = float(np.max(resource_data["cpu"])) if resource_data["cpu"] else 0,
                ram_avg     = float(np.mean(resource_data["ram"])) / 1024 if resource_data["ram"] else 0,
                ram_max     = float(np.max(resource_data["ram"])) / 1024 if resource_data["ram"] else 0,
            )

            # Matplotlib grafiklerini göster
            min_x,max_x = float(np.min(A[:,0])), float(np.max(A[:,0]))
            min_y,max_y = float(np.min(A[:,1])), float(np.max(A[:,1]))
            min_z,max_z = float(np.min(A[:,2])), float(np.max(A[:,2]))
            self.after(0, lambda: visualize(
                A, B, C_, hit_counts, avg_angles, bounce_paths,
                origin, theta_range, phi_range, n_theta, n_phi,
                min_x,max_x,min_y,max_y,min_z,max_z,
                resource_data=resource_data
            ))

            self.after(0, lambda: self._simulation_finished(results))

        except Exception as e:
            import traceback
            print(f"\n[HATA] {e}\n{traceback.format_exc()}")
            self.after(0, lambda: self._simulation_finished())

        finally:
            sys.stdout = old_stdout

    # ─────────────────────────────────────────────────────────────────────────
    # SONUÇ GÜNCELLE
    # ─────────────────────────────────────────────────────────────────────────
    def _reset_stats(self):
        for v in self._stat_vars.values():
            v.set("—")

    def _apply_results(self, r: dict):
        self._stat_vars["triangles"].set(f"{r['num_tris']:,}")
        self._stat_vars["total_rays"].set(f"{r['total_rays']:,}")
        self._stat_vars["hit_tris"].set(f"{r['hit_tris']:,}")
        self._stat_vars["bounces"].set(str(r["bounces"]))
        self._stat_vars["avg_angle"].set(f"{r['avg_angle']:.2f}")
        self._stat_vars["min_angle"].set(f"{r['min_angle']:.2f}")
        self._stat_vars["max_angle"].set(f"{r['max_angle']:.2f}")
        self._stat_vars["sim_time"].set(f"{r['sim_time']:.3f}")
        self._stat_vars["cpu_avg"].set(f"{r['cpu_avg']:.1f}")
        self._stat_vars["cpu_max"].set(f"{r['cpu_max']:.1f}")
        self._stat_vars["ram_avg"].set(f"{r['ram_avg']:.2f}")
        self._stat_vars["ram_max"].set(f"{r['ram_max']:.2f}")


# ── Yardımcı ──────────────────────────────────────────────────────────────────
def _pad(parent, h=8):
    ctk.CTkFrame(parent, fg_color="transparent", height=h).pack()


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = SimulationGUI()
    app.mainloop()
    