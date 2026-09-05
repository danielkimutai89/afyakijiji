"""
seed.py — populate the database with sample data: houses, facilities
(tiered per Kenya's real Level 1-6 MOH system), guided self-care programs,
and CHV-only resources.

Usage:
    python seed.py

ContentPage and CareProgram/ProgramStep are re-synced every run (upsert),
so editing the data below and re-running always updates the site. Facility
and User rows are only seeded once (skipped if the table already has data)
since Facility especially is meant to be replaced with real data you collect
from the Ministry of Health and local facilities.

ContentPage.body convention (parsed by templates/page.html):
    Line 1                      -> one-sentence summary (shown on the card)
    (blank line)
    "- point one" / "- point two" ...   -> key points (bulleted)
    (blank line)
    "SEEK HELP:" followed by "- ..." lines -> red-flag warning box (optional,
        public houses only -- ignored/absent on CHV resources)

Public ContentPage.category convention: the 16 "houses" use one of the three
neighbourhood keys from afya/content_meta.py ("infectious", "chronic",
"family") so the home page can group them; everything else public uses
"practical" and is shown as a separate "Practical guides" section.
"""

from werkzeug.security import generate_password_hash

from afya import create_app
from afya.extensions import db
from afya.models import User, ContentPage, Facility, CareProgram, ProgramStep

# Slugs from earlier content structures that are superseded by the 16-house
# layout below (e.g. "malaria-prevention" -> "malaria"). Upserting only adds
# or updates slugs present in CONTENT_PAGES, so these are deleted explicitly
# to avoid leaving stale duplicate cards behind after a reseed.
RETIRED_SLUGS = ["maternal-health", "hiv-awareness", "respiratory-infections", "malaria-prevention"]

# ---------------------------------------------------------------------------
# Public houses — 16 conditions across 3 neighbourhoods, plus a handful of
# "practical" supporting guides (immunization, hygiene, etc.) that don't map
# to a single condition.
# ---------------------------------------------------------------------------

