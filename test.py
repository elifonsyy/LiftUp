"""
IŞIN SİMÜLASYONU — MATLAB/Windows Tarzı GUI
Kurulum: pip install psutil numba matplotlib numpy
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
import sys
import os
import numpy as np

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# ══════════════════════════════════════════════════════════════════════════════
# RENK / FONT SABİTLERİ  (MATLAB / Windows Professional)
# ══════════════════════════════════════════════════════════════════════════════
BG      = "#F0F0F0"
PANEL   = "#FFFFFF"
HDR_BG  = "#3C6BC4"
NAV_BG  = "#E8E8E8"
BORDER  = "#C0C0C0"
ACCENT  = "#1755B0"
ACCENT2 = "#217346"
ACCENT3 = "#C0392B"
ACCENT4 = "#D4870A"
TXT     = "#1A1A1A"
TXT_DIM = "#606060"
TXT_HDR = "#FFFFFF"

FONT_UI   = "Segoe UI"
FONT_MONO = "Courier New"
F_NORMAL  = (FONT_UI, 10)
F_BOLD    = (FONT_UI, 10, "bold")
F_SMALL   = (FONT_UI, 9)
F_TITLE   = (FONT_UI, 13, "bold")
F_BIG     = (FONT_UI, 11, "bold")


# ══════════════════════════════════════════════════════════════════════════════
# TEMA
# ══════════════════════════════════════════════════════════════════════════════
def apply_theme(root):
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".", background=BG, foreground=TXT, font=F_NORMAL, relief="flat")
    style.configure("TFrame", background=BG)
    style.configure("White.TFrame", background=PANEL)
    style.configure("Nav.TFrame", background=NAV_BG)
    style.configure("Hdr.TFrame", background=HDR_BG)
    style.configure("TLabel", background=BG, foreground=TXT, font=F_NORMAL)
    style.configure("Hdr.TLabel", background=HDR_BG, foreground=TXT_HDR, font=F_BIG)
    style.configure("Sub.TLabel", background=HDR_BG, foreground="#C8DCFF", font=F_SMALL)
    style.configure("White.TLabel", background=PANEL, foreground=TXT, font=F_NORMAL)
    style.configure("Dim.TLabel", background=BG, foreground=TXT_DIM, font=F_SMALL)
    style.configure("Dim2.TLabel", background=PANEL, foreground=TXT_DIM, font=F_SMALL)
    style.configure("Title.TLabel", background=BG, foreground=ACCENT, font=F_TITLE)
    style.configure("Stat.TLabel", background=PANEL, foreground=TXT, font=(FONT_UI, 18, "bold"))
    style.configure("StatSm.TLabel", background=PANEL, foreground=TXT, font=(FONT_UI, 12, "bold"))
    style.configure("Status.TLabel", background=HDR_BG, foreground="#90EE90", font=F_BOLD)
    style.configure("RaySummary.TLabel", background=BG, foreground=ACCENT4, font=F_BOLD)
    style.configure("TEntry", fieldbackground=PANEL, background=PANEL,
                    foreground=TXT, font=F_NORMAL, borderwidth=1, relief="solid", padding=4)
    style.configure("TButton", background="#E1E1E1", foreground=TXT, font=F_NORMAL,
                    relief="raised", borderwidth=1, padding=(8, 4))
    style.map("TButton", background=[("active", "#D0D0D0"), ("pressed", "#C0C0C0")])
    style.configure("Run.TButton", background=ACCENT2, foreground="white", font=F_BOLD,
                    relief="raised", borderwidth=1, padding=(10, 5))
    style.map("Run.TButton", background=[("active", "#25864F"), ("disabled", "#8FBC8F")])
    style.configure("Stop.TButton", background="#C0392B", foreground="white", font=F_NORMAL,
                    relief="raised", borderwidth=1, padding=(8, 5))
    style.map("Stop.TButton", background=[("active", "#A93226"), ("disabled", "#D5A0A0")])
    style.configure("Blue.TButton", background=ACCENT, foreground="white", font=F_BOLD,
                    relief="raised", borderwidth=1, padding=(10, 5))
    style.map("Blue.TButton", background=[("active", "#1E6ACF"), ("disabled", "#8AAAD8")])
    style.configure("Tool.TButton", background="#E1E1E1", foreground=TXT, font=F_SMALL,
                    relief="raised", borderwidth=1, padding=(5, 3))
    style.configure("TNotebook", background=NAV_BG, tabmargins=[0, 0, 0, 0])
    style.configure("TNotebook.Tab", background=NAV_BG, foreground=TXT_DIM,
                    font=F_NORMAL, padding=[14, 7], borderwidth=1, relief="flat")
    style.map("TNotebook.Tab",
              background=[("selected", PANEL), ("active", "#D8D8D8")],
              foreground=[("selected", ACCENT)],
              font=[("selected", F_BOLD)])
    style.configure("TLabelframe", background=BG, borderwidth=1, relief="groove")
    style.configure("TLabelframe.Label", background=BG, foreground=ACCENT, font=F_BOLD)
    style.configure("TScrollbar", background="#D0D0D0", troughcolor=BG,
                    arrowcolor=TXT_DIM, borderwidth=1, relief="flat", width=14)
    style.configure("TProgressbar", troughcolor="#D0D0D0", background=ACCENT,
                    borderwidth=0, relief="flat", thickness=12)
    style.configure("Treeview", background=PANEL, foreground=TXT, font=F_NORMAL,
                    fieldbackground=PANEL, rowheight=24, borderwidth=1, relief="solid")
    style.configure("Treeview.Heading", background="#E0E8F4", foreground=ACCENT,
                    font=F_BOLD, relief="flat")
    style.map("Treeview", background=[("selected", "#CCE0FF")],
              foreground=[("selected", ACCENT)])
    style.configure("TSeparator", background=BORDER)
    style.configure("TRadiobutton", background=BG, foreground=TXT, font=F_NORMAL)
    style.configure("TScale", background=BG, troughcolor="#C8C8C8", sliderthickness=14)


# ══════════════════════════════════════════════════════════════════════════════
# YARDIMCILAR
# ══════════════════════════════════════════════════════════════════════════════
def make_labelframe(parent, title, padding=8, **kw):
    return ttk.LabelFrame(parent, text=title, padding=padding, **kw)

def make_entry(parent, textvariable, width=14):
    return ttk.Entry(parent, textvariable=textvariable, width=width, justify="right")

def make_btn(parent, text, command, style="TButton", width=None):
    kw = {"width": width} if width else {}
    return ttk.Button(parent, text=text, command=command, style=style, **kw)

def scrollable_frame(parent):
    outer  = ttk.Frame(parent)
    canvas = tk.Canvas(outer, background=BG, highlightthickness=0, bd=0)
    vsb    = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    inner  = ttk.Frame(canvas)
    win_id = canvas.create_window((0, 0), window=inner, anchor="nw")
    def _on_resize(e):  canvas.itemconfig(win_id, width=e.width)
    def _on_inner(e):   canvas.configure(scrollregion=canvas.bbox("all"))
    def _on_wheel(e):   canvas.yview_scroll(int(-1*(e.delta/120)), "units")
    canvas.bind("<Configure>", _on_resize)
    inner.bind("<Configure>", _on_inner)
    canvas.bind_all("<MouseWheel>", _on_wheel)
    return outer, inner


# ══════════════════════════════════════════════════════════════════════════════
# ANA PENCERE
# ══════════════════════════════════════════════════════════════════════════════
class SimulationGUI(tk.Tk):

    PAGES = [
        ("⚙",  "Ayarlar"),
        ("👁",  "Önizleme"),
        ("▶",  "Simülasyon"),
        ("📊", "Sonuçlar"),
        ("📄", "Rapor"),
        ("❓", "Yardım"),
    ]

    def __init__(self):
        super().__init__()
        self.title("IŞIN SİMÜLASYONU  —  Plücker + BVH")
        self.geometry("1400x900")
        self.minsize(1100, 720)
        self.configure(background=BG)
        apply_theme(self)

        self._sim_thread   = None
        self._stop_flag    = threading.Event()
        self._result_queue = queue.Queue()
        self._mesh_A = self._mesh_B = self._mesh_C = None

        self._file_path   = tk.StringVar(value="Lift_Up_Model.unv")
        self._source_type = tk.StringVar(value="Noktasal")
        self._origin_x    = tk.StringVar(value="0.0")
        self._origin_y    = tk.StringVar(value="-0.05")
        self._origin_z    = tk.StringVar(value="0.2")
        self._t_start     = tk.StringVar(value="75")
        self._t_end       = tk.StringVar(value="105")
        self._n_theta     = tk.StringVar(value="45")
        self._p_start     = tk.StringVar(value="75")
        self._p_end       = tk.StringVar(value="105")
        self._n_phi       = tk.StringVar(value="45")
        self._max_bounce  = tk.StringVar(value="100")
        self._num_threads = tk.IntVar(value=0)   # 0 = otomatik (tüm çekirdekler)
        self._cam_elev    = tk.DoubleVar(value=20.0)
        self._cam_azim    = tk.DoubleVar(value=45.0)

        self._stat_vars = {k: tk.StringVar(value="—") for k in [
            "triangles","total_rays","bounces","hit_tris",
            "avg_angle","min_angle","max_angle","std_angle","var_angle",
            "ray_tracing_time","cpu_avg","cpu_max","ram_avg","ram_max",
            "file_read_time","plucker_time","bvh_time","ray_gen_time",
            "jit_time","benchmark_time","wall_clock_total",
            "bounce_count","avg_bounce_time","min_bounce_time",
            "max_bounce_time","std_bounce_time","avg_hit_rate","last_hit_rate"
        ]}

        self._preview_canvas   = None
        self._preview_fig      = None
        self._preview_toolbar  = None
        self._mesh_mini_canvas = None
        self._mesh_mini_fig    = None
        self._sim_canvas       = None
        self._sim_fig          = None
        self._sim_toolbar      = None

        self._current_sim_tab     = tk.StringVar(value="Üçgen Işın")
        self._current_sub_option  = tk.StringVar(value="Işın Yolu")
        self._sim_data            = None
        self._sim_sub_option_btns = {}
        self._sim_tab_btns        = {}
        self._graph_cache         = {}
        self._excel_filename      = None

        self._build_ui()
        self._poll()

    # ══════════════════════════════════════════════════════════════════════════
    # UI
    # ══════════════════════════════════════════════════════════════════════════
    def _build_ui(self):
        self._build_header()
        self._build_notebook()

    def _build_header(self):
        hdr = ttk.Frame(self, style="Hdr.TFrame", height=54)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        logo_f = ttk.Frame(hdr, style="Hdr.TFrame")
        logo_f.pack(side="left", padx=20, pady=8)
        ttk.Label(logo_f, text="⬡ IŞIN SİMÜLASYONU", style="Hdr.TLabel").pack(side="left")
        ttk.Label(logo_f, text="   Plücker + Precompute + BVH", style="Sub.TLabel").pack(side="left", pady=(4,0))
        self._status_dot = ttk.Label(hdr, text="● Hazır", style="Status.TLabel")
        self._status_dot.pack(side="right", padx=24)
        ttk.Separator(self, orient="horizontal").pack(fill="x")

    def _build_notebook(self):
        self._nb = ttk.Notebook(self)
        self._nb.pack(fill="both", expand=True)
        self._pages = {}
        for icon, name in self.PAGES:
            f = ttk.Frame(self._nb)
            self._nb.add(f, text=f"  {icon}  {name}  ")
            self._pages[name] = f
        self._build_page_ayarlar()
        self._build_page_onizleme()
        self._build_page_simulasyon()
        self._build_page_sonuclar()
        self._build_page_rapor()
        self._build_page_yardim()

    def _show_page(self, name):
        names = [n for _, n in self.PAGES]
        if name in names:
            self._nb.select(names.index(name))

    # ══════════════════════════════════════════════════════════════════════════
    # SAYFA: AYARLAR
    # ══════════════════════════════════════════════════════════════════════════
    def _build_page_ayarlar(self):
        page = self._pages["Ayarlar"]
        left = ttk.Frame(page, width=470)
        left.pack(side="left", fill="both", expand=False, padx=(14,6), pady=10)
        left.pack_propagate(False)
        sc_outer, sc_inner = scrollable_frame(left)
        sc_outer.pack(fill="both", expand=True)
        self._build_param_panel(sc_inner)
        right = ttk.Frame(page)
        right.pack(side="left", fill="both", expand=True, padx=(0,14), pady=10)
        self._build_right_panel(right)

    def _build_param_panel(self, parent):
        # Mesh
        lf = make_labelframe(parent, "📁  Mesh Dosyası")
        lf.pack(fill="x", pady=(0,8))
        fr = ttk.Frame(lf)
        fr.pack(fill="x")
        ttk.Entry(fr, textvariable=self._file_path, width=32).pack(side="left", fill="x", expand=True)
        make_btn(fr, " … ", self._browse_file, "Tool.TButton").pack(side="left", padx=(4,0))

        # Işın Kaynağı
        lf2 = make_labelframe(parent, "📡  Işın Kaynağı")
        lf2.pack(fill="x", pady=(0,8))
        src_f = ttk.Frame(lf2)
        src_f.pack(fill="x", pady=(0,6))
        ttk.Label(src_f, text="Kaynak Tipi:").pack(side="left")
        ttk.Radiobutton(src_f, text="Noktasal", variable=self._source_type,
                        value="Noktasal", command=self._on_source_type_change).pack(side="left", padx=8)
        ttk.Radiobutton(src_f, text="Paralel", variable=self._source_type,
                        value="Paralel", command=self._on_source_type_change).pack(side="left")
        self._origin_frame = ttk.Frame(lf2)
        self._origin_frame.pack(fill="x")
        for lbl, var in [("X  (m)", self._origin_x), ("Y  (m)", self._origin_y), ("Z  (m)", self._origin_z)]:
            r = ttk.Frame(self._origin_frame)
            r.pack(fill="x", pady=2)
            ttk.Label(r, text=lbl, width=16).pack(side="left")
            make_entry(r, var, width=14).pack(side="right")

        # Theta
        lf3 = make_labelframe(parent, "🔻  Theta — Dikey Açı")
        lf3.pack(fill="x", pady=(0,8))
        for lbl, var in [("Başlangıç θ₀  (°)", self._t_start),
                         ("Bitiş θ₁  (°)", self._t_end),
                         ("Adım sayısı", self._n_theta)]:
            r = ttk.Frame(lf3)
            r.pack(fill="x", pady=2)
            ttk.Label(r, text=lbl, width=20).pack(side="left")
            make_entry(r, var, width=14).pack(side="right")

        # Phi
        lf4 = make_labelframe(parent, "🔹  Phi — Yatay Açı")
        lf4.pack(fill="x", pady=(0,8))
        for lbl, var in [("Başlangıç φ₀  (°)", self._p_start),
                         ("Bitiş φ₁  (°)", self._p_end),
                         ("Adım sayısı", self._n_phi)]:
            r = ttk.Frame(lf4)
            r.pack(fill="x", pady=2)
            ttk.Label(r, text=lbl, width=20).pack(side="left")
            make_entry(r, var, width=14).pack(side="right")

        # Gelişmiş
        lf5 = make_labelframe(parent, "⚙️  Gelişmiş")
        lf5.pack(fill="x", pady=(0,8))
        r = ttk.Frame(lf5)
        r.pack(fill="x", pady=2)
        ttk.Label(r, text="Maks sekme sayısı", width=20).pack(side="left")
        make_entry(r, self._max_bounce, width=14).pack(side="right")

        # CPU Çekirdeği
        import psutil as _psutil
        self._total_cores = _psutil.cpu_count(logical=True) or 1
        lf6 = make_labelframe(parent, "🖥️  CPU Çekirdeği Kullanımı")
        lf6.pack(fill="x", pady=(0,8))

        # Bilgi satırı
        info_f = ttk.Frame(lf6)
        info_f.pack(fill="x", pady=(0,6))
        ttk.Label(info_f, text=f"Sistemde {self._total_cores} mantıksal çekirdek mevcut.",
                  style="Dim.TLabel").pack(side="left")

        # Slider satırı
        sl_f = ttk.Frame(lf6)
        sl_f.pack(fill="x", pady=(0,4))
        ttk.Label(sl_f, text="Çekirdek sayısı:", width=18).pack(side="left")
        self._thread_val_lbl = ttk.Label(
            sl_f, text="Otomatik (tüm çekirdekler)",
            foreground=ACCENT, font=F_BOLD, background=BG)
        self._thread_val_lbl.pack(side="right")

        self._thread_slider = ttk.Scale(
            lf6, from_=0, to=self._total_cores,
            orient="horizontal", variable=self._num_threads,
            command=self._on_thread_slider)
        self._thread_slider.pack(fill="x", pady=(0,4))

        # Hızlı seçim butonları
        btn_row = ttk.Frame(lf6)
        btn_row.pack(fill="x")
        for label, val in [("Otomatik", 0),
                           ("¼", max(1, self._total_cores // 4)),
                           ("½", max(1, self._total_cores // 2)),
                           ("¾", max(1, self._total_cores * 3 // 4)),
                           ("Tümü", self._total_cores)]:
            make_btn(btn_row, label,
                     lambda v=val: [self._num_threads.set(v),
                                    self._on_thread_slider(v)],
                     "Tool.TButton").pack(side="left", padx=2)

        # Işın özeti
        self._ray_summary = ttk.Label(parent, text="Toplam: 45 × 45 = 2,025 ışın",
                                       style="RaySummary.TLabel")
        self._ray_summary.pack(pady=(10,4))
        for v in [self._n_theta, self._n_phi]:
            v.trace_add("write", self._update_ray_summary)

        # Butonlar
        btn_f = ttk.Frame(parent)
        btn_f.pack(fill="x", pady=(8,2))
        make_btn(btn_f, "👁   Önizlemeye Git",
                 lambda: [self._render_preview(), self._show_page("Önizleme")],
                 "Blue.TButton").pack(side="left", fill="x", expand=True, padx=(0,4))
        make_btn(btn_f, "▶   Simülasyona Git",
                 lambda: self._show_page("Simülasyon"),
                 "Run.TButton").pack(side="left", fill="x", expand=True)

    def _build_right_panel(self, parent):
        mesh_lf = make_labelframe(parent, "📐  Mesh Önizlemesi")
        mesh_lf.pack(fill="both", expand=True, pady=(0,8))
        self._mesh_preview_frame = ttk.Frame(mesh_lf, style="White.TFrame")
        self._mesh_preview_frame.pack(fill="both", expand=True)
        self._mesh_placeholder = ttk.Label(
            self._mesh_preview_frame,
            text="Mesh dosyası seçilince\nkavite önizlemesi burada görünür",
            style="Dim2.TLabel", anchor="center", justify="center")
        self._mesh_placeholder.place(relx=0.5, rely=0.5, anchor="center")

        cam_lf = make_labelframe(parent, "🎥  Kamera Açısı")
        cam_lf.pack(fill="x")
        er = ttk.Frame(cam_lf)
        er.pack(fill="x", pady=(0,2))
        ttk.Label(er, text="Yükseklik (Elev)").pack(side="left")
        self._elev_lbl = ttk.Label(er, text="20°", foreground=ACCENT, font=F_BOLD, background=BG)
        self._elev_lbl.pack(side="right")
        ttk.Scale(cam_lf, from_=-90, to=90, orient="horizontal", variable=self._cam_elev,
                  command=lambda v: self._elev_lbl.configure(text=f"{int(float(v))}°")
                  ).pack(fill="x", pady=(0,8))
        ar = ttk.Frame(cam_lf)
        ar.pack(fill="x", pady=(0,2))
        ttk.Label(ar, text="Yatay (Azim)").pack(side="left")
        self._azim_lbl = ttk.Label(ar, text="45°", foreground=ACCENT, font=F_BOLD, background=BG)
        self._azim_lbl.pack(side="right")
        ttk.Scale(cam_lf, from_=0, to=360, orient="horizontal", variable=self._cam_azim,
                  command=lambda v: self._azim_lbl.configure(text=f"{int(float(v))}°")
                  ).pack(fill="x")

    # ══════════════════════════════════════════════════════════════════════════
    # SAYFA: ÖNİZLEME
    # ══════════════════════════════════════════════════════════════════════════
    def _build_page_onizleme(self):
        page = self._pages["Önizleme"]
        tb = ttk.Frame(page, style="Nav.TFrame", height=44)
        tb.pack(fill="x"); tb.pack_propagate(False)
        ttk.Label(tb, text="  👁  Işın Önizlemesi", font=F_BIG,
                  foreground=ACCENT, background=NAV_BG).pack(side="left", padx=8, pady=8)
        ttk.Separator(tb, orient="vertical").pack(side="left", fill="y", pady=6, padx=4)
        make_btn(tb, "🔄  Yenile", self._render_preview, "Tool.TButton").pack(side="left", pady=6)
        ttk.Separator(page, orient="horizontal").pack(fill="x")
        self._preview_area = ttk.Frame(page, style="White.TFrame")
        self._preview_area.pack(fill="both", expand=True)
        self._preview_placeholder = ttk.Label(
            self._preview_area,
            text="Ayarlar sayfasından 'Önizlemeye Git' butonuna basın\n"
                 "veya yukarıdaki 🔄 Yenile butonunu kullanın.",
            style="Dim2.TLabel", anchor="center", justify="center")
        self._preview_placeholder.place(relx=0.5, rely=0.5, anchor="center")

    def _render_preview(self):
        try:
            t0  = float(self._t_start.get()); t1  = float(self._t_end.get())
            p0  = float(self._p_start.get()); p1  = float(self._p_end.get())
            nt  = int(self._n_theta.get());   np_ = int(self._n_phi.get())
        except ValueError:
            return
        src = self._source_type.get()
        if src == "Noktasal":
            try:
                origin = np.array([float(self._origin_x.get()),
                                   float(self._origin_y.get()),
                                   float(self._origin_z.get())])
            except ValueError:
                return
        else:
            origin = None

        if self._preview_canvas:
            self._preview_canvas.get_tk_widget().destroy()
            plt.close(self._preview_fig)
            self._preview_canvas = None
        if self._preview_toolbar:
            self._preview_toolbar.destroy()   # toolbar_frame'i yok et
            self._preview_toolbar = None
        self._preview_placeholder.place_forget()

        thetas = np.radians(np.linspace(t0, t1, min(nt, 10)))
        phis   = np.radians(np.linspace(p0, p1, min(np_, 10)))

        fig = plt.Figure(facecolor=PANEL)
        ax  = fig.add_subplot(111, projection="3d")
        ax.set_facecolor("#F8F8F8")
        fig.subplots_adjust(left=0.0, right=1.0, top=0.95, bottom=0.04)
        fig.suptitle(
            f"{'Noktasal' if src=='Noktasal' else 'Paralel'}  |"
            f"  θ: {t0}°–{t1}°   φ: {p0}°–{p1}°",
            color=TXT_DIM, fontsize=11)

        mesh_center = np.zeros(3)
        mesh_scale  = 1.0
        if self._mesh_A is not None:
            A, B, Cm = self._mesh_A, self._mesh_B, self._mesh_C
            all_pts  = np.concatenate([A, B, Cm], axis=0)
            mn, mx   = all_pts.min(0), all_pts.max(0)
            mesh_center = (mn + mx) / 2.0
            mesh_scale  = float((mx - mn).max())
            step = max(1, len(A) // 6000)
            pts  = np.concatenate([A[::step], B[::step], Cm[::step]], axis=0)
            z    = pts[:, 2]
            zn   = (z - z.min()) / max(float(z.max() - z.min()), 1e-9)
            cols = plt.cm.Blues(0.25 + 0.6 * zn)
            ax.scatter(pts[:,0], pts[:,1], pts[:,2],
                       c=cols, s=0.6, linewidths=0, depthshade=True, alpha=0.55)
            mr = mesh_scale / 2.0
            ax.set_xlim(mesh_center[0]-mr, mesh_center[0]+mr)
            ax.set_ylim(mesh_center[1]-mr, mesh_center[1]+mr)
            ax.set_zlim(mesh_center[2]-mr, mesh_center[2]+mr)

        RAY_LEN = mesh_scale * 0.55
        if src == "Noktasal":
            for theta in thetas:
                for phi in phis:
                    d  = np.array([np.sin(theta)*np.cos(phi),
                                   np.sin(theta)*np.sin(phi), np.cos(theta)])
                    ep = origin + d * RAY_LEN
                    ax.plot([origin[0],ep[0]],[origin[1],ep[1]],[origin[2],ep[2]],
                            color=ACCENT, alpha=0.8, linewidth=1.0)
            ax.scatter(*origin, color="cyan", s=60, marker="X", zorder=10,
                       label=f"Kaynak ({origin[0]:.2f},{origin[1]:.2f},{origin[2]:.2f})")
            ax.legend(fontsize=8)
        else:
            # Paralel kaynak: merkez yönü hesapla, mesh'e dik düzlemden grid
            theta_c = np.radians((t0 + t1) / 2.0)
            phi_c   = np.radians((p0 + p1) / 2.0)
            d_center = np.array([
                np.sin(theta_c) * np.cos(phi_c),
                np.sin(theta_c) * np.sin(phi_c),
                np.cos(theta_c)
            ])
            d_center /= np.linalg.norm(d_center)

            # Dik eksenler
            ref = np.array([0.0, 0.0, 1.0])
            if abs(np.dot(d_center, ref)) > 0.9:
                ref = np.array([1.0, 0.0, 0.0])
            u_ax = np.cross(d_center, ref); u_ax /= np.linalg.norm(u_ax)
            v_ax = np.cross(d_center, u_ax); v_ax /= np.linalg.norm(v_ax)

            # Önizleme için 5×5 grid (max 10×10)
            n_prev = min(nt, 5)
            m_prev = min(np_, 5)
            u_steps = np.linspace(-mesh_scale * 0.5, mesh_scale * 0.5, n_prev)
            v_steps = np.linspace(-mesh_scale * 0.5, mesh_scale * 0.5, m_prev)
            start_center = mesh_center - d_center * RAY_LEN

            for us in u_steps:
                for vs in v_steps:
                    sp = start_center + us * u_ax + vs * v_ax
                    ep = sp + d_center * RAY_LEN * 1.8
                    ax.plot([sp[0], ep[0]], [sp[1], ep[1]], [sp[2], ep[2]],
                            color=ACCENT2, alpha=0.8, linewidth=1.0)

            # Kaynak düzlemini göster
            corners_u = [-mesh_scale*0.5, mesh_scale*0.5,
                         mesh_scale*0.5, -mesh_scale*0.5, -mesh_scale*0.5]
            corners_v = [-mesh_scale*0.5, -mesh_scale*0.5,
                         mesh_scale*0.5,  mesh_scale*0.5, -mesh_scale*0.5]
            px = [start_center[0] + cu*u_ax[0] + cv*v_ax[0]
                  for cu, cv in zip(corners_u, corners_v)]
            py = [start_center[1] + cu*u_ax[1] + cv*v_ax[1]
                  for cu, cv in zip(corners_u, corners_v)]
            pz = [start_center[2] + cu*u_ax[2] + cv*v_ax[2]
                  for cu, cv in zip(corners_u, corners_v)]
            ax.plot(px, py, pz, color=ACCENT2, alpha=0.4,
                    linewidth=1.5, linestyle="--")

        for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
            axis.pane.fill = False
            axis.pane.set_edgecolor(BORDER)
            axis.line.set_color(BORDER)
        ax.tick_params(colors=TXT_DIM, labelsize=7)
        ax.set_xlabel("X (m)", color=TXT_DIM, fontsize=8)
        ax.set_ylabel("Y (m)", color=TXT_DIM, fontsize=8)
        ax.set_zlabel("Z (m)", color=TXT_DIM, fontsize=8)
        ax.grid(True, color=BORDER, linewidth=0.3, alpha=0.5)
        ax.view_init(elev=int(self._cam_elev.get()), azim=int(self._cam_azim.get()))
        try: ax.dist = 8
        except: pass

        toolbar_frame = tk.Frame(self._preview_area, background=NAV_BG, height=36)
        toolbar_frame.pack(side="bottom", fill="x")
        canvas = FigureCanvasTkAgg(fig, master=self._preview_area)
        nav = NavigationToolbar2Tk(canvas, toolbar_frame)
        nav.update()
        self._preview_toolbar = toolbar_frame   # frame'i sakla, destroy için
        canvas.draw()
        canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        self._preview_canvas = canvas
        self._preview_fig    = fig

    # ══════════════════════════════════════════════════════════════════════════
    # SAYFA: SİMÜLASYON
    # ══════════════════════════════════════════════════════════════════════════
    def _build_page_simulasyon(self):
        page = self._pages["Simülasyon"]
        # Toolbar
        tb = ttk.Frame(page, style="Nav.TFrame", height=48)
        tb.pack(fill="x"); tb.pack_propagate(False)
        self._run_btn = make_btn(tb, "▶   Simülasyonu Başlat",
                                  self._start_simulation, "Run.TButton")
        self._run_btn.pack(side="left", padx=10, pady=6)
        self._stop_btn = make_btn(tb, "⏹  Durdur",
                                   self._stop_simulation, "Stop.TButton")
        self._stop_btn.pack(side="left", padx=(0,10), pady=6)
        self._stop_btn.configure(state="disabled")
        ttk.Separator(tb, orient="vertical").pack(side="left", fill="y", pady=6, padx=4)
        self._progress = ttk.Progressbar(tb, mode="indeterminate", length=180)
        self._progress.pack(side="left", padx=8, pady=16)
        self._sim_status_lbl = ttk.Label(tb, text="", foreground=TXT_DIM,
                                          background=NAV_BG, font=F_SMALL)
        self._sim_status_lbl.pack(side="left", padx=8)
        ttk.Separator(page, orient="horizontal").pack(fill="x")

        # Grafik
        self._sim_visual_area = ttk.Frame(page, style="White.TFrame")
        self._sim_visual_area.pack(fill="both", expand=True)
        self._sim_placeholder = ttk.Label(
            self._sim_visual_area,
            text="Simülasyon tamamlanınca grafik burada gösterilecek.\n\n"
                 "Alttaki sekmelerden farklı görünümler seçebilirsiniz.",
            style="Dim2.TLabel", anchor="center", justify="center")
        self._sim_placeholder.place(relx=0.5, rely=0.5, anchor="center")
        ttk.Separator(page, orient="horizontal").pack(fill="x")

        # Alt sekme çubuğu
        tab_bar = ttk.Frame(page, style="Nav.TFrame", height=42)
        tab_bar.pack(fill="x"); tab_bar.pack_propagate(False)
        sim_tabs = [("📊", "Üçgen Işın"), ("📈", "Histogram"), ("💻", "CPU/RAM")]
        self._sim_tab_btns = {}
        for icon, name in sim_tabs:
            btn = tk.Button(tab_bar, text=f"  {icon}  {name}  ",
                            font=(FONT_UI, 10, "bold"),
                            bg=NAV_BG, fg=TXT_DIM,
                            activebackground="#D0D8EC", activeforeground=ACCENT,
                            relief="flat", bd=0, cursor="hand2",
                            command=lambda n=name: self._on_sim_tab_change(n))
            btn.pack(side="left", padx=4, pady=4)
            self._sim_tab_btns[name] = btn
        self._sim_tab_btns["Üçgen Işın"].configure(bg=PANEL, fg=ACCENT)

        # Alt seçenek şeridi
        sub_bar = ttk.Frame(page, style="TFrame", height=40)
        sub_bar.pack(fill="x"); sub_bar.pack_propagate(False)
        lbl = ttk.Label(sub_bar, text="Görünüm:", font=F_SMALL, foreground=TXT_DIM)
        lbl.pack(side="left", padx=(10,4), pady=8)
        ttk.Separator(sub_bar, orient="vertical").pack(side="left", fill="y", pady=4)
        self._sub_option_container = ttk.Frame(sub_bar)
        self._sub_option_container.pack(side="left", padx=6, pady=4, fill="y")
        self._build_sub_options("Üçgen Işın")

    def _build_sub_options(self, tab_name):
        for w in self._sub_option_container.winfo_children():
            w.destroy()
        self._sim_sub_option_btns.clear()
        sub_options = {
            "Üçgen Işın": [("🔵","Işın Yolu"),("🔥","Isı Haritası")],
            "Histogram":  [("📈","Sekme Dağılımı"),("🎯","Gelen Açı"),("🔄","Seken Açı")],
            "CPU/RAM":    [("🖥","CPU Kullanımı"),("💾","RAM Kullanımı")],
        }
        if tab_name not in sub_options:
            return
        for icon, name in sub_options[tab_name]:
            btn = tk.Button(self._sub_option_container,
                            text=f"{icon}  {name}", font=(FONT_UI, 10),
                            bg="#E0E8F4", fg=TXT_DIM,
                            activebackground="#CCE0FF", activeforeground=ACCENT,
                            relief="flat", bd=1, cursor="hand2", padx=10, pady=3,
                            command=lambda n=name: self._on_sim_sub_option_change(n))
            btn.pack(side="left", padx=3)
            self._sim_sub_option_btns[name] = btn
        first = sub_options[tab_name][0][1]
        self._current_sub_option.set(first)
        self._sim_sub_option_btns[first].configure(bg="#CCE0FF", fg=ACCENT)

    def _on_sim_tab_change(self, tab_name):
        self._current_sim_tab.set(tab_name)
        for n, b in self._sim_tab_btns.items():
            b.configure(bg=PANEL if n==tab_name else NAV_BG,
                        fg=ACCENT if n==tab_name else TXT_DIM)
        self._build_sub_options(tab_name)
        if self._sim_data is not None:
            self._render_simulation_graph()

    def _on_sim_sub_option_change(self, option_name):
        self._current_sub_option.set(option_name)
        for n, b in self._sim_sub_option_btns.items():
            b.configure(bg="#CCE0FF" if n==option_name else "#E0E8F4",
                        fg=ACCENT if n==option_name else TXT_DIM)
        if self._sim_data is not None:
            self._render_simulation_graph()

    def _render_simulation_graph(self):
        if self._sim_data is None:
            return
        tab    = self._current_sim_tab.get()
        option = self._current_sub_option.get()
        cache_key = f"{tab}_{option}"
        if cache_key in self._graph_cache:
            self._embed_graph(self._graph_cache[cache_key]); return
        if self._sim_canvas:
            self._sim_canvas.get_tk_widget().destroy()
            plt.close(self._sim_fig)
            self._sim_canvas = None; self._sim_fig = None
        self._sim_placeholder.configure(text="Grafik yükleniyor…")
        self._sim_placeholder.place(relx=0.5, rely=0.5, anchor="center")

        def create_graph():
            try:
                from simulation_core import (
                    create_ray_path_figure, create_heatmap_figure,
                    create_bounce_histogram,
                    create_incoming_angle_histogram, create_reflection_angle_histogram,
                    create_cpu_graph, create_ram_graph
                )
                d = self._sim_data; fig = None
                if tab == "Üçgen Işın":
                    if option == "Işın Yolu":
                        fig = create_ray_path_figure(
                            d["_A"],d["_B"],d["_Cv"],d["_paths"],d["_orig"],
                            rays_o=d.get("_rays_o"), rays_d=d.get("_rays_d"),
                            first_hit_ids=d.get("_first_hit_ids"),
                            cam_elev=d["_elev"], cam_azim=d["_azim"],
                            bg_color=PANEL, text_color=TXT)
                    elif option == "Isı Haritası":
                        fig = create_heatmap_figure(
                            d["_A"],d["_B"],d["_Cv"],d["_hit"],
                            cam_elev=d["_elev"], cam_azim=d["_azim"],
                            bg_color=PANEL, text_color=TXT)
                elif tab == "Histogram":
                    if option == "Sekme Dağılımı":
                        fig = create_bounce_histogram(
                            d["_paths"],d["_A"],d["_B"],d["_Cv"],d["_hit"],d["_ang"],
                            bg_color=PANEL, text_color=TXT)
                    elif option == "Gelen Açı":
                        fig = create_incoming_angle_histogram(d["_res"], bg_color=PANEL, text_color=TXT)
                    elif option == "Seken Açı":
                        fig = create_reflection_angle_histogram(d["_res"], bg_color=PANEL, text_color=TXT)
                elif tab == "CPU/RAM":
                    if option == "CPU Kullanımı":
                        fig = create_cpu_graph(d["_res"], bg_color=PANEL, text_color=TXT)
                        # Y eksenini veriye göre otomatik ayarla
                        if fig is not None and len(d["_res"].get("cpu", [])) >= 2:
                            ax = fig.axes[0]
                            cpu_arr = d["_res"]["cpu"]
                            mn, mx = min(cpu_arr), max(cpu_arr)
                            pad = max((mx - mn) * 0.3, 1.0)
                            ax.set_ylim(max(0, mn - pad), mx + pad)
                    elif option == "RAM Kullanımı":
                        fig = create_ram_graph(d["_res"], bg_color=PANEL, text_color=TXT)
                        # Y eksenini veriye göre otomatik ayarla
                        if fig is not None and len(d["_res"].get("ram", [])) >= 2:
                            ax = fig.axes[0]
                            ram_arr = [r / 1024.0 for r in d["_res"]["ram"]]
                            mn, mx = min(ram_arr), max(ram_arr)
                            pad = max((mx - mn) * 0.3, 0.005)
                            ax.set_ylim(max(0, mn - pad), mx + pad)
                    # Hızlı simülasyon notu varsa grafiğe ekle
                    if fig is not None and d["_res"].get("fast_sim_note"):
                        fig.text(0.5, 0.01, d["_res"]["fast_sim_note"],
                                 ha="center", va="bottom", fontsize=9,
                                 color=TXT_DIM, style="italic",
                                 transform=fig.transFigure)
                if fig is not None:
                    self._graph_cache[cache_key] = fig
                    self.after(0, lambda: self._embed_graph(fig))
                else:
                    self.after(0, lambda: self._sim_placeholder.place(relx=0.5, rely=0.5, anchor="center"))
            except Exception as e:
                import traceback
                msg = f"Grafik oluşturma hatası:\n{str(e)}"
                print(f"\n[HATA] {e}\n{traceback.format_exc()}")
                self.after(0, lambda: self._show_graph_error(msg))

        threading.Thread(target=create_graph, daemon=True).start()

    def _embed_graph(self, fig):
        try:
            self._sim_placeholder.place_forget()
            if self._sim_toolbar:
                self._sim_toolbar.destroy()
                self._sim_toolbar = None
            if self._sim_canvas:
                self._sim_canvas.get_tk_widget().destroy()
                self._sim_canvas = None
            toolbar_frame = tk.Frame(self._sim_visual_area, background=NAV_BG, height=36)
            toolbar_frame.pack(side="bottom", fill="x")
            canvas = FigureCanvasTkAgg(fig, master=self._sim_visual_area)
            nav = NavigationToolbar2Tk(canvas, toolbar_frame)
            nav.update()
            self._sim_toolbar = toolbar_frame   # frame'i sakla
            canvas.draw()
            canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
            self._sim_canvas = canvas
            self._sim_fig = fig
        except Exception as e:
            self._show_graph_error(f"Embedding hatası:\n{str(e)}")

    def _show_graph_error(self, msg):
        self._sim_placeholder.configure(text=msg)
        self._sim_placeholder.place(relx=0.5, rely=0.5, anchor="center")

    # ══════════════════════════════════════════════════════════════════════════
    # SAYFA: SONUÇLAR
    # ══════════════════════════════════════════════════════════════════════════
    def _build_page_sonuclar(self):
        page = self._pages["Sonuçlar"]
        hdr = ttk.Frame(page, style="Nav.TFrame", height=38)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ttk.Label(hdr, text="  📊  Simülasyon Sonuçları", font=F_BIG,
                  foreground=ACCENT, background=NAV_BG).pack(side="left", padx=8, pady=6)
        ttk.Separator(page, orient="horizontal").pack(fill="x")
        outer, sc = scrollable_frame(page)
        outer.pack(fill="both", expand=True, padx=10, pady=8)

        def stat_group(parent, col, row, title, icon, items):
            lf = make_labelframe(parent, f"{icon}  {title}", padding=10)
            lf.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            for key, lbl in items:
                r = ttk.Frame(lf)
                r.pack(fill="x", pady=3)
                ttk.Label(r, text=lbl, style="Dim2.TLabel", width=22, anchor="w").pack(side="left")
                ttk.Label(r, textvariable=self._stat_vars[key],
                          style="StatSm.TLabel").pack(side="right")

        sc.columnconfigure((0,1,2), weight=1, uniform="sc")
        stat_group(sc,0,0,"Mesh Bilgisi","🔺",[("triangles","Yüklenen Üçgen"),("total_rays","Toplam Işın")])
        stat_group(sc,1,0,"Sekme Sonuçları","🔁",[("bounces","Toplam Sekme"),("hit_tris","Çarpılan Üçgen")])
        stat_group(sc,2,0,"Çarpış Açıları","📐",[("avg_angle","Ortalama (°)"),("min_angle","Min (°)"),
                                                   ("max_angle","Max (°)"),("std_angle","Std Sapma (°)"),("var_angle","Varyans")])
        stat_group(sc,0,1,"Dosya & Hazırlık","📂",[("file_read_time","Dosya Okuma (sn)"),
                                                     ("plucker_time","Plücker (sn)"),("ray_gen_time","Işın Üretimi (sn)")])
        stat_group(sc,1,1,"BVH & JIT","🔧",[("bvh_time","BVH İnşası (sn)"),
                                              ("jit_time","JIT Derleme (sn)"),("benchmark_time","Benchmark (sn)")])
        stat_group(sc,2,1,"Toplam Süre  (Duvar Saati)","⏱",[
            ("ray_tracing_time", "Işın İzleme (sn)"),
            ("wall_clock_total", "GENEL TOPLAM (sn)"),
        ])
        stat_group(sc,0,2,"Sekme İstatistikleri","🔄",[("bounce_count","Sekme Sayısı"),
                                                         ("avg_bounce_time","Ort Süre (sn)"),("std_bounce_time","Std Süre (sn)")])
        stat_group(sc,1,2,"Sekme Süre Aralığı","⏲",[("min_bounce_time","Min Süre (sn)"),("max_bounce_time","Max Süre (sn)")])
        stat_group(sc,2,2,"Hit Oranları","🎯",[("avg_hit_rate","Ortalama (%)"),("last_hit_rate","Son Sekme (%)")])
        stat_group(sc,0,3,"CPU","🖥",[("cpu_avg","Ortalama (%)"),("cpu_max","Maksimum (%)")])
        stat_group(sc,1,3,"RAM","💾",[("ram_avg","Ortalama (GB)"),("ram_max","Maksimum (GB)")])

    # ══════════════════════════════════════════════════════════════════════════
    # SAYFA: RAPOR
    # ══════════════════════════════════════════════════════════════════════════
    def _build_page_rapor(self):
        page = self._pages["Rapor"]
        tb = ttk.Frame(page, style="Nav.TFrame", height=48)
        tb.pack(fill="x"); tb.pack_propagate(False)
        ttk.Label(tb, text="  📄  Analiz Raporu", font=F_BIG,
                  foreground=ACCENT, background=NAV_BG).pack(side="left", padx=8)
        self._excel_regen_btn = make_btn(tb,"🔄  Yeniden Oluştur",self._regenerate_excel,"Tool.TButton")
        self._excel_regen_btn.pack(side="right", padx=4, pady=8)
        self._excel_regen_btn.configure(state="disabled")
        self._excel_save_btn = make_btn(tb,"💾  Farklı Kaydet",self._save_excel_as,"Blue.TButton")
        self._excel_save_btn.pack(side="right", padx=4, pady=8)
        self._excel_save_btn.configure(state="disabled")
        self._excel_open_btn = make_btn(tb,"📂  Excel'i Aç",self._open_excel_file,"Run.TButton")
        self._excel_open_btn.pack(side="right", padx=4, pady=8)
        self._excel_open_btn.configure(state="disabled")
        ttk.Separator(page, orient="horizontal").pack(fill="x")
        outer, sc = scrollable_frame(page)
        outer.pack(fill="both", expand=True, padx=16, pady=12)

        status_lf = make_labelframe(sc, "Rapor Durumu", padding=12)
        status_lf.pack(fill="x", pady=(0,12))
        self._rapor_status_icon = ttk.Label(status_lf, text="⏳", font=(FONT_UI,26), anchor="center")
        self._rapor_status_icon.pack()
        self._rapor_status_lbl = ttk.Label(
            status_lf,
            text="Henüz simülasyon çalıştırılmadı.\nSimülasyon tamamlandığında rapor otomatik oluşturulur.",
            style="Dim.TLabel", anchor="center", justify="center")
        self._rapor_status_lbl.pack(pady=(6,0))
        self._rapor_file_lbl = ttk.Label(status_lf, text="", foreground=ACCENT,
                                          font=F_SMALL, background=BG, anchor="center")
        self._rapor_file_lbl.pack(pady=(4,0))
        ttk.Separator(sc, orient="horizontal").pack(fill="x", pady=8)

        self._rapor_stats_frame = ttk.Frame(sc)
        self._rapor_stats_frame.pack(fill="x")
        self._rapor_stats_frame.columnconfigure((0,1,2), weight=1, uniform="rsc")
        self._rapor_stat_vars = {}
        stat_items = [("total_rays","📡","Toplam Işın"),("hit_tris","🎯","Çarpılan Üçgen"),
                      ("avg_angle","📐","Ort. Açı (°)"),("min_angle","⬇","Min Açı (°)"),
                      ("max_angle","⬆","Max Açı (°)"),("bounces","🔁","Toplam Sekme")]
        for i, (key, icon, label) in enumerate(stat_items):
            lf = make_labelframe(self._rapor_stats_frame, f"  {icon}  {label}", padding=10)
            lf.grid(row=i//3, column=i%3, padx=5, pady=5, sticky="nsew")
            var = tk.StringVar(value="—")
            self._rapor_stat_vars[key] = var
            ttk.Label(lf, textvariable=var, style="Stat.TLabel").pack(anchor="w")

        ttk.Separator(sc, orient="horizontal").pack(fill="x", pady=8)
        note_lf = make_labelframe(sc, "📋  Excel Raporu İçeriği", padding=12)
        note_lf.pack(fill="x", pady=(0,8))
        for line in [
            "• Sayfa 1 — Simülasyon Özeti: Başlık, tarih, genel istatistikler ve renkli üçgen tablosu",
            "  → Yeşil: Dik Çarpış (< 30°)  |  Sarı: Orta Açı (30°–60°)  |  Kırmızı: Sıyırma (> 60°)",
            "• Sayfa 2 — Genel İstatistikler: Toplam ışın, sekme, varyans, std sapma (pandas)",
            "• Sayfa 3 — Üçgen Bazlı Detaylar: Her üçgenin vuruş sayısı ve açısı, vuruş sayısına göre sıralı",
        ]:
            ttk.Label(note_lf, text=line, style="Dim.TLabel",
                      wraplength=700, anchor="w", justify="left").pack(anchor="w", pady=1)

    def _update_rapor_page(self, filename):
        if filename and os.path.isfile(filename):
            self._rapor_status_icon.configure(text="✅", foreground=ACCENT2)
            self._rapor_status_lbl.configure(text="Excel raporu başarıyla oluşturuldu!", foreground=ACCENT2)
            self._rapor_file_lbl.configure(text=f"📁  {os.path.abspath(filename)}")
            self._excel_open_btn.configure(state="normal")
            self._excel_save_btn.configure(state="normal")
            self._excel_regen_btn.configure(state="normal")
        else:
            self._rapor_status_icon.configure(text="⚠️", foreground=ACCENT4)
            self._rapor_status_lbl.configure(
                text="Rapor oluşturulurken hata oluştu.\n'Yeniden Oluştur' butonunu deneyin.",
                foreground=ACCENT4)
        if self._sim_data:
            r = self._sim_data
            self._rapor_stat_vars["total_rays"].set(f"{r['total_rays']:,}")
            self._rapor_stat_vars["hit_tris"].set(f"{r['hit_tris']:,}")
            self._rapor_stat_vars["avg_angle"].set(f"{r['avg_angle']:.2f}")
            self._rapor_stat_vars["min_angle"].set(f"{r['min_angle']:.2f}")
            self._rapor_stat_vars["max_angle"].set(f"{r['max_angle']:.2f}")
            self._rapor_stat_vars["bounces"].set(str(r["bounces"]))

    def _open_excel_file(self):
        if self._excel_filename and os.path.isfile(self._excel_filename):
            import subprocess
            try:
                if sys.platform == "win32": os.startfile(self._excel_filename)
                elif sys.platform == "darwin": subprocess.run(["open", self._excel_filename])
                else: subprocess.run(["xdg-open", self._excel_filename])
            except Exception as e:
                print(f"[RAPOR] Dosya açılamadı: {e}")

    def _save_excel_as(self):
        if not self._excel_filename: return
        dest = filedialog.asksaveasfilename(
            defaultextension=".xlsx", filetypes=[("Excel Dosyası","*.xlsx")],
            initialfile=os.path.basename(self._excel_filename), title="Excel Raporunu Kaydet")
        if dest:
            import shutil
            try:
                shutil.copy2(self._excel_filename, dest)
                self._rapor_file_lbl.configure(text=f"📁  {os.path.abspath(dest)}")
                self._excel_filename = dest
            except Exception as e:
                print(f"[RAPOR] Kopyalama hatası: {e}")

    def _regenerate_excel(self):
        if not self._sim_data: return
        self._rapor_status_icon.configure(text="⏳", foreground=TXT_DIM)
        self._rapor_status_lbl.configure(text="Rapor yeniden oluşturuluyor…", foreground=TXT_DIM)
        def regen():
            try:
                from simulation_core import save_detailed_results_to_excel
                saved = save_detailed_results_to_excel(
                    self._sim_data["_hit"], self._sim_data["_ang"],
                    self._sim_data["_nt"], self._sim_data["_np"])
                self._excel_filename = saved
                self.after(0, lambda: self._update_rapor_page(saved))
            except Exception as e:
                print(f"[RAPOR] Yeniden oluşturma hatası: {e}")
                self.after(0, lambda: self._update_rapor_page(None))
        threading.Thread(target=regen, daemon=True).start()

    # ══════════════════════════════════════════════════════════════════════════
    # SAYFA: YARDIM
    # ══════════════════════════════════════════════════════════════════════════
    def _build_page_yardim(self):
        page = self._pages["Yardım"]
        outer, sc = scrollable_frame(page)
        outer.pack(fill="both", expand=True, padx=16, pady=12)
        ttk.Label(sc, text="📖  Kullanım Kılavuzu", style="Title.TLabel").pack(anchor="w", pady=(0,12))
        sections = [
            ("1️⃣  Başlangıç",[
                "• Uygulamayı başlattığınızda Ayarlar sayfası açılır",
                "• Mesh dosyanızı seçin (UNV formatı desteklenir)",
                "• Işın kaynağı tipini belirleyin (Noktasal veya Paralel)",
                "• Kaynak noktasının koordinatlarını girin (Noktasal için)"]),
            ("2️⃣  Parametre Ayarları",[
                "• Theta (Dikey Açı): Işınların dikey yayılım açısı (derece)",
                "• Phi (Yatay Açı): Işınların yatay yayılım açısı (derece)",
                "• Adım Sayısı: Her açı için kaç ışın oluşturulacağı",
                "• Maks Sekme: Işınların maksimum yansıma sayısı",
                "• Toplam ışın sayısı = Theta adımı × Phi adımı"]),
            ("3️⃣  Önizleme",[
                "• 'Önizlemeye Git' butonu ile ışın dağılımını görüntüleyin",
                "• Kamera açısını (Yükseklik ve Yatay) ayarlayabilirsiniz",
                "• Grafik araçlarını kullanarak zoom ve pan yapabilirsiniz"]),
            ("4️⃣  Simülasyon",[
                "• 'Simülasyonu Başlat' butonu ile hesaplamayı başlatın",
                "• Simülasyon sırasında 'Durdur' butonu ile iptal edebilirsiniz",
                "• Grafik sekmeleri: Üçgen Işın, Histogram, CPU/RAM"]),
            ("5️⃣  Sonuçlar",[
                "• Mesh Bilgisi: Yüklenen üçgen ve toplam ışın sayısı",
                "• Çarpış Açıları: Ortalama, minimum ve maksimum açılar",
                "• Performans: Simülasyon süresi, CPU ve RAM kullanımı"]),
            ("6️⃣  Grafik Araçları",[
                "• 🏠 Home: Orijinal görünüme dön",
                "• ⊕ Pan: Grafiği sürükleyerek hareket ettir",
                "• 🔍 Zoom: Dikdörtgen seçerek yakınlaştır",
                "• 💾 Save: Grafiği PNG olarak kaydet"]),
        ]
        for title, items in sections:
            lf = make_labelframe(sc, title, padding=10)
            lf.pack(fill="x", pady=(0,10))
            for item in items:
                ttk.Label(lf, text=item, style="Dim.TLabel",
                          anchor="w", justify="left", wraplength=900).pack(anchor="w", pady=1, padx=4)

    # ══════════════════════════════════════════════════════════════════════════
    # MESH BROWSE + MİNİ ÖNİZLEME
    # ══════════════════════════════════════════════════════════════════════════
    def _browse_file(self):
        path = filedialog.askopenfilename(
            title="UNV Mesh Dosyası Seç",
            filetypes=[("Universal Mesh","*.unv"),("Tüm Dosyalar","*.*")])
        if path:
            self._file_path.set(path)
            threading.Thread(target=self._load_mesh, args=(path,), daemon=True).start()

    def _load_mesh(self, path):
        try:
            from simulation_core import read_unv_mesh_optimized
            A, B, Cm = read_unv_mesh_optimized(path)
            self._mesh_A, self._mesh_B, self._mesh_C = A, B, Cm
            self.after(0, self._draw_mesh_mini)
        except Exception as e:
            self.after(0, lambda: self._mesh_placeholder.configure(text=f"Hata: {e}"))

    def _draw_mesh_mini(self):
        A, B, Cm = self._mesh_A, self._mesh_B, self._mesh_C
        if A is None: return
        self._mesh_placeholder.place_forget()
        if self._mesh_mini_canvas:
            self._mesh_mini_canvas.get_tk_widget().destroy()
            plt.close(self._mesh_mini_fig)
        fig = plt.Figure(facecolor=PANEL)
        ax  = fig.add_subplot(111, projection="3d")
        ax.set_facecolor("#F8F8F8")
        fig.subplots_adjust(left=0, right=1, top=0.90, bottom=0)
        total = len(A)
        step  = max(1, total // 5000)
        pts   = np.concatenate([A[::step], B[::step], Cm[::step]], axis=0)
        z     = pts[:, 2]
        zn    = (z - z.min()) / max(float(z.max()-z.min()), 1e-9)
        cols  = plt.cm.Blues(0.3 + 0.6*zn)
        ax.scatter(pts[:,0],pts[:,1],pts[:,2],c=cols,s=1.2,linewidths=0,depthshade=True,alpha=0.9)
        all_pts = np.concatenate([A, B, Cm], axis=0)
        mn, mx  = all_pts.min(0), all_pts.max(0)
        mr      = (mx-mn).max()/2.0
        mid     = (mn+mx)/2.0
        ax.set_xlim(mid[0]-mr, mid[0]+mr)
        ax.set_ylim(mid[1]-mr, mid[1]+mr)
        ax.set_zlim(mid[2]-mr, mid[2]+mr)
        ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
        ax.grid(False)
        for p in [ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane]:
            p.fill = False; p.set_edgecolor("none")
        ax.xaxis.line.set_color((0,0,0,0))
        ax.yaxis.line.set_color((0,0,0,0))
        ax.zaxis.line.set_color((0,0,0,0))
        ax.view_init(elev=22, azim=40)
        try: ax.dist = 7
        except: pass
        ax.set_title(f"{total:,} üçgen", color=ACCENT, fontsize=9, pad=2)
        canvas = FigureCanvasTkAgg(fig, master=self._mesh_preview_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self._mesh_mini_canvas = canvas
        self._mesh_mini_fig    = fig

    # ══════════════════════════════════════════════════════════════════════════
    # SİMÜLASYON
    # ══════════════════════════════════════════════════════════════════════════
    def _start_simulation(self):
        if self._sim_thread and self._sim_thread.is_alive(): return
        try:
            t0  = float(self._t_start.get()); t1  = float(self._t_end.get())
            p0  = float(self._p_start.get()); p1  = float(self._p_end.get())
            nt  = int(self._n_theta.get());   np_ = int(self._n_phi.get())
            maxb= int(self._max_bounce.get())
            assert t0<t1 and p0<p1 and nt>0 and np_>0 and maxb>0
            src = self._source_type.get()
            ox = oy = oz = 0.0
            if src == "Noktasal":
                ox = float(self._origin_x.get())
                oy = float(self._origin_y.get())
                oz = float(self._origin_z.get())
        except Exception:
            print("[HATA] Geçersiz parametre girişi."); return
        fp = self._file_path.get()
        if not os.path.isfile(fp):
            print(f"[HATA] Dosya bulunamadı: {fp}"); return

        self._run_btn.configure(state="disabled", text="⏳  Çalışıyor…")
        self._stop_btn.configure(state="normal")
        self._progress.start()
        self._set_status("● Çalışıyor", ACCENT4)
        nt_display = int(self._num_threads.get())
        core_txt = f"Otomatik ({self._total_cores} çekirdek)" if nt_display == 0 else f"{nt_display} çekirdek"
        self._sim_status_lbl.configure(text=f"Simülasyon çalışıyor…  [{core_txt}]")
        self._stop_flag.clear()
        self._reset_stats()
        self._graph_cache.clear()
        if self._sim_canvas:
            self._sim_canvas.get_tk_widget().destroy()
            plt.close(self._sim_fig)
            self._sim_canvas = None
        self._sim_placeholder.place(relx=0.5, rely=0.5, anchor="center")
        params = dict(file_path=fp, origin=[ox,oy,oz],
                      theta_range=(t0,t1), phi_range=(p0,p1),
                      n_theta=nt, n_phi=np_, max_bounces=maxb,
                      source_type=src,
                      num_threads=int(self._num_threads.get()),
                      cam_elev=int(self._cam_elev.get()),
                      cam_azim=int(self._cam_azim.get()))
        self._sim_thread = threading.Thread(target=self._sim_worker, args=(params,), daemon=True)
        self._sim_thread.start()

    def _stop_simulation(self):
        self._stop_flag.set()
        print("\n[KULLANICI] Durdurma isteği gönderildi...")

    def _sim_finished(self, results=None):
        self._run_btn.configure(state="normal", text="▶   Simülasyonu Başlat")
        self._stop_btn.configure(state="disabled")
        self._progress.stop()
        if results:
            self._set_status("● Tamamlandı", ACCENT2)
            self._sim_status_lbl.configure(text="Tamamlandı ✓")
            self._result_queue.put(results)
            self._show_page("Sonuçlar")
        else:
            self._set_status("● Durduruldu", ACCENT3)
            self._sim_status_lbl.configure(text="Durduruldu")

    def _sim_worker(self, params):
        try:
            import time
            from simulation_core import (
                read_unv_mesh_optimized, generate_beam_from_counts,
                precompute_plucker, build_bvh, plucker_bvh_tracer,
                run_simulation, visualize
            )
            fp   = params["file_path"]
            orig = params["origin"]
            tr   = params["theta_range"]; pr   = params["phi_range"]
            nt   = params["n_theta"];     np_  = params["n_phi"]
            maxb = params["max_bounces"]
            elev = params["cam_elev"];    azim = params["cam_azim"]
            num_threads = params.get("num_threads", 0)

            # Çekirdek sayısını ayarla
            from numba import set_num_threads, get_num_threads
            import psutil as _ps2
            total_cores = _ps2.cpu_count(logical=True) or 1
            if num_threads > 0:
                actual_threads = min(num_threads, total_cores)
                set_num_threads(actual_threads)
                print(f"\n[CPU] {actual_threads} çekirdek kullanılıyor "
                      f"(toplam: {total_cores})")
            else:
                set_num_threads(total_cores)
                print(f"\n[CPU] Otomatik — tüm {total_cores} çekirdek kullanılıyor")

            timing = {}

            print(f"\n[MESH] {fp} okunuyor...")
            t0 = time.perf_counter()
            A, B, Cv = read_unv_mesh_optimized(fp)
            timing['file_read'] = time.perf_counter() - t0
            print(f"  {A.shape[0]:,} üçgen yüklendi. ({timing['file_read']:.4f} sn)")

            if self._mesh_A is None:
                self._mesh_A, self._mesh_B, self._mesh_C = A, B, Cv
                self.after(0, self._draw_mesh_mini)

            if self._stop_flag.is_set():
                self.after(0, lambda: self._sim_finished()); return

            print("\n[PRECOMPUTE] Plücker kenar verileri hesaplanıyor...")
            t0 = time.perf_counter()
            dAB,mAB,dBC,mBC,dCA,mCA,N_arr,d_plane = precompute_plucker(A,B,Cv)
            timing['plucker'] = time.perf_counter() - t0
            print(f"  Tamamlandı. ({timing['plucker']:.4f} sn)")

            print("\n[BVH] Ağaç inşa ediliyor...")
            t0 = time.perf_counter()
            bvh_nodes,bvh_meta,bvh_tids = build_bvh(A,B,Cv)
            timing['bvh'] = time.perf_counter() - t0
            print(f"  {len(bvh_nodes)} düğüm. ({timing['bvh']:.4f} sn)")

            src = params["source_type"]

            t0 = time.perf_counter()
            rays_o, rays_d = generate_beam_from_counts(orig, tr, pr, nt, np_)

            # ── Paralel Kaynak Düzeltmesi ────────────────────────────────────
            # generate_beam_from_counts her zaman tüm ışınları aynı origin'den
            # başlatır. Paralel modda ışınlar farklı noktalardan, aynı yönde
            # çıkmalı (düzlemsel dalga / far-field simülasyonu).
            if src == "Paralel":
                # 1. Merkez yönü hesapla (theta/phi aralığının ortası)
                theta_c = np.radians((tr[0] + tr[1]) / 2.0)
                phi_c   = np.radians((pr[0] + pr[1]) / 2.0)
                d_center = np.array([
                    np.sin(theta_c) * np.cos(phi_c),
                    np.sin(theta_c) * np.sin(phi_c),
                    np.cos(theta_c)
                ], dtype=np.float64)
                d_center /= np.linalg.norm(d_center)

                # 2. Mesh merkezi ve boyutu
                all_pts     = np.concatenate([A, B, Cv], axis=0)
                mesh_center = (all_pts.min(0) + all_pts.max(0)) / 2.0
                mesh_scale  = float((all_pts.max(0) - all_pts.min(0)).max())

                # 3. d_center'a dik iki eksen (u, v) bul
                ref = np.array([0.0, 0.0, 1.0])
                if abs(np.dot(d_center, ref)) > 0.9:
                    ref = np.array([1.0, 0.0, 0.0])
                u = np.cross(d_center, ref)
                u /= np.linalg.norm(u)
                v = np.cross(d_center, u)
                v /= np.linalg.norm(v)

                # 4. Her ışın için (u, v) grid offseti hesapla
                # rays_d'den theta/phi bilgisini al → offset olarak kullan
                total_rays = nt * np_
                u_steps = np.linspace(-mesh_scale * 0.6, mesh_scale * 0.6, nt)
                v_steps = np.linspace(-mesh_scale * 0.6, mesh_scale * 0.6, np_)
                u_grid, v_grid = np.meshgrid(u_steps, v_steps, indexing='ij')
                u_flat = u_grid.ravel()
                v_flat = v_grid.ravel()

                # 5. Başlangıç noktaları: mesh merkezinin karşısındaki düzlem
                start_center = mesh_center - d_center * mesh_scale * 1.5
                rays_o = (start_center
                          + np.outer(u_flat, u)
                          + np.outer(v_flat, v)).astype(np.float64)

                # 6. Tüm ışınlar aynı yönde
                rays_d = np.tile(d_center, (total_rays, 1)).astype(np.float64)

                print(f"\n[PARALEL KAYNAK] {total_rays} ışın  |  "
                      f"Yön: [{d_center[0]:.3f}, {d_center[1]:.3f}, {d_center[2]:.3f}]  |  "
                      f"Grid: {nt}×{np_}  |  "
                      f"Alan: {mesh_scale*1.2:.2f}m × {mesh_scale*1.2:.2f}m")
            # ─────────────────────────────────────────────────────────────────

            timing['ray_gen'] = time.perf_counter() - t0

            print("\n[WARM-UP] Numba JIT derleniyor...")
            t0 = time.perf_counter()
            plucker_bvh_tracer(
                rays_o[:2],rays_d[:2],
                dAB[:10],mAB[:10],dBC[:10],mBC[:10],dCA[:10],mCA[:10],
                N_arr[:10],d_plane[:10],bvh_nodes,bvh_meta,bvh_tids)
            timing['jit'] = time.perf_counter() - t0
            print(f"[WARM-UP] Tamamlandı. ({timing['jit']:.4f} sn)\n")

            if self._stop_flag.is_set():
                self.after(0, lambda: self._sim_finished()); return

            print("[BENCHMARK] 5 tekrar ile ortalama hesaplanıyor...")
            benchmark_times = []
            for i in range(5):
                t0 = time.perf_counter()
                plucker_bvh_tracer(
                    rays_o[:min(100,len(rays_o))], rays_d[:min(100,len(rays_d))],
                    dAB,mAB,dBC,mBC,dCA,mCA,N_arr,d_plane,bvh_nodes,bvh_meta,bvh_tids)
                benchmark_times.append(time.perf_counter()-t0)
            timing['benchmark'] = np.mean(benchmark_times)
            print(f"  Benchmark Ort: {timing['benchmark']:.6f} sn")

            hit_counts,avg_angles,bounce_paths,resource_data,\
                first_hit_ids,initial_rays_o,initial_rays_d = run_simulation(
                    rays_o,rays_d,A,B,Cv,
                    dAB,mAB,dBC,mBC,dCA,mCA,N_arr,d_plane,
                    bvh_nodes,bvh_meta,bvh_tids,
                    max_safety_limit=maxb)

            timing['ray_tracing'] = resource_data["duration"]

            # Simülasyon çok hızlı bittiyse monitor ölçüm yapamaz.
            # psutil ile gerçek sistem ölçümü al.
            if len(resource_data.get("cpu", [])) < 2:
                import psutil as _ps
                import time as _t
                proc      = _ps.Process(os.getpid())
                num_cores = _ps.cpu_count(logical=True) or 1
                dur       = resource_data["duration"]

                # 5 noktalı gerçek CPU ölçümü (0.05s aralık)
                cpu_samples_fb = []
                ram_samples_fb = []
                for _ in range(5):
                    cpu_val = _ps.cpu_percent(interval=0.05) / num_cores
                    ram_val = proc.memory_info().rss / (1024**2)
                    cpu_samples_fb.append(cpu_val)
                    ram_samples_fb.append(ram_val)

                times_fb = [i * 1.0 / 4 for i in range(5)]  # 0.0 → 1.0 saniye aralığı (normalize)
                resource_data["cpu"]   = cpu_samples_fb
                resource_data["ram"]   = ram_samples_fb
                resource_data["times"] = times_fb
                resource_data["fast_sim_note"] = (
                    f"⚡ Simülasyon çok hızlı tamamlandı ({dur*1000:.1f} ms).\n"
                    f"Gösterilen değerler simülasyon sonrası sistem ölçümüdür.")
                print(f"[MONITOR] Hızlı simülasyon — sistem ölçümü: "
                      f"CPU≈{sum(cpu_samples_fb)/len(cpu_samples_fb):.1f}%  "
                      f"RAM≈{sum(ram_samples_fb)/len(ram_samples_fb):.0f} MB")

            # Gerçek duvar saati toplamı = tüm aşamaların toplamı
            timing['wall_clock_total'] = (
                timing.get('file_read',   0) +
                timing.get('plucker',     0) +
                timing.get('bvh',         0) +
                timing.get('ray_gen',     0) +
                timing.get('jit',         0) +
                timing.get('benchmark',   0) +
                timing.get('ray_tracing', 0)
            )

            resource_data['timing'] = timing
            active = hit_counts > 0
            res = dict(
                num_tris          = A.shape[0],
                total_rays        = nt*np_,
                hit_tris          = int(np.sum(active)),
                bounces           = len(bounce_paths),
                avg_angle         = float(np.mean(avg_angles[active])) if np.sum(active) else 0,
                min_angle         = float(np.min(avg_angles[active]))  if np.sum(active) else 0,
                max_angle         = float(np.max(avg_angles[active]))  if np.sum(active) else 0,
                std_angle         = float(np.std(avg_angles[active]))  if np.sum(active) else 0,
                var_angle         = float(np.var(avg_angles[active]))  if np.sum(active) else 0,
                ray_tracing_time  = timing['ray_tracing'],
                wall_clock_total  = timing['wall_clock_total'],
                cpu_avg           = float(np.mean(resource_data["cpu"])) if resource_data["cpu"] else 0,
                cpu_max           = float(np.max(resource_data["cpu"]))  if resource_data["cpu"] else 0,
                ram_avg           = float(np.mean(resource_data["ram"]))/1024 if resource_data["ram"] else 0,
                ram_max           = float(np.max(resource_data["ram"]))/1024  if resource_data["ram"] else 0,
                timing            = timing,
                _A=A,_B=B,_Cv=Cv,
                _hit=hit_counts,_ang=avg_angles,_paths=bounce_paths,
                _orig=orig,_tr=tr,_pr=pr,_nt=nt,_np=np_,
                _res=resource_data,_elev=elev,_azim=azim,
                _first_hit_ids=first_hit_ids,_rays_o=initial_rays_o,_rays_d=initial_rays_d,
            )
            self.after(0, lambda: self._sim_finished(res))
        except Exception as e:
            import traceback
            print(f"\n[HATA] {e}\n{traceback.format_exc()}")
            self.after(0, lambda: self._sim_finished())

    # ══════════════════════════════════════════════════════════════════════════
    # SONUÇ UYGULA
    # ══════════════════════════════════════════════════════════════════════════
    def _apply_results(self, r):
        self._stat_vars["triangles"].set(f"{r['num_tris']:,}")
        self._stat_vars["total_rays"].set(f"{r['total_rays']:,}")
        self._stat_vars["hit_tris"].set(f"{r['hit_tris']:,}")
        self._stat_vars["bounces"].set(str(r["bounces"]))
        self._stat_vars["avg_angle"].set(f"{r['avg_angle']:.2f}")
        self._stat_vars["min_angle"].set(f"{r['min_angle']:.2f}")
        self._stat_vars["max_angle"].set(f"{r['max_angle']:.2f}")
        self._stat_vars["std_angle"].set(f"{r['std_angle']:.2f}")
        self._stat_vars["var_angle"].set(f"{r['var_angle']:.2f}")
        self._stat_vars["ray_tracing_time"].set(f"{r['ray_tracing_time']:.4f}")
        self._stat_vars["wall_clock_total"].set(f"{r['wall_clock_total']:.4f}")
        self._stat_vars["cpu_avg"].set(f"{r['cpu_avg']:.1f}")
        self._stat_vars["cpu_max"].set(f"{r['cpu_max']:.1f}")
        self._stat_vars["ram_avg"].set(f"{r['ram_avg']:.2f}")
        self._stat_vars["ram_max"].set(f"{r['ram_max']:.2f}")
        timing = r.get('timing',{})
        self._stat_vars["file_read_time"].set(f"{timing.get('file_read',0):.4f}")
        self._stat_vars["plucker_time"].set(f"{timing.get('plucker',0):.4f}")
        self._stat_vars["bvh_time"].set(f"{timing.get('bvh',0):.4f}")
        self._stat_vars["ray_gen_time"].set(f"{timing.get('ray_gen',0):.4f}")
        self._stat_vars["jit_time"].set(f"{timing.get('jit',0):.4f}")
        self._stat_vars["benchmark_time"].set(f"{timing.get('benchmark',0):.6f}")
        bounce_times     = r.get('_res',{}).get('bounce_times', np.array([]))
        bounce_hit_rates = r.get('_res',{}).get('bounce_hit_rates', np.array([]))
        if len(bounce_times)>0:
            self._stat_vars["bounce_count"].set(str(len(bounce_times)))
            self._stat_vars["avg_bounce_time"].set(f"{np.mean(bounce_times):.4f}")
            self._stat_vars["min_bounce_time"].set(f"{np.min(bounce_times):.4f}")
            self._stat_vars["max_bounce_time"].set(f"{np.max(bounce_times):.4f}")
            self._stat_vars["std_bounce_time"].set(f"{np.std(bounce_times):.4f}")
        else:
            for k in ["bounce_count","avg_bounce_time","min_bounce_time","max_bounce_time","std_bounce_time"]:
                self._stat_vars[k].set("—")
        if len(bounce_hit_rates)>0:
            self._stat_vars["avg_hit_rate"].set(f"{np.mean(bounce_hit_rates):.1f}")
            self._stat_vars["last_hit_rate"].set(f"{bounce_hit_rates[-1]:.1f}")
        else:
            self._stat_vars["avg_hit_rate"].set("—")
            self._stat_vars["last_hit_rate"].set("—")
        self._sim_data = r
        self._excel_filename = None
        try:
            from simulation_core import save_detailed_results_to_excel
            saved = save_detailed_results_to_excel(r["_hit"],r["_ang"],r["_nt"],r["_np"])
            self._excel_filename = saved
            self._update_rapor_page(saved)
        except Exception as e:
            print(f"[EXCEL] Otomatik kayıt hatası: {e}")
        self._show_page("Simülasyon")
        self._render_simulation_graph()

    def _poll(self):
        while not self._result_queue.empty():
            self._apply_results(self._result_queue.get_nowait())
        self.after(80, self._poll)

    def _set_status(self, text, color):
        self._status_dot.configure(text=text, foreground=color)

    def _reset_stats(self):
        for v in self._stat_vars.values():
            v.set("—")

    def _on_thread_slider(self, val=None):
        n = int(self._num_threads.get())
        if n == 0:
            self._thread_val_lbl.configure(
                text=f"Otomatik (tüm {self._total_cores} çekirdek)")
        else:
            self._thread_val_lbl.configure(text=f"{n} çekirdek")

    def _on_source_type_change(self):
        if self._source_type.get() == "Noktasal":
            self._origin_frame.pack(fill="x")
        else:
            self._origin_frame.pack_forget()

    def _update_ray_summary(self, *_):
        try:
            nt  = int(self._n_theta.get())
            np_ = int(self._n_phi.get())
            self._ray_summary.configure(text=f"Toplam: {nt} × {np_} = {nt*np_:,} ışın")
        except ValueError:
            self._ray_summary.configure(text="Toplam: —")


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = SimulationGUI()
    app.mainloop()