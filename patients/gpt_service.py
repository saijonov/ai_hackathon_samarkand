"""
GPT Service for extracting structured medical data from voice transcripts.
"""
import json
import re
from django.conf import settings

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


# JSON Schema for Patient Registration
PATIENT_SCHEMA = {
    "ism": {"type": "string", "description": "Bemorning to'liq ismi (familiya, ism, otasining ismi)"},
    "yosh": {"type": "integer", "range": "0-150", "description": "Bemorning yoshi"},
    "jins": {"type": "string", "options": ["Erkak", "Ayol"], "description": "Jinsi"},
    "telefon": {"type": "string", "description": "Telefon raqami (+998 formatida)"},
    "manzil": {"type": "string", "description": "Yashash manzili"},
    "qon_guruhi": {"type": "string", "options": ["O(I)", "A(II)", "B(III)", "AB(IV)"], "description": "Qon guruhi"},
    "allergiyalar": {"type": "string", "description": "Allergiyalar (mavjud bo'lsa)"},
    "qand_kasalligi": {"type": "boolean", "description": "Qand kasalligi mavjudmi"},
    "gipertoniya": {"type": "boolean", "description": "Gipertoniya (yuqori qon bosimi) mavjudmi"},
    "yurak_kasalligi": {"type": "boolean", "description": "Yurak kasalligi mavjudmi"},
}


# JSON Schema for Diabetes Protocol
DIABETES_SCHEMA = {
    "pregnancies": {"type": "integer", "range": "0-17", "description": "Homiladorlik soni"},
    "glucose": {"type": "float", "range": "0-200", "description": "Glyukoza darajasi (mg/dL)"},
    "blood_pressure": {"type": "integer", "range": "0-130", "description": "Qon bosimi (mm Hg)"},
    "skin_thickness": {"type": "integer", "range": "0-99", "description": "Teri qalinligi (mm)"},
    "insulin": {"type": "float", "range": "0-850", "description": "Insulin darajasi (mu U/ml)"},
    "bmi": {"type": "float", "range": "0-70", "description": "BMI (Tana massasi indeksi)"},
    "diabetes_pedigree": {"type": "float", "range": "0.0-2.5", "description": "Irsiy omil koeffitsienti"},
    "qon_guruhi": {"type": "string", "options": ["O(I)", "A(II)", "B(III)", "AB(IV)"], "description": "Qon guruhi"},
    "allergiyalar": {"type": "string", "description": "Allergiyalar"},
    "qand_kasalligi": {"type": "boolean", "description": "Qand kasalligi mavjud"},
    "gipertoniya": {"type": "boolean", "description": "Gipertoniya mavjud"},
    "yurak_kasalligi": {"type": "boolean", "description": "Yurak kasalligi mavjud"},
}

# JSON Schema for Heart Disease Protocol
HEART_SCHEMA = {
    "sex": {"type": "integer", "options": [0, 1], "description": "Jins (0=Ayol, 1=Erkak)"},
    "chest_pain_type": {"type": "integer", "options": [0, 1, 2, 3], "description": "Ko'krak og'rig'i turi (0=Asimptomatik, 1=Atipik angina, 2=Angina bo'lmagan, 3=Tipik angina)"},
    "resting_bp": {"type": "integer", "range": "90-200", "description": "Dam olishdagi qon bosimi (mm Hg)"},
    "cholesterol": {"type": "float", "range": "100-600", "description": "Xolesterin (mg/dl)"},
    "fasting_blood_sugar": {"type": "boolean", "description": "Och qorindagi qand > 120 mg/dl"},
    "rest_ecg": {"type": "integer", "options": [0, 1, 2], "description": "Dam olishdagi EKG natijasi (0=Normal, 1=ST-T anormalligi, 2=Chap qorincha gipertrofiyasi)"},
    "max_heart_rate": {"type": "integer", "range": "70-210", "description": "Maksimal yurak urishi"},
    "exercise_angina": {"type": "boolean", "description": "Jismoniy mashqda angina"},
    "oldpeak": {"type": "float", "range": "0.0-6.5", "description": "ST depressiyasi"},
    "slope": {"type": "integer", "options": [0, 1, 2], "description": "ST segment qiyaligi (0=Pastga, 1=Tekis, 2=Yuqoriga)"},
    "num_vessels": {"type": "integer", "range": "0-3", "description": "Asosiy tomirlar soni"},
    "thal": {"type": "integer", "options": [1, 2, 3], "description": "Talassemiya (1=Normal, 2=Tuzatilgan nuqson, 3=Qaytmas nuqson)"},
    "qon_guruhi": {"type": "string", "options": ["O(I)", "A(II)", "B(III)", "AB(IV)"], "description": "Qon guruhi"},
    "allergiyalar": {"type": "string", "description": "Allergiyalar"},
    "qand_kasalligi": {"type": "boolean", "description": "Qand kasalligi mavjud"},
    "gipertoniya": {"type": "boolean", "description": "Gipertoniya mavjud"},
    "yurak_kasalligi": {"type": "boolean", "description": "Yurak kasalligi mavjud"},
}