CONTENT_PAGES = [
    # ================= Neighbourhood: Infectious Diseases =================
    {
        "slug": "hiv-aids", "title": "HIV & AIDS",
        "title_sw": "Virusi vya Ukimwi",
        "category": "infectious", "language": "en", "audience": "public",
        "body": (
            "HIV is a manageable, chronic condition today — testing early and staying on treatment lets people live long, healthy lives.\n\n"
            "- Free HIV testing and counselling is available at most public health facilities and many CHV-linked community sites.\n"
            "- Antiretroviral therapy (ART) is free through the public health system and, taken daily, keeps the virus suppressed and the immune system strong.\n"
            "- An undetectable viral load on treatment means HIV cannot be passed on to a sexual partner (U=U).\n"
            "- PrEP (pre-exposure prophylaxis) is available for people at ongoing higher risk — ask a health worker if it's right for you.\n"
            "- Mother-to-child transmission is preventable — pregnant women living with HIV should start ANC and treatment early.\n\n"
            "SEEK HELP:\n"
            "- Possible recent exposure (unprotected sex, needle injury) — post-exposure prophylaxis (PEP) works best started within 72 hours\n"
            "- Missed doses of ART for several days in a row\n"
            "- New unexplained weight loss, persistent fever, or infections that won't clear while on treatment"
        ),
    },
    {
        "slug": "tuberculosis", "title": "Tuberculosis (TB)",
        "title_sw": "Kifua Kikuu",
        "category": "infectious", "language": "en", "audience": "public",
        "body": (
            "TB is curable with a full course of treatment — but stopping early lets it come back stronger and harder to treat.\n\n"
            "- A cough lasting more than 2 weeks, especially with night sweats or weight loss, should be checked for TB at a health facility.\n"
            "- TB testing and the full treatment course are free through Kenya's public health system.\n"
            "- Treatment usually runs 6 months or longer — completing every dose is what cures it and prevents drug-resistant TB.\n"
            "- TB spreads through the air; good ventilation and covering coughs at home protects family members.\n"
            "- People living with HIV are at higher risk of TB and should be screened regularly.\n\n"
            "SEEK HELP:\n"
            "- Cough lasting more than 2 weeks\n"
            "- Coughing up blood\n"
            "- Unexplained fever, night sweats, or weight loss"
        ),
    },
    {
        "slug": "malaria", "title": "Malaria",
        "title_sw": "Homa ya Malaria",
        "category": "infectious", "language": "en", "audience": "public",
        "body": (
            "Malaria remains a leading cause of illness in Kenya — prevention and same-day testing save lives.\n\n"
            "- Sleep under a treated mosquito net every night, even during the dry season.\n"
            "- Clear stagnant water around the home where mosquitoes breed.\n"
            "- Get tested at a health facility before taking any malaria medicine — fever alone doesn't confirm malaria.\n"
            "- Complete the full prescribed course of antimalarial medicine, even after you start feeling better.\n"
            "- Pregnant women and young children are at highest risk and should be tested promptly for any fever.\n\n"
            "SEEK HELP:\n"
            "- Fever not improving after 2 days of treatment\n"
            "- Confusion, drowsiness, or convulsions\n"
            "- Repeated vomiting or inability to keep down oral medicine"
        ),
    },
    {
        "slug": "typhoid", "title": "Typhoid Fever",
        "title_sw": "Homa ya Matumbo",
        "category": "infectious", "language": "en", "audience": "public",
        "body": (
            "Typhoid spreads through contaminated food and water — safe water and hygiene are the best prevention.\n\n"
            "- Boil, filter, or chemically treat drinking water from any unprotected source.\n"
            "- Wash hands with soap before eating, before cooking, and after using the toilet.\n"
            "- Wash fruits and vegetables well, and avoid food from vendors with poor hygiene.\n"
            "- A typhoid vaccine is available at some facilities — ask a health worker, especially before travel to high-risk areas.\n"
            "- Confirmed typhoid is treated with a full course of antibiotics prescribed after testing, not guessed at home.\n\n"
            "SEEK HELP:\n"
            "- Prolonged fever (especially rising through the day) lasting more than 3 days\n"
            "- Severe abdominal pain, or a rash of flat, rose-coloured spots\n"
            "- Confusion or severe weakness"
        ),
    },
    {
        "slug": "pneumonia", "title": "Pneumonia",
        "title_sw": "Nimonia",
        "category": "infectious", "language": "en", "audience": "public",
        "body": (
            "Pneumonia is a leading cause of death in young children in Kenya — fast or difficult breathing is the danger sign to know.\n\n"
            "- Most coughs and colds clear up in 1-2 weeks with rest, fluids, and home care.\n"
            "- Keep children away from smoke — cooking fires, cigarette smoke, and indoor air pollution.\n"
            "- Fast or laboured breathing in a young child can signal pneumonia and needs same-day facility care.\n"
            "- Keep routine vaccinations up to date — the pneumococcal vaccine (PCV10) protects against a major cause of pneumonia.\n"
            "- Adults with chronic conditions (diabetes, HIV, chronic lung disease) are at higher risk and should seek care early for chest infections.\n\n"
            "SEEK HELP:\n"
            "- Fast or laboured breathing, or chest indrawing in a child\n"
            "- Bluish lips, tongue, or face\n"
            "- Unable to drink, breastfeed, or keep fluids down"
        ),
    },

    # ============= Neighbourhood: Long-Term & Lifestyle Conditions =============
    {
        "slug": "diabetes", "title": "Diabetes",
        "title_sw": "Kisukari",
        "category": "chronic", "language": "en", "audience": "public",
        "body": (
            "Diabetes is a lifelong condition that's manageable with the right routine — most complications come from going undiagnosed or untreated, not from the disease itself.\n\n"
            "- Common early signs include frequent urination, unusual thirst, unexplained weight loss, and fatigue — get tested if these persist.\n"
            "- Managing diabetes well combines medicine or insulin as prescribed, regular meals, physical activity, and routine blood sugar checks.\n"
            "- Foot care matters: check feet daily for cuts or sores, since diabetes can reduce sensation and slow healing.\n"
            "- Regular check-ups help catch complications early — eyes, kidneys, and feet should be reviewed at least yearly.\n"
            "- Diabetes is increasingly common in Kenya, including in people who are not overweight — a family history is reason enough to get screened.\n\n"
            "SEEK HELP:\n"
            "- Extreme thirst, confusion, rapid breathing, or fruity-smelling breath (possible diabetic emergency)\n"
            "- A foot wound that isn't healing, especially with swelling, redness, or odour\n"
            "- Blood sugar readings far outside the range your health worker advised, or repeated fainting or dizziness"
        ),
    },
    {
        "slug": "hypertension", "title": "High Blood Pressure (Hypertension)",
        "title_sw": "Shinikizo la Damu",
        "category": "chronic", "language": "en", "audience": "public",
        "body": (
            "High blood pressure usually has no symptoms — the only way to know is to check it, and the only way to manage it is consistently.\n\n"
            "- Have your blood pressure checked regularly, even if you feel completely well — hypertension is often silent for years.\n"
            "- Reduce salt intake, stay physically active, and limit alcohol to help control blood pressure.\n"
            "- Take prescribed medication every day, even once you feel fine — stopping is a leading cause of strokes and heart attacks.\n"
            "- Manage other risk factors together: diabetes, being overweight, and smoking all compound the risk.\n"
            "- Home blood pressure monitors are increasingly affordable and useful for tracking trends between clinic visits.\n\n"
            "SEEK HELP:\n"
            "- A very high reading with severe headache, chest pain, or blurred vision\n"
            "- Sudden weakness or numbness on one side of the body, slurred speech, or facial drooping — possible stroke, go immediately\n"
            "- Shortness of breath or swelling in the legs and feet"
        ),
    },
    {
        "slug": "cancer", "title": "Cancer",
        "title_sw": "Saratani",
        "category": "chronic", "language": "en", "audience": "public",
        "body": (
            "Cancer outcomes in Kenya improve sharply with early detection — knowing the warning signs and not delaying screening matters more than any single treatment.\n\n"
            "- Common cancers in Kenya include breast, cervical, oesophageal, and prostate cancer — ask your facility about available screening.\n"
            "- Cervical cancer is largely preventable through HPV vaccination (for girls) and regular screening (for women).\n"
            "- Breast self-checks and clinical breast exams help catch changes early — a lump is not automatically cancer, but always needs checking.\n"
            "- Treatment (surgery, chemotherapy, radiotherapy) is available at referral hospitals, and cost-support schemes exist through SHA — ask a social worker at the facility.\n"
            "- Early-stage cancers are often curable — the biggest risk is delaying that first visit.\n\n"
            "SEEK HELP:\n"
            "- A new lump, thickening, or persistent sore that doesn't heal\n"
            "- Unexplained weight loss, persistent fatigue, or unusual bleeding\n"
            "- Any change that worries you and lasts more than 2-3 weeks — get it checked rather than waiting"
        ),
    },
    {
        "slug": "kidney-disease", "title": "Kidney Disease",
        "title_sw": "Ugonjwa wa Figo",
        "category": "chronic", "language": "en", "audience": "public",
        "body": (
            "Chronic kidney disease often develops silently alongside diabetes and hypertension — controlling those two conditions is the best protection for your kidneys.\n\n"
            "- Diabetes and high blood pressure are the two leading causes of kidney disease in Kenya — managing them well protects your kidneys too.\n"
            "- Drink enough water, avoid overusing painkillers (especially NSAIDs) over long periods, and avoid unregulated herbal remedies of unknown content.\n"
            "- Routine blood and urine tests can catch kidney problems early, well before symptoms appear.\n"
            "- Dialysis and kidney care are available at county and national referral hospitals — SHA coverage can help with costs, ask a facility social worker.\n"
            "- Reducing salt intake and maintaining a healthy weight both support kidney health long-term.\n\n"
            "SEEK HELP:\n"
            "- Swelling in the legs, ankles, or around the eyes\n"
            "- A significant drop in how much urine you're passing, or urine that's foamy or bloody\n"
            "- Persistent fatigue, nausea, or confusion alongside known kidney or long-term illness"
        ),
    },
    {
        "slug": "arthritis", "title": "Arthritis & Joint Pain",
        "title_sw": "Baridi Yabisi",
        "category": "chronic", "language": "en", "audience": "public",
        "body": (
            "Joint pain and stiffness are common with age, but persistent swelling or pain that limits daily life is not something to just live with.\n\n"
            "- Gentle regular movement (walking, stretching) often helps joint stiffness more than complete rest.\n"
            "- Maintaining a healthy weight reduces the load on weight-bearing joints like knees and hips.\n"
            "- Warm compresses can ease stiffness; a health worker can advise on safe pain relief.\n"
            "- Some joint pain comes from inflammatory conditions (like rheumatoid arthritis) needing specific treatment, not just age-related wear — get persistent cases checked.\n"
            "- Physiotherapy, available at many county hospitals, can improve mobility and reduce pain over time.\n\n"
            "SEEK HELP:\n"
            "- A joint that's hot, very swollen, and painful, especially with fever — can signal infection, this is urgent\n"
            "- Sudden inability to move or bear weight on a joint\n"
            "- Joint pain and stiffness that's getting worse over weeks despite home care"
        ),
    },
    {
        "slug": "asthma", "title": "Asthma",
        "title_sw": "Pumu",
        "category": "chronic", "language": "en", "audience": "public",
        "body": (
            "Asthma is very manageable once triggers are known and medicine is used correctly — most emergencies happen when inhalers are used wrong or not at all.\n\n"
            "- Identify and reduce your personal triggers: dust, smoke, cold air, strong smells, or specific allergens.\n"
            "- Use preventer inhalers daily as prescribed, even when you feel well — they work by reducing inflammation over time.\n"
            "- Keep a reliever (rescue) inhaler on hand at all times and know how to use it correctly.\n"
            "- Children with asthma can and should participate fully in school and play once it's well controlled — don't over-restrict activity.\n"
            "- Review your asthma plan with a health worker at least yearly, or sooner if attacks are becoming more frequent.\n\n"
            "SEEK HELP:\n"
            "- Severe difficulty breathing, unable to speak full sentences, or lips/fingertips turning blue\n"
            "- No improvement after using a reliever inhaler as directed\n"
            "- Attacks becoming more frequent or severe despite following the usual treatment plan"
        ),
    },
    {
        "slug": "epilepsy", "title": "Epilepsy",
        "title_sw": "Kifafa",
        "category": "chronic", "language": "en", "audience": "public",
        "body": (
            "Epilepsy is a treatable neurological condition, not a curse or a contagious illness — most people on consistent medication live full, seizure-free lives.\n\n"
            "- Anti-seizure medication, taken consistently every day, controls seizures for most people — missed doses are the most common cause of breakthrough seizures.\n"
            "- During a seizure: clear the area of hard or sharp objects, cushion the head, turn the person on their side, and do not restrain them or put anything in their mouth.\n"
            "- Most seizures stop on their own within a few minutes — time it, and stay with the person until they're fully alert.\n"
            "- Epilepsy is not contagious and does not indicate possession or mental illness — this stigma prevents many people from seeking treatment.\n"
            "- Regular follow-up helps find the right medication and dose, especially in the first months of treatment.\n\n"
            "SEEK HELP:\n"
            "- A seizure lasting longer than 5 minutes, or a second seizure starting before full recovery from the first\n"
            "- Difficulty breathing after a seizure, or a seizure in water\n"
            "- First-ever seizure in a person, or a seizure during pregnancy"
        ),
    },

    # ============= Neighbourhood: Family & Mental Wellbeing =============
    {
        "slug": "maternal-child-health", "title": "Maternal & Child Health",
        "title_sw": "Afya ya Mama na Mtoto",
        "category": "family", "language": "en", "audience": "public",
        "body": (
            "Care before, during, and after pregnancy — and through a child's earliest years — protects both mother and baby.\n\n"
            "- Attend at least 4 antenatal care (ANC) visits, starting as early in pregnancy as possible.\n"
            "- Take iron and folic acid supplements as advised, and sleep under a treated mosquito net every night during pregnancy.\n"
            "- Plan for a skilled birth attendant and deliver at a health facility, not at home, whenever possible.\n"
            "- Breastfeed exclusively for the first 6 months, then continue alongside complementary foods to 2 years.\n"
            "- Keep the mother-and-child health booklet up to date — it tracks growth, vaccines, and every visit in one place.\n\n"
            "SEEK HELP:\n"
            "- Heavy vaginal bleeding, severe headache, or blurred vision during pregnancy\n"
            "- Reduced or no baby movement in later pregnancy\n"
            "- A child with no weight gain over 2+ months, visible wasting, or persistent lethargy"
        ),
    },
    {
        "slug": "family-planning", "title": "Family Planning",
        "title_sw": "Uzazi wa Mpango",
        "category": "family", "language": "en", "audience": "public",
        "body": (
            "Spacing and planning pregnancies supports healthier mothers, healthier children, and families who are ready.\n\n"
            "- Family planning counselling and most methods are free or low-cost at public health facilities.\n"
            "- A health worker can help you choose a method that fits your health, plans, and preferences — options range from short-acting to long-acting and permanent methods.\n"
            "- Spacing pregnancies by at least 2 years improves outcomes for both mother and child.\n"
            "- Condoms are the only method that also protects against sexually transmitted infections, including HIV.\n"
            "- Family planning is available to anyone, married or not — a partner's presence is not required to access services.\n\n"
            "SEEK HELP:\n"
            "- Severe side effects after starting a method: heavy bleeding, severe pain, or signs of infection\n"
            "- Uncertainty about a method — ask to switch rather than stop and go unprotected\n"
            "- Suspected pregnancy while trying to avoid one, or interest in emergency contraception (most effective within 72 hours)"
        ),
    },
    {
        "slug": "mental-health", "title": "Mental Health & Wellbeing",
        "title_sw": "Afya ya Akili",
        "category": "family", "language": "en", "audience": "public",
        "body": (
            "Mental health matters as much as physical health — persistent distress is treatable, not a personal weakness.\n\n"
            "- Persistent sadness, hopelessness, or loss of interest lasting 2+ weeks may be depression, not just 'stress' — it's worth talking to someone.\n"
            "- Anxiety that interferes with daily life, sleep, or relationships is a medical condition with effective treatments, including counselling.\n"
            "- Postpartum depression and anxiety are common after childbirth and treatable — they are not a sign of failing as a mother.\n"
            "- Talking to a trusted person, a counsellor, or a CHV is a strong first step — you don't have to reach crisis point to ask for help.\n"
            "- Sleep, physical activity, and staying connected to community all support mental wellbeing alongside any treatment.\n\n"
            "SEEK HELP:\n"
            "- Thoughts of self-harm or suicide — seek help immediately, you don't have to be in crisis to call a helpline\n"
            "- A sudden, severe change in behaviour, or loss of touch with reality\n"
            "- Substance use that's escalating alongside worsening mood"
        ),
    },
    {
        "slug": "substance-abuse", "title": "Substance Abuse",
        "title_sw": "Matumizi Mabaya ya Dawa za Kulevya",
        "category": "family", "language": "en", "audience": "public",
        "body": (
            "Alcohol and drug dependence is a health condition, not a moral failing — recovery support and treatment are available and effective.\n\n"
            "- Cutting down or stopping heavy, long-term alcohol or drug use can cause dangerous withdrawal — get medical support rather than stopping suddenly and alone.\n"
            "- NACADA (Kenya's National Authority for the Campaign Against Alcohol and Drug Abuse) offers free counselling, referral, and rehabilitation information.\n"
            "- Family involvement improves recovery outcomes — supporting rather than shaming someone in recovery makes a real difference.\n"
            "- Substance use often overlaps with untreated mental health conditions — treating both together works better than treating either alone.\n"
            "- Confidential counselling is available without judgment or police involvement for people seeking help for their own or a family member's use.\n\n"
            "SEEK HELP:\n"
            "- Severe withdrawal symptoms: confusion, seizures, hallucinations, or severe shaking after stopping alcohol or drugs\n"
            "- Overdose signs: unresponsiveness, very slow or stopped breathing, blue lips — this is a medical emergency\n"
            "- Thoughts of self-harm alongside substance use"
        ),
    },

    # ================= Practical guides (not a single "house") =================
    {
        "slug": "child-nutrition", "title": "Child Growth & Nutrition",
        "title_sw": "Lishe na Ukuaji wa Mtoto",
        "category": "practical", "language": "en", "audience": "public",
        "body": (
            "Exclusive breastfeeding, growth monitoring, and preventing malnutrition.\n\n"
            "- Breastfeed exclusively for the first 6 months.\n"
            "- Start nutritious complementary foods at 6 months, continue breastfeeding to 2 years.\n"
            "- Take your child for growth monitoring every month in the first year.\n"
            "- Watch for signs of malnutrition: thin limbs, swelling, low energy.\n\n"
            "SEEK HELP:\n"
            "- No weight gain over 2+ months\n"
            "- Visible wasting or swelling"
        ),
    },
    {
        "slug": "immunization-schedule", "title": "Immunization Schedule",
        "title_sw": "Ratiba ya Chanjo",
        "category": "practical", "language": "en", "audience": "public",
        "body": (
            "Kenya's routine childhood vaccination schedule (KEPI) at a glance.\n\n"
            "- At birth: BCG and OPV0.\n"
            "- 6 / 10 / 14 weeks: DPT-HepB-Hib, OPV, PCV10, Rotavirus (plus IPV at 14 weeks).\n"
            "- 9 months: Measles-Rubella 1 and Yellow Fever.\n"
            "- 18 months: Measles-Rubella 2.\n"
            "- Keep the mother-and-child health booklet safe for every visit.\n\n"
            "SEEK HELP:\n"
            "- Missed a scheduled vaccine — it's free and never too late to catch up"
        ),
    },
    {
        "slug": "diarrhea-dehydration", "title": "Diarrhea & Dehydration",
        "title_sw": "Kuhara na Upungufu wa Maji",
        "category": "practical", "language": "en", "audience": "public",
        "body": (
            "Oral rehydration and hygiene prevent most diarrhea deaths.\n\n"
            "- Give Oral Rehydration Solution (ORS) immediately.\n"
            "- Continue breastfeeding and normal feeding.\n"
            "- Ask about zinc supplements for 10-14 days for children.\n"
            "- Always boil or treat drinking water; wash hands with soap.\n\n"
            "SEEK HELP:\n"
            "- Sunken eyes, dry mouth, little/no urine\n"
            "- Blood in stool\n"
            "- Diarrhea lasting more than 2 days"
        ),
    },
    {
        "slug": "hygiene-safe-water", "title": "Hygiene & Safe Water",
        "title_sw": "Usafi na Maji Salama",
        "category": "practical", "language": "en", "audience": "public",
        "body": (
            "Simple habits that prevent most infectious diseases at home.\n\n"
            "- Wash hands with soap before eating and after the toilet.\n"
            "- Boil, filter, or treat drinking water from unprotected sources.\n"
            "- Store drinking water in a clean, covered container.\n"
            "- Build and use a latrine; keep it clean."
        ),
    },
    {
        "slug": "emergency-care", "title": "When to Seek Emergency Care",
        "title_sw": "Huduma ya Dharura",
        "category": "practical", "language": "en", "audience": "public",
        "body": (
            "Warning signs that mean you should go to a health facility right away.\n\n"
            "- Know the route to your nearest health facility in advance.\n"
            "- Keep emergency contacts written down at home.\n"
            "- Never wait out severe symptoms 'to see if they improve'.\n\n"
            "SEEK HELP:\n"
            "- Severe bleeding\n"
            "- Difficulty breathing\n"
            "- Convulsions or loss of consciousness\n"
            "- High fever with stiff neck or rash"
        ),
    },
    {
        "slug": "afya-ya-mama-mjamzito", "title": "Afya ya Mama na Mtoto",
        "category": "family", "language": "sw", "audience": "public",
        "body": (
            "Huduma kabla, wakati, na baada ya ujauzito — na katika miaka ya kwanza ya mtoto — humlinda mama na mtoto.\n\n"
            "- Hudhuria kliniki ya ANC angalau mara 4, ukianzia mapema iwezekanavyo.\n"
            "- Tumia dawa za madini ya chuma na foliki kama ulivyoshauriwa.\n"
            "- Lala chini ya neti iliyotibiwa kila usiku kuzuia malaria wakati wa ujauzito.\n"
            "- Panga kujifungulia katika kituo cha afya chenye wahudumu waliohitimu.\n"
            "- Nyonyesha mtoto maziwa ya mama pekee kwa miezi 6 ya kwanza."
        ),
    },

    # ---- CHV-only resources (audience="chv") ----
    {
        "slug": "chv-danger-signs", "title": "Recognizing Danger Signs in the Community",
        "category": "training", "language": "en", "audience": "chv",
        "body": (
            "Fast recognition and referral saves lives — your job is to spot these signs early, not to treat them.\n\n"
            "- Any of the standard emergency signs (severe bleeding, breathing difficulty, convulsions, unconsciousness) → refer to the nearest Level 4+ facility immediately.\n"
            "- Pregnant women with bleeding, severe headache, or reduced fetal movement → refer same-day, do not wait for the next scheduled visit.\n"
            "- Children under 5 with fast breathing, inability to feed, or lethargy → refer immediately, these are IMCI danger signs.\n"
            "- Always accompany or arrange transport when possible — a referral note alone is not enough for the most urgent cases."
        ),
    },
    {
        "slug": "chv-referral-process", "title": "The Referral Process & Documentation",
        "category": "training", "language": "en", "audience": "chv",
        "body": (
            "A good referral gets the patient seen faster and gives the receiving facility what they need.\n\n"
            "- Fill in the CHV referral/counter-referral form with name, age, presenting signs, and your assessment.\n"
            "- Note the time symptoms started and any home treatment already given (e.g. ORS started, paracetamol given).\n"
            "- Send referrals for non-urgent cases to the nearest Level 2/3 facility first; only urgent danger-sign cases should bypass straight to Level 4+.\n"
            "- Follow up within a few days to confirm the household reached the facility, and record the outcome in your CHV register."
        ),
    },
    {
        "slug": "chv-household-visits", "title": "Structuring a Household Visit",
        "category": "training", "language": "en", "audience": "chv",
        "body": (
            "A consistent visit structure means nothing important gets missed.\n\n"
            "- Start with the household register: who's pregnant, who's under 5, who's on chronic treatment (HIV, TB, hypertension).\n"
            "- Check immunization and ANC status against the schedule before discussing anything else.\n"
            "- Screen for the danger signs relevant to whoever is most vulnerable in that household this visit.\n"
            "- Leave with one clear, specific action agreed with the household — not a general reminder to 'be careful'."
        ),
    },
]

