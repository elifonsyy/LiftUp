"""
simulation_core.py
──────────────────
Plücker + Precompute + BVH Multi-Bounce Ray Tracer — çekirdek modül.
GUI (simulation_gui.py) bu modülü import eder.

Kurulum:
    pip install numpy numba matplotlib psutil
"""

import numpy as np
import time
import threading
import psutil
import os
import pandas as pd
import numba
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.colors as mcolors


# ══════════════════════════════════════════════════════════════════════════════
# 0. KAYNAK İZLEYİCİ
# ══════════════════════════════════════════════════════════════════════════════
class ResourceMonitor:
    def __init__(self, interval: float = 0.1):
        self.interval    = interval
        self._cpu: list  = []
        self._ram: list  = []
        self._times: list = []
        self._stop_event = threading.Event()
        self._proc       = psutil.Process(os.getpid())
        self._thread     = threading.Thread(target=self._collect, daemon=True)

    def _collect(self):
        t0 = time.perf_counter()
        self._proc.cpu_percent(interval=None)
        self._num_cores = psutil.cpu_count(logical=True) or 1
        while not self._stop_event.is_set():
            cpu_val = self._proc.cpu_percent(interval=None)
            self._cpu.append(cpu_val / self._num_cores)
            mem_mb = self._proc.memory_info().rss / (1024 ** 2)
            self._ram.append(mem_mb)
            self._times.append(time.perf_counter() - t0)
            time.sleep(self.interval)

    def start(self):  self._thread.start()
    def stop(self):
        self._stop_event.set()
        self._thread.join(timeout=2.0)
    def results(self):
        return list(self._cpu), list(self._ram), list(self._times)


# ══════════════════════════════════════════════════════════════════════════════
# 1. UNV DOSYASI OKUMA
# ══════════════════════════════════════════════════════════════════════════════
def read_unv_mesh_optimized(file_path):
    nodes     = {}
    triangles = []

    with open(file_path, 'r') as f:
        iterator = iter(f)
        for line in iterator:
            line = line.strip()
            if line == "2411":
                for line in iterator:
                    line = line.strip()
                    if line == "-1": break
                    node_info = line.split()
                    node_id   = int(node_info[0])
                    coor_line = next(iterator).strip()
                    coor_info = coor_line.split()
                    nodes[node_id] = [float(coor_info[0]),
                                      float(coor_info[1]),
                                      float(coor_info[2])]
            elif line == "2412":
                for line in iterator:
                    line = line.strip()
                    if line == "-1": break
                    point_info   = line.split()
                    point_num    = int(point_info[5])
                    node_ids_line = next(iterator).strip()
                    if point_num == 3:
                        node_ids = [int(x) for x in node_ids_line.split()]
                        triangles.append(node_ids)

    num_triangles = len(triangles)
    A = np.zeros((num_triangles, 3), dtype=np.float64)
    B = np.zeros((num_triangles, 3), dtype=np.float64)
    C = np.zeros((num_triangles, 3), dtype=np.float64)
    for i, t in enumerate(triangles):
        A[i] = nodes[t[0]]
        B[i] = nodes[t[1]]
        C[i] = nodes[t[2]]
    return A, B, C


# ══════════════════════════════════════════════════════════════════════════════
# 2. IŞIN ÜRETME
# ══════════════════════════════════════════════════════════════════════════════
def generate_beam_from_counts(origin, theta_range, phi_range, n_theta, n_phi):
    origin = np.array(origin, dtype=np.float64)
    thetas = np.radians(np.linspace(theta_range[0], theta_range[1], n_theta))
    phis   = np.radians(np.linspace(phi_range[0],   phi_range[1],   n_phi))
    theta_grid, phi_grid = np.meshgrid(thetas, phis, indexing='ij')
    theta_flat = theta_grid.ravel()
    phi_flat   = phi_grid.ravel()
    dx = np.sin(theta_flat) * np.cos(phi_flat)
    dy = np.sin(theta_flat) * np.sin(phi_flat)
    dz = np.cos(theta_flat)
    rays_d = np.stack([dx, dy, dz], axis=1).astype(np.float64)
    rays_o = np.tile(origin, (rays_d.shape[0], 1))
    return rays_o, rays_d


