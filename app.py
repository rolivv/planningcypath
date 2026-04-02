"""
Planning Cabinet Pathologistes — v3
Streamlit + PuLP (Subset-Selection ILP)
Déploiement : streamlit run app.py
"""
import streamlit as st
import math, uuid, json, calendar as cal_lib
from itertools import combinations
from datetime import date, timedelta
from collections import defaultdict
import pulp

st.set_page_config(page_title="Planning Pathologistes", page_icon="🔬",
                   layout="wide", initial_sidebar_state="collapsed")

# ─────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600&display=swap');
html,[class*="css"]{font-family:'DM Sans',sans-serif}
.app-title{font-family:'Syne',sans-serif;font-weight:800;font-size:24px;color:#17233a;
  border-bottom:2px solid #1d7a6d;padding-bottom:8px;margin-bottom:18px}
.app-title em{color:#1d7a6d;font-style:normal}

/* ── Week block ── */
.wb{border:1px solid #dcd7cf;border-radius:12px;overflow:hidden;
    margin-bottom:14px;box-shadow:0 2px 10px rgba(23,35,58,.07);background:#fff}
.wh{background:#17233a;padding:8px 14px;display:flex;
    justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px}
.wnum{font-family:'DM Mono',monospace;font-size:11px;color:rgba(255,255,255,.4)}
.wnum b{color:#28a08e;font-weight:700}
.wsum{display:flex;gap:12px;flex-wrap:wrap;align-items:center}
.wsi{display:flex;align-items:center;gap:4px;font-size:11px}
.wsidot{width:7px;height:7px;border-radius:50%;display:inline-block;flex-shrink:0}
.wsia{font-family:'DM Mono',monospace;font-weight:700;color:rgba(255,255,255,.9)}
.wsit{font-family:'DM Mono',monospace;font-size:10px;color:rgba(255,255,255,.28)}
.wsd-ok{font-family:'DM Mono',monospace;font-size:9px;color:#28a08e;font-weight:700}
.wsd-warn{font-family:'DM Mono',monospace;font-size:9px;color:#e09040;font-weight:700}
.wsd-bad{font-family:'DM Mono',monospace;font-size:9px;color:#d04050;font-weight:700}

/* ── Day grid ── */
.dg{display:grid;background:#fff}
.dc{padding:10px 9px;border-right:1px solid #e7e2db;min-height:120px;background:#fff}
.dc:last-child{border-right:none}
.dc.hol{background:#fef8ef}.dc.past{opacity:.55}.dc.wrn{background:#fff5f5}
.dtop{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px}
.dlbl{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:#8898a9}
.dnum{font-family:'Syne',sans-serif;font-weight:800;font-size:20px;color:#17233a;line-height:1}
.dnum.tod{background:#1d7a6d;color:#fff;border-radius:50%;width:28px;height:28px;
  display:inline-flex;align-items:center;justify-content:center;font-size:13px}
.htag{font-size:9px;color:#c87b2d;font-weight:700;background:#fdf1e3;
  padding:2px 5px;border-radius:3px;margin-bottom:4px;display:block;line-height:1.5}
.wtag{font-size:9px;color:#b73640;font-weight:700;background:#fce9ea;
  padding:2px 5px;border-radius:3px;margin-bottom:4px;display:block;line-height:1.5}
.chip{font-size:10px;font-weight:500;padding:3px 7px;border-radius:4px;
  display:flex;align-items:center;gap:4px;margin-bottom:3px;line-height:1.3}
.cdot{width:6px;height:6px;border-radius:50%;display:inline-block;flex-shrink:0}
.cact{font-family:'DM Mono',monospace;font-size:9px;margin-left:auto;font-weight:700}
.cpct{font-size:9px;opacity:.5;margin-left:2px}
.chip.abs{background:#fce9ea!important;color:#b73640!important;text-decoration:line-through}
.dtot{font-family:'DM Mono',monospace;font-size:9px;color:#8898a9;
  text-align:right;margin-top:5px;border-top:1px solid #e7e2db;padding-top:4px}

/* ── Week footer ── */
.wf{background:#f6f3ee;border-top:1px solid #e7e2db;
    padding:7px 14px;display:flex;gap:14px;flex-wrap:wrap;align-items:center}
.wfi{display:flex;align-items:center;gap:5px}
.wfbw{width:65px;height:5px;background:#dcd7cf;border-radius:3px;
  overflow:hidden;display:inline-block;vertical-align:middle}
.wfb{height:100%;border-radius:3px;display:inline-block}
.wfn{font-family:'DM Mono',monospace;font-size:10px;color:#5d6d82;white-space:nowrap}
.wfdp{font-family:'DM Mono',monospace;font-size:10px;font-weight:700;color:#1d7a6d}
.wfdn{font-family:'DM Mono',monospace;font-size:10px;font-weight:700;color:#b73640}
.wfdz{font-family:'DM Mono',monospace;font-size:10px;font-weight:700;color:#8898a9}

/* ── Legend / badges ── */
.leg{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:16px}
.lchip{display:inline-flex;align-items:center;gap:5px;font-size:12px;font-weight:500;
  background:#fff;border:1px solid #dcd7cf;padding:4px 10px;border-radius:20px}
.ldot{width:10px;height:10px;border-radius:50%;display:inline-block}
.ltgt{font-family:'DM Mono',monospace;font-size:10px;color:#8898a9}
.bdg{font-size:10px;font-weight:700;padding:2px 7px;border-radius:20px;display:inline-block}
.bt{background:#e3f2f0;color:#1d7a6d}.ba{background:#fdf1e3;color:#c87b2d}
.br{background:#fce9ea;color:#b73640}.bg{background:#e4f2ea;color:#2a7d50}
.bn{background:#eef0f3;color:#5d6d82}

/* ── Alerts ── */
.aw{background:#fdf1e3;border:1px solid #c87b2d;border-radius:8px;
  padding:9px 13px;font-size:12px;color:#c87b2d;margin-bottom:10px}
.ai{background:#e3f2f0;border:1px solid #1d7a6d;border-radius:8px;
  padding:9px 13px;font-size:12px;color:#1d7a6d;margin-bottom:10px}
.ae{background:#fce9ea;border:1px solid #b73640;border-radius:8px;
  padding:9px 13px;font-size:12px;color:#b73640;margin-bottom:10px}

/* ── Stats ── */
.sbox{background:#fff;border:1px solid #dcd7cf;border-radius:10px;
  padding:14px;text-align:center}
.sval{font-family:'Syne',sans-serif;font-weight:800;font-size:28px;
  color:#17233a;line-height:1}
.slbl{font-size:10px;text-transform:uppercase;letter-spacing:.5px;color:#5d6d82;margin-top:3px}
.pbw{background:#dcd7cf;border-radius:4px;height:8px;overflow:hidden}
.pb{height:100%;border-radius:4px}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# DEFAULTS & SESSION STATE
# ─────────────────────────────────────────────────────────────
INIT = {
    "pathologistes": [],
    "absences": [],
    "planning": {},          # iso_date -> [patho_id, ...]
    "plan_alerts": [],
    "settings": {
        "days": 5,
        "activity": 70,
        "min_present": 2,
        "region": "metro",
        "conc2": 650, "conc3": 900, "conc4": 1200,
        "show_pct": True, "show_act": True, "show_wf": True,
        # Constraint hierarchy (list of constraint ids in priority order)
        "constraint_order": ["balance", "spread", "wish1", "wish2", "wish3", "concentrated"],
    },
    "cur_year": date.today().year,
    "cur_month": date.today().month,
    "editing_patho_id": None,
    "tmp_wishes": [],
    "show_abs_inline": False,
}
for k, v in INIT.items():
    if k not in st.session_state:
        st.session_state[k] = v if not isinstance(v, dict) else dict(v)
SS = st.session_state

COLORS = ["#1d7a6d","#7c5cbf","#c87b2d","#b73640","#2c6fa7",
          "#6a7e28","#af5898","#267851","#a04e2e","#3a798e","#874365","#4a5f80"]
JJ = ["Lun","Mar","Mer","Jeu","Ven","Sam"]
MM = ["Janvier","Février","Mars","Avril","Mai","Juin",
      "Juillet","Août","Septembre","Octobre","Novembre","Décembre"]
CONSTR_LABELS = {
    "balance":      "⚖️ Équilibre activité/parts (±10%)",
    "spread":       "📆 Mode lissé (jours répartis)",
    "wish1":        "⭐⭐⭐ Vœux priorité 1",
    "wish2":        "⭐⭐ Vœux priorité 2",
    "wish3":        "⭐ Vœux priorité 3+",
    "concentrated": "🗜️ Mode concentré (jours groupés)",
}

# ─────────────────────────────────────────────────────────────
# UTILS
# ─────────────────────────────────────────────────────────────
def uid(): return str(uuid.uuid4())[:8]
def gp(pid): return next((p for p in SS.pathologistes if p["id"] == pid), None)
def tp(): return sum(p["parts"] for p in SS.pathologistes)

def is_absent(pid, d):
    for a in SS.absences:
        if a["patho_id"] == pid:
            s, e = date.fromisoformat(a["start"]), date.fromisoformat(a["end"])
            if s <= d <= e:
                return True
    return False

# ─────────────────────────────────────────────────────────────
# JOURS FÉRIÉS (timezone-safe)
# ─────────────────────────────────────────────────────────────
def get_easter(y):
    a,b,c = y%19, y//100, y%100
    d,e = b//4, b%4
    f,g = (b+8)//25, (b-((b+8)//25)+1)//3
    h = (19*a+b-d-g+15)%30
    i,k = c//4, c%4
    l = (32+2*e+2*i-h-k)%7
    m = (a+11*h+22*l)//451
    mo = (h+l-7*m+114)//31
    dy = (h+l-7*m+114)%31 + 1
    return date(y, mo, dy)

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
        a(E-timedelta(2),   "Vendredi Saint")
        a(date(year,12,26), "Saint-Étienne")
    return H

def get_work_days(year, month):
    s = SS.settings
    H = get_holidays(year, s["region"])
    max_dow = s["days"] - 1
    out = []
    for d in range(1, cal_lib.monthrange(year, month)[1]+1):
        dt = date(year, month, d)
        if dt.weekday() <= max_dow and dt not in H:
            out.append(dt)
    return out, H

def get_weeks(year, month):
    wd, H = get_work_days(year, month)
    weeks = defaultdict(list)
    for dt in wd:
        monday = dt - timedelta(days=dt.weekday())
        weeks[monday].append(dt)
    return dict(sorted(weeks.items())), H

# ─────────────────────────────────────────────────────────────
# LARGEST REMAINDER
# ─────────────────────────────────────────────────────────────
def lr(items, total):
    """items: [(id, float_value)], total: int → {id: int}"""
    arr = [(id_, v, math.floor(v), v % 1) for id_, v in items]
    extra = round(total) - sum(x[2] for x in arr)
    arr.sort(key=lambda x: (-x[3], x[0]))
    return {x[0]: x[2] + (1 if i < extra else 0) for i, x in enumerate(arr)}

# ─────────────────────────────────────────────────────────────
# CONCENTRATED: target days/week from monthly activity
# ─────────────────────────────────────────────────────────────
def conc_target_days(p, approx_work_days=21):
    T = tp()
    if T == 0: return SS.settings["days"]
    s = SS.settings
    m_tgt = p["parts"] / T * approx_work_days * s["activity"]
    if m_tgt > s["conc4"]: return s["days"]
    if m_tgt > s["conc3"]: return 4
    if m_tgt > s["conc2"]: return 3
    return 2

# ─────────────────────────────────────────────────────────────
# COMPUTE MAX DEVIATION (%) from target activity
# ─────────────────────────────────────────────────────────────
def compute_max_dev(result, pathos, days, activity):
    T = sum(p["parts"] for p in pathos)
    if T == 0: return 0.0
    W = len(days)
    tgt = {p["id"]: p["parts"] / T * W * activity for p in pathos}
    act = {p["id"]: 0.0 for p in pathos}
    for d in days:
        pres = result.get(d, [])
        pp = sum(gp(pid)["parts"] for pid in pres if gp(pid))
        for pid in pres:
            p_obj = gp(pid)
            if p_obj and pp > 0:
                act[pid] += activity * p_obj["parts"] / pp
    max_dev = 0.0
    for p in pathos:
        if tgt[p["id"]] > 0:
            dev = abs(act[p["id"]] - tgt[p["id"]]) / tgt[p["id"]]
            max_dev = max(max_dev, dev)
    return max_dev * 100

# ─────────────────────────────────────────────────────────────
# CORE ILP SOLVER — Subset-Selection
#
# For each day, choose ONE subset of doctors.
# Hard: absences, min_present.
# Objective: minimize max deviation from proportional activity.
# Soft: spread/concentrated mode, wishes (penalty weights).
# ─────────────────────────────────────────────────────────────
def solve_week_ilp(pathos, days, abs_dates, min_present, activity,
                   enforce_balance=True,
                   enforce_spread=True,
                   enforce_concentrated=True,
                   wish_levels=(1, 2, 3, 4, 5),
                   max_days_override=None):   # {pid: int}
    """
    Returns (result: {date: [pid]}, max_dev_pct: float)
    or (None, inf) if infeasible.
    """
    if not days or not pathos:
        return ({d: [] for d in days}, 0.0)

    T = sum(p["parts"] for p in pathos)
    if T == 0:
        return ({d: [] for d in days}, 0.0)

    W = len(days)

    # ── Build valid subsets for each day ─────────────────────
    # abs_dates: set of (pid, date)
    day_subsets = []   # day_subsets[di] = list of tuples of patho objects
    for d in days:
        avail = [p for p in pathos if (p["id"], d) not in abs_dates]
        subs = []
        for size in range(min_present, len(avail) + 1):
            for combo in combinations(avail, size):
                subs.append(tuple(combo))
        if not subs:
            # No valid subset possible — infeasible
            return (None, float("inf"))
        day_subsets.append(subs)

    # ── Compute activity contribution ─────────────────────────
    # act_contrib[di][si][pid] = activity * pid.parts / sum_parts(subset)
    act_contrib = []
    for di, subs in enumerate(day_subsets):
        day_c = []
        for sub in subs:
            pp = sum(p["parts"] for p in sub)
            sub_c = {p["id"]: activity * p["parts"] / pp for p in sub}
            day_c.append(sub_c)
        act_contrib.append(day_c)

    # ── Target days/week per doctor ───────────────────────────
    total_needed_slots = max(
        round(sum(p["parts"] / T * W for p in pathos)),
        min_present * W
    )
    raw_slots = []
    for p in pathos:
        prop = p["parts"] / T * total_needed_slots
        if max_days_override and p["id"] in max_days_override:
            prop = min(prop, max_days_override[p["id"]])
        # Cap by available days
        avail_count = sum(1 for d in days if (p["id"], d) not in abs_dates)
        prop = min(prop, avail_count)
        raw_slots.append((p["id"], prop))
    tgt_days = lr(raw_slots, min(total_needed_slots, sum(math.ceil(v) for _, v in raw_slots)))

    # Ensure caps respected
    for p in pathos:
        avail_count = sum(1 for d in days if (p["id"], d) not in abs_dates)
        tgt_days[p["id"]] = min(tgt_days.get(p["id"], 0), avail_count)

    # ── ILP ───────────────────────────────────────────────────
    prob = pulp.LpProblem("week", pulp.LpMinimize)

    # y[di][si] = 1 if subset si used on day di
    y = [[pulp.LpVariable(f"y_{di}_{si}", cat="Binary")
          for si in range(len(day_subsets[di]))]
         for di in range(W)]

    # One subset per day (hard)
    for di in range(W):
        prob += pulp.lpSum(y[di]) == 1

    # x[pid][di] = 1 if doctor pid present on day di (derived from y)
    x = {}
    for p in pathos:
        for di in range(W):
            x[(p["id"], di)] = pulp.lpSum(
                y[di][si]
                for si, sub in enumerate(day_subsets[di])
                if p in sub
            )

    # Target days constraint (hard)
    for p in pathos:
        prob += pulp.lpSum(x[(p["id"], di)] for di in range(W)) == tgt_days[p["id"]]

    # Max daily activity constraint (per doctor)
    max_da = {p["id"]: p.get("max_day_act") for p in pathos}
    for p in pathos:
        if max_da[p["id"]] is not None:
            for di in range(W):
                for si, sub in enumerate(day_subsets[di]):
                    if p in sub:
                        act = act_contrib[di][si].get(p["id"], 0)
                        if act > max_da[p["id"]] + 0.01:
                            prob += y[di][si] == 0  # forbid this subset

    # ── Objective ────────────────────────────────────────────
    obj_terms = []

    # 1. BALANCE: minimize max deviation %
    if enforce_balance:
        tgt_act = {p["id"]: p["parts"] / T * W * activity for p in pathos}
        dev_pos = {p["id"]: pulp.LpVariable(f"dp_{p['id']}", lowBound=0) for p in pathos}
        dev_neg = {p["id"]: pulp.LpVariable(f"dn_{p['id']}", lowBound=0) for p in pathos}
        max_dev_var = pulp.LpVariable("max_dev", lowBound=0)

        for p in pathos:
            actual = pulp.lpSum(
                y[di][si] * act_contrib[di][si].get(p["id"], 0)
                for di in range(W)
                for si in range(len(day_subsets[di]))
            )
            prob += actual - tgt_act[p["id"]] == dev_pos[p["id"]] - dev_neg[p["id"]]
            if tgt_act[p["id"]] > 0:
                prob += (dev_pos[p["id"]] + dev_neg[p["id"]]) / tgt_act[p["id"]] <= max_dev_var

        obj_terms.append(10000 * max_dev_var)

    # 2. SPREAD / CONCENTRATED adjacency
    adj = {}
    for p in pathos:
        for di in range(W - 1):
            v = pulp.LpVariable(f"adj_{p['id']}_{di}", cat="Binary")
            prob += v >= x[(p["id"], di)] + x[(p["id"], di+1)] - 1
            prob += v <= x[(p["id"], di)]
            prob += v <= x[(p["id"], di+1)]
            adj[(p["id"], di)] = v
        # Wrap-around Fri-Mon (cyclic)
        if W >= 2:
            v = pulp.LpVariable(f"adjW_{p['id']}", cat="Binary")
            prob += v >= x[(p["id"], 0)] + x[(p["id"], W-1)] - 1
            prob += v <= x[(p["id"], 0)]
            prob += v <= x[(p["id"], W-1)]
            adj[(p["id"], "W")] = v

    if enforce_spread:
        for p in pathos:
            if p["mode"] == "spread":
                for key, av in adj.items():
                    if key[0] == p["id"]:
                        obj_terms.append(200 * av)   # penalty: avoid consecutive

    if enforce_concentrated:
        for p in pathos:
            if p["mode"] == "concentrated":
                for key, av in adj.items():
                    if key[0] == p["id"]:
                        obj_terms.append(-150 * av)  # bonus: prefer consecutive

    # 3. WISHES
    for p in pathos:
        for w in (p.get("wishes") or []):
            if w["priority"] not in wish_levels:
                continue
            base = 800.0 / w["priority"]
            wtype, wdays = w["type"], set(w.get("days") or [])
            for di, d in enumerate(days):
                dw = d.weekday()
                if wtype == "prefer" and dw in wdays:
                    obj_terms.append(-base * x[(p["id"], di)])
                elif wtype == "avoid" and dw in wdays:
                    obj_terms.append(base * x[(p["id"], di)])
                elif wtype == "consecutive":
                    for key, av in adj.items():
                        if key[0] == p["id"]:
                            obj_terms.append(-base * 0.5 * av)

    if obj_terms:
        prob += pulp.lpSum(obj_terms)
    else:
        prob += 0

    solver = pulp.PULP_CBC_CMD(msg=0, timeLimit=20)
    prob.solve(solver)

    if pulp.LpStatus[prob.status] not in ("Optimal", "Not Solved"):
        # CBC sometimes returns "Not Solved" but has a feasible solution
        pass

    # Extract result
    result = {d: [] for d in days}
    for di, d in enumerate(days):
        for si, sub in enumerate(day_subsets[di]):
            val = pulp.value(y[di][si])
            if val is not None and val > 0.5:
                result[d] = [p["id"] for p in sub]
                break

    # Check if all days assigned
    if any(not result[d] for d in days
           if (d, ) not in [(k,) for k in result if not result[k]]):
        pass

    max_dev = compute_max_dev(result, pathos, days, activity)
    return result, max_dev


# ─────────────────────────────────────────────────────────────
# GENERATE PLANNING WITH RELAXATION
# ─────────────────────────────────────────────────────────────
def generate_planning():
    pathos = SS.pathologistes
    if not pathos:
        return False, ["Aucun pathologiste configuré."]

    year, month = SS.cur_year, SS.cur_month
    s = SS.settings
    weeks, H = get_weeks(year, month)
    if not weeks:
        return False, ["Aucun jour ouvré ce mois."]

    T = tp()
    # Build absence set
    abs_set = set()
    for ab in SS.absences:
        d = date.fromisoformat(ab["start"])
        end = date.fromisoformat(ab["end"])
        while d <= end:
            if d.weekday() < s["days"] and d not in H:
                abs_set.add((ab["patho_id"], d))
            d += timedelta(1)

    planning = {}
    alerts = []
    constraint_order = s.get("constraint_order",
                             ["balance","spread","wish1","wish2","wish3","concentrated"])

    # Relaxation levels: each level removes the LAST constraint in the order
    # Level 0: all constraints
    # Level 1: remove last
    # Level 2: remove last 2, etc.

    progress = st.progress(0.0, text="Initialisation…")
    total = len(weeks)

    for wi, (monday, days) in enumerate(weeks.items()):
        progress.progress(wi / max(total, 1),
                          text=f"Semaine du {monday.strftime('%d/%m')}…")

        # Concentrated: compute max_days per doctor
        max_days_ov = {}
        for p in pathos:
            if p["mode"] == "concentrated":
                max_days_ov[p["id"]] = conc_target_days(p)

        best_result, best_dev = None, float("inf")
        used_relax_level = 0

        # Try progressively relaxed constraint sets
        for relax_level in range(len(constraint_order) + 1):
            active = constraint_order[:max(0, len(constraint_order) - relax_level)]

            # Map active constraints to flags
            en_balance      = "balance"      in active
            en_spread       = "spread"       in active
            en_conc         = "concentrated" in active
            wish_levels     = set()
            if "wish1" in active: wish_levels.add(1)
            if "wish2" in active: wish_levels.add(2)
            if "wish3" in active: wish_levels |= {3, 4, 5}

            # For concentrated mode relaxation: try max_days from tight to loose
            conc_variants = []
            if en_conc:
                for extra_days in range(0, s["days"]):
                    variant = {pid: min(s["days"], d + extra_days)
                               for pid, d in max_days_ov.items()}
                    conc_variants.append(variant)
                conc_variants.append(None)  # no limit
            else:
                conc_variants = [None]

            for conc_v in conc_variants:
                result, max_dev = solve_week_ilp(
                    pathos, days, abs_set,
                    min_present=s["min_present"],
                    activity=s["activity"],
                    enforce_balance=en_balance,
                    enforce_spread=en_spread,
                    enforce_concentrated=en_conc and conc_v is not None,
                    wish_levels=wish_levels if wish_levels else set(range(1, 6)),
                    max_days_override=conc_v,
                )
                if result is not None and max_dev < best_dev:
                    best_result, best_dev = result, max_dev
                    used_relax_level = relax_level

                # Stop early if deviation acceptable (≤10%)
                if best_dev <= 10.0:
                    break

            if best_dev <= 10.0:
                break

        # Write best result
        if best_result is None:
            alerts.append(f"❌ {monday.strftime('%d/%m')}: impossible de générer. Vérifiez les absences.")
            for d in days:
                planning[d.isoformat()] = []
        else:
            for d, pids in best_result.items():
                planning[d.isoformat()] = pids
            if used_relax_level > 0:
                removed = constraint_order[-(used_relax_level):]
                alerts.append(
                    f"⚠️ {monday.strftime('%d/%m')}: contraintes relâchées "
                    f"({', '.join(CONSTR_LABELS.get(c, c) for c in removed)}) "
                    f"— écart max {best_dev:.1f}%"
                )
            elif best_dev > 10.0:
                alerts.append(f"⚠️ {monday.strftime('%d/%m')}: écart max {best_dev:.1f}% (> 10%)")

    progress.progress(1.0, text="✅ Terminé")
    import time; time.sleep(0.4); progress.empty()

    SS.planning = planning
    SS.plan_alerts = alerts
    return True, alerts


# ─────────────────────────────────────────────────────────────
# CALENDAR HTML RENDERER (pure HTML, no st.columns)
# ─────────────────────────────────────────────────────────────
def render_calendar():
    year, month = SS.cur_year, SS.cur_month
    s = SS.settings
    weeks, H = get_weeks(year, month)
    today = date.today()
    T = tp()
    planning = SS.planning
    pathos = SS.pathologistes
    has_plan = bool(planning)
    nCols = s["days"]
    DOW = ["LUN","MAR","MER","JEU","VEN","SAM"]

    wd_list, _ = get_work_days(year, month)
    total_month_act = len(wd_list) * s["activity"]

    # ── Header ────────────────────────────────────────────────
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(
            f"<div class='app-title'>🔬 Planning<em>.</em>Patho<br>"
            f"<span style='font-size:18px;font-weight:700'>{MM[month-1]} {year}</span></div>",
            unsafe_allow_html=True)
        if pathos:
            st.caption(f"{len(pathos)} médecin(s) · {T} parts · {s['activity']} act./jour · min {s['min_present']}/jour")
    with c2:
        bc = st.columns(6)
        with bc[0]:
            if st.button("◀", use_container_width=True, help="Mois précédent"):
                SS.cur_month -= 1
                if SS.cur_month < 1: SS.cur_month = 12; SS.cur_year -= 1
                st.rerun()
        with bc[1]:
            if st.button("Auj.", use_container_width=True):
                SS.cur_year = date.today().year; SS.cur_month = date.today().month
                st.rerun()
        with bc[2]:
            if st.button("▶", use_container_width=True, help="Mois suivant"):
                SS.cur_month += 1
                if SS.cur_month > 12: SS.cur_month = 1; SS.cur_year += 1
                st.rerun()
        with bc[3]:
            if st.button("⚡ Générer", use_container_width=True, type="primary"):
                if not pathos:
                    st.error("Ajoutez d'abord des pathologistes.")
                else:
                    ok, alerts = generate_planning()
                    if ok: st.rerun()
        with bc[4]:
            if st.button("🔴 Absence", use_container_width=True):
                SS.show_abs_inline = not SS.get("show_abs_inline", False)
                st.rerun()
        with bc[5]:
            if st.button("🗑️ Planning", use_container_width=True, help="Effacer le planning"):
                SS.planning = {}; SS.plan_alerts = []; st.rerun()

    # Quick absence form
    if SS.get("show_abs_inline") and pathos:
        with st.expander("🔴 Déclarer une absence", expanded=True):
            fa, fb, fc, fd = st.columns(4)
            with fa: who_n = st.selectbox("Médecin", [p["name"] for p in pathos], key="qi_who")
            with fb: qi_s = st.date_input("Début", key="qi_start")
            with fc: qi_e = st.date_input("Fin", key="qi_end")
            with fd: qi_r = st.text_input("Motif", key="qi_reason")
            if st.button("Enregistrer", key="qi_save"):
                pid = next(p["id"] for p in pathos if p["name"] == who_n)
                end = qi_e if qi_e >= qi_s else qi_s
                SS.absences.append({"id": uid(), "patho_id": pid,
                                    "start": qi_s.isoformat(), "end": end.isoformat(),
                                    "reason": qi_r})
                SS.show_abs_inline = False
                st.success("Absence enregistrée.")
                st.rerun()

    # Alerts
    for al in SS.plan_alerts:
        cls = "ae" if al.startswith("❌") else "aw"
        st.markdown(f"<div class='{cls}'>{al}</div>", unsafe_allow_html=True)

    if not pathos:
        st.info("Ajoutez des pathologistes dans l'onglet **Pathologistes**, puis cliquez **⚡ Générer**.")
        return

    # Legend
    leg_html = "<div class='leg'>"
    for p in pathos:
        pct = round(p["parts"] / T * 100) if T else 0
        tgt = round(p["parts"] / T * total_month_act) if T else 0
        mode_lbl = (f"Concentré ≤{conc_target_days(p)}j/sem"
                    if p["mode"] == "concentrated" else "Lissé")
        leg_html += (f"<span class='lchip'>"
                     f"<span class='ldot' style='background:{p['color']}'></span>"
                     f"<strong>{p['name']}</strong>"
                     f"<span class='bdg bt'>{p['parts']}p·{pct}%</span>"
                     f"<span style='font-size:11px;color:#8898a9'>{mode_lbl}</span>"
                     f"<span class='ltgt'>cible: {tgt}</span>"
                     f"</span>")
    leg_html += "</div>"
    st.markdown(leg_html, unsafe_allow_html=True)

    if not weeks:
        st.info("Aucun jour ouvré ce mois.")
        return

    # ── Weeks ─────────────────────────────────────────────────
    for monday, days in weeks.items():
        wnum = monday.isocalendar()[1]
        work_days = [d for d in days if d not in H]

        # Compute week stats
        w_act = {p["id"]: 0.0 for p in pathos}
        w_days_count = {p["id"]: 0 for p in pathos}
        for d in work_days:
            pres = planning.get(d.isoformat(), [])
            pp = sum((gp(pid) or {}).get("parts", 0) for pid in pres)
            for pid in pres:
                p_obj = gp(pid)
                if p_obj and pp > 0:
                    w_act[p_obj["id"]] += s["activity"] * p_obj["parts"] / pp
                    w_days_count[p_obj["id"]] += 1

        w_tgt_act  = {p["id"]: (p["parts"] / T * len(work_days) * s["activity"] if T else 0) for p in pathos}
        w_tgt_days = {p["id"]: (p["parts"] / T * len(work_days) if T else 0) for p in pathos}
        has_hol = any(d in H for d in days)
        warn_days = (sum(1 for d in work_days
                         if len(planning.get(d.isoformat(), [])) < s["min_present"])
                     if has_plan else 0)

        # ── Week header HTML ──────────────────────────────────
        badges = ""
        if has_hol:     badges += "<span class='bdg ba'>🏖️ Férié</span> "
        if warn_days:   badges += f"<span class='bdg br'>⚠ {warn_days}j sous min</span> "
        if has_plan and not warn_days:
            badges += "<span class='bdg bt'>✓ OK</span>"

        wsum_html = ""
        if has_plan and pathos:
            for p in pathos:
                a = w_act[p["id"]]; t = w_tgt_act[p["id"]]
                diff = a - t
                pct_t = t * 0.05 + 0.5
                dcls = "wsd-ok" if abs(diff) <= pct_t else ("wsd-warn" if abs(diff) <= t*0.10 else "wsd-bad")
                dstr = f"{'+' if diff >= 0 else ''}{diff:.0f}"
                wsum_html += (f"<div class='wsi'>"
                              f"<span class='wsidot' style='background:{p['color']}'></span>"
                              f"<span style='font-size:10px;color:rgba(255,255,255,.45)'>{p['name'].split()[-1]}</span>"
                              f"<span class='wsia'>{a:.0f}</span>"
                              f"<span class='wsit'>/{t:.0f}</span>"
                              f"<span class='{dcls}'>{dstr}</span>"
                              f"</div>")

        # ── Day cells HTML ────────────────────────────────────
        cells_html = ""
        for i in range(nCols):
            cell_date = next((d for d in days if d.weekday() == i), None)
            if cell_date is None:
                cells_html += "<div class='dc' style='background:#f0ede7;opacity:.25'></div>"
                continue

            is_hol  = cell_date in H
            is_past = cell_date < today
            is_today= cell_date == today
            pres    = planning.get(cell_date.isoformat(), [])
            pp      = sum((gp(pid) or {}).get("parts", 0) for pid in pres)
            warn_m  = (not is_hol and has_plan and
                       len(pres) < s["min_present"] and len(pres) > 0)

            dc_cls = "dc"
            if is_hol:   dc_cls += " hol"
            if is_past:  dc_cls += " past"
            if warn_m:   dc_cls += " wrn"

            num_html = (f"<span class='dnum tod'>{cell_date.day}</span>"
                        if is_today else f"<span class='dnum'>{cell_date.day}</span>")

            tags_html = ""
            if is_hol:  tags_html += f"<span class='htag'>{H[cell_date]}</span>"
            if warn_m:  tags_html += f"<span class='wtag'>⚠&lt;{s['min_present']}</span>"

            chips_html = ""
            for p in pathos:
                here   = p["id"] in pres
                absent = is_absent(p["id"], cell_date)
                if not here and not absent:
                    continue
                act = (s["activity"] * p["parts"] / pp
                       if here and not absent and pp > 0 else 0)
                pct_v = round(p["parts"] / T * 100) if T else 0
                cls = "chip abs" if absent else "chip"
                bg  = "" if absent else f"background:{p['color']}1a;color:{p['color']}"
                dot_c = "#b73640" if absent else p["color"]
                act_s = (f"<span class='cact'>{act:.0f}</span>"
                         if s["show_act"] and here and not absent else "")
                pct_s = (f"<span class='cpct'>({pct_v}%)</span>"
                         if s["show_pct"] and here and not absent else "")
                abs_s = "<span style='font-size:9px'>(abs.)</span>" if absent else ""
                chips_html += (f"<div class='{cls}' style='{bg}'>"
                               f"<span class='cdot' style='background:{dot_c}'></span>"
                               f"{p['name'].split()[-1]}{act_s}{pct_s}{abs_s}"
                               f"</div>")

            if not chips_html and not is_hol:
                chips_html = "<span style='font-size:10px;color:#b7c3cf'>—</span>"

            tot_html = (f"<div class='dtot'>Total: {s['activity']}</div>"
                        if pres and not is_hol else "")

            cells_html += (f"<div class='{dc_cls}'>"
                           f"<div class='dtop'>"
                           f"<div><div class='dlbl'>{DOW[i]}</div>{tags_html}</div>"
                           f"{num_html}"
                           f"</div>"
                           f"<div>{chips_html}</div>"
                           f"{tot_html}"
                           f"</div>")

        # ── Week footer HTML ──────────────────────────────────
        foot_html = ""
        if s["show_wf"] and has_plan and pathos:
            foot_html = "<div class='wf'>"
            for p in pathos:
                nd  = w_days_count[p["id"]]
                ntg = w_tgt_days[p["id"]]
                a   = w_act[p["id"]]
                t   = w_tgt_act[p["id"]]
                pct_bar = min(100, a / t * 100) if t else 0
                dd  = nd - round(ntg)
                dcls = "wfdp" if dd > 0 else ("wfdn" if dd < 0 else "wfdz")
                dstr = f"{'+' if dd >= 0 else ''}{dd}j"
                foot_html += (f"<div class='wfi'>"
                              f"<span class='wsidot' style='background:{p['color']}'></span>"
                              f"<strong style='font-size:11px'>{p['name'].split()[-1]}</strong>"
                              f"<span class='wfbw'>"
                              f"<span class='wfb' style='width:{pct_bar:.0f}%;background:{p['color']}'></span>"
                              f"</span>"
                              f"<span class='wfn'>{nd}j/{ntg:.1f}j · {a:.0f}/{t:.0f}</span>"
                              f"<span class='{dcls}'>{dstr}</span>"
                              f"</div>")
            foot_html += "</div>"

        # ── Assemble week block ───────────────────────────────
        col_templ = " ".join(["1fr"] * nCols)
        week_html = (f"<div class='wb'>"
                     f"<div class='wh'>"
                     f"<div><span class='wnum'>Semaine <b>{wnum}</b></span> {badges}</div>"
                     f"<div class='wsum'>{wsum_html}</div>"
                     f"</div>"
                     f"<div class='dg' style='grid-template-columns:{col_templ}'>"
                     f"{cells_html}"
                     f"</div>"
                     f"{foot_html}"
                     f"</div>")
        st.markdown(week_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# PATHOLOGISTES
# ─────────────────────────────────────────────────────────────
def render_pathologistes():
    st.markdown("<div class='app-title'>👥 Équipe médicale</div>", unsafe_allow_html=True)
    T = tp()

    # ── List ─────────────────────────────────────────────────
    if SS.pathologistes:
        for p in SS.pathologistes:
            pct = round(p["parts"] / T * 100) if T else 0
            mode_lbl = (f"Concentré ≤{conc_target_days(p)}j/sem"
                        if p["mode"] == "concentrated" else "Lissé")
            wc = len(p.get("wishes", []))
            mda = p.get("max_day_act")
            cols = st.columns([3, 1, 2, 1, 1, 1])
            with cols[0]:
                st.markdown(
                    f"<div style='display:flex;align-items:center;gap:8px;padding:6px 0'>"
                    f"<span style='width:13px;height:13px;border-radius:50%;"
                    f"background:{p['color']};display:inline-block'></span>"
                    f"<strong>{p['name']}</strong></div>",
                    unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f"<span class='bdg bt'>{p['parts']}p·{pct}%</span>",
                            unsafe_allow_html=True)
            with cols[2]:
                extra = (f" | max {mda}/j" if mda else "")
                wbdg = (f" <span class='bdg ba'>{wc} vœu{'x' if wc>1 else ''}</span>"
                        if wc else "")
                st.markdown(f"<span style='font-size:12px;color:#5d6d82'>{mode_lbl}{extra}</span>{wbdg}",
                            unsafe_allow_html=True)
            with cols[3]:
                st.caption(f"{wc} vœu{'x' if wc > 1 else ''}" if wc else "—")
            with cols[4]:
                if st.button("✏️", key=f"edit_{p['id']}", help="Modifier",
                             use_container_width=True):
                    SS.editing_patho_id = p["id"]
                    SS.tmp_wishes = list(p.get("wishes", []))
                    st.rerun()
            with cols[5]:
                if st.button("🗑️", key=f"del_{p['id']}", help="Supprimer",
                             use_container_width=True):
                    SS.pathologistes = [x for x in SS.pathologistes if x["id"] != p["id"]]
                    SS.absences = [a for a in SS.absences if a["patho_id"] != p["id"]]
                    if SS.editing_patho_id == p["id"]:
                        SS.editing_patho_id = None
                    st.rerun()
        st.markdown("---")

    # ── Add / Edit form ───────────────────────────────────────
    edit_id = SS.get("editing_patho_id")
    ep = gp(edit_id) if edit_id else None
    form_title = f"✏️ Modifier — {ep['name']}" if ep else "➕ Nouveau pathologiste"

    with st.expander(form_title, expanded=True):
        # Detect change in which doctor we're editing
        _key_prefix = edit_id or "new"

        fa, fb, fc, fd = st.columns([3, 1, 2, 1])
        with fa:
            name = st.text_input("Nom / Prénom", value=ep["name"] if ep else "",
                                 key=f"pf_name_{_key_prefix}")
        with fb:
            parts = st.number_input("Parts", min_value=0.5, max_value=20.0, step=0.5,
                                    value=float(ep["parts"]) if ep else 1.0,
                                    key=f"pf_parts_{_key_prefix}")
        with fc:
            mode = st.selectbox("Mode", ["spread", "concentrated"],
                                format_func=lambda x: "📆 Lissé" if x == "spread" else "🗜️ Concentré",
                                index=0 if (not ep or ep["mode"] == "spread") else 1,
                                key=f"pf_mode_{_key_prefix}")
        with fd:
            mda_default = ep.get("max_day_act") if ep else None
            mda_input = st.number_input("Max act./jour (0=illimité)",
                                        min_value=0, max_value=99999,
                                        value=int(mda_default) if mda_default else 0,
                                        key=f"pf_mda_{_key_prefix}")
            max_day_act = mda_input if mda_input > 0 else None

        # Color selector
        used_colors = [p["color"] for p in SS.pathologistes if p["id"] != edit_id]
        default_color = ep["color"] if ep else next(
            (c for c in COLORS if c not in used_colors), COLORS[0])
        # Use radio buttons for color selection
        col_html = "<div style='display:flex;gap:5px;flex-wrap:wrap;margin:4px 0 8px'>"
        for c in COLORS:
            border = "3px solid #17233a" if c == default_color else "2px solid transparent"
            col_html += (f"<span style='width:24px;height:24px;border-radius:50%;"
                         f"background:{c};border:{border};display:inline-block;cursor:pointer'></span>")
        col_html += "</div>"
        sel_color = st.radio("Couleur",
                             COLORS,
                             format_func=lambda c: "●",
                             index=COLORS.index(default_color) if default_color in COLORS else 0,
                             horizontal=True,
                             key=f"pf_color_{_key_prefix}")

        # Wishes
        st.markdown("**⭐ Vœux / Desiderata**")
        wishes = SS.tmp_wishes if edit_id else SS.get("tmp_wishes_new", [])
        wish_key = "tmp_wishes" if edit_id else "tmp_wishes_new"

        if wishes:
            for w in sorted(wishes, key=lambda w: w["priority"]):
                wc1, wc2, wc3, wc4 = st.columns([1, 2, 3, 1])
                with wc1:
                    st.markdown(f"<span class='bdg bt'>Vœu n°{w['priority']}</span>",
                                unsafe_allow_html=True)
                with wc2:
                    st.write({"prefer":"✅ Préférer","avoid":"🚫 Éviter",
                              "consecutive":"📅 Consécutifs"}[w["type"]])
                with wc3:
                    st.write(" · ".join(JJ[i] for i in (w.get("days") or []))
                             if w["type"] != "consecutive" else "(jours adjacents)")
                with wc4:
                    if st.button("🗑️", key=f"dw_{w['id']}_{_key_prefix}"):
                        SS[wish_key] = [x for x in wishes if x["id"] != w["id"]]
                        st.rerun()

        with st.expander("➕ Ajouter un vœu"):
            wa, wb2, wc2 = st.columns([1, 2, 3])
            with wa:
                wprio = st.selectbox("Priorité", [1,2,3,4,5],
                                     format_func=lambda x: f"{'⭐'*max(1,4-x)} n°{x}",
                                     key=f"wf_p_{_key_prefix}")
            with wb2:
                wtype = st.selectbox("Type", ["prefer","avoid","consecutive"],
                                     format_func=lambda x:{"prefer":"✅ Préférer",
                                                            "avoid":"🚫 Éviter",
                                                            "consecutive":"📅 Consécutifs"}[x],
                                     key=f"wf_t_{_key_prefix}")
            with wc2:
                if wtype != "consecutive":
                    wdays = st.multiselect("Jours", list(range(SS.settings["days"])),
                                           format_func=lambda i: JJ[i],
                                           key=f"wf_d_{_key_prefix}")
                else:
                    wdays = []
                    st.info("Jours consécutifs : les jours travaillés seront groupés.")
            if st.button("✓ Valider ce vœu", key=f"wf_ok_{_key_prefix}"):
                if wtype != "consecutive" and not wdays:
                    st.error("Sélectionnez au moins un jour.")
                else:
                    SS[wish_key] = wishes + [{"id": uid(), "priority": wprio,
                                              "type": wtype, "days": wdays}]
                    st.rerun()

        # Save / Cancel
        sc1, sc2 = st.columns(2)
        with sc1:
            if st.button("💾 Enregistrer", type="primary", use_container_width=True,
                         key=f"pf_save_{_key_prefix}"):
                if not name.strip():
                    st.error("Entrez un nom.")
                else:
                    new_p = {
                        "id": edit_id or uid(),
                        "name": name.strip(),
                        "parts": parts,
                        "mode": mode,
                        "color": sel_color,
                        "max_day_act": max_day_act,
                        "wishes": list(SS.get(wish_key, [])),
                    }
                    if edit_id:
                        SS.pathologistes = [p if p["id"] != edit_id else new_p
                                            for p in SS.pathologistes]
                        SS.editing_patho_id = None
                        SS.tmp_wishes = []
                    else:
                        SS.pathologistes.append(new_p)
                        SS.tmp_wishes_new = []
                    st.success(f"✅ {new_p['name']} enregistré·e !")
                    st.rerun()
        with sc2:
            if edit_id and st.button("✕ Annuler", use_container_width=True,
                                     key=f"pf_cancel_{_key_prefix}"):
                SS.editing_patho_id = None
                SS.tmp_wishes = []
                st.rerun()


# ─────────────────────────────────────────────────────────────
# ABSENCES
# ─────────────────────────────────────────────────────────────
def render_absences():
    st.markdown("<div class='app-title'>🔴 Absences</div>", unsafe_allow_html=True)
    pathos = SS.pathologistes
    if not pathos:
        st.warning("Ajoutez d'abord des pathologistes.")
        return

    with st.form("abs_form", clear_on_submit=True):
        c1,c2,c3,c4 = st.columns([2,1,1,2])
        with c1: who = st.selectbox("Médecin", [p["name"] for p in pathos])
        with c2: abs_s = st.date_input("Début", value=date.today())
        with c3: abs_e = st.date_input("Fin", value=date.today())
        with c4: reason = st.text_input("Motif")
        if st.form_submit_button("🔴 Enregistrer l'absence", type="primary"):
            pid = next(p["id"] for p in pathos if p["name"] == who)
            e = abs_e if abs_e >= abs_s else abs_s
            SS.absences.append({"id":uid(),"patho_id":pid,
                                 "start":abs_s.isoformat(),"end":e.isoformat(),"reason":reason})
            st.success("Absence enregistrée."); st.rerun()

    if not SS.absences:
        st.info("Aucune absence déclarée."); return

    st.markdown("---")
    for a in sorted(SS.absences, key=lambda x: x["start"]):
        p = gp(a["patho_id"])
        if not p: continue
        lbl = a["start"] if a["start"] == a["end"] else f"{a['start']} → {a['end']}"
        c1,c2,c3,c4,c5 = st.columns([0.5,2,2,2,0.5])
        with c1: st.markdown(
            f"<span style='width:12px;height:12px;border-radius:50%;"
            f"background:{p['color']};display:inline-block'></span>", unsafe_allow_html=True)
        with c2: st.markdown(f"**{p['name']}**")
        with c3: st.code(lbl, language=None)
        with c4: st.write(a.get("reason",""))
        with c5:
            if st.button("🗑️", key=f"da_{a['id']}"):
                SS.absences = [x for x in SS.absences if x["id"] != a["id"]]; st.rerun()


# ─────────────────────────────────────────────────────────────
# STATS
# ─────────────────────────────────────────────────────────────
def render_stats():
    year, month = SS.cur_year, SS.cur_month
    s = SS.settings
    wd_list, H = get_work_days(year, month)
    T = tp()
    total_act = len(wd_list) * s["activity"]
    hol_c = sum(1 for d in H if d.year == year and d.month == month)

    st.markdown(f"<div class='app-title'>📊 Statistiques — {MM[month-1]} {year}</div>",
                unsafe_allow_html=True)

    cols = st.columns(5)
    for i, (v, lbl) in enumerate([
        (len(wd_list), "Jours ouvrés"),
        (hol_c, "Jours fériés"),
        (f"{total_act:,}".replace(",", " "), "Activité totale"),
        (len(SS.pathologistes), "Pathologistes"),
        (sum(1 for a in SS.absences
             if a["start"][:7] == f"{year}-{month:02d}"
             or a["end"][:7] == f"{year}-{month:02d}"), "Absences"),
    ]):
        with cols[i]:
            st.markdown(f"<div class='sbox'><div class='sval'>{v}</div>"
                        f"<div class='slbl'>{lbl}</div></div>",
                        unsafe_allow_html=True)

    if not SS.pathologistes or not SS.planning:
        st.info("Générez d'abord un planning."); return

    st.markdown("---")
    st.markdown("### ⚖️ Activité cible vs réalisée")

    p_act = {p["id"]: 0.0 for p in SS.pathologistes}
    p_days = {p["id"]: 0 for p in SS.pathologistes}
    for d in wd_list:
        pres = SS.planning.get(d.isoformat(), [])
        pp = sum((gp(pid) or {}).get("parts", 0) for pid in pres)
        for pid in pres:
            p_obj = gp(pid)
            if p_obj and pp > 0:
                p_act[p_obj["id"]] += s["activity"] * p_obj["parts"] / pp
                p_days[p_obj["id"]] += 1

    for p in SS.pathologistes:
        tgt = (p["parts"] / T * total_act) if T else 0
        act = p_act[p["id"]]
        tgtd = (p["parts"] / T * len(wd_list)) if T else 0
        actd = p_days[p["id"]]
        bar = min(100, act / tgt * 100) if tgt else 0
        diff = act - tgt; diffpct = diff / tgt * 100 if tgt else 0
        dcls = "color:#2a7d50" if abs(diffpct) < 3 else (
               "color:#b73640" if diffpct < 0 else "color:#c87b2d")
        dday = actd - round(tgtd)
        ddcls = "color:#2a7d50" if dday == 0 else (
                "color:#b73640" if dday < 0 else "color:#c87b2d")
        pctP = round(p["parts"] / T * 100) if T else 0

        c1, c2, c3 = st.columns([2, 4, 3])
        with c1:
            st.markdown(
                f"<div style='display:flex;align-items:center;gap:7px;padding:4px 0'>"
                f"<span style='width:13px;height:13px;border-radius:50%;"
                f"background:{p['color']};display:inline-block'></span>"
                f"<strong>{p['name']}</strong>"
                f"<span class='bdg bt'>{p['parts']}p·{pctP}%</span>"
                f"</div>", unsafe_allow_html=True)
        with c2:
            st.markdown(
                f"<div class='pbw'><div class='pb' style='width:{bar:.0f}%;background:{p['color']}'></div></div>"
                f"<div style='font-size:11px;color:#5d6d82;margin-top:3px'>"
                f"<strong>{act:.1f}</strong> / cible <strong>{tgt:.1f}</strong> "
                f"<span style='{dcls};font-weight:700'>({'+' if diff >= 0 else ''}{diffpct:.1f}%)</span>"
                f"</div>", unsafe_allow_html=True)
        with c3:
            st.markdown(
                f"<div style='font-size:11px;color:#5d6d82;padding:4px 0'>"
                f"Jours : <strong>{actd}</strong>/cible <strong>{tgtd:.1f}</strong> "
                f"<span style='{ddcls};font-weight:700'>({'+' if dday >= 0 else ''}{dday}j)</span><br>"
                f"Act./jour moy. : <strong>{act/actd:.1f}</strong>"
                f"</div>" if actd else
                "<div style='font-size:11px;color:#8898a9'>Absent ce mois</div>",
                unsafe_allow_html=True)
        st.markdown("<hr style='border:none;border-top:1px solid #e7e2db;margin:4px 0'>",
                    unsafe_allow_html=True)

    st.markdown("### 📊 Répartition des parts")
    bar_html = "<div style='display:flex;height:30px;border-radius:8px;overflow:hidden;margin-bottom:10px'>"
    for p in SS.pathologistes:
        w = (p["parts"] / T * 100) if T else 0
        lbl = p["name"].split()[-1] if w > 7 else ""
        pc = p["color"]
        bar_html += (f"<div style='width:{w:.1f}%;background:{pc};"
                     f"display:flex;align-items:center;justify-content:center;"
                     f"color:#fff;font-size:11px;font-weight:600;"
                     f"overflow:hidden;white-space:nowrap;padding:0 3px'>{lbl}</div>")
    bar_html += "</div>"
    leg_html = "<div class='leg'>"
    for p in SS.pathologistes:
        pct = round(p["parts"] / T * 100) if T else 0
        pc = p["color"]
        leg_html += (f"<span class='lchip'><span class='ldot' style='background:{pc}'></span>"
                     f"<strong>{p['name']}</strong> — {pct}% ({p['parts']}p)</span>")
    leg_html += "</div>"
    st.markdown(bar_html + leg_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# SETTINGS
# ─────────────────────────────────────────────────────────────
def render_settings():
    st.markdown("<div class='app-title'>⚙️ Paramètres</div>", unsafe_allow_html=True)
    s = SS.settings

    st.markdown("### 🏥 Cabinet")
    c1,c2,c3,c4 = st.columns(4)
    with c1: days = st.selectbox("Jours d'activité", [4,5,6],
                  format_func=lambda x:{4:"Lun→Jeu",5:"Lun→Ven",6:"Lun→Sam"}[x],
                  index=[4,5,6].index(s["days"]))
    with c2: activity = st.number_input("Activité totale / jour", 1, 99999, int(s["activity"]))
    with c3: min_p = st.number_input("Min. médecins présents / jour",
                                      1, 10, int(s["min_present"]))
    with c4: region = st.selectbox("Région", ["metro","alsace"],
                  format_func=lambda x:{"metro":"France métropolitaine","alsace":"Alsace-Moselle"}[x],
                  index=["metro","alsace"].index(s["region"]))

    st.markdown("### 🗜️ Seuils mode Concentré")
    st.caption("Activité mensuelle cible → nombre de jours/semaine pour un médecin Concentré")
    d1,d2,d3 = st.columns(3)
    with d1: c2v = st.number_input("≤ seuil → 2j/sem", value=int(s["conc2"]), min_value=1)
    with d2: c3v = st.number_input("≤ seuil → 3j/sem", value=int(s["conc3"]), min_value=1)
    with d3: c4v = st.number_input("≤ seuil → 4j/sem", value=int(s["conc4"]), min_value=1)
    st.caption("Au-delà du seuil 4j : le médecin concentré est traité comme lissé (5j/sem).")

    st.markdown("### 🎯 Hiérarchie des contraintes")
    st.caption("Ordre de priorité lors de la génération. Si une contrainte bloque l'équilibre (>10%), "
               "les contraintes **du bas** sont relâchées en premier.")

    current_order = s.get("constraint_order",
                          ["balance","spread","wish1","wish2","wish3","concentrated"])
    new_order = st.multiselect(
        "Contraintes actives (de la plus prioritaire en haut → à la plus relâchable en bas)",
        options=list(CONSTR_LABELS.keys()),
        default=current_order,
        format_func=lambda x: CONSTR_LABELS.get(x, x),
    )
    st.caption("💡 Désactivez une contrainte en la retirant de la liste pour qu'elle ne soit jamais appliquée.")

    st.markdown("### 🖥️ Affichage")
    v1,v2,v3 = st.columns(3)
    with v1: show_pct = st.checkbox("% des parts / chip", s["show_pct"])
    with v2: show_act = st.checkbox("Activité / chip", s["show_act"])
    with v3: show_wf  = st.checkbox("Bilan semaine", s["show_wf"])

    if st.button("💾 Sauvegarder les paramètres", type="primary"):
        SS.settings.update({
            "days": days, "activity": activity, "min_present": min_p, "region": region,
            "conc2": c2v, "conc3": c3v, "conc4": c4v,
            "constraint_order": new_order,
            "show_pct": show_pct, "show_act": show_act, "show_wf": show_wf,
        })
        st.success("✅ Paramètres sauvegardés.")

    st.markdown("---")
    st.markdown("### 💾 Export / Import")
    col_e, col_i = st.columns(2)
    with col_e:
        data = {"pathologistes": SS.pathologistes, "absences": SS.absences,
                "planning": SS.planning, "settings": SS.settings}
        st.download_button("⬇️ Exporter (JSON)",
                           data=json.dumps(data, indent=2, ensure_ascii=False),
                           file_name=f"planning_{date.today().isoformat()}.json",
                           mime="application/json", use_container_width=True)
    with col_i:
        up = st.file_uploader("⬆️ Importer (JSON)", type=["json"])
        if up:
            try:
                d = json.loads(up.read())
                SS.pathologistes = d.get("pathologistes", [])
                SS.absences = d.get("absences", [])
                SS.planning = d.get("planning", {})
                SS.settings.update(d.get("settings", {}))
                st.success("✅ Importé !"); st.rerun()
            except Exception as e:
                st.error(f"Erreur : {e}")

    st.markdown("---")
    if st.button("🗑️ Réinitialiser toutes les données"):
        for k, v in INIT.items():
            SS[k] = v if not isinstance(v, dict) else dict(v)
        st.success("✅ Réinitialisé."); st.rerun()


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 Planning", "👥 Pathologistes", "🔴 Absences", "📊 Statistiques", "⚙️ Paramètres"
])
with tab1: render_calendar()
with tab2: render_pathologistes()
with tab3: render_absences()
with tab4: render_stats()
with tab5: render_settings()