# ---------------------------------------------------------------------------
# Facilities — Kenya's real Level 1-6 MOH tier system.
# Level 5/6 entries below are real, publicly known national/county referral
# hospitals. Level 2-4 entries are illustrative placeholders (fictional
# names) -- replace with your local facility list.
# ---------------------------------------------------------------------------

FACILITY_LEVELS = {
    2: "Level 2 - Dispensary / Clinic",
    3: "Level 3 - Health Centre",
    4: "Level 4 - Sub-County Hospital",
    5: "Level 5 - County Referral Hospital",
    6: "Level 6 - National Referral Hospital",
}

FACILITIES = [
    # Real national referral hospitals (Level 6)
    {"name": "Kenyatta National Hospital", "county": "Nairobi", "ward": "Upper Hill",
     "level": FACILITY_LEVELS[6], "is_national_referral": True,
     "latitude": -1.3011, "longitude": 36.8073},
    {"name": "Moi Teaching and Referral Hospital", "county": "Uasin Gishu", "ward": "Eldoret City",
     "level": FACILITY_LEVELS[6], "is_national_referral": True,
     "latitude": 0.5203, "longitude": 35.2698},

    # Sample County Referral Hospitals (Level 5) -- illustrative
    {"name": "Machakos Level 5 Hospital", "county": "Machakos", "ward": "Machakos Central",
     "level": FACILITY_LEVELS[5], "is_national_referral": False,
     "latitude": -1.5177, "longitude": 37.2634},
    {"name": "Coast General Teaching & Referral Hospital", "county": "Mombasa", "ward": "Tudor",
     "level": FACILITY_LEVELS[5], "is_national_referral": False,
     "latitude": -4.0435, "longitude": 39.6682},
    {"name": "Jaramogi Oginga Odinga Teaching & Referral Hospital", "county": "Kisumu", "ward": "Kisumu Central",
     "level": FACILITY_LEVELS[5], "is_national_referral": False,
     "latitude": -0.0917, "longitude": 34.7680},

    # Sample Sub-County Hospitals (Level 4) -- illustrative
    {"name": "Naivasha Sub-County Hospital", "county": "Nakuru", "ward": "Naivasha",
     "level": FACILITY_LEVELS[4], "is_national_referral": False,
     "latitude": -0.7172, "longitude": 36.4310},

    # Sample Health Centres (Level 3) -- illustrative
    {"name": "Kijiji Health Centre", "county": "Machakos", "ward": "Machakos Central",
     "level": FACILITY_LEVELS[3], "is_national_referral": False,
     "latitude": -1.5177, "longitude": 37.2634},
    {"name": "Ziwa Health Centre", "county": "Kisumu", "ward": "Kisumu Central",
     "level": FACILITY_LEVELS[3], "is_national_referral": False,
     "latitude": -0.0917, "longitude": 34.7680},

    # Sample Dispensaries/Clinics (Level 2) -- illustrative
    {"name": "Bahari Dispensary", "county": "Mombasa", "ward": "Nyali",
     "level": FACILITY_LEVELS[2], "is_national_referral": False,
     "latitude": -4.0435, "longitude": 39.6682},
    {"name": "Jua Kali Dispensary", "county": "Machakos", "ward": "Kangundo",
     "level": FACILITY_LEVELS[2], "is_national_referral": False,
     "latitude": -1.2833, "longitude": 37.3167},
]