def get_schema_for_protocol(protocol_type):
    """Get the appropriate schema based on protocol type"""
    if protocol_type == 'diabetes':
        return DIABETES_SCHEMA
    elif protocol_type == 'heart':
        return HEART_SCHEMA
    return {}


def create_gpt_prompt(protocol_type, transcript):
    """Create a detailed prompt for GPT to extract medical data from transcript"""
    schema = get_schema_for_protocol(protocol_type)

    schema_description = json.dumps(schema, indent=2, ensure_ascii=False)

    prompt = f"""Sen tibbiy ma'lumotlarni ajratib oluvchi AI assistantisin.
Quyidagi shifokor-bemor suhbati transkriptidan tibbiy ma'lumotlarni JSON formatida ajratib ol.

PROTOCOL TURI: {"Qand kasalligi (Diabetes)" if protocol_type == 'diabetes' else "Yurak kasalligi (Heart Disease)"}

JSON SCHEMA (maydonlar va ularning turlari):
{schema_description}

MUHIM QOIDALAR:
1. Faqat transkriptda aytilgan ma'lumotlarni qo'sh
2. Agar ma'lumot topilmasa, o'sha maydonni null qilib qoldir
3. Raqamlarni to'g'ri formatda qo'sh (integer yoki float)
4. Boolean qiymatlarni true/false qilib yoz
5. Faqat JSON formatida javob ber, boshqa hech narsa yozma
6. O'zbek tilida aytilgan raqamlarni ham tushuning (masalan: "yuz yigirma" = 120)

TRANSKRIPT:
{transcript}

JAVOB (faqat JSON):"""

    return prompt


def extract_json_from_response(response_text):
    """Extract JSON from GPT response, handling potential formatting issues"""
    # Try to find JSON in the response
    json_match = re.search(r'\{[\s\S]*\}', response_text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    # Try direct parsing
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    return {}


def extract_medical_data_from_transcript(protocol_type, transcript):
    """
    Use GPT to extract medical data from a voice transcript.
    Returns a dictionary with extracted fields.
    """
    if not OPENAI_AVAILABLE:
        return {"error": "OpenAI library not installed. Run: pip install openai"}

    api_key = getattr(settings, 'OPENAI_API_KEY', '')
    if not api_key:
        return {"error": "OpenAI API key not configured in settings"}

    try:
        client = OpenAI(api_key=api_key)

        prompt = create_gpt_prompt(protocol_type, transcript)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Sen tibbiy ma'lumotlarni JSON formatida ajratib oluvchi AI assistantisin. Faqat JSON formatida javob ber."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=1000
        )

        response_text = response.choices[0].message.content.strip()
        extracted_data = extract_json_from_response(response_text)

        # Validate and clean the extracted data
        schema = get_schema_for_protocol(protocol_type)
        cleaned_data = {}

        for key, value in extracted_data.items():
            if key in schema and value is not None:
                field_info = schema[key]

                # Type conversion and validation
                if field_info['type'] == 'integer' and value is not None:
                    try:
                        cleaned_data[key] = int(value)
                    except (ValueError, TypeError):
                        pass
                elif field_info['type'] == 'float' and value is not None:
                    try:
                        cleaned_data[key] = float(value)
                    except (ValueError, TypeError):
                        pass
                elif field_info['type'] == 'boolean':
                    if isinstance(value, bool):
                        cleaned_data[key] = value
                    elif isinstance(value, str):
                        cleaned_data[key] = value.lower() in ('true', 'ha', 'bor', '1', 'yes')
                elif field_info['type'] == 'string':
                    cleaned_data[key] = str(value) if value else None

        return cleaned_data

    except Exception as e:
        return {"error": str(e)}


