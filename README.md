# Afya Kijiji — Health Village

A Kenya-focused health education platform, inspired by Finland's Terveyskylä
("Health Village"). Sixteen conditions ("houses") grouped into three
neighbourhoods, a symptom checker, guided self-care programs, a facility
directory, a personal "My Path" portal, and a Community Health Volunteer
(CHV) portal — all in plain English and Kiswahili.

## Running it before the panel — do this tonight, not tomorrow morning

```bash
cd afyakijiji
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py                  # loads the 16 houses, programs, facilities, demo users
python app.py
```

Then open **http://127.0.0.1:5000** in a browser.

If you already have an older `afyakijiji.db` from a previous version of this
app (before the 16-house redesign), **delete it first** — the content
structure changed and `seed.py` won't retrofit an old database:

```bash
rm -f afyakijiji.db
python seed.py
```

Demo accounts (created by `seed.py`):
- Family account: `demo@afyakijiji.ke` / `afyakijiji123`
- CHV account: `chv@afyakijiji.ke` / `chvdemo123` (unlocks the CHV Portal nav item)

## What to click through in the demo

1. **Home** — the hero, then the 16 houses grouped into three neighbourhoods
   (Infectious Diseases / Long-Term & Lifestyle Conditions / Family & Mental
   Wellbeing). The search bar at the top of "The houses" filters live as you
   type.
2. Open any house (e.g. **Malaria** or **Diabetes**) — self-care key points
   and a red "Seek help right away if" box, plus links into the symptom
   checker or a guided program where one exists.
3. **Symptom Checker** — a short branching questionnaire (pregnancy, child
   fever, breathing trouble, malaria symptoms, diarrhea, mental health).
4. **Programs** — step-by-step guided journeys (e.g. the pregnancy/ANC
   path); log in to check off steps and see them saved under **My Path**.
5. **Facilities** — Kenya's Level 1–6 referral tiers, filterable by county.
   Only Kenyatta National Hospital and Moi Teaching & Referral Hospital are
   real; the rest are placeholders to replace with verified local data.
6. **Emergency** — the mint-panel of verified national helpline numbers
   (tap-to-dial on a phone) plus warning signs pulled from every house.
7. **CHV Portal** (log in as the CHV demo account) — danger-sign and
   referral-process training material, plus the national referral hospital
   list.
8. **About** — the Terveyskylä inspiration story and the "this is
   education, not diagnosis" disclaimer.
9. The **A / A+ / A++** control in the header scales text size site-wide,
   for older or low-vision users — a small but real accessibility touch
   worth mentioning to the panel.

## What's real vs. placeholder — be upfront about this with the panel

- **Emergency numbers** (Emergency page and footer) were individually
  verified against public sources as of September 2026: 999/112, the SHA
  922 Lifeline, Kenya Red Cross (1199), the GBV hotline (1195), the child
  helpline (116), NACADA (1192), LVCT one2one (1190), and the National
  Poison Control Centre (0800 720 021). Numbers and services can still
  change — worth a line in the pitch that you'd confirm these with MOH
  directly.
- **Facility listings** are almost entirely placeholder data (clearly
  commented as such in `seed.py`) except the two national referral
  hospitals. This is the biggest open item — exactly the kind of thing a
  Ministry of Health partnership would fill in with real facility data.
- **Condition content** (the 16 houses) is written to be medically sound
  and Kenya-relevant, but it's a first draft — positioning it to the panel
  as "ready to be reviewed and signed off by MOH clinical staff" is more
  accurate than presenting it as final.

## A note on tomorrow's live demo

Running a Flask server live in front of a panel carries real risk — wifi,
projector setup, a forgotten `source venv/bin/activate`, a stuck port. If
you want a zero-setup backup that works from any browser with no server to
start, I can publish a matching static version of this design (same look,
same content, no login/database features) to a shareable link — just ask.
