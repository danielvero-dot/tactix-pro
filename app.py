import streamlit as st
import time
from streamlit_autorefresh import st_autorefresh

# 1. SET CONFIG & HIGH-CONTRAST OUTDOOR THEME
st.set_page_config(
    page_title="Tactix Pro - High Contrast", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Injeksi CSS Khusus Outdoor: Roboto Condensed, Navy Blue & Racing Orange
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@400;700&display=swap');
    
    /* Paksa Background Putih Bersih & Teks Hitam Pekat */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-family: 'Roboto Condensed', sans-serif !important;
    }
    
    /* Navigasi Atas: Biru Navy, Teks Putih Tegas Gede */
    div[data-testid="stHorizontalBlock"] button {
        background-color: #1e3a8a !important;
        color: #ffffff !important;
        border: 2px solid #111827 !important;
        padding: 14px 5px !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        text-transform: uppercase;
    }
    
    /* Widget Metrik: Border Oranye Balap Tajam */
    div[data-testid="stMetric"] {
        background-color: #f8fafc !important;
        border: 3px solid #f97316 !important;
        padding: 15px;
        border-radius: 14px;
    }
    div[data-testid="stMetricLabel"] { 
        color: #1e293b !important; 
        font-size: 15px !important; 
        font-weight: 700 !important; 
        text-transform: uppercase;
    }
    div[data-testid="stMetricValue"] { 
        color: #1e3a8a !important; 
        font-size: 36px !important; 
        font-weight: 700 !important; 
    }
    
    /* Tombol Utama: Biru Navy Solid Teks Putih Gede Banget */
    div.stButton > button {
        background: #1e3a8a !important;
        color: #ffffff !important; 
        border: 3px solid #111827 !important;
        padding: 16px 24px !important;
        font-size: 18px !important;
        font-weight: 700 !important; 
        border-radius: 12px !important; 
        width: 100% !important;
        text-transform: uppercase;
    }
    
    /* Form & Input Label */
    label, p, span {
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }
    
    /* Kotak Highlight Low Time: Border Merah Gila-Gilaan */
    .low-time-box {
        background-color: #fef2f2 !important; 
        border: 4px solid #dc2626 !important; 
        padding: 14px; 
        border-radius: 10px; 
        margin-bottom: 12px;
    }
    .normal-time-box {
        background-color: #ffffff !important;
        border: 2px solid #1e3a8a !important;
        padding: 14px;
        border-radius: 10px;
        margin-bottom: 12px;
    }
    
    /* Status Box Lapangan vs Cadangan */
    .field-status-box {
        background-color: #f0fdf4 !important;
        border: 3px solid #16a34a !important;
        padding: 14px;
        border-radius: 10px;
        margin-bottom: 12px;
    }
    .bench-status-box {
        background-color: #fff7ed !important;
        border: 3px solid #f97316 !important; /* Oranye untuk Cadangan */
        padding: 14px;
        border-radius: 10px;
        margin-bottom: 18px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. GLOBAL SESSIONS MEMORY ---
if 'daftar_pemain' not in st.session_state:
    st.session_state.daftar_pemain = [
        "Simon", "Noah", "Nolan", "Harvey", "Anaya", 
        "Benjamin", "George", "Alistair", "Arjun", "William",
        "Laila", "Laclan", "James", "Thor", "Leroy"
    ]
if 'pemain_hadir' not in st.session_state:
    st.session_state.pemain_hadir = st.session_state.daftar_pemain.copy()
if 'kiper_terpilih' not in st.session_state:
    st.session_state.kiper_terpilih = "-- Select Goalkeeper --"
if 'pemain_di_lapangan' not in st.session_state:
    st.session_state.pemain_di_lapangan = []
if 'log_pergantian' not in st.session_state:
    st.session_state.log_pergantian = []
if 'menit_bermain' not in st.session_state:
    st.session_state.menit_bermain = {p: 0.0 for p in st.session_state.daftar_pemain}
if 'riwayat_kiper' not in st.session_state:
    st.session_state.riwayat_kiper = []

# Timer Memory
if 'timer_status' not in st.session_state:
    st.session_state.timer_status = "STOPPED"
if 'start_time' not in st.session_state:
    st.session_state.start_time = 0.0
if 'elapsed_minutes' not in st.session_state:
    st.session_state.elapsed_minutes = 0.0
if 'last_calculated_minute' not in st.session_state:
    st.session_state.last_calculated_minute = 0.0

# --- 3. SIDEBAR CONFIG ---
st.sidebar.markdown("### ⚙️ MATCH SETTINGS")
total_menit = st.sidebar.number_input("Total Match Duration (Mins)", min_value=1, value=50, step=5)
format_game = st.sidebar.number_input("Match Format (Players on Field)", min_value=1, value=9, step=1)
interval_ideal = st.sidebar.number_input("Rotation Alert Every (Mins)", min_value=1, value=10, step=1)

# Rumus Est Menit Main/Anak
total_hadir = len(st.session_state.pemain_hadir)
if st.session_state.kiper_terpilih != "-- Select Goalkeeper --":
    semua_kiper = [st.session_state.kiper_terpilih] + st.session_state.riwayat_kiper
    pemain_hadir_lapangan = [p for p in st.session_state.pemain_hadir if p not in semua_kiper]
    total_hadir_lapangan = len(pemain_hadir_lapangan)
    format_game_lapangan = format_game - 1
    menit_per_pemain = (total_menit * format_game_lapangan) / max(total_hadir_lapangan, 1)
else:
    pemain_hadir_lapangan = st.session_state.pemain_hadir
    total_hadir_lapangan = total_hadir
    format_game_lapangan = format_game
    menit_per_pemain = (total_menit * format_game) / max(total_hadir, 1)

# --- 4. SMOOTH BACKGROUND TIME TRACKING ---
if st.session_state.timer_status == "RUNNING":
    st_autorefresh(interval=5000, limit=1000, key="global_timer_refresh")
    current_elapsed = st.session_state.elapsed_minutes + ((time.time() - st.session_state.start_time) / 60.0)
    if current_elapsed >= total_menit:
        current_elapsed = float(total_menit)
        st.session_state.timer_status = "STOPPED"
        
    delta_time = current_elapsed - st.session_state.last_calculated_minute
    if delta_time > 0:
        for p in st.session_state.pemain_di_lapangan:
            st.session_state.menit_bermain[p] += delta_time
        st.session_state.last_calculated_minute = current_elapsed
else:
    current_elapsed = st.session_state.elapsed_minutes

# --- 5. INTERFACE NAVIGASI (4 SCREENS) ---
st.markdown("<h2 style='text-align: center; color: #000000; font-size: 26px; font-weight:700; margin-bottom: 5px;'>📋 TACTIX PRO</h2>", unsafe_allow_html=True)
menu_aktif = st.radio(
    "Navigation", 
    ["1. Attendance", "2. Set GK & Lineup", "3. Live Match & Subs", "4. Stats Tracker"], 
    horizontal=True, 
    label_visibility="collapsed"
)
st.write("---")

# SCREEN 1: ATTENDANCE CHECK
if menu_aktif == "1. Attendance":
    st.markdown("<h3 style='color: #1e3a8a; font-size: 22px; font-weight:700;'>⚡ Screen 1: Squad Check-In</h3>", unsafe_allow_html=True)
    col_absen1, col_absen2, col_absen3 = st.columns(3)
    temp_hadir = []
    for i, p in enumerate(st.session_state.daftar_pemain):
        target_col = col_absen1 if i % 3 == 0 else (col_absen2 if i % 3 == 1 else col_absen3)
        with target_col:
            if st.checkbox(p, value=(p in st.session_state.pemain_hadir), key=f"scr1_{p}"): temp_hadir.append(p)
    st.session_state.pemain_hadir = temp_hadir
    st.info(f"🟢 Total players present: {len(st.session_state.pemain_hadir)} players.")

# SCREEN 2: SET GK & STARTER
elif menu_aktif == "2. Set GK & Lineup":
    st.markdown("<h3 style='color: #1e3a8a; font-size: 22px; font-weight:700;'>🧤 Screen 2: Goalkeeper & Starting Lineup Setup</h3>", unsafe_allow_html=True)
    if total_hadir < format_game:
        st.error(f"Not enough players for a {format_game}v{format_game} match!")
    else:
        st.markdown("**1. Select Main Goalkeeper:**")
        kiper_baru_pilih = st.selectbox("Goalkeeper:", options=["-- Select Goalkeeper --"] + st.session_state.pemain_hadir, index=0 if st.session_state.kiper_terpilih not in st.session_state.pemain_hadir else st.session_state.pemain_hadir.index(st.session_state.kiper_terpilih)+1, label_visibility="collapsed")
        if kiper_baru_pilih != st.session_state.kiper_terpilih:
            st.session_state.kiper_terpilih = kiper_baru_pilih
            if kiper_baru_pilih != "-- Select Goalkeeper --" and kiper_baru_pilih not in st.session_state.pemain_di_lapangan:
                st.session_state.pemain_di_lapangan.append(kiper_baru_pilih)

        st.write("---")
        st.markdown(f"**2. Tap Player Names to Set Starting Lineup (Must Be Exactly {format_game} Players):**")
        jumlah_terpilih = len(st.session_state.pemain_di_lapangan)
        if jumlah_terpilih == format_game: st.success(f"🎉 Perfect! {jumlah_terpilih} Starters Selected.")
        else: st.warning(f"📋 Need {format_game - jumlah_terpilih} more player(s).")

        col_btn1, col_btn2, col_btn3 = st.columns(3)
        for i, p in enumerate(st.session_state.pemain_hadir):
            target_col = col_btn1 if i % 3 == 0 else (col_btn2 if i % 3 == 1 else col_btn3)
            with target_col:
                is_starter = p in st.session_state.pemain_di_lapangan
                label_tombol = f"💪 {p} (STARTER)" if is_starter else f"➕ {p}"
                if st.button(label_tombol, key=f"btn_choose_{p}"):
                    if is_starter: st.session_state.pemain_di_lapangan.remove(p)
                    else: st.session_state.pemain_di_lapangan.append(p)
                    st.rerun()

        st.write("---")
        if len(st.session_state.pemain_di_lapangan) == format_game:
            if st.session_state.kiper_terpilih != "-- Select Goalkeeper --" and st.session_state.kiper_terpilih not in st.session_state.pemain_di_lapangan:
                st.error(f"🚨 Main Goalkeeper ({st.session_state.kiper_terpilih}) must be part of the Starting Lineup!")
            else:
                st.success("✅ Setup complete! Move to Screen 3 for Kick-off.")

# SCREEN 3: LIVE MATCH & SUBS
elif menu_aktif == "3. Live Match & Subs":
    st.markdown("<h3 style='color: #1e3a8a; font-size: 22px; font-weight:700;'>🏃‍♂️ Screen 3: Live Dashboard & Rotation Control</h3>", unsafe_allow_html=True)
    if len(st.session_state.pemain_di_lapangan) != format_game:
        st.error("🚨 Lineup size mismatch! Please set your starting lineup on Screen 2 first.")
    else:
        # STOPWATCH CONTROLLER
        st.markdown("**⏱️ STOPWATCH CONTROL**")
        c1, c2 = st.columns(2)
        with c1:
            if st.session_state.timer_status == "STOPPED" and current_elapsed == 0:
                if st.button("▶️ START KICK-OFF"):
                    st.session_state.start_time = time.time()
                    st.session_state.last_calculated_minute = 0.0
                    st.session_state.timer_status = "RUNNING"
                    st.rerun()
            elif st.session_state.timer_status == "PAUSED" or (st.session_state.timer_status == "STOPPED" and current_elapsed > 0):
                if st.button("▶️ RESUME MATCH"):
                    st.session_state.start_time = time.time()
                    st.session_state.timer_status = "RUNNING"
                    st.rerun()
            elif st.session_state.timer_status == "RUNNING": st.success("⚽ MATCH IS LIVE NOW")

        with c2:
            if st.session_state.timer_status == "RUNNING":
                if st.button("⏸️ PAUSE MATCH"):
                    st.session_state.elapsed_minutes = current_elapsed
                    st.session_state.timer_status = "PAUSED"
                    st.rerun()

        # LIVE DASHBOARD METRICS
        st.write("")
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1: st.metric("CURRENT MATCH MINUTE", f"Min {current_elapsed:.1f}")
        with col_m2: st.metric("EST. TARGET MINS / PLAYER", f"{menit_per_pemain:.1f} Mins")
        with col_m3: st.metric("FIXED ROTATION ALERT EVERY", f"{float(interval_ideal):.1f} Mins")

        # --- SMART FIXED ROTATION ALERT ---
        if current_elapsed > 0:
            sisa_ke_jendela = current_elapsed % interval_ideal
            if sisa_ke_jendela < 1.0 and current_elapsed < total_menit:
                st.warning(f"🔔 **ROTATION TIME!** Match reached **{current_elapsed:.1f} mins**. Please swap players below!")

        # EMERGENCY GK INJURY PANEL
        if st.session_state.kiper_terpilih != "-- Select Goalkeeper --":
            with st.expander("🚨 GOALKEEPER EMERGENCY CHANGE"):
                kiper_baru = st.selectbox("New Goalkeeper:", options=["-- Select Substitute --"] + [p for p in st.session_state.pemain_hadir if p != st.session_state.kiper_terpilih])
                ganti_gk_darurat = st.button("🚨 EXECUTE EMERGENCY GK CHANGE")
                if ganti_gk_darurat and kiper_baru != "-- Select Substitute --":
                    st.session_state.riwayat_kiper.append(st.session_state.kiper_terpilih)
                    if kiper_baru in st.session_state.pemain_di_lapangan: st.session_state.pemain_di_lapangan.remove(kiper_baru)
                    st.session_state.pemain_di_lapangan.remove(st.session_state.kiper_terpilih)
                    st.session_state.pemain_di_lapangan.append(kiper_baru)
                    st.session_state.log_pergantian.append(f"🚨 **Min {current_elapsed:.1f}** | 🧤 GK CHANGE: {kiper_baru} for {st.session_state.kiper_terpilih}")
                    st.session_state.kiper_terpilih = kiper_baru
                    st.rerun()

        pemain_di_cadangan = [p for p in st.session_state.pemain_hadir if p not in st.session_state.pemain_di_lapangan]

        # Squad Status Box UI (Navy and Orange Border Elements)
        st.markdown(f"""
            <div class='field-status-box'>
                <span style='color: #16a34a; font-weight: bold; font-size: 14px;'>🟢 ACTIVE ON FIELD ({len(st.session_state.pemain_di_lapangan)})</span><br>
                <span style='font-size: 18px; font-weight: 700; color: #000000;'>{", ".join(st.session_state.pemain_di_lapangan)}</span>
            </div>
            <div class='bench-status-box'>
                <span style='color: #f97316; font-weight: bold; font-size: 14px;'>🔴 ON THE BENCH ({len(pemain_di_cadangan)})</span><br>
                <span style='font-size: 18px; font-weight: 700; color: #000000;'>{", ".join(pemain_di_cadangan) if pemain_di_cadangan else "None"}</span>
            </div>
        """, unsafe_allow_html=True)

        # SUBSTITUTION INPUT
        st.markdown("**🔄 Quick Substitution Controls:**")
        col_in, col_out = st.columns(2)
        with col_in: daftar_pemain_masuk = st.multiselect("🟢 Entering (From Bench):", options=pemain_di_cadangan, key="live_multi_in")
        with col_out:
            opsi_keluar = [p for p in st.session_state.pemain_di_lapangan if p != st.session_state.kiper_terpilih]
            daftar_pemain_keluar = st.multiselect("🔴 Exiting (To Bench):", options=opsi_keluar, key="live_multi_out")
            
        tambah_log = st.button("SUBSTITUTE PLAYERS NOW ⇄")
        if tambah_log:
            if len(daftar_pemain_masuk) > 0 and len(daftar_pemain_keluar) > 0:
                if len(daftar_pemain_masuk) == len(daftar_pemain_keluar):
                    for p_keluar in daftar_pemain_keluar: st.session_state.pemain_di_lapangan.remove(p_keluar)
                    for p_masuk in daftar_pemain_masuk: st.session_state.pemain_di_lapangan.append(p_masuk)
                    teks_masuk = ", ".join(daftar_pemain_masuk)
                    teks_keluar = ", ".join(daftar_pemain_keluar)
                    st.session_state.log_pergantian.append(f"⏱️ **Min {current_elapsed:.1f}** | 🟢 ({teks_masuk}) In ⇄ 🔴 ({teks_keluar}) Out")
                    st.rerun()
                else: st.error("🚨 Substitution mismatch!")

# SCREEN 4: MINUTE TRACKER (ROBOTO CONDENSED EXTRA BOLD)
elif menu_aktif == "4. Stats Tracker":
    st.markdown("<h3 style='color: #1e3a8a; font-size: 22px; font-weight:700;'>📊 Screen 4: Player Minutes Tracker & Logs</h3>", unsafe_allow_html=True)
    
    st.info(f"⏱️ **Match Progress:** Min {current_elapsed:.1f} / Alert Window Every {float(interval_ideal):.1f} Mins.")
    st.write("")
    st.markdown("**📉 Live Player Minutes Breakdown (Roboto Condensed - High Contrast):**")
    
    outfield_players = [p for p in st.session_state.pemain_hadir if p != st.session_state.kiper_terpilih and p not in st.session_state.riwayat_kiper]
    if outfield_players:
        rata_menit_skuad = sum(st.session_state.menit_bermain[p] for p in outfield_players) / len(outfield_players)
    else:
        rata_menit_skuad = 0.0

    for p in st.session_state.pemain_hadir:
        menit_sekarang = st.session_state.menit_bermain[p]
        persentase_main = min(menit_sekarang / total_menit, 1.0)
        status_badge = "🧤 GK" if p == st.session_state.kiper_terpilih else ("🟢 Active" if p in st.session_state.pemain_di_lapangan else "🔴 Bench")
        
        is_low_time = p != st.session_state.kiper_terpilih and p not in st.session_state.riwayat_kiper and menit_sekarang < rata_menit_skuad and current_elapsed > 5.0
        
        box_class = "low-time-box" if is_low_time else "normal-time-box"
        alert_badge = " <span style='background-color:#dc2626; color:white; padding:4px 8px; font-size:12px; font-weight:700; border-radius:4px; margin-left:5px;'>⚠️ LOW TIME</span>" if is_low_time else ""
        
        st.markdown(f"<div class='{box_class}'>", unsafe_allow_html=True)
        col_pname, col_pbar = st.columns([1.5, 3])
        with col_pname:
            st.markdown(f"<span style='font-size:18px; font-weight:700; color:#000000; text-transform:uppercase;'>{p}</span>{alert_badge}<br><span style='color:#475569; font-size:13px; font-weight:700;'>{status_badge}</span>", unsafe_allow_html=True)
        with col_pbar:
            st.progress(persentase_main, text=f"{menit_sekarang:.1f}m / target {menit_per_pemain:.1f}m")
        st.markdown("</div>", unsafe_allow_html=True)

    # MATCH HISTORY LOG
    if st.session_state.log_pergantian:
        st.write("---")
        st.markdown("**📝 Match Timeline & Logs**")
        for log in reversed(st.session_state.log_pergantian):
            st.markdown(f"<div style='background-color: #f1f5f9; border: 2px solid #1e3a8a; padding: 10px; border-radius: 8px; margin-bottom: 5px; font-size: 15px; color:#000000; font-weight:700;'>{log}</div>", unsafe_allow_html=True)
            
        if st.button("🗑️ Reset Entire Match"):
            st.session_state.log_pergantian = []
            st.session_state.menit_bermain = {p: 0.0 for p in st.session_state.daftar_pemain}
            st.session_state.elapsed_minutes = 0.0
            st.session_state.last_calculated_minute = 0.0
            st.session_state.riwayat_kiper = []
            st.session_state.pemain_di_lapangan = []
            st.session_state.kiper_terpilih = "-- Select Goalkeeper --"
            st.session_state.timer_status = "STOPPED"
            st.rerun()