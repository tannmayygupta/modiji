import zipfile
import io
from lxml import etree
from datetime import datetime

class AadhaarParserError(Exception):
    pass

def parse_aadhaar_zip(zip_bytes: bytes, share_code: str) -> dict:
    """
    Parse UIDAI Aadhaar offline XML ZIP file.
    Returns extracted profile data. NEVER returns Aadhaar number.
    """
    if not share_code.isdigit() or len(share_code) != 4:
        raise AadhaarParserError("Share code must be exactly 4 digits")

    try:
        # In a real scenario, python's zipfile using a password is slow and lacks AES support,
        # but UIDAI standard offline XML zips use standard ZipCrypto with the share_code.
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            # Set the password for decryption
            z.setpassword(share_code.encode('utf-8'))
            
            xml_files = [f for f in z.namelist() if f.endswith('.xml')]
            if not xml_files:
                raise AadhaarParserError("No XML file found in ZIP")
            
            try:
                xml_bytes = z.read(xml_files[0])
            except RuntimeError as e:
                if 'Bad password' in str(e) or 'password required' in str(e):
                    raise AadhaarParserError("Invalid share code.")
                raise AadhaarParserError("Error reading ZIP contents. Ensure it's a valid Aadhaar ZIP.")
                
    except zipfile.BadZipFile:
        raise AadhaarParserError("Invalid ZIP file. Please download your Aadhaar XML again.")

    try:
        root = etree.fromstring(xml_bytes)
    except etree.XMLSyntaxError:
        raise AadhaarParserError("Corrupted XML file. Please re-download.")

    # The UIDAI XML structure usually has a root tag like OfflinePaperlessKyc
    # Search for Poi and Poa anywhere in the tree
    poi = root.find('.//Poi')   # Proof of Identity
    poa = root.find('.//Poa')   # Proof of Address

    if poi is None or poa is None:
        raise AadhaarParserError("Invalid Aadhaar XML structure. Missing Poi or Poa.")

    dob_str = poi.get('dob', '')
    age = 0
    dob_date = None
    if dob_str:
        try:
            # Format is DD-MM-YYYY
            dob_date = datetime.strptime(dob_str, '%d-%m-%Y').date()
            today = datetime.today().date()
            age = today.year - dob_date.year - (
                (today.month, today.day) < (dob_date.month, dob_date.day)
            )
        except ValueError:
            pass

    district = poa.get('dist', '') or poa.get('vtc', '')
    state    = poa.get('state', '')

    ASPIRATIONAL_DISTRICTS = [
        "Vizianagaram", "Nandurbar", "Yavatmal", "Washim", "Osmanabad",
        "Raigad", "Gadchiroli", "Gondia", "Beed", "Hingoli", "Jalna",
        "Palghar", "Nawapara", "Nabarangpur", "Malkangiri", "Rayagada",
        "Koraput", "Dhenkanal", "Gajapati", "Kandhamal", "Bolangir",
        "Nuapada", "Kalahandi", "Bargarh", "Chitrakoot", "Sidhi",
        "Singrauli", "Tikamgarh", "Datia", "Vidisha", "Sheopur",
        "Rajgarh", "Chhatarpur", "Damoh", "Raisen", "Sehore",
        "Bahraich", "Shravasti", "Balrampur", "Kushinagar", "Chandauli",
        "Chitrakoot", "Sonbhadra", "Fatehpur", "Ambedkar Nagar", "Siddharthnagar",
        "Pilibhit", "Kheri", "Hardoi", "Bulandshahr", "Rae Bareli",
        "Raichur", "Yadgir", "Koppal", "Bidar", "Chamarajanagar",
        "Virudhunagar", "Ariyalur", "Dharmapuri", "Ramanthapuram", "Villupuram",
        "Banka", "Araria", "Aurangabad", "Gaya", "Jamui",
        "Katihar", "Khagaria", "Kishanganj", "Muzaffarpur", "Nawada",
        "Purnia", "Sheohar", "Sitamarhi", "Supaul", "West Champaran",
        "Dantewada", "Bijapur", "Sukma", "Narayanpur", "Kondagaon",
        "Bastar", "Rajnandgaon", "Kanker", "Jashpur", "Surguja",
        "Ribhoi", "East Khasi Hills", "South Garo Hills", "West Garo Hills",
        "Hamirpur", "Chamba", "Kinnaur", "Lahaul Spiti", "Sirmaur",
        "Poonch", "Rajouri", "Ramban", "Reasi", "Kishtwar",
        "Bokaro", "Garhwa", "Giridih", "Hazaribagh", "Khunti",
        "Latehar", "Pakur", "Palamu", "Sahebganj", "Simdega",
        "West Singhbhum", "Dumka", "Godda", "Jamtara", "Deoghar"
    ]

    is_rural = any(
        d.lower() in district.lower()
        for d in ASPIRATIONAL_DISTRICTS
    ) or poa.get('type', '') in ['Village', 'Rural']

    return {
        "full_name":   poi.get('name', '').strip(),
        "date_of_birth": dob_date.isoformat() if dob_date else None,
        "age":         age,
        "gender":      poi.get('gender', 'M'),
        "district":    district.strip(),
        "state":       state.strip(),
        "pincode":     poa.get('pc', '').strip(),
        "is_rural":    is_rural,
        "is_eligible": 18 <= age <= 25
    }