# ══════════════════════════════════════════════════════════════════════════════
# 3. PLÜCKER PRECOMPUTE
# ══════════════════════════════════════════════════════════════════════════════
def precompute_plucker(A, B, C):
    dAB = B - A;  mAB = np.cross(A, dAB)
    dBC = C - B;  mBC = np.cross(B, dBC)
    dCA = A - C;  mCA = np.cross(C, dCA)
    N_arr   = np.cross(dAB, C - A)
    d_plane = np.einsum('ij,ij->i', N_arr, A)
    return (dAB.astype(np.float64), mAB.astype(np.float64),
            dBC.astype(np.float64), mBC.astype(np.float64),
            dCA.astype(np.float64), mCA.astype(np.float64),
            N_arr.astype(np.float64), d_plane.astype(np.float64))


# ══════════════════════════════════════════════════════════════════════════════
# 4. BVH
# ══════════════════════════════════════════════════════════════════════════════
MAX_LEAF_TRIS = 8

def build_bvh(A, B, C):
    num_tris  = A.shape[0]
    centroids = (A + B + C) / 3.0
    node_aabb = []
    node_meta = []

    def compute_aabb(indices):
        pts = np.concatenate([A[indices], B[indices], C[indices]], axis=0)
        return pts.min(axis=0), pts.max(axis=0)

    def build(indices, depth=0):
        node_idx = len(node_aabb)
        mn, mx   = compute_aabb(indices)
        node_aabb.append(np.concatenate([mn, mx]))

        if len(indices) <= MAX_LEAF_TRIS:
            start = len(tri_ids_list)
            tri_ids_list.extend(indices.tolist())
            end   = len(tri_ids_list)
            node_meta.append([-1, end, start])
            return node_idx

        extent = mx - mn
        axis   = int(np.argmax(extent))
        order  = np.argsort(centroids[indices, axis])
        sorted_indices = indices[order]
        mid    = len(sorted_indices) // 2

        node_meta.append([-1, -1, -1])
        left_child  = build(sorted_indices[:mid],  depth + 1)
        right_child = build(sorted_indices[mid:],  depth + 1)
        node_meta[node_idx] = [left_child, right_child, -1]
        return node_idx

    tri_ids_list = []
    build(np.arange(num_tris, dtype=np.int32))

    return (np.array(node_aabb, dtype=np.float64),
            np.array(node_meta, dtype=np.int32),
            np.array(tri_ids_list, dtype=np.int32))


# ══════════════════════════════════════════════════════════════════════════════
# 5. IŞIN-KUTU KESİŞİM
# ══════════════════════════════════════════════════════════════════════════════
@numba.njit(fastmath=True)
def ray_aabb_intersect(ox, oy, oz, idx, idy, idz, mn, mx, t_max):
    tx1 = (mn[0]-ox)*idx;  tx2 = (mx[0]-ox)*idx
    t_near = min(tx1,tx2); t_far = max(tx1,tx2)
    ty1 = (mn[1]-oy)*idy;  ty2 = (mx[1]-oy)*idy
    t_near = max(t_near,min(ty1,ty2)); t_far = min(t_far,max(ty1,ty2))
    tz1 = (mn[2]-oz)*idz;  tz2 = (mx[2]-oz)*idz
    t_near = max(t_near,min(tz1,tz2)); t_far = min(t_far,max(tz1,tz2))
    return t_far >= max(t_near, 1e-9) and t_near < t_max


