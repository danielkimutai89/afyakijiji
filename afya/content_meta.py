"""
content_meta.py — display metadata that isn't really "data" (it doesn't need
a migration to change): the three neighbourhoods houses are grouped into,
category icons, the verified national emergency/helpline numbers, and the
static copy for the About page.

Kept separate from models.py so templates/routes can import it without
touching the database layer, and so seed.py's CONTENT_PAGES stays focused on
actual page content.
"""

# ---------------------------------------------------------------------------
# Neighbourhoods — the three groupings the 16 "houses" (ContentPage rows with
# audience="public" and category in NEIGHBOURHOOD keys) are organized under
# on the home page, mirroring the original Afya Kijiji's structure.
# ---------------------------------------------------------------------------

NEIGHBOURHOODS = [
    {
        "key": "infectious",
        "name": "Infectious Diseases",
        "name_sw": "Magonjwa ya Kuambukiza",
        "icon": "🦠",
        "blurb": "Illnesses spread by germs, mosquitoes, or contaminated food and water.",
        "color": "#1f7d6f",  # deep teal
    },
    {
        "key": "chronic",
        "name": "Long-Term & Lifestyle Conditions",
        "name_sw": "Magonjwa Sugu",
        "icon": "❤️‍🩹",
        "blurb": "Conditions managed over months and years, one steady routine at a time.",
        "color": "#bb4f2e",  # rust / terracotta
    },
    {
        "key": "family",
        "name": "Family & Mental Wellbeing",
        "name_sw": "Ustawi wa Familia na Akili",
        "icon": "🌿",
        "blurb": "Care for mothers, children, minds, and the whole household.",
        "color": "#7c4f9b",  # deep plum
    },
]

# category -> icon shown on cards. Includes the neighbourhood keys, the
# "practical" supporting guides, and "training" for CHV-only resources.
CATEGORY_ICONS = {
    "infectious": "🦠",
    "chronic": "❤️‍🩹",
    "family": "🌿",
    "practical": "🧭",
    "training": "📋",
}

# category -> accent color, so each neighbourhood reads as its own place in
# the village rather than everything sharing one amber accent. Colors are
# tuned dark enough to work as text/icons on the site's light cream content
# background (they double as a color-mix base for softly tinted card
# backgrounds). "practical" and "training" stay on the neutral brand amber
# since they're cross-cutting, not a neighbourhood of their own.
CATEGORY_COLORS = {
    "infectious": "#1f7d6f",
    "chronic": "#bb4f2e",
    "family": "#7c4f9b",
    "practical": "#a8640d",
    "training": "#a8640d",
}
DEFAULT_ICON = "🩺"
DEFAULT_COLOR = "#a8640d"

# ---------------------------------------------------------------------------
# National emergency & helpline numbers — verified against public sources
# (news coverage of the SHA 922 Lifeline launch, the operators' own social
# accounts / sites) as of September 2026. Numbers and services can change;
# re-verify with the Ministry of Health if this list is ever in doubt.
# ---------------------------------------------------------------------------

NATIONAL_NUMBERS = [
    {
        "label": "General emergency (police / fire / ambulance)",
        "number": "999 or 112",
        "tel": "999",
        "note": "Kenya's general emergency lines — free from any network.",
    },
    {
        "label": "SHA 922 Lifeline",
        "number": "922",
        "tel": "922",
        "note": "National ambulance dispatch, launched 2026 by the Social Health Authority — free ambulance response across all 47 counties.",
    },
    {
        "label": "Kenya Red Cross emergency hotline",
        "number": "1199",
        "tel": "1199",
        "note": "24/7 hotline for ambulance and emergency response.",
    },
    {
        "label": "GBV & rape crisis hotline",
        "number": "1195",
        "tel": "1195",
        "note": "For survivors of gender-based violence and sexual assault.",
    },
    {
        "label": "Child helpline",
        "number": "116",
        "tel": "116",
        "note": "Free, 24/7 line for reporting child abuse or a child in danger.",
    },
    {
        "label": "NACADA substance-use helpline",
        "number": "1192",
        "tel": "1192",
        "note": "Counselling and referral for alcohol and drug-related emergencies.",
    },
    {
        "label": "LVCT one2one helpline",
        "number": "1190",
        "tel": "1190",
        "note": "Confidential counselling on HIV, mental health, and sexual health.",
    },
    {
        "label": "National Poison Control Centre",
        "number": "0800 720 021",
        "tel": "0800720021",
        "note": "Toll-free advice for suspected poisoning.",
    },
]

# ---------------------------------------------------------------------------
# About page copy
# ---------------------------------------------------------------------------

ABOUT_STORY = [
    ("Our Mission", 
     "Afya Kijiji exists to make trusted health information accessible to every Kenyan family. We bring together clear, practical guidance on everyday conditions — from malaria and tuberculosis to diabetes, maternal health, and mental wellbeing."),
    
    ("Built for Kenya", 
     "This platform is designed with Kenyan communities in mind. Content is available in English and Kiswahili, and reflects the realities of local health systems, facilities, and family life. Our goal is to provide a health village online — one place for the questions you search at midnight."),
    
    ("Community and Collaboration", 
     "Afya Kijiji grows with the people it serves. Health workers, families, and community volunteers are invited to share feedback and contribute insights, ensuring the information stays relevant and trustworthy."),
]

ABOUT_DISCLAIMER = (
    "Afya Kijiji is a health‑education reference, not a diagnosis. "
    "It does not examine, diagnose, or treat you, and it is not a substitute for seeing a qualified health worker. "
    "In an emergency, go to your nearest facility or call national emergency numbers (999, 112, or 911). "
    "Always verify local facility listings and guidance with official sources."
)

