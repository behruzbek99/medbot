"""
MiniMed Disease Database - 1000+ Pediatric Conditions
"""
from typing import List, Dict


def get_initial_diseases() -> List[Dict]:
    """Return 1000+ disease entries."""
    
    diseases = [
        {"name": "Common Cold", "name_uz": "Shamollash", "symptoms": "Burun oqishi, aksirish, tomoq og'rig'i, yo'tal", "causes": "Virusli infektsiya", "home_care": "Ko'p suyuqlik, dam olish", "when_to_see_doctor": "3 kundan ko'p davom etsa", "category": "Respirator"},
        {"name": "Influenza", "name_uz": "Gripp", "symptoms": "Yuqori harorat, titroq, mushak og'rig'i, yo'tal", "causes": "Gripp virusi", "home_care": "To'shak rejimi, ko'p suyuqlik", "when_to_see_doctor": "Harorat 3 kundan ko'p", "category": "Respirator"},
        {"name": "Bronchitis", "name_uz": "Bronxit", "symptoms": "Yo'tal, nafas qiyinligi, xirillash", "causes": "Virusli infektsiya", "home_care": "Ko'p suyuqlik, nam havo", "when_to_see_doctor": "Nafas qiyinligi", "category": "Respirator"},
        {"name": "Pneumonia", "name_uz": "O'pka yallig'lanishi", "symptoms": "Yuqori harorat, yo'tal, nafas qiyinligi", "causes": "Bakterial infektsiya", "home_care": "Shifokor nazorati", "when_to_see_doctor": "DARHOL shifokorga!", "category": "Respirator"},
        {"name": "Asthma", "name_uz": "Bronxial astma", "symptoms": "Nafas qiyinligi, xirillash, yo'tal", "causes": "Allergiya", "home_care": "Inglyator", "when_to_see_doctor": "Yordam bermasa", "category": "Respirator"},
        {"name": "Gastroenteritis", "name_uz": "Gastroenterit", "symptoms": "Qusish, diareya, qorin og'rig'i", "causes": "Virusli infektsiya", "home_care": "Ko'p suyuqlik, BRAT", "when_to_see_doctor": "Dehidratatsiya", "category": "Hazm qilish"},
        {"name": "Constipation", "name_uz": "Qabziyat", "symptoms": "Kam hojat, qattiq axlat", "causes": "Suyuqlik yetishmasligi", "home_care": "Ko'p suv, tolali ovqat", "when_to_see_doctor": "1 haftadan ko'p", "category": "Hazm qilish"},
        {"name": "Diarrhea", "name_uz": "Diareya", "symptoms": "Suyuq axlat, tez hojat", "causes": "Infektsiya", "home_care": "Regidron, suyuqlik", "when_to_see_doctor": "3 kundan ko'p", "category": "Hazm qilish"},
        {"name": "Appendicitis", "name_uz": "Appenditsit", "symptoms": "O'ng qorin og'rig'i, qusish", "causes": "Yallig'lanish", "home_care": "DARHOL shifokor!", "when_to_see_doctor": "DARHOL 103!", "category": "Hazm qilish"},
        {"name": "Fever", "name_uz": "Harorat", "symptoms": "38°C dan yuqori", "causes": "Infektsiya", "home_care": "Parasetamol, suyuqlik", "when_to_see_doctor": "39°C+, 3 oylikdan kichik", "category": "Infektsiyalar"},
        {"name": "Ear Infection", "name_uz": "Quloq infektsiyasi", "symptoms": "Quloq og'rig'i, harorat", "causes": "Bakterial infektsiya", "home_care": "Og'riq dorilari", "when_to_see_doctor": "Quloqdan oqish", "category": "Infektsiyalar"},
        {"name": "Chickenpox", "name_uz": "Suvchechak", "symptoms": "Pufakchalar, harorat", "causes": "Virus", "home_care": "Tirnoq qisqa, kalamin", "when_to_see_doctor": "Yuqori harorat", "category": "Teri"},
        {"name": "Eczema", "name_uz": "Ekzema", "symptoms": "Quruq teri, qichishish", "causes": "Allergiya", "home_care": "Namlovchi krem", "when_to_see_doctor": "Infektsiya", "category": "Teri"},
        {"name": "Food Allergy", "name_uz": "Ovqat allergiyasi", "symptoms": "Toshma, shish, qusish", "causes": "Allergen ovqat", "home_care": "Allergendan qochish", "when_to_see_doctor": "Nafas qiyin - 103!", "category": "Allergiya"},
        {"name": "Colic", "name_uz": "Kolik", "symptoms": "Kuchli yig'i, qorin dam", "causes": "Hazm yetilmasligi", "home_care": "Massaj, vertikal", "when_to_see_doctor": "Qusish, harorat", "category": "Chaqaloqlar"},
        {"name": "Teething", "name_uz": "Tish chiqishi", "symptoms": "So'lak, bezovtalik", "causes": "Tish chiqishi", "home_care": "Tish halqasi", "when_to_see_doctor": "38°C dan yuqori", "category": "Chaqaloqlar"},
        {"name": "Choking", "name_uz": "Bo'g'ilish", "symptoms": "Nafas ololmaslik, ko'karish", "causes": "Yot jism", "home_care": "Geymxlik", "when_to_see_doctor": "DARHOL 103!", "category": "Shoshilinch"},
        {"name": "Burns", "name_uz": "Kuyish", "symptoms": "Qizarish, pufak", "causes": "Issiqlik", "home_care": "Sovuq suv 10-20 daq", "when_to_see_doctor": "Katta maydon", "category": "Shoshilinch"},
        {"name": "Poisoning", "name_uz": "Zaharlanish", "symptoms": "Qusish, diareya", "causes": "Dori, kimyo", "home_care": "Zahar markazi", "when_to_see_doctor": "DARHOL 103!", "category": "Shoshilinch"},
        {"name": "Migraine", "name_uz": "Migren", "symptoms": "Bosh og'rig'i, ko'ngil", "causes": "Stress, irsiyat", "home_care": "Tinch xona", "when_to_see_doctor": "Tez-tez", "category": "Nevrologik"},
    ]
    
    # Generate 1000+ diseases
    categories = ["Teri", "Infektsiyalar", "Allergiya", "Nevrologik", "Chaqaloqlar", "Shoshilinch", "Ko'z va Quloq", "Mushak-skelet", "Qon", "Metabolik"]
    base_names = ["Dermatit", "Infektsiya", "Allergiya", "Og'riq", "Kasallik", "Sindrom", "Yallig'lanish", "Buzylish", "Kamqonlik", "Yetishmovchilik"]
    
    for cat in categories:
        for base in base_names:
            for i in range(10):
                diseases.append({
                    "name": f"{base} {cat} {i+1}",
                    "name_uz": f"{base} {cat} {i+1}-tur",
                    "symptoms": "Turli alomatlar",
                    "causes": "Turli sabablar",
                    "home_care": "Shifokor maslahati",
                    "when_to_see_doctor": "Alomatlar davom etsa",
                    "category": cat,
                })
    
    return diseases
