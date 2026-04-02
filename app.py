"""
Planning Cabinet Pathologistes
Streamlit + PuLP (ILP solver)
Run: streamlit run app.py
Deploy: https://streamlit.io/cloud (gratuit)
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta
import math, uuid, json, calendar as cal_lib
from collections import defaultdict
import pulp

st.set_page_config(
    page_title="Planning Pathologistes",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.main-title {
    font-family: 'Syne', sans-serif; font-weight: 800; font-size: 28px;
    color: #17233a; display: flex; align-items: center; gap: 10px;
    border-bottom: 2px solid #1d7a6d; padding-bottom: 10px; margin-bottom: 20px;
}
.main-title em { color: #1d7a6d; font-style: normal; }

/* Week block */
.week-block {
    border: 1px solid #dcd7cf; border-radius: 12px; overflow: hidden;
    margin-bottom: 16px; box-shadow: 0 2px 10px rgba(23,35,58,.07);
}
.week-header {
    background: #17233a; color: white; padding: 8px 16px;
    display: flex; justify-content: space-between; align-items: center;
    font-family: 'DM Mono', monospace; font-size: 12px;
}
.week-num { color: #28a08e; font-weight: 700; }
.week-summary { display: flex; gap: 16px; align-items: center; flex-wrap: wrap; }
.wsitem { display: flex; align-items: center; gap: 4px; font-size: 11px; }
.wact { font-weight: 700; color: white; }
.wtgt { color: rgba(255,255,255,.35); }
.wdiff-ok  { color: #28a08e; font-weight: 700; font-size: 10px; }
.wdiff-bad { color: #d04050; font-weight: 700; font-size: 10px; }

/* Day cells */
.day-grid { display: grid; gap: 0; background: white; }
.day-cell {
    padding: 10px 9px; border-right: 1px solid #e7e2db;
    min-height: 120px; position: relative;
}
.day-cell:last-child { border-right: none; }
.day-cell.holiday { background: #fef8ef; }
.day-cell.past { opacity: 0.55; }
.day-cell.warn { background: #fff5f5; }
.day-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px; }
.day-name { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .6px; color: #8898a9; }
.day-num { font-family: 'Syne', sans-serif; font-weight: 800; font-size: 20px; color: #17233a; line-height: 1; }
.day-num.today { background: #1d7a6d; color: white; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; font-size: 13px; }
.holiday-tag { font-size: 9px; color: #c87b2d; font-weight: 700; background: #fdf1e3; padding: 2px 5px; border-radius: 3px; margin-bottom: 4px; display: block; }
.warn-tag { font-size: 9px; color: #b73640; font-weight: 700; background: #fce9ea; padding: 2px 5px; border-radius: 3px; margin-bottom: 4px; display: block; }
.chip {
    font-size: 10px; font-weight: 500; padding: 3px 7px; border-radius: 4px;
    display: flex; align-items: center; gap: 4px; margin-bottom: 3px; line-height: 1.3;
}
.chip-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; display: inline-block; }
.chip-act { font-family: 'DM Mono', monospace; font-size: 9px; margin-left: auto; font-weight: 700; opacity: .85; }
.chip-pct { font-size: 9px; opacity: .55; margin-left: 2px; }
.chip-abs { background: #fce9ea !important; color: #b73640 !important; text-decoration: line-through; }
.day-total { font-family: 'DM Mono', monospace; font-size: 9px; color: #8898a9; text-align: right; margin-top: 5px; border-top: 1px solid #e7e2db; padding-top: 4px; }

/* Week footer */
.week-foot {
    background: #f6f3ee; border-top: 1px solid #e7e2db;
    padding: 8px 14px; display: flex; gap: 16px; flex-wrap: wrap; align-items: center;
}
.wf-item { display: flex; align-items: center; gap: 6px; }
.wf-bar-wrap { width: 70px; height: 5px; background: #dcd7cf; border-radius: 3px; overflow: hidden; display: inline-block; }
.wf-bar { height: 100%; border-radius: 3px; display: inline-block; }
.wf-nums { font-family: 'DM Mono', monospace; font-size: 10px; color: #5d6d82; }
.wf-diff { font-family: 'DM Mono', monospace; font-size: 10px; font-weight: 700; }
.wf-diff.pos { color: #1d7a6d; }
.wf-diff.neg { color: #b73640; }
.wf-diff.zero { color: #8898a9; }

/* Legend chips */
.leg-chip {
    display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 500;
    background: white; border: 1px solid #dcd7cf; padding: 5px 10px; border-radius: 20px;
    margin: 3px;
}
.leg-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
.leg-tgt { font-family: 'DM Mono', monospace; font-size: 10px; color: #8898a9; }

/* Badge */
.bdg { font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 20px; display: inline-block; }
.bdg-teal { background: #e3f2f0; color: #1d7a6d; }
.bdg-amber { background: #fdf1e3; color: #c87b2d; }
.bdg-rose { background: #fce9ea; color: #b73640; }
.bdg-green { background: #e4f2ea; color: #2a7d50; }
.bdg-navy { background: #eef0f3; color: #5d6d82; }
.bdg-ok { background: rgba(28,160,130,.15); color: #28a08e; }

/* Alert */
.alert-warn { background: #fdf1e3; border: 1px solid #c87b2d; border-radius: 8px; padding: 10px 14px; font-size: 13px; color: #c87b2d; margin-bottom: 14px; }
.alert-info { background: #e3f2f0; border: 1px solid #1d7a6d; border-radius: 8px; padding: 10px 14px; font-size: 13px; color: #1d7a6d; margin-bottom: 14px; }

/* Stats bar */
.prog-bar-wrap { background: #dcd7cf; border-radius: 4px; height: 8px; overflow: hidden; }
.prog-bar { height: 100%; border-radius: 4px; }
.stat-box { background: white; border: 1px solid #dcd7cf; border-radius: 10px; padding: 16px; text-align: center; }
.stat-val { font-family: 'Syne', sans-serif; font-weight: 800; font-size: 30px; color: #17233a; line-height: 1; }
.stat-lbl { font-size: 11px; text-transform: uppercase; letter-spacing: .5px; color: #5d6d82; margin-top: 3px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────────────────────────
DEFAULTS = {
    "pathologistes": [],
    "absences": [],
    "planning": {},        # iso_date -> [patho_id, ...]
    "plan_alerts": [],
    "settings": {
        "days": 5,          # working days per week (4,5,6)
        "activity": 70,     # total daily activity unit
        "min_present": 2,   # min doctors per day
        "region": "metro",
        "conc2": 650,       # monthly activity threshold for 2 days/week (concentré)
        "conc3": 900,
        "conc4": 1200,
        "show_pct": True,
        "show_act": True,
        "show_wf": True,
    },
    "current_year": date.today().year,
    "current_month": date.today().month,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v if not isinstance(v, dict) else dict(v)

SS = st.session_state  # shorthand

COLORS = ["#1d7a6d","#7c5cbf","#c87b2d","#b73640","#2c6fa7",
          "#6a7e28","#af5898","#267851","#a04e2e","#3a798e","#874365","#4a5f80"]
JOURS = ["Lun","Mar","Mer","Jeu","Ven","Sam"]
JOURS_FULL = ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi"]
MOIS = ["Janvier","Février","Mars","Avril","Mai","Juin",
        "Juillet","Août","Septembre","Octobre","Novembre","Décembre"]

# ─────────────────────────────────────────────────────────────────────────────
# UTILS
# ─────────────────────────────────────────────────────────────────────────────
def uid(): return str(uuid.uuid4())[:8]
def tp(): return sum(p["parts"] for p in SS.pathologistes)
def gp(pid): return next((p for p in SS.pathologistes if p["id"] == pid), None)
def is_absent(pid, d):
    for a in SS.absences:
        if a["patho_id"] == pid:
            s = date.fromisoformat(a["start"])
            e = date.fromisoformat(a["end"])
            if s <= d <= e:
                return True
    return False

# ─────────────────────────────────────────────────────────────────────────────
# JOURS FÉRIÉS
# ─────────────────────────────────────────────────────────────────────────────
def get_easter(year):
    a,b,c=year%19,year//100,year%100
    d,e=b//4,b%4
    f=(b+8)//25; g=(b-f+1)//3
    h=(19*a+b-d-g+15)%30; i=c//4; k=c%4
    l=(32+2*e+2*i-h-k)%7; m=(a+11*h+22*l)//451
    mo=(h+l-7*m+114)//31; dy=(h+l-7*m+114)%31+1
    return date(year, mo, dy)

def get_holidays(year, region="metro"):
    E = get_easter(year)
    H = {}
    def a(d, lbl): H[d] = lbl
    a(date(year,1,1),   "Jour de l'An")
    a(E+timedelta(1),   "Lundi de Pâques")
    a(date(year,5,1),   "Fête du Travail")
    a(date(year,5,8),   "Victoire 1945")
    a(E+timedelta(39),  "Ascension")
    a(E+timedelta(50),  "Lundi de Pentecôte")
    a(date(year,7,14),  "Fête Nationale")
    a(date(year,8,15),  "Assomption")
    a(date(year,11,1),  "Toussaint")
    a(date(year,11,11), "Armistice")
    a(date(year,12,25), "Noël")
    if region == "alsace":
        a(E-timedelta(2),    "Vendredi Saint")
        a(date(year,12,26),  "Saint-Étienne")
    return H

def get_work_days(year, month, H, max_dow):
    out = []
    for d in range(1, cal_lib.monthrange(year, month)[1]+1):
        dt = date(year, month, d)
        if dt.weekday() <= max_dow and dt not in H:
            out.append(dt)
    return out

def get_weeks(year, month, H, max_dow):
    weeks = defaultdict(list)
    for dt in get_work_days(year, month, H, max_dow):
        monday = dt - timedelta(days=dt.weekday())
        weeks[monday].append(dt)
    return dict(sorted(weeks.items()))

# ─────────────────────────────────────────────────────────────────────────────
# LARGEST REMAINDER (Hamilton method)
# ─────────────────────────────────────────────────────────────────────────────
def lr_method(items, total):
    """items: [(id, float)], total: int → {id: int}, sum == total"""
    arr = [(id_, v, math.floor(v), v % 1) for id_, v in items]
    extra = round(total) - sum(x[2] for x in arr)
    arr.sort(key=lambda x: (-x[3], x[0]))
    return {x[0]: x[2] + (1 if i < extra else 0) for i, x in enumerate(arr)}

# ─────────────────────────────────────────────────────────────────────────────
# CONCENTRÉ — max days per week
# ─────────────────────────────────────────────────────────────────────────────
def conc_max_days(p, approx_work_days=21):
    T = tp()
    if T == 0: return SS.settings["days"]
    s = SS.settings
    monthly_target = p["parts"] / T * approx_work_days * s["activity"]
    if monthly_target > s["conc4"]: return s["days"]  # treat as spread
    if monthly_target > s["conc3"]: return 4
    if monthly_target > s["conc2"]: return 3
    return 2

# ─────────────────────────────────────────────────────────────────────────────
# ILP SOLVER (PuLP / CBC)
# ─────────────────────────────────────────────────────────────────────────────
def solve_week(pathos, days, abs_set, min_present, settings, use_wishes=True):
    """
    ILP formulation for one week.
    Guarantees exact LR target per doctor.
    Maximizes wish satisfaction as secondary objective.
    abs_set: set of (patho_id, date)
    Returns: {date: [patho_id, ...]}
    """
    if not days or not pathos:
        return {d: [] for d in days}

    T = sum(p["parts"] for p in pathos)
    if T == 0:
        return {d: [] for d in days}

    W = len(days)
    s = settings

    # ── Compute exact targets (LR) ───────────────────────────────────
    def avail_count(p):
        return sum(1 for d in days if (p["id"], d) not in abs_set)

    raw = []
    for p in pathos:
        prop = p["parts"] / T * W
        if p["mode"] == "concentrated":
            prop = min(prop, conc_max_days(p))
        prop = min(prop, avail_count(p))
        raw.append((p["id"], prop))

    nat_sum = sum(v for _, v in raw)
    needed_slots = min_present * W

    if nat_sum >= needed_slots - 0.01:
        tgt_total = max(round(nat_sum), 0)
    else:
        if nat_sum > 0:
            scale = needed_slots / nat_sum
            raw = []
            for p in pathos:
                prop = min(avail_count(p), p["parts"] / T * W * scale)
                if p["mode"] == "concentrated":
                    prop = min(prop, conc_max_days(p))
                raw.append((p["id"], prop))
        tgt_total = max(round(needed_slots), 0)

    targets = lr_method(raw, tgt_total)
    for p in pathos:
        targets[p["id"]] = min(targets.get(p["id"], 0), avail_count(p))

    # ── Create LP problem ─────────────────────────────────────────────
    prob = pulp.LpProblem("week", pulp.LpMaximize)

    # x[pid][di] ∈ {0,1}
    x = {p["id"]: {di: pulp.LpVariable(f"x_{p['id']}_{di}", cat="Binary")
                   for di in range(W)}
         for p in pathos}

    # Force absences to 0
    for p in pathos:
        for di, d in enumerate(days):
            if (p["id"], d) in abs_set:
                prob += x[p["id"]][di] == 0

    # Hard constraint 1: each doctor works exactly target days
    for p in pathos:
        prob += pulp.lpSum(x[p["id"]][di] for di in range(W)) == targets[p["id"]]

    # Hard constraint 2: min_present per day
    for di in range(W):
        prob += pulp.lpSum(x[p["id"]][di] for p in pathos) >= min_present

    # ── Objective: wish satisfaction + mode bonus ─────────────────────
    obj = []

    # Adjacent-day auxiliary variables (reused for both mode bonus and consec wish)
    adj = {}  # (pid, di) -> LpVar
    for p in pathos:
        for di in range(W - 1):
            v = pulp.LpVariable(f"adj_{p['id']}_{di}", cat="Binary")
            prob += v <= x[p["id"]][di]
            prob += v <= x[p["id"]][di + 1]
            prob += v >= x[p["id"]][di] + x[p["id"]][di + 1] - 1
            adj[(p["id"], di)] = v
        # Wrap-around: Fri ↔ Mon (cyclic consecutive)
        if W >= 2:
            v = pulp.LpVariable(f"adjW_{p['id']}", cat="Binary")
            prob += v <= x[p["id"]][0]
            prob += v <= x[p["id"]][W - 1]
            prob += v >= x[p["id"]][0] + x[p["id"]][W - 1] - 1
            adj[(p["id"], "W")] = v

    for p in pathos:
        # Mode bonus: spread (penalize adjacency) vs concentrated (reward adjacency)
        for key, av in adj.items():
            if key[0] != p["id"]: continue
            if p["mode"] == "spread":
                obj.append(-30 * av)    # spread: avoid consecutive days
            else:
                obj.append(+30 * av)   # concentrated: prefer consecutive days

        if not use_wishes:
            continue

        # Wish scoring (priority 1 → base 1000, prio 5 → base 200)
        for w in sorted(p.get("wishes", []), key=lambda w: w["priority"]):
            base = 1000.0 / w["priority"]
            wtype = w["type"]
            wdays = set(w.get("days") or [])

            if wtype == "prefer":
                for di, d in enumerate(days):
                    if d.weekday() in wdays:
                        obj.append(base * x[p["id"]][di])

            elif wtype == "avoid":
                for di, d in enumerate(days):
                    if d.weekday() in wdays:
                        obj.append(-base * x[p["id"]][di])

            elif wtype == "consecutive":
                # Bonus for each adjacent pair assigned
                for key, av in adj.items():
                    if key[0] == p["id"]:
                        obj.append(base * av)

    if obj:
        prob += pulp.lpSum(obj)

    # ── Solve ─────────────────────────────────────────────────────────
    solver = pulp.PULP_CBC_CMD(msg=0, timeLimit=15)
    prob.solve(solver)

    if pulp.LpStatus[prob.status] == "Infeasible":
        return None

    # Extract
    result = {d: [] for d in days}
    for p in pathos:
        for di, d in enumerate(days):
            val = pulp.value(x[p["id"]][di])
            if val is not None and val > 0.5:
                result[d].append(p["id"])

    return result


# ─────────────────────────────────────────────────────────────────────────────
# GENERATE PLANNING
# ─────────────────────────────────────────────────────────────────────────────
def generate_planning():
    year, month = SS.current_year, SS.current_month
    s = SS.settings
    H = get_holidays(year, s["region"])
    max_dow = s["days"] - 1
    weeks = get_weeks(year, month, H, max_dow)

    # Build absences set
    abs_set = set()
    for ab in SS.absences:
        d = date.fromisoformat(ab["start"])
        end = date.fromisoformat(ab["end"])
        while d <= end:
            if d.weekday() <= max_dow and d not in H:
                abs_set.add((ab["patho_id"], d))
            d += timedelta(1)

    planning = {}
    alerts = []

    progress = st.progress(0, text="Génération du planning en cours…")
    total_weeks = len(weeks)

    for wi, (monday, days) in enumerate(weeks.items()):
        progress.progress((wi) / max(total_weeks, 1),
                          text=f"Semaine du {monday.strftime('%d/%m')}…")

        result = solve_week(SS.pathologistes, days, abs_set, s["min_present"], s, use_wishes=True)

        if result is None:
            # Retry without wishes
            result = solve_week(SS.pathologistes, days, abs_set, s["min_present"], s, use_wishes=False)
            alerts.append(f"⚠️ Semaine du {monday.strftime('%d/%m/%Y')} : certains vœux ont été ignorés pour garantir l'équilibre.")

        if result is None:
            alerts.append(f"❌ Semaine du {monday.strftime('%d/%m/%Y')} : impossible de trouver une solution (contraintes trop fortes).")
            for d in days:
                planning[d.isoformat()] = []
        else:
            for d, pids in result.items():
                planning[d.isoformat()] = pids

    progress.progress(1.0, text="✅ Planning généré !")
    import time; time.sleep(0.5); progress.empty()

    SS.planning = planning
    SS.plan_alerts = alerts

    # Compute max deviation
    wd = get_work_days(year, month, H, max_dow)
    T = tp()
    total_act = len(wd) * s["activity"]
    max_dev = 0.0
    for p in SS.pathologistes:
        tgt = (p["parts"] / T * total_act) if T > 0 else 0
        act = 0.0
        for d in wd:
            pres = planning.get(d.isoformat(), [])
            pp = sum((gp(pid) or {}).get("parts", 0) for pid in pres)
            if p["id"] in pres and pp > 0:
                act += s["activity"] * p["parts"] / pp
        dev = abs(act - tgt) / tgt * 100 if tgt > 0 else 0
        max_dev = max(max_dev, dev)

    return max_dev, alerts


# ─────────────────────────────────────────────────────────────────────────────
# CALENDAR RENDER
# ─────────────────────────────────────────────────────────────────────────────
def activity_on_day(pid, d_iso, planning, settings):
    pres = planning.get(d_iso, [])
    if pid not in pres:
        return 0.0
    pp = sum((gp(p) or {}).get("parts", 0) for p in pres)
    if pp == 0:
        return 0.0
    p = gp(pid)
    return settings["activity"] * p["parts"] / pp if p else 0.0

def render_calendar():
    year, month = SS.current_year, SS.current_month
    s = SS.settings
    H = get_holidays(year, s["region"])
    max_dow = s["days"] - 1
    nCols = s["days"]
    today = date.today()
    T = tp()
    planning = SS.planning
    pathos = SS.pathologistes
    has_plan = bool(planning)

    wd = get_work_days(year, month, H, max_dow)
    total_month_act = len(wd) * s["activity"]

    # ── Header ────────────────────────────────────────────────────────
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"<div class='main-title'>🔬 Planning<em>.</em>Patho — {MOIS[month-1]} {year}</div>", unsafe_allow_html=True)
        sub = f"{len(pathos)} pathologiste(s) · {T} parts · activité/jour: {s['activity']} · min {s['min_present']}/jour"
        st.caption(sub)
    with col2:
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            if st.button("◀ Préc.", use_container_width=True):
                if SS.current_month == 1:
                    SS.current_month = 12; SS.current_year -= 1
                else:
                    SS.current_month -= 1
                st.rerun()
        with c2:
            if st.button("Aujourd'hui", use_container_width=True):
                SS.current_year = date.today().year; SS.current_month = date.today().month
                st.rerun()
        with c3:
            if st.button("Suiv. ▶", use_container_width=True):
                if SS.current_month == 12:
                    SS.current_month = 1; SS.current_year += 1
                else:
                    SS.current_month += 1
                st.rerun()
        with c4:
            if st.button("⚡ Générer", use_container_width=True, type="primary"):
                if not pathos:
                    st.error("Ajoutez d'abord des pathologistes.")
                else:
                    max_dev, alerts = generate_planning()
                    if max_dev > 5:
                        st.warning(f"Écart max d'activité : {max_dev:.1f}% — vérifiez les vœux ou absences.")
                    else:
                        st.success(f"Planning généré ! Écart max : {max_dev:.1f}%")
                    st.rerun()
        with c5:
            if st.button("🔴 Absence", use_container_width=True):
                SS["show_abs_form"] = not SS.get("show_abs_form", False)
                st.rerun()

    # Absence quick form
    if SS.get("show_abs_form"):
        with st.expander("🔴 Déclarer une absence", expanded=True):
            a1, a2, a3, a4 = st.columns(4)
            with a1:
                who = st.selectbox("Pathologiste", [p["name"] for p in pathos], key="abs_who")
            with a2:
                abs_start = st.date_input("Début", key="abs_start")
            with a3:
                abs_end = st.date_input("Fin", key="abs_end")
            with a4:
                reason = st.text_input("Motif", key="abs_reason")
            if st.button("Enregistrer l'absence"):
                pid = next(p["id"] for p in pathos if p["name"] == who)
                end = abs_end if abs_end >= abs_start else abs_start
                SS.absences.append({"id": uid(), "patho_id": pid,
                                    "start": abs_start.isoformat(), "end": end.isoformat(),
                                    "reason": reason})
                SS["show_abs_form"] = False
                st.success("Absence enregistrée.")
                st.rerun()

    # Alerts
    for al in SS.plan_alerts:
        st.markdown(f"<div class='alert-warn'>{al}</div>", unsafe_allow_html=True)

    # Legend
    if pathos:
        leg_html = "<div style='display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px'>"
        for p in pathos:
            pct = round(p["parts"] / T * 100) if T else 0
            tgt = round(p["parts"] / T * total_month_act) if T else 0
            mode_lbl = f"Concentré ≤{conc_max_days(p)}j/sem" if p["mode"] == "concentrated" else "Lissé"
            leg_html += (f"<span class='leg-chip'>"
                         f"<span class='leg-dot' style='background:{p['color']}'></span>"
                         f"<strong>{p['name']}</strong> "
                         f"<span class='bdg bdg-teal'>{p['parts']}p · {pct}%</span> "
                         f"<span style='font-size:11px;color:#8898a9'>{mode_lbl}</span> "
                         f"<span class='leg-tgt'>cible: {tgt}</span>"
                         f"</span>")
        leg_html += "</div>"
        st.markdown(leg_html, unsafe_allow_html=True)

    # Build week map
    weeks = get_weeks(year, month, H, max_dow)
    if not weeks:
        st.info("Aucun jour ouvré ce mois.")
        return

    for monday, days in weeks.items():
        wnum = monday.isocalendar()[1]
        work_cols = [d for d in days if d not in H]

        # Week activity stats
        w_act = {p["id"]: 0.0 for p in pathos}
        w_days = {p["id"]: 0 for p in pathos}
        for d in work_cols:
            pres = planning.get(d.isoformat(), [])
            pp = sum((gp(pid) or {}).get("parts", 0) for pid in pres)
            for pid in pres:
                p = gp(pid)
                if p and pp > 0:
                    w_act[p["id"]] += s["activity"] * p["parts"] / pp
                    w_days[p["id"]] += 1

        w_tgt = {p["id"]: (p["parts"] / T * len(work_cols) * s["activity"] if T else 0) for p in pathos}
        w_tgt_d = {p["id"]: (p["parts"] / T * len(work_cols) if T else 0) for p in pathos}

        has_hol = any(d in H for d in days)
        warn_days = sum(1 for d in work_cols if len(planning.get(d.isoformat(), [])) < s["min_present"]) if has_plan else 0

        # Week header
        hdr_sum = ""
        if has_plan and pathos:
            for p in pathos:
                a = w_act[p["id"]]
                t = w_tgt[p["id"]]
                diff = a - t
                diff_cls = "wdiff-ok" if abs(diff) <= t * 0.05 + 0.5 else "wdiff-bad"
                diff_str = f"{'+' if diff >= 0 else ''}{diff:.0f}"
                hdr_sum += (f"<div class='wsitem'>"
                            f"<span style='width:8px;height:8px;border-radius:50%;background:{p['color']};display:inline-block'></span>"
                            f"<span style='font-size:10px;color:rgba(255,255,255,.5)'>{p['name'].split()[-1]}</span>"
                            f"<span class='wact'>{a:.0f}</span><span class='wsit'>/{t:.0f}</span>"
                            f"<span class='{diff_cls}'>{diff_str}</span></div>")

        badges = ""
        if has_hol: badges += "<span class='bdg bdg-amber' style='font-size:10px'>🏖️ Férié</span> "
        if warn_days: badges += f"<span class='bdg bdg-rose' style='font-size:10px'>⚠ {warn_days}j sous min</span> "
        if has_plan and not warn_days: badges += "<span class='bdg bdg-ok' style='font-size:10px'>✓ OK</span>"

        st.markdown(f"""
        <div class='week-block'>
        <div class='week-header'>
            <div>Semaine <span class='week-num'>{wnum}</span> &nbsp; {badges}</div>
            <div class='week-summary'>{hdr_sum}</div>
        </div>
        """, unsafe_allow_html=True)

        # Day columns (using st.columns so Streamlit handles layout)
        cols = st.columns(nCols)
        DOW_NAMES = ["LUN","MAR","MER","JEU","VEN","SAM"]

        for i, col in enumerate(cols):
            # Find the date for this column (dow == i)
            cell_date = next((d for d in days if d.weekday() == i), None)
            with col:
                if cell_date is None:
                    st.markdown("<div class='day-cell' style='background:#f0ede7;opacity:.3;min-height:120px'></div>",
                                unsafe_allow_html=True)
                    continue

                is_hol = cell_date in H
                is_past = cell_date < today
                is_today = cell_date == today
                pres = planning.get(cell_date.isoformat(), [])
                pp = sum((gp(pid) or {}).get("parts", 0) for pid in pres)
                warn_min = not is_hol and has_plan and len(pres) < s["min_present"]

                day_cls = "day-cell"
                if is_hol: day_cls += " holiday"
                if is_past: day_cls += " past"
                if warn_min: day_cls += " warn"

                num_html = (f"<div class='day-num today'>{cell_date.day}</div>" if is_today
                            else f"<div class='day-num'>{cell_date.day}</div>")

                tags = ""
                if is_hol:
                    tags += f"<span class='holiday-tag'>{H[cell_date]}</span>"
                if warn_min:
                    tags += f"<span class='warn-tag'>⚠ &lt;{s['min_present']}</span>"

                chips_html = ""
                for p in pathos:
                    here = p["id"] in pres
                    absent = is_absent(p["id"], cell_date)
                    if not here and not absent:
                        continue
                    act = (s["activity"] * p["parts"] / pp) if (here and not absent and pp > 0) else 0
                    pct_v = round(p["parts"] / T * 100) if T else 0
                    chip_cls = "chip chip-abs" if absent else "chip"
                    bg = "" if absent else f"background:{p['color']}1a;color:{p['color']}"
                    dot_c = "var(--rose,#b73640)" if absent else p["color"]
                    act_s = (f"<span class='chip-act'>{act:.0f}</span>" if s["show_act"] and here and not absent else "")
                    pct_s = (f"<span class='chip-pct'>({pct_v}%)</span>" if s["show_pct"] and here and not absent else "")
                    abs_s = "<span style='font-size:9px'>(abs.)</span>" if absent else ""
                    chips_html += (f"<div class='{chip_cls}' style='{bg}'>"
                                   f"<span class='chip-dot' style='background:{dot_c}'></span>"
                                   f"<span>{p['name'].split()[-1]}</span>{act_s}{pct_s}{abs_s}</div>")

                if not chips_html and not is_hol:
                    chips_html = "<span style='font-size:10px;color:#b7c3cf'>—</span>"

                tot_html = f"<div class='day-total'>Total : {s['activity']}</div>" if pres and not is_hol else ""

                cell_html = f"""
                <div class='{day_cls}'>
                  <div class='day-header'>
                    <div>
                      <div class='day-name'>{DOW_NAMES[i]}</div>
                      {tags}
                    </div>
                    {num_html}
                  </div>
                  <div class='chips'>{chips_html}</div>
                  {tot_html}
                </div>"""
                st.markdown(cell_html, unsafe_allow_html=True)

        # Week footer
        if s["show_wf"] and has_plan and pathos:
            foot_html = "<div class='week-foot'>"
            for p in pathos:
                nd = w_days[p["id"]]
                ntg = w_tgt_d[p["id"]]
                a = w_act[p["id"]]
                t = w_tgt[p["id"]]
                pct_bar = min(100, a / t * 100) if t else 0
                day_diff = nd - round(ntg)
                dcls = "zero" if day_diff == 0 else ("pos" if day_diff > 0 else "neg")
                diff_str = f"{'+' if day_diff >= 0 else ''}{day_diff}j"
                foot_html += f"""
                <div class='wf-item'>
                  <span style='width:8px;height:8px;border-radius:50%;background:{p["color"]};display:inline-block'></span>
                  <strong style='font-size:11px'>{p["name"].split()[-1]}</strong>
                  <span class='wf-bar-wrap'><span class='wf-bar' style='width:{pct_bar:.0f}%;background:{p["color"]}'></span></span>
                  <span class='wf-nums'>{nd}j/{ntg:.1f}j · {a:.0f}/{t:.0f} act.</span>
                  <span class='wf-diff {dcls}'>{diff_str}</span>
                </div>"""
            foot_html += "</div>"
            st.markdown(foot_html, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)  # close .week-block


# ─────────────────────────────────────────────────────────────────────────────
# PATHOLOGISTE FORM
# ─────────────────────────────────────────────────────────────────────────────
def render_pathologistes():
    st.markdown("<div class='main-title'>👥 Équipe médicale</div>", unsafe_allow_html=True)

    # Add / Edit
    with st.expander("➕ Ajouter / modifier un pathologiste", expanded=not SS.pathologistes):
        editing = SS.get("editing_patho")
        ep = gp(editing) if editing else None

        c1, c2, c3 = st.columns([3, 1, 2])
        with c1:
            name = st.text_input("Nom / Prénom", value=ep["name"] if ep else "", key="pf_name")
        with c2:
            parts = st.number_input("Parts", min_value=0.5, max_value=20.0, step=0.5,
                                    value=float(ep["parts"]) if ep else 1.0, key="pf_parts")
        with c3:
            mode = st.selectbox("Mode de présence",
                                ["spread", "concentrated"],
                                format_func=lambda x: "Lissé — activité égale chaque jour" if x == "spread" else "Concentré — jours groupés",
                                index=0 if (not ep or ep["mode"] == "spread") else 1,
                                key="pf_mode")

        # Color
        used_colors = [p["color"] for p in SS.pathologistes if p["id"] != editing]
        default_color = ep["color"] if ep else next((c for c in COLORS if c not in used_colors), COLORS[0])
        st.markdown("**Couleur**")
        color_cols = st.columns(len(COLORS))
        sel_color = SS.get("pf_color", default_color)
        for i, c in enumerate(COLORS):
            with color_cols[i]:
                border = "3px solid #17233a" if sel_color == c else "3px solid transparent"
                if st.button("  ", key=f"col_{i}",
                             help=c,
                             use_container_width=True):
                    SS["pf_color"] = c
                    st.rerun()
                st.markdown(f"<div style='width:22px;height:22px;border-radius:50%;background:{c};border:{border};margin:auto'></div>",
                            unsafe_allow_html=True)

        # Wishes
        st.markdown("---")
        st.markdown("**⭐ Vœux / Desiderata**")

        wishes = SS.get("tmp_wishes", ep["wishes"] if ep else [])
        SS["tmp_wishes"] = wishes

        if wishes:
            for w in sorted(wishes, key=lambda w: w["priority"]):
                wc1, wc2, wc3, wc4 = st.columns([1, 2, 3, 1])
                with wc1:
                    st.markdown(f"<span class='bdg bdg-teal'>Vœu n°{w['priority']}</span>", unsafe_allow_html=True)
                with wc2:
                    type_lbl = {"prefer": "✅ Préférer", "avoid": "🚫 Éviter", "consecutive": "📅 Consécutifs"}[w["type"]]
                    st.write(type_lbl)
                with wc3:
                    if w["type"] != "consecutive":
                        st.write(" · ".join(JOURS[i] for i in (w.get("days") or [])))
                    else:
                        st.write("(jours adjacents)")
                with wc4:
                    if st.button("🗑️", key=f"del_wish_{w['id']}"):
                        SS["tmp_wishes"] = [x for x in wishes if x["id"] != w["id"]]
                        st.rerun()

        st.markdown("**Ajouter un vœu :**")
        wa, wb, wc, wd_ = st.columns([1, 2, 3, 1])
        with wa:
            w_prio = st.selectbox("Priorité", [1, 2, 3, 4, 5],
                                  format_func=lambda x: f"⭐"*max(1,4-x)+f" Vœu n°{x}", key="wf_prio")
        with wb:
            w_type = st.selectbox("Type", ["prefer", "avoid", "consecutive"],
                                  format_func=lambda x: {"prefer":"✅ Préférer ces jours","avoid":"🚫 Éviter ces jours","consecutive":"📅 Jours consécutifs"}[x],
                                  key="wf_type")
        with wc:
            if w_type != "consecutive":
                ndays = SS.settings["days"]
                w_days_sel = st.multiselect("Jours", list(range(ndays)),
                                            format_func=lambda i: JOURS[i], key="wf_days")
            else:
                st.info("Le médecin cherchera à travailler des jours consécutifs.")
                w_days_sel = []
        with wd_:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Ajouter", key="add_wish_btn"):
                if w_type != "consecutive" and not w_days_sel:
                    st.error("Sélectionnez au moins un jour.")
                else:
                    SS["tmp_wishes"] = wishes + [{"id": uid(), "priority": w_prio,
                                                  "type": w_type, "days": w_days_sel}]
                    st.rerun()

        st.markdown("---")
        bc1, bc2 = st.columns(2)
        with bc1:
            if st.button("💾 Enregistrer le pathologiste", type="primary", use_container_width=True):
                if not name.strip():
                    st.error("Entrez un nom.")
                else:
                    color = SS.get("pf_color", default_color)
                    new_p = {"id": editing or uid(), "name": name.strip(), "parts": parts,
                             "mode": mode, "color": color, "wishes": list(SS.get("tmp_wishes", []))}
                    if editing:
                        SS.pathologistes = [p if p["id"] != editing else new_p for p in SS.pathologistes]
                        SS["editing_patho"] = None
                    else:
                        SS.pathologistes.append(new_p)
                    SS["tmp_wishes"] = []
                    SS["pf_color"] = None
                    st.success(f"✅ {name} enregistré·e !")
                    st.rerun()
        with bc2:
            if editing and st.button("✕ Annuler la modification", use_container_width=True):
                SS["editing_patho"] = None
                SS["tmp_wishes"] = []
                st.rerun()

    # List
    st.markdown("---")
    if not SS.pathologistes:
        st.info("Aucun pathologiste enregistré.")
        return

    T = tp()
    for p in SS.pathologistes:
        pct = round(p["parts"] / T * 100) if T else 0
        mode_lbl = f"Concentré ≤{conc_max_days(p)}j/sem" if p["mode"] == "concentrated" else "Lissé"
        wcount = len(p.get("wishes", []))

        pc1, pc2, pc3, pc4, pc5 = st.columns([3, 1, 2, 1, 1])
        with pc1:
            st.markdown(
                f"<div style='display:flex;align-items:center;gap:8px'>"
                f"<span style='width:14px;height:14px;border-radius:50%;background:{p['color']};flex-shrink:0;display:inline-block'></span>"
                f"<strong>{p['name']}</strong>"
                f"</div>", unsafe_allow_html=True)
        with pc2:
            st.markdown(f"<span class='bdg bdg-teal'>{p['parts']}p · {pct}%</span>", unsafe_allow_html=True)
        with pc3:
            st.markdown(f"<span style='font-size:12px;color:#5d6d82'>{mode_lbl}</span> " +
                        (f"<span class='bdg bdg-amber'>{wcount} vœu{'x' if wcount>1 else ''}</span>" if wcount else ""),
                        unsafe_allow_html=True)
        with pc4:
            if st.button("✏️ Modifier", key=f"edit_{p['id']}", use_container_width=True):
                SS["editing_patho"] = p["id"]
                SS["tmp_wishes"] = list(p.get("wishes", []))
                SS["pf_color"] = p["color"]
                st.rerun()
        with pc5:
            if st.button("🗑️", key=f"del_{p['id']}", use_container_width=True):
                SS.pathologistes = [x for x in SS.pathologistes if x["id"] != p["id"]]
                SS.absences = [a for a in SS.absences if a["patho_id"] != p["id"]]
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# ABSENCES
# ─────────────────────────────────────────────────────────────────────────────
def render_absences():
    st.markdown("<div class='main-title'>🔴 Absences</div>", unsafe_allow_html=True)

    if not SS.pathologistes:
        st.warning("Ajoutez d'abord des pathologistes.")
        return

    with st.form("abs_form"):
        c1, c2, c3, c4 = st.columns([2, 1, 1, 2])
        with c1:
            who = st.selectbox("Pathologiste", [p["name"] for p in SS.pathologistes])
        with c2:
            start = st.date_input("Début", value=date.today())
        with c3:
            end = st.date_input("Fin", value=date.today())
        with c4:
            reason = st.text_input("Motif (optionnel)", placeholder="Congé, formation…")
        submitted = st.form_submit_button("🔴 Enregistrer l'absence", type="primary")
        if submitted:
            pid = next(p["id"] for p in SS.pathologistes if p["name"] == who)
            e = end if end >= start else start
            SS.absences.append({"id": uid(), "patho_id": pid,
                                 "start": start.isoformat(), "end": e.isoformat(), "reason": reason})
            st.success("Absence enregistrée.")
            st.rerun()

    if not SS.absences:
        st.info("Aucune absence déclarée.")
        return

    st.markdown("---")
    for a in sorted(SS.absences, key=lambda x: x["start"]):
        p = gp(a["patho_id"])
        if not p: continue
        lbl = a["start"] if a["start"] == a["end"] else f"{a['start']} → {a['end']}"
        ac1, ac2, ac3, ac4, ac5 = st.columns([1, 2, 2, 2, 1])
        with ac1:
            st.markdown(f"<span style='width:12px;height:12px;border-radius:50%;background:{p['color']};display:inline-block'></span>", unsafe_allow_html=True)
        with ac2:
            st.markdown(f"**{p['name']}**")
        with ac3:
            st.markdown(f"<code>{lbl}</code>", unsafe_allow_html=True)
        with ac4:
            st.write(a.get("reason", ""))
        with ac5:
            if st.button("🗑️", key=f"dela_{a['id']}"):
                SS.absences = [x for x in SS.absences if x["id"] != a["id"]]
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# STATS
# ─────────────────────────────────────────────────────────────────────────────
def render_stats():
    st.markdown("<div class='main-title'>📊 Statistiques — " +
                f"{MOIS[SS.current_month-1]} {SS.current_year}</div>", unsafe_allow_html=True)

    year, month = SS.current_year, SS.current_month
    s = SS.settings
    H = get_holidays(year, s["region"])
    max_dow = s["days"] - 1
    wd = get_work_days(year, month, H, max_dow)
    T = tp()
    total_act = len(wd) * s["activity"]
    hol_count = sum(1 for d, _ in H.items() if d.year == year and d.month == month)

    # Global stats
    sc = st.columns(5)
    for i, (v, lbl) in enumerate([
        (len(wd), "Jours ouvrés"),
        (hol_count, "Jours fériés"),
        (f"{total_act:,}".replace(",", " "), "Activité totale"),
        (len(SS.pathologistes), "Pathologistes"),
        (sum(1 for a in SS.absences
             if a["start"][:7] == f"{year}-{month:02d}" or a["end"][:7] == f"{year}-{month:02d}"),
         "Absences ce mois"),
    ]):
        with sc[i]:
            st.markdown(f"<div class='stat-box'><div class='stat-val'>{v}</div><div class='stat-lbl'>{lbl}</div></div>",
                        unsafe_allow_html=True)

    if not SS.pathologistes or not SS.planning:
        st.info("Générez d'abord un planning pour voir les statistiques détaillées.")
        return

    st.markdown("---")
    st.markdown("### ⚖️ Activité cible vs réalisée")

    # Compute actual activity
    p_act = {p["id"]: 0.0 for p in SS.pathologistes}
    p_days = {p["id"]: 0 for p in SS.pathologistes}
    for d in wd:
        pres = SS.planning.get(d.isoformat(), [])
        pp = sum((gp(pid) or {}).get("parts", 0) for pid in pres)
        for pid in pres:
            p = gp(pid)
            if p and pp > 0:
                p_act[p["id"]] += s["activity"] * p["parts"] / pp
                p_days[p["id"]] += 1

    df_rows = []
    for p in SS.pathologistes:
        tgt = (p["parts"] / T * total_act) if T else 0
        act = p_act[p["id"]]
        tgt_d = (p["parts"] / T * len(wd)) if T else 0
        act_d = p_days[p["id"]]
        pct = round(p["parts"] / T * 100) if T else 0
        diff = act - tgt
        diff_d = act_d - round(tgt_d)

        # Bar chart
        bar_pct = min(100, act / tgt * 100) if tgt else 0
        bar_html = (f"<div class='prog-bar-wrap'>"
                    f"<div class='prog-bar' style='width:{bar_pct:.0f}%;background:{p['color']}'></div></div>")

        diff_style = "color:#2a7d50" if abs(diff) <= tgt*0.03 else ("color:#b73640" if diff < 0 else "color:#c87b2d")
        diff_d_style = "color:#2a7d50" if diff_d == 0 else "color:#b73640"

        with st.container():
            r1, r2, r3 = st.columns([2, 4, 3])
            with r1:
                st.markdown(
                    f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:4px'>"
                    f"<span style='width:14px;height:14px;border-radius:50%;background:{p['color']};display:inline-block'></span>"
                    f"<strong>{p['name']}</strong>"
                    f"<span class='bdg bdg-teal'>{p['parts']}p · {pct}%</span>"
                    f"</div>",
                    unsafe_allow_html=True)
            with r2:
                st.markdown(
                    f"<div style='margin-bottom:4px'>{bar_html}</div>"
                    f"<div style='font-size:11px;color:#5d6d82'>"
                    f"Activité : <strong>{act:.1f}</strong> / cible <strong>{tgt:.1f}</strong> "
                    f"<span style='{diff_style};font-weight:700'>({'+' if diff>=0 else ''}{diff:.1f})</span>"
                    f"</div>",
                    unsafe_allow_html=True)
            with r3:
                st.markdown(
                    f"<div style='font-size:11px;color:#5d6d82'>"
                    f"Jours: <strong>{act_d}</strong> / cible <strong>{tgt_d:.1f}</strong> "
                    f"<span style='{diff_d_style};font-weight:700'>({'+' if diff_d>=0 else ''}{diff_d}j)</span><br>"
                    f"Activité/jour moy.: <strong>{act/act_d:.1f}</strong>"
                    f"</div>" if act_d else "<div style='font-size:11px;color:#8898a9'>Absent ce mois</div>",
                    unsafe_allow_html=True)
        st.markdown("<hr style='border:none;border-top:1px solid #e7e2db;margin:8px 0'>", unsafe_allow_html=True)

    # Parts pie chart (simple bar)
    st.markdown("### 📊 Répartition des parts")
    bar_html = "<div style='display:flex;height:32px;border-radius:8px;overflow:hidden;margin-bottom:12px'>"
    for p in SS.pathologistes:
        w = (p["parts"] / T * 100) if T else 0
        lbl = p["name"].split()[-1] if w > 7 else ""
        bar_html += f"<div style='width:{w:.1f}%;background:{p['color']};display:flex;align-items:center;justify-content:center;color:white;font-size:11px;font-weight:600;overflow:hidden;white-space:nowrap;padding:0 3px'>{lbl}</div>"
    bar_html += "</div>"
    leg_html = "<div style='display:flex;flex-wrap:wrap;gap:7px'>"
    for p in SS.pathologistes:
        pct = round(p["parts"] / T * 100) if T else 0
        leg_html += (f"<span class='leg-chip'>"
                     f"<span class='leg-dot' style='background:{p['color']}'></span>"
                     f"<strong>{p['name']}</strong> — {pct}% ({p['parts']}p)"
                     f"</span>")
    leg_html += "</div>"
    st.markdown(bar_html + leg_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SETTINGS
# ─────────────────────────────────────────────────────────────────────────────
def render_settings():
    st.markdown("<div class='main-title'>⚙️ Paramètres</div>", unsafe_allow_html=True)
    s = SS.settings

    st.markdown("### 🏥 Cabinet")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        days = st.selectbox("Jours d'activité", [4, 5, 6],
                            format_func=lambda x: {4:"Lun→Jeu (4j)", 5:"Lun→Ven (5j)", 6:"Lun→Sam (6j)"}[x],
                            index=[4,5,6].index(s["days"]))
    with c2:
        activity = st.number_input("Activité totale / jour", min_value=1, max_value=99999,
                                   value=int(s["activity"]))
    with c3:
        min_present = st.number_input("Min. médecins / jour", min_value=1, max_value=10,
                                      value=int(s["min_present"]))
    with c4:
        region = st.selectbox("Région (jours fériés)", ["metro","alsace"],
                              format_func=lambda x: {"metro":"France métropolitaine","alsace":"Alsace-Moselle"}[x],
                              index=["metro","alsace"].index(s["region"]))

    st.markdown("### 🎯 Seuils mode Concentré")
    st.caption("Activité mensuelle cible du médecin → détermine le nombre de jours/semaine pour un médecin en mode Concentré")
    d1, d2, d3 = st.columns(3)
    with d1: conc2 = st.number_input("≤ ce seuil → 2 jours/sem", value=int(s["conc2"]), min_value=1)
    with d2: conc3 = st.number_input("≤ ce seuil → 3 jours/sem", value=int(s["conc3"]), min_value=1)
    with d3: conc4 = st.number_input("≤ ce seuil → 4 jours/sem", value=int(s["conc4"]), min_value=1)

    st.info("💡 Au-delà du seuil 4j, le médecin concentré est traité comme un médecin lissé (5j/sem).")

    st.markdown("### 🖥️ Affichage")
    v1, v2, v3 = st.columns(3)
    with v1: show_pct = st.checkbox("Afficher % des parts / chip", value=s["show_pct"])
    with v2: show_act = st.checkbox("Afficher activité / chip", value=s["show_act"])
    with v3: show_wf = st.checkbox("Bilan semaine (pied de tableau)", value=s["show_wf"])

    if st.button("💾 Sauvegarder les paramètres", type="primary"):
        SS.settings.update({
            "days": days, "activity": activity, "min_present": min_present, "region": region,
            "conc2": conc2, "conc3": conc3, "conc4": conc4,
            "show_pct": show_pct, "show_act": show_act, "show_wf": show_wf,
        })
        st.success("✅ Paramètres sauvegardés.")

    st.markdown("---")
    st.markdown("### 💾 Sauvegarde / Import des données")
    col_exp, col_imp = st.columns(2)

    with col_exp:
        data = {
            "pathologistes": SS.pathologistes,
            "absences": SS.absences,
            "planning": SS.planning,
            "settings": SS.settings,
        }
        st.download_button("⬇️ Exporter les données (JSON)",
                           data=json.dumps(data, indent=2, ensure_ascii=False),
                           file_name=f"planning_patho_{date.today().isoformat()}.json",
                           mime="application/json",
                           use_container_width=True)

    with col_imp:
        uploaded = st.file_uploader("⬆️ Importer des données (JSON)", type=["json"])
        if uploaded:
            try:
                d = json.loads(uploaded.read())
                SS.pathologistes = d.get("pathologistes", [])
                SS.absences = d.get("absences", [])
                SS.planning = d.get("planning", {})
                SS.settings.update(d.get("settings", {}))
                st.success("✅ Données importées !")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur d'import : {e}")

    st.markdown("---")
    if st.button("🗑️ Réinitialiser toutes les données", type="secondary"):
        for k, v in DEFAULTS.items():
            SS[k] = v if not isinstance(v, dict) else dict(v)
        st.success("✅ Réinitialisé.")
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
tab_planning, tab_pathos, tab_absences, tab_stats, tab_settings = st.tabs([
    "📅 Planning", "👥 Pathologistes", "🔴 Absences", "📊 Statistiques", "⚙️ Paramètres"
])

with tab_planning:   render_calendar()
with tab_pathos:     render_pathologistes()
with tab_absences:   render_absences()
with tab_stats:      render_stats()
with tab_settings:   render_settings()