# ---------------------------------------------------------------------------
# Guided self-care programs (style step-by-step journeys)
# ---------------------------------------------------------------------------

CARE_PROGRAMS = [
    {
        "slug": "pregnancy-journey",
        "title": "Pregnancy Journey: Your ANC Path",
        "description": "A step-by-step path through antenatal care, from your first visit to delivery planning.",
        "house_slug": "maternal-child-health",
        "steps": [
            ("Book your first ANC visit", "Go to your nearest health facility as soon as you know you're pregnant — earlier is better, even before 12 weeks."),
            ("Start iron & folic acid supplements", "Ask for these at your first visit if you haven't already started them."),
            ("Get a treated mosquito net", "Ask your facility about a free or subsidized net if you don't already sleep under one."),
            ("Attend ANC visit 2 (around week 20)", "Your health worker will check growth, blood pressure, and answer questions."),
            ("Attend ANC visit 3 (around week 26)", "Discuss your birth plan: which facility, how you'll get there, who will accompany you."),
            ("Attend ANC visit 4 (around week 34)", "Final checks before delivery — confirm your facility and transport plan are ready."),
            ("Pack your delivery bag", "Prepare items for you and the baby ahead of time so you're not rushing when labor starts."),
        ],
    },
    {
        "slug": "child-immunization-journey",
        "title": "Child Immunization Journey",
        "description": "Track your child's vaccinations against Kenya's KEPI schedule, dose by dose.",
        "house_slug": "immunization-schedule",
        "steps": [
            ("Birth: BCG & OPV0", "Given at the facility right after delivery, or within the first days of life."),
            ("6 weeks: 1st doses", "DPT-HepB-Hib 1, OPV1, PCV10 1, Rotavirus 1."),
            ("10 weeks: 2nd doses", "DPT-HepB-Hib 2, OPV2, PCV10 2, Rotavirus 2."),
            ("14 weeks: 3rd doses + IPV", "DPT-HepB-Hib 3, OPV3, PCV10 3, IPV."),
            ("9 months: Measles-Rubella 1 & Yellow Fever", "A key milestone visit — don't skip it even if your child seems healthy."),
            ("18 months: Measles-Rubella 2", "The final routine dose in this schedule."),
        ],
    },
    {
        "slug": "malaria-recovery",
        "title": "Living Well Through Malaria Treatment",
        "description": "What to do from a positive test through to full recovery at home.",
        "house_slug": "malaria",
        "steps": [
            ("Get tested, don't guess", "Confirm malaria with a test at a health facility before starting any medicine."),
            ("Start the full prescribed course", "Take the complete course of antimalarial medicine exactly as directed."),
            ("Manage fever at home", "Use paracetamol as advised, and drink plenty of fluids."),
            ("Watch for danger signs daily", "Confusion, repeated vomiting, or fever not improving after 2 days means go back immediately."),
            ("Finish the course even if you feel better", "Stopping early risks the infection coming back, or resistance developing."),
            ("Prevent the next one", "Sleep under a treated net every night and clear standing water around the home."),
        ],
    },
]