def get_empty_schema_json(protocol_type):
    """Return an empty JSON structure for the protocol type (for manual filling)"""
    schema = get_schema_for_protocol(protocol_type)
    return {key: None for key in schema.keys()}


def extract_patient_data_from_transcript(transcript):
    """
    Use GPT to extract patient registration data from a voice transcript.
    Returns a dictionary with extracted fields.
    """
    if not OPENAI_AVAILABLE:
        return {"error": "OpenAI library not installed. Run: pip install openai"}

    api_key = getattr(settings, 'OPENAI_API_KEY', '')
    if not api_key:
        return {"error": "OpenAI API key not configured in settings"}

    try:
        client = OpenAI(api_key=api_key)

        schema_description = json.dumps(PATIENT_SCHEMA, indent=2, ensure_ascii=False)

        prompt = f"""Sen tibbiy ma'lumotlarni ajratib oluvchi AI assistantisin.
Quyidagi shifokor-bemor suhbati transkriptidan bemor ro'yxatga olish ma'lumotlarini JSON formatida ajratib ol.

JSON SCHEMA (maydonlar va ularning turlari):
{schema_description}

MUHIM QOIDALAR:
1. Faqat transkriptda aytilgan ma'lumotlarni qo'sh
2. Agar ma'lumot topilmasa, o'sha maydonni null qilib qoldir
3. Raqamlarni to'g'ri formatda qo'sh (integer yoki float)
4. Boolean qiymatlarni true/false qilib yoz
5. Faqat JSON formatida javob ber, boshqa hech narsa yozma
6. O'zbek tilida aytilgan raqamlarni ham tushuning (masalan: "yigirma besh yoshda" = 25)
7. Telefon raqamini +998 formatida yoz
8. Ismni to'liq yoz (familiya, ism, otasining ismi)
9. "Ha", "bor", "mavjud" kabi so'zlar true, "yo'q", "mavjud emas" kabi so'zlar false
10. Jinsi uchun "erkak"/"ayol" yoki "er/xotin" degan so'zlarni Erkak/Ayol ga o'gir

TRANSKRIPT:
{transcript}

JAVOB (faqat JSON):"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Sen tibbiy ma'lumotlarni JSON formatida ajratib oluvchi AI assistantisin. Faqat JSON formatida javob ber."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=1000
        )

        response_text = response.choices[0].message.content.strip()
        extracted_data = extract_json_from_response(response_text)

        # Validate and clean the extracted data
        cleaned_data = {}

        for key, value in extracted_data.items():
            if key in PATIENT_SCHEMA and value is not None:
                field_info = PATIENT_SCHEMA[key]

                # Type conversion and validation
                if field_info['type'] == 'integer' and value is not None:
                    try:
                        cleaned_data[key] = int(value)
                    except (ValueError, TypeError):
                        pass
                elif field_info['type'] == 'float' and value is not None:
                    try:
                        cleaned_data[key] = float(value)
                    except (ValueError, TypeError):
                        pass
                elif field_info['type'] == 'boolean':
                    if isinstance(value, bool):
                        cleaned_data[key] = value
                    elif isinstance(value, str):
                        cleaned_data[key] = value.lower() in ('true', 'ha', 'bor', '1', 'yes', 'mavjud')
                elif field_info['type'] == 'string':
                    cleaned_data[key] = str(value) if value else None

        return cleaned_data

    except Exception as e:
        return {"error": str(e)}
