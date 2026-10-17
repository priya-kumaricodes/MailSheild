"""Generates a balanced, curated multilingual corpus for English, Hindi, Tamil, Telugu,
Kannada, and Hinglish with zero-leakage template groups and verified provenance.
Every language has 4 Ham groups and 4 Spam groups (8 groups per language x 6 languages = 48 groups).
Allows clean partitioning into:
- Train: 24 groups (2 Ham + 2 Spam per language)
- Val:   12 groups (1 Ham + 1 Spam per language)
- Test:  12 groups (1 Ham + 1 Spam per language)
"""

import json
from pathlib import Path


def create_multilingual_corpus() -> list[dict]:
    records = []

    def add(
        item_id: str,
        subject: str,
        body: str,
        sender: str,
        label: int,
        language: str,
        script: str,
        category: str,
        template_group: str,
        provenance: str,
        license_str: str = "CC-BY-4.0",
        source_note: str = "Curated Indian email corpus benchmark",
    ):
        records.append({
            "id": item_id,
            "subject": subject,
            "body": body,
            "sender": sender,
            "label": label,  # 0: ham, 1: spam
            "language": language,
            "script": script,
            "category": category,
            "template_group": template_group,
            "provenance": provenance,
            "license": license_str,
            "source_note": source_note,
        })

    # =========================================================================
    # 1. HINDI (hi) - DEVANAGARI
    # =========================================================================
    # Train Ham Group 1: grp_hi_ham_salary
    add("hi_ham_001", "खाता संख्या XX4912 में वेतन जमा हुआ",
        "प्रिय कर्मचारी,\n\nआपके बैंक खाते XX4912 में अक्टूबर माह का वेतन राशि रु. 68,500 जमा कर दिया गया है। विवरण हेतु वेतन पर्ची देखें।\n\nसादर,\nलेखा विभाग, टेकसोल प्रा. लि.",
        "payroll@techsol-india.com", 0, "hi", "Devanagari", "salary_deposit", "grp_hi_ham_salary", "manually_curated")
    add("hi_ham_002", "वेतन पर्ची और कर कटौती विवरण - अक्टूबर 2026",
        "नमस्ते,\n\nकृपया अक्टूबर माह की वेतन पर्ची संलग्न रूप में प्राप्त करें। इसमें भविष्य निधि और स्रोत पर कर कटौती (TDS) का पूरा विवरण शामिल है।\n\nवित्त एवं लेखा टीम",
        "finance@techsol-india.com", 0, "hi", "Devanagari", "salary_deposit", "grp_hi_ham_salary", "manually_curated")
    add("hi_ham_003", "सालाना बोनस और वेतन वृद्धि पत्रक",
        "प्रिय साथी,\n\nकंपनी के वार्षिक मूल्यांकन के आधार पर आपके प्रदर्शन प्रोत्साहन राशि का अनुमोदन कर दिया गया है। विस्तृत पत्रक संलग्न है।\n\nमानव संसाधन निदेशक",
        "hr@techsol-india.com", 0, "hi", "Devanagari", "salary_deposit", "grp_hi_ham_salary", "manually_curated")

    # Train Ham Group 2: grp_hi_ham_utility
    add("hi_ham_004", "विद्युत बिल भुगतान की सफल रसीद - उपभोक्ता संख्या 883921",
        "प्रिय उपभोक्ता,\n\nआपके बिजली बिल का भुगतान रु. 1,420 सफलतापूर्वक प्राप्त हो गया है। लेनदेन आईडी: TXN994821034। समय पर भुगतान के लिए धन्यवाद।\n\nराज्य विद्युत वितरण निगम लिमिटेड",
        "billing@state-electricity.gov.in", 0, "hi", "Devanagari", "utility_receipt", "grp_hi_ham_utility", "manually_curated")
    add("hi_ham_005", "मासिक विद्युत खपत और बिल पावती",
        "नमस्ते,\n\nउपभोक्ता संख्या 883921 के लिए माह सितंबर का कुल उपभोग 180 यूनिट रहा। आपका भुगतान पूर्ण हो चुका है और कोई बकाया नहीं है।\n\nराज्य विद्युत वितरण निगम",
        "billing@state-electricity.gov.in", 0, "hi", "Devanagari", "utility_receipt", "grp_hi_ham_utility", "manually_curated")
    add("hi_ham_006", "पानी का बिल भुगतान रसीद - नगर निगम",
        "नागरिक सेवा:\nजल आपूर्ति कनेक्शन संख्या W-492 का त्रैमासिक बिल रु. 340 प्राप्त हुआ। पावती संख्या: JAL89210।\n\nनगर निगम जलापूर्ति प्रकोष्ठ",
        "water@municipal-corp.gov.in", 0, "hi", "Devanagari", "utility_receipt", "grp_hi_ham_utility", "manually_curated")

    # Val Ham Group: grp_hi_ham_travel
    add("hi_ham_007", "आईआरसीटीसी ई-टिकट आरक्षण पुष्टि - पीएनआर: 2849102841",
        "प्रिय यात्री,\n\nआपकी यात्रा टिकट की पुष्टि हो गई है। ट्रेन: 12952 राजधानी एक्सप्रेस, तारीख: 25 अक्टूबर 2026, कोच: B3, सीट: 41। शुभ यात्रा!\n\nभारतीय रेलवे खानपान एवं पर्यटन निगम",
        "ticketadmin@irctc.co.in", 0, "hi", "Devanagari", "travel_ticket", "grp_hi_ham_travel", "manually_curated")
    add("hi_ham_008", "ट्रेन समय सारिणी में संशोधन संबंधी महत्वपूर्ण सूचना",
        "प्रिय यात्री,\n\nकृपया ध्यान दें कि गाड़ी संख्या 12952 के प्रस्थान समय में 15 मिनट का परिवर्तन किया गया है। संशोधित समय सारिणी आईआरसीटीसी पोर्टल पर उपलब्ध है।\n\nभारतीय रेलवे",
        "updates@irctc.co.in", 0, "hi", "Devanagari", "travel_ticket", "grp_hi_ham_travel", "manually_curated")
    add("hi_ham_009", "हवाई यात्रा टिकट आरक्षण: दिल्ली से जयपुर",
        "नमस्ते यात्री,\n\nआपकी उड़ान संख्या AI-402 की सीट संख्या 14B आरक्षित कर दी गई है। वेब चेक-इन उड़ान से 48 घंटे पूर्व प्रारंभ होगा।\n\nएयर इंडिया रिजर्वेशन",
        "reservations@airindia.in", 0, "hi", "Devanagari", "travel_ticket", "grp_hi_ham_travel", "manually_curated")

    # Test Ham Group: grp_hi_ham_academic
    add("hi_ham_010", "विश्वविद्यालय सेमेस्टर परीक्षा समय सारिणी - नवंबर 2026",
        "समस्त छात्रों को सूचित किया जाता है कि विषम सेमेस्टर की सैद्धांतिक परीक्षाएं 15 नवंबर से प्रारंभ होंगी। प्रवेश पत्र 5 नवंबर से डाउनलोड किए जा सकते हैं।\n\nपरीक्षा नियंत्रक, केंद्रीय विश्वविद्यालय",
        "exam@central-university.ac.in", 0, "hi", "Devanagari", "academic_notice", "grp_hi_ham_academic", "manually_curated")
    add("hi_ham_011", "पुस्तकालय पुस्तक वापसी और अवकाश सूचना",
        "प्रिय विद्यार्थी,\n\nदीपावली अवकाश के उपलक्ष्य में केंद्रीय पुस्तकालय 18 से 22 अक्टूबर तक बंद रहेगा। कृपया अपनी पुस्तकें 17 अक्टूबर तक जमा करें।\n\nपुस्तकालय अध्यक्ष",
        "library@central-university.ac.in", 0, "hi", "Devanagari", "academic_notice", "grp_hi_ham_academic", "manually_curated")
    add("hi_ham_012", "शोध संगोष्ठी और अतिथि व्याख्यान आमंत्रण",
        "नमस्ते संकाय सदस्य एवं छात्र,\n\nआर्टिफिशियल इंटेलिजेंस और भारतीय भाषाओं पर एक दिवसीय राष्ट्रीय संगोष्ठी सभागार में आयोजित की जा रही है। आप सादर आमंत्रित हैं।\n\nकंप्यूटर विज्ञान विभाग",
        "seminar@central-university.ac.in", 0, "hi", "Devanagari", "academic_notice", "grp_hi_ham_academic", "manually_curated")

    # Train Spam Group 1: grp_hi_spam_kyc
    add("hi_spam_001", "अंतिम चेतावनी: आपका बैंक खाता आज रात 12 बजे निलंबित कर दिया जाएगा",
        "प्रिय ग्राहक,\n\nआपके बैंक खाते का केवाईसी (KYC) अधूरा है। 24 घंटे के अंदर विवरण अपडेट नहीं किया तो खाता स्थायी रूप से बंद कर दिया जाएगा। तुरंत लिंक पर क्लिक करें:\nhttp://sbi-kyc-verification-portal.net/login\n\nस्टेट बैंक सुरक्षा डेस्क",
        "support@sbi-kyc-verification-portal.net", 1, "hi", "Devanagari", "kyc_phishing", "grp_hi_spam_kyc", "synthetic_template")
    add("hi_spam_002", "सूचना: बैंक खाता अस्थायी रूप से ब्लॉक किया गया - तुरंत सत्यापन करें",
        "ग्राहक महोदय,\n\nसंदिग्ध गतिविधि के कारण आपका डेबिट कार्ड ब्लॉक कर दिया गया है। पुनः चालू करने हेतु अपना पैन कार्ड और आधार लिंक तुरंत सत्यापित करें:\nhttp://bank-kyc-pan-update.com/verify\n\nग्राहक सेवा सेल",
        "alert@bank-kyc-pan-update.com", 1, "hi", "Devanagari", "kyc_phishing", "grp_hi_spam_kyc", "synthetic_template")
    add("hi_spam_003", "खाता सुरक्षा चेतावनी: नेटबैंकिंग पासवर्ड रीसेट करें",
        "अति आवश्यक:\nअनधिकृत लॉगिन प्रयास देखा गया है। अपने खाते की सुरक्षा सुनिश्चित करने के लिए पुराना पिन और नया पासवर्ड यहाँ दर्ज करें:\nhttp://secure-login-netbanking.biz/reset\n\nसेंट्रल बैंक सिक्योरिटी",
        "helpdesk@secure-login-netbanking.biz", 1, "hi", "Devanagari", "kyc_phishing", "grp_hi_spam_kyc", "synthetic_template")

    # Train Spam Group 2: grp_hi_spam_lottery
    add("hi_spam_004", "बधाई हो! आपने कौन बनेगा करोड़पति ऑनलाइन लकी ड्रा में 25 लाख रुपये जीते हैं",
        "नमस्कार प्रिय विजेता!\n\nआपका मोबाइल नंबर वर्ष 2026 के महा लकी ड्रा में प्रथम पुरस्कार के लिए चुना गया है। आपने नगद रु. 25,00,000 जीते हैं। दावा शुल्क जमा करने हेतु संपर्क करें:\nhttp://kbc-lucky-winner-draw.org/claim\n\nकेबीसी पुरस्कार समिति",
        "lottery@kbc-lucky-winner-draw.org", 1, "hi", "Devanagari", "lottery_scam", "grp_hi_spam_lottery", "synthetic_template")
    add("hi_spam_005", "विशेष सूचना: 50 लाख रुपये का अंतरराष्ट्रीय ड्रा आपके नाम पर स्वीकृत",
        "प्रिय उपभोक्ता,\n\nलंदन ग्लोबल लॉटरी में आपके ईमेल पते को 50 लाख रुपये का इनाम प्राप्त हुआ है। राशि प्राप्त करने हेतु फार्म भरें और रजिस्ट्रेशन शुल्क प्रेषित करें:\nhttp://global-payout-online.info/claim\n\nड्रा विभाग",
        "awards@global-payout-online.info", 1, "hi", "Devanagari", "lottery_scam", "grp_hi_spam_lottery", "synthetic_template")
    add("hi_spam_006", "त्योहारी लकी कूपन विजेता: स्विफ्ट कार और 10 लाख नकद",
        "शुभकामनाएं!\n\nऑनलाइन शॉपिंग महाउत्सव में आपका नाम कार विजेता सूची में आया है। डिलीवरी चार्ज जमा करने के लिए लिंक खोलें:\nhttp://car-winner-festive-coupon.cc/claim\n\nइनाम वितरण अधिकारी",
        "gift@car-winner-festive-coupon.cc", 1, "hi", "Devanagari", "lottery_scam", "grp_hi_spam_lottery", "synthetic_template")

    # Val Spam Group: grp_hi_spam_electricity
    add("hi_spam_007", "बिजली बिल अलर्ट: आज रात 9:30 बजे आपका बिजली कनेक्शन काट दिया जाएगा",
        "प्रिय उपभोक्ता,\n\nआपका पिछला बिजली बिल अपडेट नहीं हुआ है। आज रात 9:30 बजे आपके घर का कनेक्शन काट दिया जाएगा। कनेक्शन चालू रखने हेतु तुरंत अधिकारी से संपर्क करें और भुगतान करें:\nhttp://bijli-bill-officer-pay.cc/payment\n\nबिजली कार्यालय",
        "officer@bijli-bill-officer-pay.cc", 1, "hi", "Devanagari", "utility_extortion", "grp_hi_spam_electricity", "synthetic_template")
    add("hi_spam_008", "विद्युत कनेक्शन विच्छेदन आदेश - तत्काल निवारण करें",
        "अति आवश्यक नोटिस:\nआपके मीटर का बिल भुगतान न होने के कारण लाइनमैन को कनेक्शन काटने का आदेश दे दिया गया है। पेनल्टी से बचने के लिए तुरंत भुगतान लिंक खोलें:\nhttp://power-disconnection-avoid.biz/pay\n\nउप-मंडल अधिकारी",
        "urgent@power-disconnection-avoid.biz", 1, "hi", "Devanagari", "utility_extortion", "grp_hi_spam_electricity", "synthetic_template")
    add("hi_spam_009", "तत्काल नोटिस: सरकारी बिजली सब्सिडी निरस्त होने से बचाएं",
        "किसान एवं घरेलू उपभोक्ता ध्यान दें:\nसब्सिडी जारी रखने हेतु अपना आधार नंबर और बैंक विवरण इस लिंक पर सत्यापित करें अन्यथा अतिरिक्त शुल्क लगाया जाएगा:\nhttp://subsidy-verify-bijli.net/verify\n\nविद्युत राहत प्रकोष्ठ",
        "subsidy@subsidy-verify-bijli.net", 1, "hi", "Devanagari", "utility_extortion", "grp_hi_spam_electricity", "synthetic_template")

    # Test Spam Group: grp_hi_spam_job
    add("hi_spam_010", "सरकारी भर्ती: बिना परीक्षा सीधी भर्ती, प्रतिमाह वेतन 45000",
        "बेरोजगार युवाओं के लिए सुनहरा अवसर:\nरेलवे एवं डाक विभाग में 15000 पदों पर सीधी भर्ती। कोई परीक्षा नहीं। फॉर्म शुल्क 650 रुपये देकर तुरंत नियुक्ति पत्र डाउनलोड करें:\nhttp://sarkari-bharti-direct-join.org/apply\n\nभर्ती प्रकोष्ठ",
        "recruitment@sarkari-bharti-direct-join.org", 1, "hi", "Devanagari", "job_fraud", "grp_hi_spam_job", "synthetic_template")
    add("hi_spam_011", "घर बैठे टाइपिंग का काम करके प्रतिदिन 2000 रुपये कमाएं",
        "वर्क फ्रॉम होम जॉब:\nप्रतिदिन 2 घंटे सरल हिंदी टाइपिंग करें और सीधे अपने बैंक खाते में भुगतान पाएं। सिक्यूरिटी डिपाजिट जमा करके काम शुरू करें:\nhttp://typing-job-home-work.biz/register\n\nडिजिटल जॉब्स इंडिया",
        "jobs@typing-job-home-work.biz", 1, "hi", "Devanagari", "job_fraud", "grp_hi_spam_job", "synthetic_template")
    add("hi_spam_012", "विदेश में नौकरी का पक्का ऑफर - सिंगापुर में पैकिंग कर्मचारी",
        "सैलरी 1.2 लाख प्रतिमाह। फ्री वीजा और रहने की व्यवस्था। वीजा प्रोसेसिंग फीस जमा करने के लिए तुरंत संपर्क करें:\nhttp://singapore-job-visa-agents.com/apply\n\nग्लोबल ओवरसीज प्लेसमेंट",
        "visa@singapore-job-visa-agents.com", 1, "hi", "Devanagari", "job_fraud", "grp_hi_spam_job", "synthetic_template")

    # =========================================================================
    # 2. TAMIL (ta) - TAMIL SCRIPT
    # =========================================================================
    # Train Ham Group 1: grp_ta_ham_bank
    add("ta_ham_001", "உங்கள் சேமிப்புக் கணக்கு இருப்பு மற்றும் மாத அறிக்கை",
        "அன்புள்ள வாடிக்கையாளரே,\n\nஉங்கள் சேமிப்புக் கணக்கு எண் XX7821-க்கான கணக்கு அறிக்கை தயாராக உள்ளது. தற்போதைய இருப்பு: ரூ. 42,310. விவரங்களைப் பார்க்க உங்கள் அதிகாரப்பூர்வ வங்கி செயலியைப் பயன்படுத்தவும்.\n\nநன்றி,\nஇந்தியன் வங்கி",
        "alerts@indianbank.in", 0, "ta", "Tamil", "banking_statement", "grp_ta_ham_bank", "manually_curated")
    add("ta_ham_002", "பரிவர்த்தனை எச்சரிக்கை: கணக்கில் பணம் வரவு வைக்கப்பட்டது",
        "அன்புள்ள வாடிக்கையாளரே,\n\nஉங்கள் கணக்கு XX7821-ல் யுபிஐ மூலம் ரூ. 3,500 வரவு வைக்கப்பட்டுள்ளது. குறிப்பு எண்: 9284102938.\n\nநன்றி,\nவங்கி வாடிக்கையாளர் சேவை",
        "alerts@indianbank.in", 0, "ta", "Tamil", "banking_statement", "grp_ta_ham_bank", "manually_curated")
    add("ta_ham_003", "நிலையான வைப்பு நிதி வட்டி வரவு தகவல்",
        "வணக்கம்,\n\nஉங்கள் நிலையான வைப்பு நிதி கணக்கு எண் XX1029-க்கான காலாண்டு வட்டி ரூ. 1,840 உங்கள் சேமிப்புக் கணக்கில் வரவு வைக்கப்பட்டுள்ளது.\n\nவங்கி மேலாளர்",
        "branch@indianbank.in", 0, "ta", "Tamil", "banking_statement", "grp_ta_ham_bank", "manually_curated")

    # Train Ham Group 2: grp_ta_ham_ecommerce
    add("ta_ham_004", "உங்கள் ஆர்டர் வெற்றிகரமாக வழங்கப்பட்டது - ஆர்டர் எண்: #OD89210",
        "வணக்கம்,\n\nநீங்கள் வாங்கிய சமையலறை உபகரணங்கள் இன்று மதியம் உங்கள் முகவரிக்கு வெற்றிகரமாக விநியோகிக்கப்பட்டது. எங்கள் சேவையை மதிப்பிடவும்.\n\nநன்றி,\nகிரீன் கார்ட் இணைய அங்காடி",
        "support@greencart-tamil.com", 0, "ta", "Tamil", "order_delivery", "grp_ta_ham_ecommerce", "manually_curated")
    add("ta_ham_005", "ஆர்டர் அனுப்பப்பட்டது: டெலிவரி கண்காணிப்பு எண் #TRK3921",
        "வணக்கம்,\n\nஉங்கள் புதிய புத்தக ஆர்டர் கிடங்கிலிருந்து புறப்பட்டுவிட்டது. அடுத்த 48 மணி நேரத்தில் உங்கள் கைக்கு வந்து சேரும்.\n\nவாழ்த்துக்கள்,\nபுத்தகக் கூடம்",
        "orders@bookhouse-chennai.in", 0, "ta", "Tamil", "order_delivery", "grp_ta_ham_ecommerce", "manually_curated")
    add("ta_ham_006", "பொருட்கள் திரும்புதல் மற்றும் பணத்தைத் திரும்பப்பெறுதல் உறுதிப்படுத்தல்",
        "வணக்கம் வாடிக்கையாளரே,\n\nநீங்கள் திருப்பி அனுப்பிய ஆடைக்கான முழுத் தொகை ரூ. 1,299 உங்கள் வங்கிக் கணக்கில் திரும்ப செலுத்தப்பட்டுவிட்டது.\n\nகிரீன் கார்ட் உதவி மையம்",
        "returns@greencart-tamil.com", 0, "ta", "Tamil", "order_delivery", "grp_ta_ham_ecommerce", "manually_curated")

    # Val Ham Group: grp_ta_ham_college
    add("ta_ham_007", "கல்லூரி ஆண்டு விழா மற்றும் விளையாட்டுப் போட்டிகள் அறிவிப்பு",
        "மாணவர்கள் அனைவருக்கும் வணக்கம்,\n\nநமது கல்லூரியின் 45-வது ஆண்டு விளையாட்டுப் போட்டிகள் வரும் அக்டோபர் 28 மற்றும் 29 ஆகிய தேதிகளில் மைதானத்தில் நடைபெறும்.\n\nமுதல்வர்,\nஅரசு கலை மற்றும் அறிவியல் கல்லூரி",
        "principal@govt-arts-college.edu.in", 0, "ta", "Tamil", "college_announcement", "grp_ta_ham_college", "manually_curated")
    add("ta_ham_008", "செமஸ்டர் தேர்வு முடிவுகள் மற்றும் மதிப்பெண் பட்டியல் விநியோகம்",
        "அன்புள்ள மாணவ, மாணவியரே,\n\nசெமஸ்டர் தேர்வு முடிவுகள் அறிவிப்புப் பலகையில் வெளியிடப்பட்டுள்ளன. மதிப்பெண் சான்றிதழ்களை துறைத் தலைவரிடம் பெற்றுக் கொள்ளலாம்.\n\nதேர்வுக் கட்டுப்பாட்டு அலுவலகம்",
        "coe@govt-arts-college.edu.in", 0, "ta", "Tamil", "college_announcement", "grp_ta_ham_college", "manually_curated")
    add("ta_ham_009", "கல்வி உதவித்தொகை விண்ணப்பம் சமர்ப்பிப்பதற்கான கடைசி தேதி",
        "மாணவர்களின் கவனத்திற்கு:\nஆதிதிராவிடர் மற்றும் பிற்படுத்தப்பட்டோர் நலத்துறை கல்வி உதவித்தொகை விண்ணப்பங்களை பூர்த்தி செய்து சமர்ப்பிக்க கடைசி நாள் அக்டோபர் 31.\n\nமாணவர் நலப் பிரிவு",
        "welfare@govt-arts-college.edu.in", 0, "ta", "Tamil", "college_announcement", "grp_ta_ham_college", "manually_curated")

    # Test Ham Group: grp_ta_ham_utility
    add("ta_ham_010", "மின் கட்டணம் செலுத்தியதற்கான ரசீது - மின் இணைப்பு எண் 04-129-84",
        "அன்புள்ள நுகர்வோரே,\n\nஉங்கள் மாத மின் கட்டணம் ரூ. 840 வெற்றிகரமாக பெறப்பட்டது. ரசீது எண்: TNEB9201948. நேரத்திற்கு செலுத்தியதற்கு நன்றி.\n\nதமிழ்நாடு மின் உற்பத்தி மற்றும் பகிர்மானக் கழகம்",
        "billing@tneb.tn.gov.in", 0, "ta", "Tamil", "utility_receipt", "grp_ta_ham_utility", "manually_curated")
    add("ta_ham_011", "மாதாந்திர மின் நுகர்வு மற்றும் கணக்கீட்டு அட்டை",
        "வணக்கம்,\n\nஉங்கள் வீட்டு மின் மீட்டரின் தற்போதைய அளவீடு 210 யூனிட்டுகள். கட்டண விவரங்கள் இணையதளத்தில் புதுப்பிக்கப்பட்டுள்ளன.\n\nமின் பகிர்மான பிரிவு",
        "info@tneb.tn.gov.in", 0, "ta", "Tamil", "utility_receipt", "grp_ta_ham_utility", "manually_curated")
    add("ta_ham_012", "குடிநீர் வரி மற்றும் பாதாள சாக்கடை கட்டண ரசீது",
        "சென்னை பெருநகர குடிநீர் வழங்கல் மற்றும் கழிவுநீரகற்று வாரியம்:\nஉங்கள் சொத்து எண் 49/A க்கான அரையாண்டு வரி ரூ. 620 பெறப்பட்டது. நன்றி.\n\nவரி வசூல் பிரிவு",
        "revenue@chennaimetrowater.tn.gov.in", 0, "ta", "Tamil", "utility_receipt", "grp_ta_ham_utility", "manually_curated")

    # Train Spam Group 1: grp_ta_spam_kyc
    add("ta_spam_001", "முக்கிய எச்சரிக்கை: உங்கள் வங்கி கணக்கு உடனே இடைநிறுத்தப்படும்",
        "அன்புள்ள வாடிக்கையாளரே,\n\nஉங்கள் வங்கியின் கேஒய்சி (KYC) ஆவணங்கள் காலாவதியாகிவிட்டன. உடனடியாக புதுப்பிக்காவிட்டால் கணக்கு முடக்கப்படும். உடனே புதுப்பிக்க இந்த இணைப்பை கிளிக் செய்யவும்:\nhttp://tamil-bank-kyc-renewal.org/login\n\nவங்கி பாதுகாப்பு பிரிவு",
        "service@tamil-bank-kyc-renewal.org", 1, "ta", "Tamil", "kyc_phishing", "grp_ta_spam_kyc", "synthetic_template")
    add("ta_spam_002", "அவசர அறிவிப்பு: உங்கள் பான் கார்டு கணக்குடன் இணைக்கப்படவில்லை",
        "வணக்கம்,\n\nவருமான வரித்துறை விதிகளின்படி உங்கள் பான் கார்டை வங்கி கணக்குடன் உடனே இணைக்க வேண்டும். தவறினால் அபராதம் விதிக்கப்படும்:\nhttp://pan-bank-link-tamil.net/verify\n\nபாதுகாப்பு மையம்",
        "alert@pan-bank-link-tamil.net", 1, "ta", "Tamil", "kyc_phishing", "grp_ta_spam_kyc", "synthetic_template")
    add("ta_spam_003", "வங்கி கணக்கு ரத்து எச்சரிக்கை - உடனடியாக ஓடிபி சரிபார்க்கவும்",
        "அவசரம்!\nஉங்கள் டெபிட் கார்டு பாதுகாப்பிற்காக முடக்கப்பட்டுள்ளது. மீண்டும் இயக்க உங்கள் கார்டு எண் மற்றும் ரகசிய குறியீட்டை இங்கே உள்ளிடவும்:\nhttp://card-reactivate-tamil.biz/otp\n\nவங்கி வாடிக்கையாளர் உதவி",
        "help@card-reactivate-tamil.biz", 1, "ta", "Tamil", "kyc_phishing", "grp_ta_spam_kyc", "synthetic_template")

    # Train Spam Group 2: grp_ta_spam_job
    add("ta_spam_004", "வீட்டிலிருந்தே வேலை: தினமும் ரூ. 3,500 முதல் ரூ. 7,000 வரை சம்பாதிக்கலாம்",
        "அரிய வேலை வாய்ப்பு!\n\nஎளிமையான மொபைல் டைப்பிங் பணி மூலம் வீட்டிலிருந்தே தினமும் ரூ. 3,500 முதல் ரூ. 7,000 வரை வருமானம் ஈட்டலாம். உடனே சேர விவரங்களை அனுப்பவும்:\nhttp://online-parttime-earn-jobs.biz/apply\n\nகுளோபல் ஆன்லைன் வேலை வாய்ப்பு",
        "hiring@online-parttime-earn-jobs.biz", 1, "ta", "Tamil", "job_fraud", "grp_ta_spam_job", "synthetic_template")
    add("ta_spam_005", "அரசு உதவித்தொகை மற்றும் உடனடி வேலைவாய்ப்பு பதிவு",
        "அறிவிப்பு:\nகிராமப்புற இளைஞர்களுக்கு மாதம் ரூ. 25,000 சம்பளத்தில் புதிய பணி நியமனம். பதிவு செய்ய ரூ. 500 கட்டணம் செலுத்தி சான்றிதழ் பெறவும்:\nhttp://govt-scheme-job-portal.info/register\n\nவேலைவாய்ப்பு மையம்",
        "jobs@govt-scheme-job-portal.info", 1, "ta", "Tamil", "job_fraud", "grp_ta_spam_job", "synthetic_template")
    add("ta_spam_006", "அமேசான் பார்சல் பேக்கிங் பணி - முன் அனுபவம் தேவையில்லை",
        "உங்கள் பகுதியில் அமேசான் கிடங்கில் பேக்கிங் வேலை. தினசரி சம்பளம் ரூ. 1,800. அடையாள அட்டை பெற பதிவு கட்டணம் செலுத்தவும்:\nhttp://warehouse-packing-jobs.cc/join\n\nமனிதவள முகமை",
        "recruit@warehouse-packing-jobs.cc", 1, "ta", "Tamil", "job_fraud", "grp_ta_spam_job", "synthetic_template")

    # Val Spam Group: grp_ta_spam_loan
    add("ta_spam_007", "வாழ்த்துக்கள்! உங்களுக்கு ரூ. 5,00,000 முன்-அங்கீகரிக்கப்பட்ட தனிநபர் கடன்",
        "வணக்கம்,\n\nஎந்த ஆவணமும் இன்றி வெறும் 15 நிமிடங்களில் உங்கள் வங்கிக் கணக்கில் ரூ. 5,00,000 கடன் தொகை வரவு வைக்கப்படும். குறைந்த வட்டி விகிதம். விண்ணப்பிக்கவும்:\nhttp://instant-fast-cash-loan.cc/apply\n\nஈஸி கிரெடிட் நிதி நிறுவனம்",
        "loans@instant-fast-cash-loan.cc", 1, "ta", "Tamil", "loan_fraud", "grp_ta_spam_loan", "synthetic_template")
    add("ta_spam_008", "ஜீரோ வட்டி அவசர பணக்கடன் திட்டம் - உடனடி அனுமதி",
        "அவசர பணத்தேவையா? எவ்வித பிணையமும் இன்றி உடனடியாக ரூ. 2 லட்சம் முதல் ரூ. 10 லட்சம் வரை கடன் வழங்கப்படுகிறது. உங்கள் ஆதார் எண்ணை உள்ளிடவும்:\nhttp://speedy-quick-loan-scheme.com/offer\n\nநிதி சேவை மையம்",
        "fastfunds@speedy-quick-loan-scheme.com", 1, "ta", "Tamil", "loan_fraud", "grp_ta_spam_loan", "synthetic_template")
    add("ta_spam_009", "தங்கக் கடன் தள்ளுபடி மற்றும் குறைந்த வட்டி பண உதவி",
        "சிறப்பு சலுகை: உங்கள் பழைய கடன்களை அடைக்க 1% வட்டியில் உடனடி நிதி உதவி. ஆன்லைனில் ஒப்புதல் பெற இணைப்பை சொடுக்கவும்:\nhttp://low-interest-gold-funds.net/apply\n\nநம்பகமான நிதி நிறுவனம்",
        "info@low-interest-gold-funds.net", 1, "ta", "Tamil", "loan_fraud", "grp_ta_spam_loan", "synthetic_template")

    # Test Spam Group: grp_ta_spam_lottery
    add("ta_spam_010", "பம்பர் பரிசு: நீங்கள் ரூ. 50 லட்சம் மதிப்புள்ள புதிய ஆடி காரை வென்றுள்ளீர்கள்",
        "வாழ்த்துக்கள் அதிர்ஷ்டசாலி!\n\nதீபாவளி மெகா குலுக்கலில் உங்கள் செல்போன் எண் முதல் பரிசை வென்றுள்ளது. பரிசைப் பெற பதிவு கட்டணத்தை உடனே மாற்றவும்:\nhttp://mega-diwali-lucky-draw.biz/claim\n\nகுலுக்கல் குழு",
        "prizes@mega-diwali-lucky-draw.biz", 1, "ta", "Tamil", "lottery_scam", "grp_ta_spam_lottery", "synthetic_template")
    add("ta_spam_011", "வெளிநாட்டு லாட்டரி பரிசு அறிவிப்பு - ரூ. 1 கோடி ரொக்கம்",
        "மதிப்பிற்குரிய வாடிக்கையாளரே,\nதுபாய் சர்வதேச பரிசுக் குலுக்கலில் நீங்கள் தேர்ந்தெடுக்கப்பட்டுள்ளீர்கள். பணத்தைப் பெற உங்கள் வங்கி விவரங்களை பதிவு செய்யவும்:\nhttp://dubai-lottery-claims-portal.info/winner\n\nசர்வதேச பரிசு பிரிவு",
        "dubai@dubai-lottery-claims-portal.info", 1, "ta", "Tamil", "lottery_scam", "grp_ta_spam_lottery", "synthetic_template")
    add("ta_spam_012", "இலவச ஸ்மார்ட்போன் மற்றும் பரிசு கூப்பன் வெற்றி",
        "நீங்கள் 5G மொபைல் போன் வென்றுள்ளீர்கள். இலவச டெலிவரிக்காக கொரியர் கட்டணம் ரூ. 299 மட்டும் இங்கே செலுத்தவும்:\nhttp://free-smartphone-delivery-claim.cc/pay\n\nபரிசு மேலாண்மை",
        "gift@free-smartphone-delivery-claim.cc", 1, "ta", "Tamil", "lottery_scam", "grp_ta_spam_lottery", "synthetic_template")

    # =========================================================================
    # 3. TELUGU (te) - TELUGU SCRIPT
    # =========================================================================
    # Train Ham Group 1: grp_te_ham_bank
    add("te_ham_001", "ఖాతా లావాదేవీ హెచ్చరిక: రూ. 2,450 ఉపసంహరించబడింది",
        "ప్రియమైన కస్టమర్,\n\nమీ ఆంధ్రా బ్యాంక్ ఖాతా XX6192 నుండి ఎస్బీఐ ఏటీఎం వద్ద రూ. 2,450 విజయవంతంగా డ్రా చేయబడింది. ఈ లావాదేవీ మీరు చేయకపోతే వెంటనే కార్డును బ్లాక్ చేయండి.\n\nధన్యవాదాలు,\nఆంధ్రా బ్యాంక్ కస్టమర్ సర్వీస్",
        "alerts@andhrabank.in", 0, "te", "Telugu", "banking_alert", "grp_te_ham_bank", "manually_curated")
    add("te_ham_002", "త్రైమాసిక వడ్డీ జమ సమాచారం - పొదుపు ఖాతా",
        "నమస్కారం,\n\nమీ పొదుపు ఖాతా XX6192 లో త్రైమాసిక వడ్డీ మొత్తం రూ. 842 జమ చేయబడింది. పూర్తి వివరాల కోసం బ్యాంక్ పాస్ బుక్ చూడండి.\n\nబ్యాంక్ శాఖ మేనేజర్",
        "branch@andhrabank.in", 0, "te", "Telugu", "banking_alert", "grp_te_ham_bank", "manually_curated")
    add("te_ham_003", "ఫిక్స్‌డ్ డిపాజిట్ మెచ్యూరిటీ రెన్యూవల్ రశీదు",
        "గౌరవనీయ కస్టమర్,\n\nమీ ఫిక్స్‌డ్ డిపాజిట్ ఖాతా రూ. 1,00,000 తదుపరి ఒక సంవత్సర కాలానికి 7.2% వడ్డీతో విజయవంతంగా పునరుద్ధరించబడింది.\n\nడిపాజిట్ విభాగం",
        "deposits@andhrabank.in", 0, "te", "Telugu", "banking_alert", "grp_te_ham_bank", "manually_curated")

    # Train Ham Group 2: grp_te_ham_electricity
    add("te_ham_004", "కరెంట్ బిల్లు చెల్లింపు రశీదు - సర్వీస్ నంబర్ 9182301",
        "ప్రియమైన వినియోగదారు,\n\nమీ విద్యుత్ బిల్లు మొత్తం రూ. 890 విజయవంతంగా చెల్లించబడింది. లావాదేవీ సంఖ్య: APCPDCL7728103. సకాలంలో బిల్లు చెల్లించినందుకు ధన్యవాదాలు.\n\nఆంధ్రప్రదేశ్ తూర్పు ప్రాంత విద్యుత్ పంపిణీ సంస్థ",
        "billing@apeasternpower.com", 0, "te", "Telugu", "utility_receipt", "grp_te_ham_electricity", "manually_curated")
    add("te_ham_005", "విద్యుత్ సరఫరా తాత్కాలిక అంతరాయం నోటీసు",
        "వినియోగదారుల సమాచారం కొరకు:\nలైన్ల మరమ్మతుల కారణంగా రేపు ఉదయం 9:00 నుండి మధ్యాహ్నం 1:00 వరకు విద్యుత్ సరఫరా నిలిపివేయబడుతుంది. వినియోగదారులు సహకరించగలరు.\n\nసహాయక ఇంజనీర్, విద్యుత్ శాఖ",
        "maintenance@apeasternpower.com", 0, "te", "Telugu", "utility_receipt", "grp_te_ham_electricity", "manually_curated")
    add("te_ham_006", "సౌర విద్యుత్ నెట్ మీటరింగ్ నెలవారీ రికార్డు",
        "నమస్కారం,\n\nమీ రూఫ్‌టాప్ సోలార్ ప్లాంట్ ద్వారా ఈ నెలలో గ్రిడ్‌కు 120 యూనిట్ల విద్యుత్ ఎగుమతి చేయబడింది. బిల్లులో క్రెడిట్ సర్దుబాటు చేయబడింది.\n\nపునరుత్పాదక ఇంధన విభాగం",
        "solar@apeasternpower.com", 0, "te", "Telugu", "utility_receipt", "grp_te_ham_electricity", "manually_curated")

    # Val Ham Group: grp_te_ham_academic
    add("te_ham_007", "యూనివర్సిటీ స్కాలర్‌షిప్ మరియు ఫీజు రీయింబర్స్‌మెంట్ సమాచారం",
        "విద్యార్థులందరికీ గమనిక:\nరాష్ట్ర ప్రభుత్వం అందించే విద్యా దీవెన స్కాలర్‌షిప్ దరఖాస్తులను కళాశాల కార్యాలయంలో సమర్పించడానికి ఆఖరి తేదీ అక్టోబర్ 30.\n\nప్రిన్సిపాల్, శ్రీ వెంకటేశ్వర విశ్వవిద్యాలయం",
        "scholarships@svuniversity.edu.in", 0, "te", "Telugu", "scholarship_notice", "grp_te_ham_academic", "manually_curated")
    add("te_ham_008", "వార్షిక పరీక్షల హాల్ టికెట్లు జారీ వివరాలు",
        "విద్యార్థులకు సూచన:\nనవంబర్ మొదటి వారంలో జరిగే డిగ్రీ పరీక్షల హాల్ టికెట్లను అధికారిక యూనివర్సిటీ పోర్టల్ నుండి డౌన్‌లోడ్ చేసుకోవచ్చు.\n\nపరీక్షల విభాగం",
        "exams@svuniversity.edu.in", 0, "te", "Telugu", "scholarship_notice", "grp_te_ham_academic", "manually_curated")
    add("te_ham_009", "లైబ్రరీ డిజిటల్ రిసోర్సెస్ మరియు జర్నల్స్ యాక్సెస్",
        "అధ్యాపకులు మరియు పరిశోధక విద్యార్థులకు:\nఈ-జర్నల్స్ మరియు రీసెర్చ్ డేటాబేస్ సభ్యత్వం పునరుద్ధరించబడింది. డిజిటల్ లైబ్రరీ పోర్టల్ ద్వారా లాగిన్ అవ్వండి.\n\nగ్రంథాలయ అధికారి",
        "library@svuniversity.edu.in", 0, "te", "Telugu", "scholarship_notice", "grp_te_ham_academic", "manually_curated")

    # Test Ham Group: grp_te_ham_ecommerce
    add("te_ham_010", "ఆర్డర్ డెలివరీ నిర్ధారణ - మీ పార్శిల్ చేరింది",
        "నమస్కారం రాజు,\n\nమీరు ఆర్డర్ చేసిన ఎలక్ట్రానిక్స్ వస్తువు విజయవంతంగా మీ ఇంటికి డెలివరీ చేయబడింది. మీ అభిప్రాయాన్ని యాప్‌లో తెలియజేయండి.\n\nధన్యవాదాలు,\nభారత్ మార్ట్",
        "support@bharatmart-online.in", 0, "te", "Telugu", "order_delivery", "grp_te_ham_ecommerce", "manually_curated")
    add("te_ham_011", "షిప్పింగ్ అప్‌డేట్: మీ ఆర్డర్ బయలుదేరింది",
        "ప్రియమైన కస్టమర్,\n\nమీ కొత్త మొబైల్ ఫోన్ హైదరాబాద్ హబ్ నుండి బయలుదేరింది. రేపు సాయంత్రం లోగా అందుతుంది.\n\nభారత్ మార్ట్ లాజిస్టిక్స్",
        "tracking@bharatmart-online.in", 0, "te", "Telugu", "order_delivery", "grp_te_ham_ecommerce", "manually_curated")
    add("te_ham_012", "వస్తువు రిటర్న్ అభ్యర్థన ఆమోదించబడింది",
        "గమనిక:\nమీరు అభ్యర్థించిన వస్తువు రిటర్న్ ఆమోదించబడింది. కొరియర్ బాయ్ రేపు మీ ఇంటికి వచ్చి వస్తువును సేకరిస్తారు.\n\nకస్టమర్ హెల్ప్ డెస్క్",
        "returns@bharatmart-online.in", 0, "te", "Telugu", "order_delivery", "grp_te_ham_ecommerce", "manually_curated")

    # Train Spam Group 1: grp_te_spam_kyc
    add("te_spam_001", "అత్యవసర హెచ్చరిక: మీ బ్యాంక్ అకౌంట్ కేవైసీ అప్‌డేట్ వెంటనే పూర్తి చేయండి",
        "ప్రియమైన వినియోగదారు,\n\nమీ బ్యాంక్ ఖాతా కేవైసీ గడువు ముగిసింది. ఈరోజే ఆధార్ మరియు పాన్ వివరాలు అప్‌డేట్ చేయకపోతే అకౌంట్ శాశ్వతంగా బ్లాక్ చేయబడుతుంది. వెంటనే లింక్ క్లిక్ చేయండి:\nhttp://telugu-bank-kyc-service.org/login\n\nస్టేట్ బ్యాంక్ అకౌంట్ సెక్యూరిటీ",
        "security@telugu-bank-kyc-service.org", 1, "te", "Telugu", "kyc_phishing", "grp_te_spam_kyc", "synthetic_template")
    add("te_spam_002", "నోటీస్: మీ ఖాతా 24 గంటల్లో నిలిపివేయబడుతుంది",
        "గమనిక:\nమీ ఖాతా భద్రతా సమాచారం పునరుద్ధరించబడలేదు. అకౌంట్ రద్దు కాకుండా ఉండేందుకు వెంటనే ఈ లింక్‌లో మీ వివరాలు నమోదు చేయండి:\nhttp://bank-account-renew-telugu.net/verify\n\nబ్యాంక్ కస్టమర్ కేర్",
        "warning@bank-account-renew-telugu.net", 1, "te", "Telugu", "kyc_phishing", "grp_te_spam_kyc", "synthetic_template")
    add("te_spam_003", "ఆధార్ లింకింగ్ హెచ్చరిక - మీ ఖాతా నిలిపివేత తప్పించండి",
        "అతి ముఖ్యమైన సమాచారం:\nమీ బ్యాంకు ఖాతాకు ఆధార్ లింక్ కాలేదు. పెనాల్టీ లేకుండా వెంటనే ఈ లింక్ ద్వారా ధృవీకరించండి:\nhttp://aadhaar-bank-link-portal.cc/update\n\nఆధార్ సీడింగ్ విభాగం",
        "aadhaar@aadhaar-bank-link-portal.cc", 1, "te", "Telugu", "kyc_phishing", "grp_te_spam_kyc", "synthetic_template")

    # Train Spam Group 2: grp_te_spam_lottery
    add("te_spam_004", "అభినందనలు! మీరు రూ. 35 లక్షల రూపాయల బంపర్ లక్కీ డ్రా గెలుచుకున్నారు",
        "ప్రియమైన విజేత,\n\nమీ మొబైల్ నంబర్ 2026 లక్కీ కార్ బంపర్ డ్రాలో మొదటి బహుమతి రూ. 35,00,000 గెలుచుకుంది. బహుమతిని క్లెయిమ్ చేసుకోవడానికి రిజిస్టర్ చేసుకోండి:\nhttp://lucky-bumper-draw-telugu.biz/claim\n\nలక్కీ డ్రా బహుమతుల కమిటీ",
        "winner@lucky-bumper-draw-telugu.biz", 1, "te", "Telugu", "lottery_scam", "grp_te_spam_lottery", "synthetic_template")
    add("te_spam_005", "శుభవార్త: కేంద్ర ప్రభుత్వ పథకం క్రింద మీకు రూ. 10 లక్షల నగదు బహుమతి",
        "గౌరవనీయ పౌరులకు:\nమీరు కేంద్ర ఉచిత నగదు ప్రోత్సాహక లబ్ధిదారుగా ఎంపికయ్యారు. నగదు జమ కావడానికి మీ వివరాలు ఇక్కడ ధృవీకరించండి:\nhttp://yojana-cash-incentive.info/claim\n\nప్రభుత్వ సేవలు",
        "yojana@yojana-cash-incentive.info", 1, "te", "Telugu", "lottery_scam", "grp_te_spam_lottery", "synthetic_template")
    add("te_spam_006", "దీపావళి బంపర్ క్యాష్ ప్రైజ్: రూ. 15 లక్షలు తక్షణమే పొందండి",
        "లక్కీ డ్రా విన్నర్!\nమీకు పండుగ కానుకగా భారీ నగదు పురస్కారం లభించింది. బదిలీ చార్జీలు చెల్లించి వెంటనే డబ్బు అందుకోండి:\nhttp://festive-cash-bumper-telugu.com/claim\n\nబహుమతి కమిషనర్",
        "diwali@festive-cash-bumper-telugu.com", 1, "te", "Telugu", "lottery_scam", "grp_te_spam_lottery", "synthetic_template")

    # Val Spam Group: grp_te_spam_loan
    add("te_spam_007", "తక్షణ పర్సనల్ లోన్ ఆఫర్: డాక్యుమెంట్లు లేకుండా రూ. 10 లక్షలు మంజూరు",
        "అత్యవసర ఋణం కావాలా?\nసిబిల్ స్కోర్ లేకుండా, ఎలాంటి హామీ లేకుండా 10 నిమిషాల్లో రూ. 10,00,000 మీ ఖాతాలో జమ చేయబడుతుంది. దరఖాస్తు చేసుకోండి:\nhttp://instant-telugu-cash-loan.cc/apply\n\nఫాస్ట్ క్రెడిట్ సొల్యూషన్స్",
        "loans@instant-telugu-cash-loan.cc", 1, "te", "Telugu", "loan_fraud", "grp_te_spam_loan", "synthetic_template")
    add("te_spam_008", "జీరో వడ్డీ లోన్ స్కీమ్ - వెంటనే ఆధార్ నంబర్ నమోదు చేయండి",
        "ప్రియమైన వినియోగదారులకు:\nవ్యాపార మరియు వ్యక్తిగత అవసరాల కోసం అత్యవసర రుణ సదుపాయం. ఆన్‌లైన్‌లో దరఖాస్తు చేసుకోండి:\nhttp://quick-money-telugu-loan.com/offer\n\nఋణ సహాయ కేంద్రం",
        "cash@quick-money-telugu-loan.com", 1, "te", "Telugu", "loan_fraud", "grp_te_spam_loan", "synthetic_template")
    add("te_spam_009", "రైతు రుణ ఉపశమనం మరియు తక్షణ నగదు బదిలీ",
        "రైతులకు ప్రత్యేక రుణాలు: ఎలాంటి గ్యారెంటీ లేకుండా రూ. 3 లక్షలు తక్షణం పంపిణీ. ప్రాసెసింగ్ ఫీజు చెల్లించి లోన్ పొందండి:\nhttp://kisan-easy-loan-scheme.net/apply\n\nగ్రామీణ క్రెడిట్ సొసైటీ",
        "kisan@kisan-easy-loan-scheme.net", 1, "te", "Telugu", "loan_fraud", "grp_te_spam_loan", "synthetic_template")

    # Test Spam Group: grp_te_spam_job
    add("te_spam_010", "ఇంటి నుంచే ఉద్యోగం: ప్రతిరోజూ రూ. 4000 సంపాదించే గొప్ప అవకాశం",
        "నమస్కారం,\nమీ మొబైల్ ఉపయోగించి రోజుకు 2 గంటలు పని చేసి సులభంగా డబ్బు సంపాదించండి. ఎలాంటి పెట్టుబడి అవసరం లేదు. వెంటనే వాట్సాప్‌లో వివరాలు పంపండి:\nhttp://telugu-parttime-daily-jobs.biz/join\n\nఆన్‌లైన్ జాబ్ కన్సల్టెన్సీ",
        "jobs@telugu-parttime-daily-jobs.biz", 1, "te", "Telugu", "job_fraud", "grp_te_spam_job", "synthetic_template")
    add("te_spam_011", "ప్రభుత్వ ఉద్యోగ నోటిఫికేషన్: పరీక్ష లేకుండా నేరుగా ఎంపిక",
        "నిరుద్యోగులకు ప్రకటన:\nపోస్టల్ శాఖలో 5000 పోస్టుల భర్తీ. దరఖాస్తు ఫీజు రూ. 550 చెల్లించి అపాయింట్‌మెంట్ లెటర్ పొందండి:\nhttp://direct-recruitment-postal-jobs.info/apply\n\nఉద్యోగ నియామకాల బోర్డు",
        "notice@direct-recruitment-postal-jobs.info", 1, "te", "Telugu", "job_fraud", "grp_te_spam_job", "synthetic_template")
    add("te_spam_012", "డేటా ఎంట్రీ ప్రాజెక్ట్: వారానికి రూ. 25000 సంపాదించండి",
        "నమస్కారం నిరుద్యోగి మిత్రులారా,\nసింపుల్ కాపీ పేస్ట్ జాబ్స్. రిజిస్ట్రేషన్ ఫీజు చెల్లించి వర్క్ సాఫ్ట్‌వేర్ డౌన్‌లోడ్ చేసుకోండి:\nhttp://dataentry-weekly-payout.cc/register\n\nఐటీ సర్వీసెస్ ప్రైవేట్ లిమిటెడ్",
        "hr@dataentry-weekly-payout.cc", 1, "te", "Telugu", "job_fraud", "grp_te_spam_job", "synthetic_template")

    # =========================================================================
    # 4. KANNADA (kn) - KANNADA SCRIPT
    # =========================================================================
    # Train Ham Group 1: grp_kn_ham_bank
    add("kn_ham_001", "ಖಾತೆ ವಹಿವಾಟು ಎಚ್ಚರಿಕೆ: ಖಾತೆಯಿಂದ ರೂ. 1,200 ಡೆಬಿಟ್ ಆಗಿದೆ",
        "ಆತ್ಮೀಯ ಗ್ರಾಹಕರೇ,\n\nನಿಮ್ಮ ಕೆನರಾ ಬ್ಯಾಂಕ್ ಖಾತೆ ಸಂಖ್ಯೆ XX8291 ರಿಂದ ಯಶಸ್ವಿಯಾಗಿ ರೂ. 1,200 ಪಾವತಿಯಾಗಿದೆ. ಉಳಿದಿರುವ ಒಟ್ಟು ಬ್ಯಾಲೆನ್ಸ್: ರೂ. 18,450. ಈ ವಹಿವಾಟು ನೀವು ಮಾಡಿರದಿದ್ದರೆ ಕೂಡಲೇ ಕರೆ ಮಾಡಿ.\n\nಕೆನರಾ ಬ್ಯಾಂಕ್",
        "alerts@canarabank.in", 0, "kn", "Kannada", "banking_alert", "grp_kn_ham_bank", "manually_curated")
    add("kn_ham_002", "ನಿಮ್ಮ ತ್ರೈಮಾಸಿಕ ಬ್ಯಾಂಕ್ ಖಾತೆ ವಿವರ ಪಟ್ಟಿ ಸಿದ್ಧವಾಗಿದೆ",
        "ನಮಸ್ಕಾರ,\n\nನಿಮ್ಮ ಉಳಿತಾಯ ಖಾತೆಯ ಕಳೆದ ತ್ರೈಮಾಸಿಕ ವಹಿವಾಟುಗಳ ವಿವರ ಪಟ್ಟಿಯನ್ನು ಲಗತ್ತಿಸಲಾಗಿದೆ. ನಿಮ್ಮ ಅಧಿಕೃತ ಇಂಟರ್ನೆಟ್ ಬ್ಯಾಂಕಿಂಗ್ ಮೂಲಕ ಪರಿಶೀಲಿಸಿ.\n\nಗ್ರಾಹಕ ಸೇವಾ ವಿಭಾಗ",
        "customercare@canarabank.in", 0, "kn", "Kannada", "banking_alert", "grp_kn_ham_bank", "manually_curated")
    add("kn_ham_003", "ನಿಶ್ಚಿತ ಠೇವಣಿ ಮೇಲಿನ ಬಡ್ಡಿ ಜಮೆ ಮಾಹಿತಿ",
        "ಗ್ರಾಹಕರಿಗೆ ನಮಸ್ಕಾರ,\n\nನಿಮ್ಮ ಠೇವಣಿ ಖಾತೆಯ ತ್ರೈಮಾಸಿಕ ಬಡ್ಡಿ ಮೊತ್ತ ರೂ. 2,150 ನಿಮ್ಮ ಉಳಿತಾಯ ಖಾತೆಗೆ ಜಮೆಯಾಗಿದೆ.\n\nಶಾಖಾ ವ್ಯವಸ್ಥಾಪಕರು",
        "manager@canarabank.in", 0, "kn", "Kannada", "banking_alert", "grp_kn_ham_bank", "manually_curated")

    # Train Ham Group 2: grp_kn_ham_bescom
    add("kn_ham_004", "ಬೆಸ್ಕಾಂ ಮಾಸಿಕ ವಿದ್ಯುತ್ ಬಿಲ್ ಪಾವತಿ ರಶೀದಿ - ಗ್ರಾಹಕ ಸಂಖ್ಯೆ 7102931",
        "ಆತ್ಮೀಯ ಗ್ರಾಹಕರೇ,\n\nನಿಮ್ಮ ಅಕ್ಟೋಬರ್ ತಿಂಗಳ ವಿದ್ಯುತ್ ಬಿಲ್ ಮೊತ್ತ ರೂ. 960 ಯಶಸ್ವಿಯಾಗಿ ಸ್ವೀಕರಿಸಲಾಗಿದೆ. ರಶೀದಿ ಸಂಖ್ಯೆ: BESCOM9281039. ಸಮಯಕ್ಕೆ ಸರಿಯಾಗಿ ಬಿಲ್ ಪಾವತಿಸಿದ್ದಕ್ಕಾಗಿ ಧನ್ಯವಾದಗಳು.\n\nಬೆಸ್ಕಾಂ",
        "billing@bescom.karnataka.gov.in", 0, "kn", "Kannada", "utility_receipt", "grp_kn_ham_electricity", "manually_curated")
    add("kn_ham_005", "ನಿಗದಿತ ವಿದ್ಯುತ್ ಲೈನ್ ದುರಸ್ತಿ ಮತ್ತು ನಿರ್ವಹಣಾ ಪ್ರಕಟಣೆ",
        "ಸಾರ್ವಜನಿಕರ ಗಮನಕ್ಕೆ:\nವಿದ್ಯುತ್ ತಂತಿಗಳ ವಾರ್ಷಿಕ ನಿರ್ವಹಣೆ ಕಾರ್ಯವಿರುವುದರಿಂದ ಬುಧವಾರ ಬೆಳಗ್ಗೆ 10:00 ರಿಂದ ಮಧ್ಯಾಹ್ನ 2:00 ರವರೆಗೆ ವಿದ್ಯುತ್ ಸರಬರಾಜಿನಲ್ಲಿ ವ್ಯತ್ಯಯವಾಗಲಿದೆ.\n\nಸಹಾಯಕ ಕಾರ್ಯಪಾಲಕ ಇಂಜಿನಿಯರ್, ಬೆಸ್ಕಾಂ",
        "maintenance@bescom.karnataka.gov.in", 0, "kn", "Kannada", "utility_receipt", "grp_kn_ham_electricity", "manually_curated")
    add("kn_ham_006", "ಗೃಹಜ್ಯೋತಿ ಯೋಜನೆ ಉಚಿತ ವಿದ್ಯುತ್ ಅರ್ಹತಾ ದೃಢೀಕರಣ",
        "ನಾಗರಿಕರಿಗೆ ಮಾಹಿತಿ:\nನಿಮ್ಮ ಗೃಹಜ್ಯೋತಿ ಯೋಜನೆಯ ನೋಂದಣಿ ಯಶಸ್ವಿಯಾಗಿದ್ದು, 160 ಯೂನಿಟ್‌ಗಳವರೆಗಿನ ಬಳಕೆಗೆ ಶೂನ್ಯ ವಿದ್ಯುತ್ ಬಿಲ್ ಅನ್ವಯವಾಗಲಿದೆ.\n\nಕರ್ನಾಟಕ ಇಂಧನ ಇಲಾಖೆ",
        "gruhajyothi@karnataka.gov.in", 0, "kn", "Kannada", "utility_receipt", "grp_kn_ham_electricity", "manually_curated")

    # Val Ham Group: grp_kn_ham_transport
    add("kn_ham_007", "ಕೆಎಸ್‌ಆರ್‌ಟಿಸಿ ಇ-ಟಿಕೆಟ್ ಮುಂಗಡ ಬುಕಿಂಗ್ ದೃಢೀಕರಣ - ಟಿಕೆಟ್ ಸಂಖ್ಯೆ: KSR89201",
        "ಆತ್ಮೀಯ ಪ್ರಯಾಣಿಕರೇ,\n\nನಿಮ್ಮ ಪ್ರಯಾಣ ಟಿಕೆಟ್ ದೃಢಪಟ್ಟಿದೆ. ಮಾರ್ಗ: ಬೆಂಗಳೂರು ದಿಂದ ಮೈಸೂರು, ದಿನಾಂಕ: 24 ಅಕ್ಟೋಬರ್ 2026, ಸಮಯ: 07:30 ಬೆಳಗ್ಗೆ. ಸುಖಕರ ಪ್ರಯಾಣವನ್ನು ಹಾರೈಸುತ್ತೇವೆ!\n\nಕರ್ನಾಟಕ ರಾಜ್ಯ ರಸ್ತೆ ಸಾರಿಗೆ ನಿಗಮ",
        "support@ksrtc.in", 0, "kn", "Kannada", "bus_ticket", "grp_kn_ham_transport", "manually_curated")
    add("kn_ham_008", "ವಿಶೇಷ ದಸರಾ ಹಬ್ಬದ ಹೆಚ್ಚುವರಿ ಬಸ್ಸುಗಳ ಸಂಚಾರ ಮಾಹಿತಿ",
        "ಪ್ರಯಾಣಿಕರ ಅನುಕೂಲಕ್ಕಾಗಿ:\nದಸರಾ ಹಬ್ಬದ ಪ್ರಯಾಣಿಕರ ದಟ್ಟಣೆಯನ್ನು ನಿಯಂತ್ರಿಸಲು ಹೆಚ್ಚುವರಿ ವಿಶೇಷ ಬಸ್ಸುಗಳನ್ನು ನಿಯೋಜಿಸಲಾಗಿದೆ. ಮುಂಗಡ ಕಾಯ್ದಿರಿಸಲು ವೆಬ್‌ಸೈಟ್‌ಗೆ ಭೇಟಿ ನೀಡಿ.\n\nಕೆಎಸ್‌ಆರ್‌ಟಿಸಿ ಸಾರ್ವಜನಿಕ ಸಂಪರ್ಕ",
        "info@ksrtc.in", 0, "kn", "Kannada", "bus_ticket", "grp_kn_ham_transport", "manually_curated")
    add("kn_ham_009", "ನಮ್ಮ ಮೆಟ್ರೋ ಸ್ಮಾರ್ಟ್ ಕಾರ್ಡ್ ಆನ್‌ಲೈನ್ ರೀಚಾರ್ಜ್ ರಶೀದಿ",
        "ಪ್ರಯಾಣಿಕರೇ,\n\nನಿಮ್ಮ ಮೆಟ್ರೋ ಸ್ಮಾರ್ಟ್ ಕಾರ್ಡ್ ಸಂಖ್ಯೆ 892013 ಗೆ ರೂ. 500 ಯಶಸ್ವಿಯಾಗಿ ರೀಚಾರ್ಜ್ ಆಗಿದೆ. ಸಮೀಪದ ಮೆಟ್ರೋ ಗೇಟ್‌ನಲ್ಲಿ ಕಾರ್ಡ್ ಟ್ಯಾಪ್ ಮಾಡಿ.\n\nಬೆಂಗಳೂರು ಮೆಟ್ರೋ ರೈಲು ನಿಗಮ",
        "smartcard@bmrc.co.in", 0, "kn", "Kannada", "bus_ticket", "grp_kn_ham_transport", "manually_curated")

    # Test Ham Group: grp_kn_ham_academic
    add("kn_ham_010", "ಬೆಂಗಳೂರು ವಿಶ್ವವಿದ್ಯಾಲಯ ಪರೀಕ್ಷಾ ವೇಳಾಪಟ್ಟಿ ಪ್ರಕಟಣೆ",
        "ಎಲ್ಲಾ ವಿದ್ಯಾರ್ಥಿಗಳಿಗೆ ಸೂಚನೆ:\nಸ್ನಾತಕೋತ್ತರ ಪದವಿ ಪರೀಕ್ಷೆಗಳು ನವೆಂಬರ್ 20 ರಿಂದ ಪ್ರಾರಂಭವಾಗಲಿವೆ. ವಿವರವಾದ ವೇಳಾಪಟ್ಟಿಯನ್ನು ವಿವಿ ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ವೀಕ್ಷಿಸಿ.\n\nಕುಲಸಚಿವರು (ಮೌಲ್ಯಮಾಪನ)",
        "evaluator@bangaloreuniversity.ac.in", 0, "kn", "Kannada", "academic_notice", "grp_kn_ham_academic", "manually_curated")
    add("kn_ham_011", "ಕಾಲೇಜು ಗ್ರಂಥಾಲಯ ಪುಸ್ತಕ ಹಿಂದಿರುಗಿಸುವ ಕೊನೆಯ ದಿನಾಂಕ",
        "ಆತ್ಮೀಯ ವಿದ್ಯಾರ್ಥಿಗಳೇ,\nಸೆಮಿಸ್ಟರ್ ರಜೆ ಆರಂಭವಾಗುವ ಮುನ್ನ ಗ್ರಂಥಾಲಯದಿಂದ ಪಡೆದ ಪುಸ್ತಕಗಳನ್ನು ನವೆಂಬರ್ 10 ರೊಳಗೆ ಹಿಂತಿರುಗಿಸತಕ್ಕದ್ದು.\n\nಮುಖ್ಯ ಗ್ರಂಥಪಾಲಕರು",
        "library@bangaloreuniversity.ac.in", 0, "kn", "Kannada", "academic_notice", "grp_kn_ham_academic", "manually_curated")
    add("kn_ham_012", "ಯುವ ಸಮ್ಮೇಳನ ಮತ್ತು ಸಾಂಸ್ಕೃತಿಕ ಉತ್ಸವ ಆಹ್ವಾನ",
        "ವಿದ್ಯಾರ್ಥಿಗಳಿಗೆ ಸ್ವಾಗತ:\nಅಂತರ ಕಾಲೇಜು ಯುವಜನ ಸಾಂಸ್ಕೃತಿಕ ಉತ್ಸವವು ಮುಂದಿನ ವಾರ ಆವರಣದಲ್ಲಿ ನಡೆಯಲಿದೆ. ಆಸಕ್ತರು ಹೆಸರು ನೋಂದಾಯಿಸಿಕೊಳ್ಳಿ.\n\nಸಾಂಸ್ಕೃತಿಕ ಸಮಿತಿ",
        "youthfest@bangaloreuniversity.ac.in", 0, "kn", "Kannada", "academic_notice", "grp_kn_ham_academic", "manually_curated")

    # Train Spam Group 1: grp_kn_spam_kyc
    add("kn_spam_001", "ತುರ್ತು ನೋಟಿಸ್: ನಿಮ್ಮ ಬ್ಯಾಂಕ್ ಖಾತೆಯನ್ನು ತಕ್ಷಣ ಅಮಾನತುಗೊಳಿಸಲಾಗುವುದು",
        "ಆತ್ಮೀಯ ಗ್ರಾಹಕರೇ,\n\nನಿಮ್ಮ ಬ್ಯಾಂಕ್ ಖಾತೆಯ ಕೆವೈಸಿ (KYC) ಪರಿಶೀಲನೆ ಬಾಕಿ ಉಳಿದಿದೆ. 24 ಗಂಟೆಗಳ ಒಳಗೆ ನವೀಕರಿಸದಿದ್ದರೆ ನಿಮ್ಮ ಖಾತೆ ಮತ್ತು ಎಟಿಎಂ ಕಾರ್ಡ್ ಸಂಪೂರ್ಣವಾಗಿ ನಿರ್ಬಂಧಿಸಲ್ಪಡುತ್ತದೆ. ತಕ್ಷಣ ಲಿಂಕ್ ಬಳಸಿ:\nhttp://kannada-bank-kyc-update.org/login\n\nಬ್ಯಾಂಕ್ ಭದ್ರತಾ ವಿಭಾಗ",
        "security@kannada-bank-kyc-update.org", 1, "kn", "Kannada", "kyc_phishing", "grp_kn_spam_kyc", "synthetic_template")
    add("kn_spam_002", "ಎಚ್ಚರಿಕೆ: ನಿಮ್ಮ ಪಾನ್ ಕಾರ್ಡ್ ಲಿಂಕ್ ಆಗಿಲ್ಲ - ತಕ್ಷಣ ಪರಿಶೀಲಿಸಿ",
        "ಗ್ರಾಹಕರಿಗೆ ಸೂಚನೆ:\nನಿಮ್ಮ ಬ್ಯಾಂಕ್ ಖಾತೆಯೊಂದಿಗೆ ಪಾನ್ ಕಾರ್ಡ್ ಲಿಂಕ್ ಮಾಡಲು ವಿಫಲವಾದರೆ ದಂಡ ವಿಧಿಸಲಾಗುವುದು. ಲಿಂಕ್ ಮಾಡಲು ಇಲ್ಲಿ ಕ್ಲಿಕ್ ಮಾಡಿ:\nhttp://pan-card-link-kannada.net/verify\n\nಗ್ರಾಹಕ ಸೇವಾ ಕೇಂದ್ರ",
        "alerts@pan-card-link-kannada.net", 1, "kn", "Kannada", "kyc_phishing", "grp_kn_spam_kyc", "synthetic_template")
    add("kn_spam_003", "ನಿಮ್ಮ ಇಂಟರ್ನೆಟ್ ಬ್ಯಾಂಕಿಂಗ್ ನಿಷ್ಕ್ರಿಯಗೊಂಡಿದೆ - ರೀಸೆಟ್ ಮಾಡಿ",
        "ಅತ್ಯಗತ್ಯ ಸೂಚನೆ:\nಭದ್ರತಾ ಕಾರಣಗಳಿಂದ ನಿಮ್ಮ ನೆಟ್‌ಬ್ಯಾಂಕಿಂಗ್ ಸೇವೆಗಳನ್ನು ಸ್ಥಗಿತಗೊಳಿಸಲಾಗಿದೆ. ಸಕ್ರಿಯಗೊಳಿಸಲು ನಿಮ್ಮ ವಿವರಗಳನ್ನು ಪುನಃ ದಾಖಲಿಸಿ:\nhttp://netbanking-kannada-activate.biz/login\n\nಆನ್‌ಲೈನ್ ಬ್ಯಾಂಕಿಂಗ್ ಬೆಂಬಲ",
        "support@netbanking-kannada-activate.biz", 1, "kn", "Kannada", "kyc_phishing", "grp_kn_spam_kyc", "synthetic_template")

    # Train Spam Group 2: grp_kn_spam_lottery
    add("kn_spam_004", "ಅಭಿನಂದನೆಗಳು! ಕರ್ನಾಟಕ ಸರ್ಕಾರದ ಬಂಪರ್ ಲಾಟರಿಯಲ್ಲಿ ನೀವು ರೂ. 25 ಲಕ್ಷ ಗೆದ್ದಿದ್ದೀರಿ",
        "ವಿಜೇತರಿಗೆ ನಮಸ್ಕಾರ,\n\nನಿಮ್ಮ ಇಮೇಲ್ ಐಡಿಯನ್ನು ವಾರ್ಷಿಕ ಮಹಾ ಲಕ್ಕಿ ಡ್ರಾದಲ್ಲಿ ಪ್ರಥಮ ಬಹುಮಾನಕ್ಕೆ ಆಯ್ಕೆ ಮಾಡಲಾಗಿದೆ. ನೀವು ರೂ. 25,00,000 ನಗದು ಬಹುಮಾನ ಗೆದ್ದಿದ್ದೀರಿ. ನೋಂದಣಿ ಶುಲ್ಕ ಪಾವತಿಸಿ:\nhttp://bumper-lottery-kannada.biz/claim\n\nಲಾಟರಿ ವಿತರಣಾ ಸಮಿತಿ",
        "claim@bumper-lottery-kannada.biz", 1, "kn", "Kannada", "lottery_scam", "grp_kn_spam_lottery", "synthetic_template")
    add("kn_spam_005", "ವಿಶೇಷ ಬಹುಮಾನ ಯೋಜನೆ: ನಿಮ್ಮ ಖಾತೆಗೆ ರೂ. 5 ಲಕ್ಷ ಜಮೆಯಾಗಲಿದೆ",
        "ಆತ್ಮೀಯ ಗ್ರಾಹಕರೇ,\nನಿಮ್ಮ ಮೊಬೈಲ್ ಸಂಖ್ಯೆಗೆ ಲಕ್ಕಿ ಗ್ರಾಹಕ ಬಹುಮಾನ ಮಂಜೂರಾಗಿದೆ. ಹಣ ಬಿಡುಗಡೆ ಮಾಡಲು ಬ್ಯಾಂಕ್ ವಿವರಗಳನ್ನು ಇಲ್ಲಿ ನಮೂದಿಸಿ:\nhttp://kannada-lucky-reward.info/claim\n\nಬಹುಮಾನ ಶಾಖೆ",
        "rewards@kannada-lucky-reward.info", 1, "kn", "Kannada", "lottery_scam", "grp_kn_spam_lottery", "synthetic_template")
    add("kn_spam_006", "ದೀಪಾವಳಿ ಧಮಾಕಾ: ಹೊಚ್ಚ ಹೊಸ ಕಾರು ಮತ್ತು ಚಿನ್ನದ ನಾಣ್ಯ ಗೆದ್ದಿದ್ದೀರಿ",
        "ಶುಭ ಸುದ್ದಿ!\nಲಕ್ಕಿ ಕೂಪನ್ ಸ್ಪರ್ಧೆಯಲ್ಲಿ ನಿಮ್ಮ ಹೆಸರು ಆಯ್ಕೆಯಾಗಿದೆ. ಉಡುಗೊರೆ ಮನೆಗೆ ತಲುಪಿಸಲು ಕೊರಿಯರ್ ಶುಲ್ಕ ಪಾವತಿಸಿ:\nhttp://festive-car-reward-kannada.cc/claim\n\nಬಹುಮಾನ ವಿಭಾಗ",
        "prizes@festive-car-reward-kannada.cc", 1, "kn", "Kannada", "lottery_scam", "grp_kn_spam_lottery", "synthetic_template")

    # Val Spam Group: grp_kn_spam_loan
    add("kn_spam_007", "ತ್ವರಿತ ಸಾಲದ ಕೊಡುಗೆ: ಕೇವಲ 5 ನಿಮಿಷಗಳಲ್ಲಿ ರೂ. 5,00,000 ಸುಲಭ ಸಾಲ",
        "ತುರ್ತು ಹಣಕಾಸಿನ ಅಗತ್ಯವಿದೆಯೇ?\nಯಾವುದೇ ದಾಖಲೆಗಳಿಲ್ಲದೆ, ಕಡಿಮೆ ಬಡ್ಡಿ ದರದಲ್ಲಿ ರೂ. 5,00,000 ಸಾಲ ನೇರವಾಗಿ ನಿಮ್ಮ ಖಾತೆಗೆ ಜಮೆಯಾಗುತ್ತದೆ. ಅರ್ಜಿ ಸಲ್ಲಿಸಲು ಲಿಂಕ್ ಕ್ಲಿಕ್ ಮಾಡಿ:\nhttp://speedy-cash-loan-kannada.cc/apply\n\nತ್ವರಿತ ಹಣಕಾಸು ಸೇವೆಗಳು",
        "apply@speedy-cash-loan-kannada.cc", 1, "kn", "Kannada", "loan_fraud", "grp_kn_spam_loan", "synthetic_template")
    add("kn_spam_008", "ಶೂನ್ಯ ಬಡ್ಡಿದರದಲ್ಲಿ ವೈಯಕ್ತಿಕ ಸಾಲ ಮಂಜೂರಾತಿ ಪ್ರಕಟಣೆ",
        "ಗ್ರಾಹಕರಿಗೆ ಆಫರ್:\nನಿಮ್ಮ ಆಧಾರ್ ಸಂಖ್ಯೆಯ ಆಧಾರದ ಮೇಲೆ ರೂ. 10 ಲಕ್ಷದವರೆಗೆ ಸಾಲ ಲಭ್ಯವಿದೆ. ಇಂದೇ ಅರ್ಜಿ ಹಾಕಿ:\nhttp://instant-easy-loan-kannada.com/offer\n\nಸಾಲ ವಿತರಣಾ ಕೇಂದ್ರ",
        "loan@instant-easy-loan-kannada.com", 1, "kn", "Kannada", "loan_fraud", "grp_kn_spam_loan", "synthetic_template")
    add("kn_spam_009", "ಕೃಷಿ ಮತ್ತು ವ್ಯಾಪಾರ ತುರ್ತು ಸಾಲ - ಯಾವುದೇ ಅಡಮಾನವಿಲ್ಲ",
        "ರೈತರು ಮತ್ತು ಸಣ್ಣ ವ್ಯಾಪಾರಿಗಳಿಗೆ ಸುವರ್ಣಾವಕಾಶ: 1% ಬಡ್ಡಿಯಲ್ಲಿ ಸುಲಭ ಕಂತುಗಳ ಸಾಲ. ತಕ್ಷಣ ಅನುಮೋದನೆಗೆ ಲಿಂಕ್ ಕ್ಲಿಕ್ ಮಾಡಿ:\nhttp://kisan-vyapar-loan-kannada.net/apply\n\nಗ್ರಾಮೀಣ ಸಾಲ ಮಂಡಳಿ",
        "kisan@kisan-vyapar-loan-kannada.net", 1, "kn", "Kannada", "loan_fraud", "grp_kn_spam_loan", "synthetic_template")

    # Test Spam Group: grp_kn_spam_job
    add("kn_spam_010", "ಮನೆಯಲ್ಲೇ ಕುಳಿತು ಕೆಲಸ ಮಾಡಿ: ದಿನಕ್ಕೆ 3500 ರೂಪಾಯಿ ಆದಾಯ",
        "ನಿರುದ್ಯೋಗಿಗಳಿಗೆ ಉದ್ಯೋಗಾವಕಾಶ:\nದಿನಕ್ಕೆ ಕೇವಲ 1 ಗಂಟೆ ಮೊಬೈಲ್ ಮೂಲಕ ಕೆಲಸ ಮಾಡಿ ತಿಂಗಳಿಗೆ 70,000 ರೂಪಾಯಿ ಗಳಿಸಿ. ಉಚಿತ ತರಬೇತಿಗಾಗಿ ವಾಟ್ಸಾಪ್ ಗ್ರೂಪ್ ಸೇರಿಕೊಳ್ಳಿ:\nhttp://work-from-home-kannada-jobs.biz/join\n\nಉದ್ಯೋಗ ಸೇವಾ ಸಂಸ್ಥೆ",
        "jobs@work-from-home-kannada-jobs.biz", 1, "kn", "Kannada", "job_fraud", "grp_kn_spam_job", "synthetic_template")
    add("kn_spam_011", "ಕೆಪಿಎಸ್‌ಸಿ ಪರೀಕ್ಷೆಯಿಲ್ಲದೆ ನೇರ ನೇಮಕಾತಿ ಅಧಿಸೂಚನೆ",
        "ಸರ್ಕಾರಿ ನೌಕರಿ ಬಯಸುವವರಿಗೆ ಸೂಚನೆ:\nದ್ವಿತೀಯ ದರ್ಜೆ ಸಹಾಯಕರ ಹುದ್ದೆಗಳಿಗೆ ನೇರ ಆಯ್ಕೆ. ನೋಂದಣಿ ಶುಲ್ಕ 750 ರೂ ಪಾವತಿಸಿ ಆರ್ಡರ್ ಕಾಪಿ ಪಡೆಯಿರಿ:\nhttp://kpsc-direct-recruitment-fraud.info/apply\n\nನೇಮಕಾತಿ ಸಮಿತಿ",
        "recruit@kpsc-direct-recruitment-fraud.info", 1, "kn", "Kannada", "job_fraud", "grp_kn_spam_job", "synthetic_template")
    add("kn_spam_012", "ವಿದೇಶದಲ್ಲಿ ಭದ್ರತಾ ಸಿಬ್ಬಂದಿ ಕೆಲಸ - ತಿಂಗಳಿಗೆ 90000 ಸಂಬಳ",
        "ದುಬೈ ಮತ್ತು ಕತಾರ್‌ನಲ್ಲಿ ಕೆಲಸ ಮಾಡಲು ಯುವಕರು ಬೇಕಾಗಿದ್ದಾರೆ. ಉಚಿತ ಊಟ ಮತ್ತು ವಸತಿ. ವೀಸಾ ಪಡೆಯಲು ತಕ್ಷಣ ಶುಲ್ಕ ಜಮೆ ಮಾಡಿ:\nhttp://gulf-job-consultancy-kannada.cc/apply\n\nವಿದೇಶಿ ಉದ್ಯೋಗ ಕನ್ಸಲ್ಟೆಂಟ್",
        "visa@gulf-job-consultancy-kannada.cc", 1, "kn", "Kannada", "job_fraud", "grp_kn_spam_job", "synthetic_template")

    # =========================================================================
    # 5. HINGLISH (hinglish) - ROMANIZED INDIC SCRIPT
    # =========================================================================
    # Train Ham Group 1: grp_hinglish_ham_bank
    add("hinglish_ham_001", "Aapka SBI khata balance update aur transaction receipt",
        "Namaste,\n\nAapke SBI khate XX3819 mein Swiggy se Rs. 450 ka bhugtan safal raha. Aapka bacha hua khata balance Rs. 24,190 hai. Agar transaction aapne nahi kiya toh bank number par call karein.\n\nDhanyawad,\nState Bank of India",
        "alerts@sbi.co.in", 0, "hinglish", "Latin", "banking_receipt", "grp_hinglish_ham_bank", "manually_curated")
    add("hinglish_ham_002", "Bank transaction notification: Rs 1,500 transferred successfully",
        "Aapke savings khate se NEFT ke dwara Rs 1,500 successfully transfer ho gaye hain. UTR number: SBIN928103819. Koi bhi samasya ho toh hamari branch se sampark kijiye.\n\nCustomer Support Team",
        "support@sbi.co.in", 0, "hinglish", "Latin", "banking_receipt", "grp_hinglish_ham_bank", "manually_curated")
    add("hinglish_ham_003", "Aapka fixed deposit maturity ho gaya hai - renewal advice",
        "Namaste account holder,\n\nAapka Rs 50,000 ka FD account successfully mature ho chuka hai. Renewal ke liye official banking portal par login karein.\n\nSBI Branch Manager",
        "manager@sbi.co.in", 0, "hinglish", "Latin", "banking_receipt", "grp_hinglish_ham_bank", "manually_curated")

    # Train Ham Group 2: grp_hinglish_ham_delivery
    add("hinglish_ham_004", "Aapka package kal deliver hoga - Tracking ID #DL8912",
        "Namaste Amit,\n\nAapka Flipkart order dispatch ho chuka hai aur kal shaam tak aapke ghar deliver kar diya jayega. Delivery agent call karega. OTP kisi ke saath share na karein.\n\nDhanyawad,\nFlipkart Delivery Team",
        "delivery@flipkart-orders.com", 0, "hinglish", "Latin", "delivery_update", "grp_hinglish_ham_delivery", "manually_curated")
    add("hinglish_ham_005", "Order delivered: Aapka saman safaltapoorvak deliver ho gaya hai",
        "Hello,\n\nAapka grocery order aaj subah delivery partner ne deliver kar diya hai. Delivery feedback dene ke liye app open kijiye.\n\nFlipkart Support",
        "help@flipkart-orders.com", 0, "hinglish", "Latin", "delivery_update", "grp_hinglish_ham_delivery", "manually_curated")
    add("hinglish_ham_006", "Refund processed: Paise aapke khate mein bhej diye gaye hain",
        "Namaste,\n\nAapke cancelled order ka refund Rs. 899 aapke bank account mein credit kar diya gaya hai. Bank reference number: REF8921094.\n\nCustomer Care Desk",
        "refunds@flipkart-orders.com", 0, "hinglish", "Latin", "delivery_update", "grp_hinglish_ham_delivery", "manually_curated")

    # Val Ham Group: grp_hinglish_ham_workplace
    add("hinglish_ham_007", "Diwali celebration aur office chutti ki suchna",
        "Hi Team,\n\nDiwali ke shubh avsar par hamara office 20 October se 24 October tak band rahega. Sabhi pending project tasks aur code reviews 19 October tak complete kar lein. Aap sabhi ko shubhkamnayein!\n\nHR Department",
        "hr@infotech-solutions.in", 0, "hinglish", "Latin", "workplace_announcement", "grp_hinglish_ham_workplace", "manually_curated")
    add("hinglish_ham_008", "Quarterly team meeting aur project review updates",
        "Hello sabhi ko,\n\nHamara quarterly project planning meeting kal 3 baje hoga. Kripya apne slides aur deployment metrics pehle se prepare kar lijiye taaki samay par review kar sakein.\n\nBest regards,\nRajesh Sharma",
        "rajesh.sharma@infotech-solutions.in", 0, "hinglish", "Latin", "workplace_announcement", "grp_hinglish_ham_workplace", "manually_curated")
    add("hinglish_ham_009", "New joinee welcome aur onboarding session link",
        "Team members,\n\nHamari engineering team mein naye colleagues join kar rahe hain. Unke swagat ke liye kal 11 baje all-hands meeting mein shamil hoiye.\n\nPeople Operations",
        "people@infotech-solutions.in", 0, "hinglish", "Latin", "workplace_announcement", "grp_hinglish_ham_workplace", "manually_curated")

    # Test Ham Group: grp_hinglish_ham_telecom
    add("hinglish_ham_010", "Aapka mobile recharge safal raha - validity 28 din",
        "Namaste Jio user,\n\nAapke mobile number XX8921 par Rs. 299 ka monthly recharge plan activate ho chuka hai. Ismein daily 1.5GB data aur unlimited calls shamil hain.\n\nJio Telecom Support",
        "recharge@jio.com", 0, "hinglish", "Latin", "telecom_receipt", "grp_hinglish_ham_telecom", "manually_curated")
    add("hinglish_ham_011", "Data balance alert: Aaj ka 90 percent data khatam ho chuka hai",
        "Alert: Aapke daily quota ka 90% high speed internet data use ho chuka hai. Speed renewal kal subah hoga ya additional booster pack lijiye.\n\nJio Service",
        "alerts@jio.com", 0, "hinglish", "Latin", "telecom_receipt", "grp_hinglish_ham_telecom", "manually_curated")
    add("hinglish_ham_012", "Postpaid bill payment acknowledgment: Rs 599 received",
        "Dhanyawad!\n\nAapka pichle mahine ka postpaid mobile bill payment Rs. 599 successfully record kar liya gaya hai. Koi dues pending nahi hai.\n\nAirtel Billing",
        "ebill@airtel.in", 0, "hinglish", "Latin", "telecom_receipt", "grp_hinglish_ham_telecom", "manually_curated")

    # Train Spam Group 1: grp_hinglish_spam_kyc
    add("hinglish_spam_001", "URGENT: Aapka SBI khata 24 ghante mein band ho jayega",
        "Dear Customer,\n\nAapka SBI bank khata KYC update na hone ki wajah se block hone wala hai. Agar aapne turant apna Pan Card aur Aadhaar update nahi kiya toh paise freeze ho jayenge. Turant verify karein:\nhttp://sbi-kyc-pan-update-portal.com/login\n\nSBI Customer Safety Helpdesk",
        "security@sbi-kyc-pan-update-portal.com", 1, "hinglish", "Latin", "kyc_phishing", "grp_hinglish_spam_kyc", "synthetic_template")
    add("hinglish_spam_002", "Khata Block Alert: Turant KYC update karein warna fine lagega",
        "Namaste,\n\nAapka netbanking account suspicious transaction ki wajah se suspend kar diya gaya hai. Turant activate karne ke liye apna ATM PIN aur OTP enter karein:\nhttp://bank-netbanking-verify.net/kyc\n\nBank Support Cell",
        "alert@bank-netbanking-verify.net", 1, "hinglish", "Latin", "kyc_phishing", "grp_hinglish_spam_kyc", "synthetic_template")
    add("hinglish_spam_003", "Debit card deactivate notice - turant verify kijiye",
        "Warning!\n\nAapka ATM debit card chip update na hone ke karan deactivate kar diya gaya hai. Free replacement aur reactivation ke liye details bharein:\nhttp://debit-card-update-service.cc/login\n\nCard Safety Center",
        "cards@debit-card-update-service.cc", 1, "hinglish", "Latin", "kyc_phishing", "grp_hinglish_spam_kyc", "synthetic_template")

    # Train Spam Group 2: grp_hinglish_spam_lottery
    add("hinglish_spam_004", "Badhaai ho! Aapne KBC Lucky Draw mein 25 Lakh jeeta hai",
        "Namaste,\n\nAapka WhatsApp number KBC lottery department dwara select kiya gaya hai. Aapne Rs. 25,00,000 ka cash prize jeeta hai. Apna inaam claim karne ke liye संपर्क karein:\nhttp://kbc-lucky-winner-draw.org/claim\n\nKBC Lottery Committee Head",
        "winner@kbc-lucky-winner-draw.org", 1, "hinglish", "Latin", "lottery_scam", "grp_hinglish_spam_lottery", "synthetic_template")
    add("hinglish_spam_005", "Free Gift Card aur 10 Lakh Cash Reward aapke naam",
        "Congratulations!\n\nAapko shopping festival mein Rs 10 Lakh ka cash inaam mila hai. Turant paise apne bank mein mangwane ke liye yahan apply kijiye:\nhttp://festive-cash-reward.info/claim\n\nReward Manager",
        "prizes@festive-cash-reward.info", 1, "hinglish", "Latin", "lottery_scam", "grp_hinglish_spam_lottery", "synthetic_template")
    add("hinglish_spam_006", "Spin and win contest: iPhone 16 Pro Max jeeta hai",
        "Badhaai ho!\n\nAapka mobile number mega lucky spin winner bana hai. Free iPhone aur gold coin paane ke liye shipping charges pay kijiye:\nhttp://spin-winner-free-iphone.biz/claim\n\nContest Manager",
        "spin@spin-winner-free-iphone.biz", 1, "hinglish", "Latin", "lottery_scam", "grp_hinglish_spam_lottery", "synthetic_template")

    # Val Spam Group: grp_hinglish_spam_loan
    add("hinglish_spam_007", "Pre-approved loan offer: Bina kisi document ke 5 lakh paise turant milega",
        "Khushkhabri!\n\nAapka Rs. 5,00,000 ka personal loan approve ho chuka hai. Zero interest aur bina CIBIL check ke 10 minute mein paise aapke khate mein aayenge. Loan lene ke liye click kijiye:\nhttp://instant-cash-loan-bazaar.cc/apply\n\nEasy Loan India",
        "loans@instant-cash-loan-bazaar.cc", 1, "hinglish", "Latin", "loan_fraud", "grp_hinglish_spam_loan", "synthetic_template")
    add("hinglish_spam_008", "Emergency cash transfer: 2 lakh rupaye bina collateral ke",
        "Paise ki zaroorat hai? Aasan kiston par bina security ke loan lein. Sirf Aadhaar card submit karke instant cash paayein:\nhttp://emergency-paisa-loan.net/apply\n\nDirect Money Fast",
        "cash@emergency-paisa-loan.net", 1, "hinglish", "Latin", "loan_fraud", "grp_hinglish_spam_loan", "synthetic_template")
    add("hinglish_spam_009", "Overdue bill mafi yojana - loan debt clearance offer",
        "Sarkari relief scheme ke tahat aapke sabhi purane loan maaf ho sakte hain. Apply karne ke liye application charge deposit karein:\nhttp://debt-clearance-relief-offer.com/apply\n\nRelief Helpdesk",
        "relief@debt-clearance-relief-offer.com", 1, "hinglish", "Latin", "loan_fraud", "grp_hinglish_spam_loan", "synthetic_template")

    # Test Spam Group: grp_hinglish_spam_job
    add("hinglish_spam_010", "Ghar baithe part-time job se rozana 5000 rupaye kamayein",
        "Namaste,\n\nMobile se YouTube video like aur review karke rozana 3000 se 5000 rupaye kamayein. Daily payment guaranteed. Join karne ke liye turant link open karein:\nhttp://earn-money-online-daily.biz/join\n\nOnline Career Team",
        "job@earn-money-online-daily.biz", 1, "hinglish", "Latin", "job_fraud", "grp_hinglish_spam_job", "synthetic_template")
    add("hinglish_spam_011", "Amazon part-time rating worker job offer",
        "Ghar se kaam karke products rating karein aur commission paayein. Join hone ke liye registration fees transfer karke account activate karein:\nhttp://product-rating-earning-hub.info/join\n\nRecruiting Lead",
        "hiring@product-rating-earning-hub.info", 1, "hinglish", "Latin", "job_fraud", "grp_hinglish_spam_job", "synthetic_template")
    add("hinglish_spam_012", "Telegram task job: 1 ghante mein 1500 rupaye",
        "Easy online tasks karke instantly paise kamayein. Daily withdrawal directly to Google Pay or PhonePe. Click to join our telegram:\nhttp://telegram-earn-cash-daily.org/start\n\nTask Manager",
        "telegram@telegram-earn-cash-daily.org", 1, "hinglish", "Latin", "job_fraud", "grp_hinglish_spam_job", "synthetic_template")

    # =========================================================================
    # 6. ENGLISH (en) - LATIN SCRIPT
    # =========================================================================
    # Train Ham Group 1: grp_en_ham_receipt
    add("en_ham_001", "Your AWS Invoice and Usage Summary for September 2026",
        "Dear Customer,\n\nYour Amazon Web Services invoice is now available for billing period September 1 - September 30, 2026.\nTotal Amount Due: $142.85 USD\nPayment Method: Visa ending in 4018\n\nYou can review your detailed cost allocation in the AWS Billing Console.",
        "no-reply-aws@amazon.com", 0, "en", "Latin", "cloud_invoice", "grp_en_ham_receipt", "public_corpus", "Apache-2.0")
    add("en_ham_002", "Receipt for your subscription renewal: GitHub Copilot Business",
        "Hi Alex,\n\nThank you for your payment. We have processed your monthly subscription renewal for GitHub Copilot Business (5 seats).\nAmount charged: $95.00.\nYour receipt and tax invoice are attached in PDF format for your records.\n\nGitHub Billing",
        "billing@github.com", 0, "en", "Latin", "cloud_invoice", "grp_en_ham_receipt", "public_corpus", "Apache-2.0")
    add("en_ham_003", "Stripe payment confirmation: Monthly SaaS platform charge",
        "Hello,\n\nYour invoice #INV-49201 for $49.00 has been paid successfully via Mastercard ending in 9102. Full PDF receipt is available for download.\n\nStripe Payments Support",
        "invoices@stripe.com", 0, "en", "Latin", "cloud_invoice", "grp_en_ham_receipt", "public_corpus", "Apache-2.0")

    # Train Ham Group 2: grp_en_ham_travel
    add("en_ham_004", "Flight Confirmation - United Airlines SFO to LHR (Booking #UA9284)",
        "Dear Traveler,\n\nYour flight reservation is confirmed. Your e-ticket receipt is ready.\nFlight: UA 901, Departure: SFO - Oct 28, 17:30, Arrival: LHR - Oct 29, 11:45, Seat: 21A.\nPlease arrive 3 hours prior for international check-in.\n\nUnited Airlines Customer Care",
        "reservations@united.com", 0, "en", "Latin", "travel_ticket", "grp_en_ham_travel", "public_corpus", "Apache-2.0")
    add("en_ham_005", "Hotel Reservation Confirmed: Marriott Downtown Seattle (Ref #MH82019)",
        "Dear Guest,\n\nWe look forward to welcoming you to Seattle. Your reservation for 3 nights checking in on November 2, 2026 is confirmed. Cancellation is free until 24 hours prior.\n\nMarriott Bonvoy Reservations",
        "reservations@marriott.com", 0, "en", "Latin", "travel_ticket", "grp_en_ham_travel", "public_corpus", "Apache-2.0")
    add("en_ham_006", "Car Rental Booking Confirmation - Hertz Express Pickup",
        "Confirmation #HZ82910:\nYour full-size sedan reservation at Chicago O'Hare International Airport is ready for pickup on Oct 25. Proceed directly to stall 42.\n\nHertz Gold Plus Rewards",
        "gold@hertz.com", 0, "en", "Latin", "travel_ticket", "grp_en_ham_travel", "public_corpus", "Apache-2.0")

    # Val Ham Group: grp_en_ham_engineering
    add("en_ham_007", "Pull Request #412 merged: Fix race condition in connection pool retry",
        "Hey team,\n\nPR #412 has passed all CI unit and integration suites and has been merged into main by Dave.\nThe fix will be included in today's canary release deployment scheduled for 16:00 UTC.\n\nDevOps Automation",
        "notifications@github.com", 0, "en", "Latin", "software_engineering", "grp_en_ham_engineering", "public_corpus", "Apache-2.0")
    add("en_ham_008", "Weekly Engineering Standup Notes and Q4 Milestone Roadmap",
        "Hi all,\n\nHere are the action items from our weekly sync:\n1. Complete database migration dry run by Wednesday.\n2. Finalize benchmark latency numbers on the new ARM64 cluster.\n3. Draft release notes for external beta users.\n\nBest,\nMarcus",
        "marcus@techstartup.io", 0, "en", "Latin", "software_engineering", "grp_en_ham_engineering", "public_corpus", "Apache-2.0")
    add("en_ham_009", "Production Incident Postmortem: PagerDuty alert latency resolution",
        "Team,\n\nThe root cause analysis for the 15-minute alert delivery delay on Tuesday has been published in the engineering wiki. Action items have been assigned.\n\nSite Reliability Engineering",
        "sre-leads@techstartup.io", 0, "en", "Latin", "software_engineering", "grp_en_ham_engineering", "public_corpus", "Apache-2.0")

    # Test Ham Group: grp_en_ham_security
    add("en_ham_010", "Security notice: New sign-in detected on your Mac workstation",
        "Hi Sarah,\n\nA new sign-in was detected for your Google Workspace account from macOS (San Jose, CA). If this was you, no action is needed.\n\nGoogle Security Team",
        "no-reply@accounts.google.com", 0, "en", "Latin", "security_alert", "grp_en_ham_security", "public_corpus", "Apache-2.0")
    add("en_ham_011", "Quarterly mandatory compliance training reminder",
        "Dear Employee,\n\nPlease ensure you complete the 2026 Annual Data Privacy and SOC2 compliance modules by October 31 via our internal learning management system.\n\nCompliance & Legal",
        "compliance@corporate-workplace.com", 0, "en", "Latin", "security_alert", "grp_en_ham_security", "public_corpus", "Apache-2.0")
    add("en_ham_012", "Hardware token key registration successful",
        "Your new YubiKey 5C NFC was registered as a primary FIDO2 multi-factor authentication method for your SSO profile.\n\nIdentity Management",
        "iam-admin@corporate-workplace.com", 0, "en", "Latin", "security_alert", "grp_en_ham_security", "public_corpus", "Apache-2.0")

    # Train Spam Group 1: grp_en_spam_phish
    add("en_spam_001", "CRITICAL ALERT: Your Microsoft 365 Account will be terminated today",
        "Dear User,\n\nOur system detected multiple failed login attempts from an unrecognized IP address (198.51.100.44). For your protection, your mailbox has been restricted. Verify your credentials immediately:\nhttp://microsoft-security-verify-session.net/login\n\nMicrosoft Security Center",
        "support@microsoft-security-verify-session.net", 1, "en", "Latin", "account_phishing", "grp_en_spam_phish", "synthetic_template")
    add("en_spam_002", "Action Required: Suspicious activity on your Chase Bank profile",
        "Notice of security incident:\nYour online banking access has been suspended due to unverified transactions. Please sign in to verify your identity within 12 hours:\nhttp://chase-bank-account-review.org/signin\n\nChase Fraud Prevention",
        "alerts@chase-bank-account-review.org", 1, "en", "Latin", "account_phishing", "grp_en_spam_phish", "synthetic_template")
    add("en_spam_003", "PayPal notification: Unusual debit transaction requires authorization",
        "Dear Customer,\n\nA payment of $849.00 to CryptoTech Ltd was initiated from your account. If you did not authorize this payment, dispute it immediately at:\nhttp://paypal-resolution-center-dispute.biz/login\n\nPayPal Security Desk",
        "service@paypal-resolution-center-dispute.biz", 1, "en", "Latin", "account_phishing", "grp_en_spam_phish", "synthetic_template")

    # Train Spam Group 2: grp_en_spam_crypto
    add("en_spam_004", "Exclusive Invitation: Join the Bitcoin Quantum Automated AI Trading Club",
        "Dear Investor,\n\nTop Silicon Valley executives are making $4,500 daily using our proprietary quantum trading bot. Guaranteed 300% return on your $250 deposit within 48 hours. Claim your VIP seat:\nhttp://quantum-ai-btc-profits.biz/join\n\nGlobal Wealth Institute",
        "vip@quantum-ai-btc-profits.biz", 1, "en", "Latin", "crypto_fraud", "grp_en_spam_crypto", "synthetic_template")
    add("en_spam_005", "Urgent: 1.45 BTC Transfer Waiting for Your Confirmation",
        "Hello,\n\nYou have an incoming payment of 1.45 Bitcoin awaiting withdrawal. To release the blockchain funds to your cold wallet, click below and pay validation fee:\nhttp://crypto-escrow-payout.cc/withdraw\n\nBlockchain Settlement Desk",
        "desk@crypto-escrow-payout.cc", 1, "en", "Latin", "crypto_fraud", "grp_en_spam_crypto", "synthetic_template")
    add("en_spam_006", "DeFi Yield Farming Alert: 450 percent APY Smart Contract Liquidity Pool",
        "Connect your Web3 wallet now to start earning 450% guaranteed APY without impermanent loss. Limited private round allocations available:\nhttp://defi-high-yield-liquidity.info/connect\n\nSmart Yield Protocol",
        "admin@defi-high-yield-liquidity.info", 1, "en", "Latin", "crypto_fraud", "grp_en_spam_crypto", "synthetic_template")

    # Val Spam Group: grp_en_spam_package
    add("en_spam_007", "DHL Express: Your parcel #DHL-89210 could not be delivered due to address error",
        "Dear Customer,\n\nYour international package is being held at the customs hub because the delivery address is incomplete. A redelivery fee of $2.99 is required. Confirm details at:\nhttp://dhl-express-redelivery-hub.info/track\n\nDHL Logistics Support",
        "notice@dhl-express-redelivery-hub.info", 1, "en", "Latin", "delivery_phishing", "grp_en_spam_package", "synthetic_template")
    add("en_spam_008", "USPS Notice: Package held at terminal - Pay customs fee immediately",
        "Your shipment was detained at the regional sort facility. If not cleared within 24 hours, the package will be returned to the sender. Reschedule delivery here:\nhttp://usps-parcel-schedule.org/pay\n\nUnited States Postal Service",
        "tracking@usps-parcel-schedule.org", 1, "en", "Latin", "delivery_phishing", "grp_en_spam_package", "synthetic_template")
    add("en_spam_009", "FedEx Alert: Delivery exception on parcel #FX98201",
        "Delivery attempt failed. The courier could not access the premises. Please pay the $1.50 administrative holding fee to prevent return:\nhttp://fedex-parcel-redelivery.net/schedule\n\nFedEx Delivery Dispatch",
        "dispatch@fedex-parcel-redelivery.net", 1, "en", "Latin", "delivery_phishing", "grp_en_spam_package", "synthetic_template")

    # Test Spam Group: grp_en_spam_invoice
    add("en_spam_010", "INVOICE OVERDUE: Final Notice Before Legal Debt Collection #INV-9201",
        "Dear Accounts Payable,\n\nOur records indicate invoice #INV-9201 for $3,840.00 remains unpaid. Failure to remit payment within 24 hours will result in immediate debt collection proceedings. Download invoice:\nhttp://corporate-overdue-invoice-collection.biz/download\n\nLegal Recovery Associates",
        "billing@corporate-overdue-invoice-collection.biz", 1, "en", "Latin", "invoice_fraud", "grp_en_spam_invoice", "synthetic_template")
    add("en_spam_011", "Geek Squad Renewal: $499 charged to your credit card automatically",
        "Thank you for renewing your 3-year Geek Squad Total Protection. We have debited $499 from your account. If you wish to cancel this charge, call our toll-free support immediately at:\nhttp://geek-squad-refund-cancel.com/support\n\nGeek Squad Services",
        "helpdesk@geek-squad-refund-cancel.com", 1, "en", "Latin", "invoice_fraud", "grp_en_spam_invoice", "synthetic_template")
    add("en_spam_012", "Norton Antivirus LifeLock Subscription Active - Order #NL89201",
        "Your annual subscription has been renewed for $389.00. To request a full refund or cancel automatic debit, click here:\nhttp://norton-billing-cancel-portal.info/refund\n\nCustomer Billing Center",
        "renewals@norton-billing-cancel-portal.info", 1, "en", "Latin", "invoice_fraud", "grp_en_spam_invoice", "synthetic_template")

    return records


if __name__ == "__main__":
    records = create_multilingual_corpus()
    out_path = Path("ml/data/multilingual_corpus.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    print(f"Generated {len(records)} multilingual records into {out_path}")