DEMO_USER = {
    "email": "demo@afyakijiji.ke",
    "password": "afyakijiji123",  # local/dev demo only — change or remove for real use
    "role": "family",
}

DEMO_CHV_USER = {
    "email": "chv@afyakijiji.ke",
    "password": "chvdemo123",
    "role": "chv",
}


def seed():
    app = create_app()
    with app.app_context():
        retired = ContentPage.query.filter(ContentPage.slug.in_(RETIRED_SLUGS)).all()
        if retired:
            for page in retired:
                db.session.delete(page)
            print(f"Removed {len(retired)} retired house(s): {', '.join(p.slug for p in retired)}.")

        for page in CONTENT_PAGES:
            existing = ContentPage.query.filter_by(slug=page["slug"]).first()
            if existing:
                for key, value in page.items():
                    setattr(existing, key, value)
            else:
                db.session.add(ContentPage(**page))
        print(f"Synced {len(CONTENT_PAGES)} content pages (houses + CHV resources).")

        for prog in CARE_PROGRAMS:
            existing = CareProgram.query.filter_by(slug=prog["slug"]).first()
            if existing:
                program = existing
                program.title = prog["title"]
                program.description = prog["description"]
                program.house_slug = prog["house_slug"]
                for step in list(program.steps):
                    db.session.delete(step)
            else:
                program = CareProgram(
                    slug=prog["slug"], title=prog["title"],
                    description=prog["description"], house_slug=prog["house_slug"],
                )
                db.session.add(program)
                db.session.flush()  # get program.id for the steps below

            for i, (title, description) in enumerate(prog["steps"]):
                db.session.add(ProgramStep(
                    program_id=program.id, order=i, title=title, description=description
                ))
        print(f"Synced {len(CARE_PROGRAMS)} guided care programs.")

        if not Facility.query.first():
            for fac in FACILITIES:
                db.session.add(Facility(**fac))
            print(f"Seeded {len(FACILITIES)} facilities (2 real national referral hospitals + samples).")
        else:
            print("Facility already has data — skipped (delete afyakijiji.db to reseed).")

        for demo in (DEMO_USER, DEMO_CHV_USER):
            if not User.query.filter_by(email=demo["email"]).first():
                user = User(
                    email=demo["email"],
                    password_hash=generate_password_hash(demo["password"]),
                    role=demo["role"],
                )
                db.session.add(user)
                print(f"Seeded demo user: {demo['email']} / {demo['password']} (role={demo['role']})")
            else:
                print(f"Demo user {demo['email']} already exists — skipped.")

        db.session.commit()


if __name__ == "__main__":
    seed()