# ══════════════════════════════════════════════════════════════════════════════
# 6. PLÜCKER + BVH TRACER
# ══════════════════════════════════════════════════════════════════════════════
@numba.njit(parallel=True, fastmath=True)
def plucker_bvh_tracer(rays_o, rays_d,
                        dAB, mAB, dBC, mBC, dCA, mCA,
                        N_arr, d_plane,
                        bvh_nodes, bvh_meta, bvh_tids):
    num_rays = rays_o.shape[0]
    hit_triangle_ids = np.full(num_rays, -1,     dtype=np.int32)
    hit_distances    = np.full(num_rays, np.inf, dtype=np.float64)

    for i in numba.prange(num_rays):
        ox = rays_o[i,0]; oy = rays_o[i,1]; oz = rays_o[i,2]
        dx = rays_d[i,0]; dy = rays_d[i,1]; dz = rays_d[i,2]
        mRx = oy*dz - oz*dy; mRy = oz*dx - ox*dz; mRz = ox*dy - oy*dx
        idx = 1.0/dx if abs(dx)>1e-12 else 1e12
        idy = 1.0/dy if abs(dy)>1e-12 else 1e12
        idz = 1.0/dz if abs(dz)>1e-12 else 1e12

        closest_t   = np.inf
        closest_tri = -1
        stack    = np.empty(64, dtype=np.int32)
        stack[0] = 0; sp = 1

        while sp > 0:
            sp -= 1
            node_idx = stack[sp]
            mn = bvh_nodes[node_idx,:3]; mx = bvh_nodes[node_idx,3:]
            if not ray_aabb_intersect(ox,oy,oz,idx,idy,idz,mn,mx,closest_t):
                continue
            left_child = bvh_meta[node_idx,0]
            tri_end    = bvh_meta[node_idx,1]
            tri_start  = bvh_meta[node_idx,2]

            if left_child == -1:
                for k in range(tri_start, tri_end):
                    j = bvh_tids[k]
                    s0 = (dx*mAB[j,0]+dy*mAB[j,1]+dz*mAB[j,2] +
                          dAB[j,0]*mRx+dAB[j,1]*mRy+dAB[j,2]*mRz)
                    s1 = (dx*mBC[j,0]+dy*mBC[j,1]+dz*mBC[j,2] +
                          dBC[j,0]*mRx+dBC[j,1]*mRy+dBC[j,2]*mRz)
                    if (s0>0. and s1<0.) or (s0<0. and s1>0.): continue
                    s2 = (dx*mCA[j,0]+dy*mCA[j,1]+dz*mCA[j,2] +
                          dCA[j,0]*mRx+dCA[j,1]*mRy+dCA[j,2]*mRz)
                    if not ((s0>=0. and s1>=0. and s2>=0.) or
                            (s0<=0. and s1<=0. and s2<=0.)): continue
                    Nx=N_arr[j,0]; Ny=N_arr[j,1]; Nz=N_arr[j,2]
                    denom = dx*Nx+dy*Ny+dz*Nz
                    if abs(denom) < 1e-9: continue
                    t = (d_plane[j]-(ox*Nx+oy*Ny+oz*Nz)) / denom
                    if t < 1e-9 or t >= closest_t: continue
                    closest_t=t; closest_tri=j
            else:
                stack[sp]=left_child; stack[sp+1]=tri_end; sp+=2

        if closest_tri != -1:
            hit_triangle_ids[i] = closest_tri
            hit_distances[i]    = closest_t

    return hit_triangle_ids, hit_distances


# ══════════════════════════════════════════════════════════════════════════════
# 7. MULTI-BOUNCE SİMÜLASYONU
# ══════════════════════════════════════════════════════════════════════════════
def run_simulation(rays_o, rays_d, A, B, C,
                   dAB, mAB, dBC, mBC, dCA, mCA,
                   N_arr, d_plane,
                   bvh_nodes, bvh_meta, bvh_tids,
                   max_safety_limit=500):

    num_triangles = A.shape[0]
    hit_counts  = np.zeros(num_triangles, dtype=np.int32)
    angle_sum   = np.zeros(num_triangles, dtype=np.float64)
    angle_count = np.zeros(num_triangles, dtype=np.int32)
    bounce_paths = []

    print(f"\nIşınlar kaviteden çıkana kadar serbest bırakıldı!")
    current_rays_o = rays_o.copy()
    current_rays_d = rays_d.copy()

    monitor = ResourceMonitor(interval=0.1)
    monitor.start()
    total_sim_start = time.perf_counter()

    bounce = 0
    while bounce < max_safety_limit:
        bounce += 1
        num_active = current_rays_o.shape[0]
        print(f"  --> Sekme {bounce}: Kavite içinde {num_active} ışın...")

        hit_ids, hit_dists = plucker_bvh_tracer(
            current_rays_o, current_rays_d,
            dAB, mAB, dBC, mBC, dCA, mCA,
            N_arr, d_plane, bvh_nodes, bvh_meta, bvh_tids
        )

        valid_hits = hit_ids != -1
        if np.sum(valid_hits) == 0:
            print(f"  --> SONUÇ: Tüm ışınlar kaviteden çıktı! ({bounce-1}. sekmede bitti)")
            break

        valid_hit_ids = hit_ids[valid_hits]
        valid_rays_o  = current_rays_o[valid_hits]
        valid_rays_d  = current_rays_d[valid_hits]
        valid_dists   = hit_dists[valid_hits]
        hit_points    = valid_rays_o + valid_rays_d * valid_dists[:,np.newaxis]

        normals = N_arr[valid_hit_ids].copy()
        norm_lengths = np.linalg.norm(normals, axis=1)
        norm_lengths[norm_lengths == 0] = 1.0
        normals /= norm_lengths[:, np.newaxis]

        I = valid_rays_d
        dot_product = np.einsum('ij,ij->i', I, normals)
        cos_angles  = np.clip(np.abs(dot_product), 0.0, 1.0)
        angles_deg  = np.degrees(np.arccos(cos_angles))

        for k, hit_id in enumerate(valid_hit_ids):
            hit_counts[hit_id]  += 1
            angle_sum[hit_id]   += angles_deg[k] 
            angle_count[hit_id] += 1

        bounce_paths.append((valid_rays_o, hit_points))

        R = I - 2.0 * dot_product[:, np.newaxis] * normals
        current_rays_o = hit_points + R * 1e-4
        current_rays_d = R

    total_sim_end = time.perf_counter()
    monitor.stop()
    cpu_samples, ram_samples, time_samples = monitor.results()
    total_elapsed = total_sim_end - total_sim_start

    print(f"\n--- SİMÜLASYON BİTTİ ---")
    print(f"Toplam Süre: {total_elapsed:.4f} sn")
    if cpu_samples:
        print(f"CPU  Ort: {np.mean(cpu_samples):.1f}%  Maks: {np.max(cpu_samples):.1f}%")
        print(f"RAM  Ort: {np.mean(ram_samples):.0f} MB  Maks: {np.max(ram_samples):.0f} MB")

    avg_angles = np.zeros(num_triangles, dtype=np.float64)
    mask = angle_count > 0
    avg_angles[mask] = angle_sum[mask] / angle_count[mask]

    resource_data = {
        "cpu":  cpu_samples, "ram":   ram_samples,
        "times":time_samples,"duration":total_elapsed,
    }
    return hit_counts, avg_angles, bounce_paths, resource_data

