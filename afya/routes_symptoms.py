from flask import Blueprint, render_template, request

symptoms_bp = Blueprint("symptoms", __name__)

FLOW = {
    "start": {
        "question": "What is the main problem?",
        "options": [
            {"label": "Pregnancy-related", "next": "pregnancy"},
            {"label": "Child fever", "next": "child_fever"},
            {"label": "Breathing difficulty", "next": "breathing"},
            {"label": "Possible malaria", "next": "malaria_symptoms"},
            {"label": "Diarrhea", "next": "diarrhea_symptoms"},
            {"label": "Mental health / mood", "next": "mental_health_check"},
        ],
    },
    "pregnancy": {
        "question": "Are you having severe abdominal pain or heavy bleeding?",
        "options": [
            {"label": "Yes", "advice": "Go to the nearest facility immediately."},
            {"label": "No", "advice": "Book an antenatal visit soon and monitor symptoms."},
        ],
    },
    "child_fever": {
        "question": "Is the child unable to drink or very sleepy?",
        "options": [
            {"label": "Yes", "advice": "This is an emergency. Go to a facility now."},
            {"label": "No", "advice": "Give fluids, monitor, and visit a clinic within 24 hours."},
        ],
    },
    "breathing": {
        "question": "Is the person struggling to speak full sentences?",
        "options": [
            {"label": "Yes", "advice": "Call emergency services or go to hospital immediately."},
            {"label": "No", "advice": "Seek medical review today if breathing is still difficult."},
        ],
    },
    "malaria_symptoms": {
        "question": "Fever with confusion, repeated vomiting, or convulsions?",
        "options": [
            {"label": "Yes", "advice": "This is a danger sign. Go to a facility immediately."},
            {"label": "No", "advice": "Get tested for malaria at a health facility before taking any medicine."},
        ],
    },
    "diarrhea_symptoms": {
        "question": "Sunken eyes, very dry mouth, or little/no urine?",
        "options": [
            {"label": "Yes", "advice": "Signs of dehydration. Start ORS now and go to a facility today."},
            {"label": "No", "advice": "Start Oral Rehydration Solution (ORS) and continue feeding. Monitor closely."},
        ],
    },
    "mental_health_check": {
        "question": "Any thoughts of self-harm, or unable to function day to day?",
        "options": [
            {"label": "Yes", "advice": "Please seek help immediately — talk to a health worker or someone you trust right now."},
            {"label": "No", "advice": "Talking to a health worker or counselor at your facility can help. You don't have to manage this alone."},
        ],
    },
}


@symptoms_bp.route("/", methods=["GET", "POST"])
def flow():
    node = request.values.get("node", "start")
    current = FLOW.get(node, FLOW["start"])
    if request.method == "POST":
        # In a real system, log choices, user, timestamp
        pass
    return render_template("page.html", page="symptoms", node=node, data=current)
