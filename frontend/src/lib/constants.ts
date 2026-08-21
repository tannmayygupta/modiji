// Shared domain constants.
// The landing page quotes counts from these arrays, so the numbers on "/"
// can never drift away from what the wizard actually offers.

export const EDUCATION_LEVELS = ["10TH", "12TH", "ITI", "DIPLOMA", "GRADUATE", "PG"];

export const EDUCATION_LABELS: Record<string, string> = {
  "10TH": "10th Pass",
  "12TH": "12th Pass",
  "ITI": "ITI / Vocational",
  "DIPLOMA": "Diploma",
  "GRADUATE": "Undergraduate",
  "PG": "Post Graduate",
};

export const COMMON_SKILLS = [
  "Python", "JavaScript", "Java", "SQL", "React", "Node.js", "C++",
  "Data Analysis", "Excel", "Communication", "Machine Learning",
  "HTML/CSS", "Git", "MongoDB", "Django", "Flask", "REST API",
  "AutoCAD", "Marketing", "Sales", "HR", "Content Writing",
  "Graphic Design", "Video Editing", "UI/UX Design", "DevOps",
  "Cloud Computing", "Networking", "Cybersecurity", "Power BI",
  "Tally", "SAP", "Project Management", "Six Sigma",
];

export const SECTORS = [
  "IT & Software Development", "Banking & Financial Services",
  "Healthcare", "Manufacturing & Industrial", "Automotive",
  "Pharmaceutical", "Oil, Gas & Energy", "Telecom",
  "Infrastructure & Construction", "FMCG",
  "Retail & Consumer Durables", "Agriculture & Allied",
  "Media, Entertainment & Education", "Consulting Services",
  "Travel & Hospitality", "Chemical", "Metals & Mining",
  "Aviation & Defence", "Textile Manufacturing",
  "Cement & Building Materials", "Gems & Jewellery",
];

export const STATES = [
  "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar",
  "Chhattisgarh", "Goa", "Gujarat", "Haryana",
  "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala",
  "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
  "Mizoram", "Nagaland", "Odisha", "Punjab",
  "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana",
  "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
  "Delhi", "Chandigarh", "Jammu & Kashmir", "Ladakh",
  "Puducherry", "Andaman & Nicobar",
];

/** Steps 1-6 of the profile wizard (step 0 is Aadhaar KYC, shown before the bar). */
export const WIZARD_TOTAL_STEPS = 6;