def save_detailed_results_to_excel(hit_counts, avg_angles, n_theta, n_phi, filename="Simulasyon_Raporu.xlsx"):
    """
    Excel raporuna geliş/sekme açılarını ve toplam ışın bilgisini ekler.
    """
    import pandas as pd
    
    active_indices = np.where(hit_counts > 0)[0]
    if len(active_indices) == 0:
        print("⚠️ Kaydedilecek veri bulunamadı!")
        return

    # 1. Üçgen Bazlı Detaylar (Geliş ve Sekme Açıları)
    # Fiziksel olarak Geliş Açısı = Sekme Açısıdır.
    hit_data = {
        "Ucgen_ID": active_indices,
        "Vurus_Sayisi": hit_counts[active_indices],
        "Ortalama_Gelis_Acisi_Deg": avg_angles[active_indices],
        "Ortalama_Sekme_Acisi_Deg": avg_angles[active_indices] # Yansıma kuralı gereği aynıdır
    }
    df_hits = pd.DataFrame(hit_data).sort_values(by="Vurus_Sayisi", ascending=False)

    # 2. Genel İstatistikler ve Işın Bilgisi
    angles_only = avg_angles[active_indices]
    total_sent_rays = n_theta * n_phi # Kaynaktan çıkan toplam ışın
    total_bounces = np.sum(hit_counts) # Toplam gerçekleşen sekme sayısı

    summary_data = {
        "Metrik": [
            "Kaynaktan Çıkan Toplam Işın",
            "Toplam Gerçekleşen Sekme Sayısı",
            "Vuruş Alan Toplam Üçgen Sayısı",
            "Genel Ortalama Açı (Geliş/Sekme)",
            "Minimum Açı",
            "Maksimum Açı",
            "Açı Varyansı (Dağılım)",
            "En Çok Sekme Alan Üçgen ID"
        ],
        "Değer": [
            total_sent_rays,
            total_bounces,
            len(active_indices),
            np.mean(angles_only),
            np.min(angles_only),
            np.max(angles_only),
            np.var(angles_only),
            df_hits.iloc[0]["Ucgen_ID"]
        ]
    }
    df_summary = pd.DataFrame(summary_data)

    # Excel'e Kaydet
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df_summary.to_excel(writer, sheet_name='Genel_Ozet', index=False)
        df_hits.to_excel(writer, sheet_name='Detayli_Aci_Listesi', index=False)
    
    print(f"\n✅ Excel dosyası oluşturuldu: {filename}")
     
# ══════════════════════════════════════════════════════════════════════════════
# 8. GÖRSELLEŞTİRME
# ══════════════════════════════════════════════════════════════════════════════
def visualize(A, B, C, hit_counts, avg_angles, bounce_paths,
              origin, theta_range, phi_range, n_theta, n_phi,
              min_x, max_x, min_y, max_y, min_z, max_z,
              resource_data=None):

    total_rays  = n_theta * n_phi
    active_hits = hit_counts > 0

    if np.sum(active_hits) > 0:
        print(f"\n--- AÇI İSTATİSTİKLERİ ---")
        print(f"  Ortalama : {np.mean(avg_angles[active_hits]):.2f}°")
        print(f"  Min      : {np.min(avg_angles[active_hits]):.2f}°")
        print(f"  Max      : {np.max(avg_angles[active_hits]):.2f}°")
        print(f"  Çarpılan : {np.sum(active_hits)} üçgen")

    has_resource = (resource_data is not None
                    and len(resource_data.get("cpu",[])) > 1)

    if has_resource:
        fig = plt.figure(figsize=(22,14))
        gs  = gridspec.GridSpec(2, 3, figure=fig,
                                height_ratios=[1.15, 0.85],
                                hspace=0.38, wspace=0.35)
        fig.subplots_adjust(left=0.05,right=0.97,top=0.92,bottom=0.06)
    else:
        fig = plt.figure(figsize=(22,9))
        gs  = gridspec.GridSpec(1, 2, width_ratios=[1.1,1], figure=fig)
        fig.subplots_adjust(left=0.05,right=0.97,top=0.90,bottom=0.08,wspace=0.35)

    fig.suptitle(
        f"PLÜCKER + PRECOMPUTE + BVH  |  θ: {theta_range}°  |  φ: {phi_range}°  |  "
        f"Toplam Işın: {n_theta}×{n_phi} = {total_rays}",
        fontsize=12, fontweight='bold'
    )

    ax1 = fig.add_subplot(gs[0,0] if has_resource else gs[0], projection='3d')
    ax1.set_title('Vuruş Sayısı Isı Haritası', fontweight='bold')

    if np.sum(active_hits) > 0:
        hit_A  = A[active_hits]; hit_B = B[active_hits]; hit_C = C[active_hits]
        counts = hit_counts[active_hits]
        verts  = [[hit_A[i], hit_B[i], hit_C[i]] for i in range(len(hit_A))]
        norm1  = mcolors.Normalize(vmin=1, vmax=np.max(counts))
        cmap1  = plt.get_cmap('jet')
        ax1.add_collection3d(Poly3DCollection(verts, facecolors=cmap1(norm1(counts)),
                                               edgecolors='none', alpha=0.9))
        mappable1 = plt.cm.ScalarMappable(norm=norm1, cmap=cmap1)
        mappable1.set_array(counts)
        fig.colorbar(mappable1, ax=ax1, shrink=0.5, aspect=15,
                     label='Vuruş Sayısı')

    for start_pts, end_pts in bounce_paths:
        n    = start_pts.shape[0]
        step = max(1, n // 100)
        for i in range(0, n, step):
            ax1.plot([start_pts[i,0],end_pts[i,0]],
                     [start_pts[i,1],end_pts[i,1]],
                     [start_pts[i,2],end_pts[i,2]],
                     color='magenta', alpha=0.4, linewidth=0.5)

    ax1.scatter(*origin, color='cyan', s=300, marker='X',
                label='Radar Kaynağı', depthshade=False)
    ax1.scatter(A[::10,0],A[::10,1],A[::10,2],
                color='gray', s=0.1, alpha=0.05)
    ax1.set_xlabel('X (m)'); ax1.set_ylabel('Y (m)'); ax1.set_zlabel('Z (m)')
    ax1.set_xlim([min_x,max_x]); ax1.set_ylim([min_y,max_y]); ax1.set_zlim([min_z,max_z])
    ax1.view_init(elev=20, azim=45); ax1.legend(fontsize=8)

    ax2 = fig.add_subplot(gs[0,1] if has_resource else gs[1])
    ax2.set_title('Sekme Açıları Dağılımı\n(0°=Dik Çarpış  →  90°=Sıyırma)',
                  fontweight='bold')
    if np.sum(active_hits) > 0:
        angles = avg_angles[active_hits]
        ax2.hist(angles, bins=45, range=(0,90),
                 color='steelblue', edgecolor='white', linewidth=0.4, alpha=0.85)
        ax2.axvline(np.mean(angles), color='red', linestyle='--', linewidth=1.5,
                    label=f'Ort: {np.mean(angles):.1f}°')
        ax2.axvline(np.median(angles), color='orange', linestyle=':', linewidth=1.5,
                    label=f'Medyan: {np.median(angles):.1f}°')
        ax2.set_xlabel('Gelme Açısı (°)', fontsize=11)
        ax2.set_ylabel('Üçgen Sayısı', fontsize=11)
        ax2.set_xlim(0,90); ax2.legend(fontsize=9)
        ax2.grid(axis='y', linestyle='--', alpha=0.4)

    if has_resource:
        import psutil as _ps
        cpu_arr = np.array(resource_data["cpu"])
        ram_arr = np.array(resource_data["ram"])
        t_arr   = np.array(resource_data["times"])
        ram_gb  = ram_arr / 1024.0
        total_ram_gb = _ps.virtual_memory().total / (1024**3)

        ax3 = fig.add_subplot(gs[1,0])
        ax3.set_title('CPU Kullanımı — Zaman Serisi', fontweight='bold')
        ax3.plot(t_arr, cpu_arr, color='#2196F3', linewidth=1.0, alpha=0.8)
        ax3.fill_between(t_arr, cpu_arr, alpha=0.15, color='#2196F3')
        ax3.axhline(np.mean(cpu_arr),color='red',linestyle='--',linewidth=1.2,
                    label=f'Ort: {np.mean(cpu_arr):.1f}%')
        ax3.axhline(np.max(cpu_arr),color='orange',linestyle=':',linewidth=1.0,
                    label=f'Maks: {np.max(cpu_arr):.1f}%')
        ax3.set_xlabel('Süre (sn)'); ax3.set_ylabel('CPU (%)')
        ax3.set_ylim(0,max(100,np.max(cpu_arr)*1.15))
        ax3.set_xlim(0,t_arr[-1]); ax3.legend(fontsize=8)
        ax3.grid(linestyle='--',alpha=0.35)

        ax4 = fig.add_subplot(gs[1,1])
        ax4.set_title('RAM Kullanımı — Zaman Serisi', fontweight='bold')
        ax4.plot(t_arr, ram_gb, color='#4CAF50', linewidth=1.0, alpha=0.8)
        ax4.fill_between(t_arr, ram_gb, alpha=0.15, color='#4CAF50')
        ax4.axhline(np.mean(ram_gb),color='red',linestyle='--',linewidth=1.2,
                    label=f'Ort: {np.mean(ram_gb):.2f} GB')
        ax4.axhline(np.max(ram_gb),color='orange',linestyle=':',linewidth=1.0,
                    label=f'Maks: {np.max(ram_gb):.2f} GB')
        ax4.set_xlabel('Süre (sn)'); ax4.set_ylabel('RAM (GB)')
        ax4.set_xlim(0,t_arr[-1]); ax4.legend(fontsize=8)
        ax4.grid(linestyle='--',alpha=0.35)

        ax5 = fig.add_subplot(gs[1,2])
        ax5.axis('off')
        ax5.set_title('Kaynak Özeti', fontweight='bold')
        ram_delta = np.max(ram_gb) - ram_gb[0]
        pct_used  = (np.max(ram_gb) / total_ram_gb) * 100.0
        lines = [
            ("── CPU ──",""),("Ortalama",f"{np.mean(cpu_arr):.1f}%"),
            ("Maksimum",f"{np.max(cpu_arr):.1f}%"),
            ("Minimum",f"{np.min(cpu_arr):.1f}%"),
            ("",""),("── RAM ──",""),
            ("Ortalama",f"{np.mean(ram_gb):.2f} GB"),
            ("Maksimum",f"{np.max(ram_gb):.2f} GB"),
            ("Simülasyon artışı",f"+{ram_delta:.2f} GB"),
            ("Toplam RAM",f"{total_ram_gb:.1f} GB  ({pct_used:.1f}%)"),
            ("",""),("── GENEL ──",""),
            ("Simülasyon süresi",f"{resource_data['duration']:.2f} sn"),
            ("Örnekler",f"{len(cpu_arr)}"),
        ]
        y = 0.97
        for label, value in lines:
            if label.startswith("──"):
                ax5.text(0.05,y,label,transform=ax5.transAxes,
                         fontsize=9,fontweight='bold',color='#333333',va='top')
            elif label:
                ax5.text(0.05,y,label,transform=ax5.transAxes,
                         fontsize=9,color='#555555',va='top')
                ax5.text(0.65,y,value,transform=ax5.transAxes,
                         fontsize=9,fontweight='bold',color='#111111',va='top',ha='left')
            y -= 0.068

    plt.show()
