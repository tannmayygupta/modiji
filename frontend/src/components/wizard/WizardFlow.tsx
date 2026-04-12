"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { motion, AnimatePresence } from "framer-motion";
import {
  Lock, GraduationCap, Lightbulb, Building2, MapPin, Camera,
  CheckCircle2, ShieldCheck, Upload, FileText, AlertTriangle
} from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const EDUCATION_LEVELS = ["10TH", "12TH", "ITI", "DIPLOMA", "GRADUATE", "PG"];
const EDUCATION_LABELS: Record<string, string> = {
  "10TH": "10th Pass",
  "12TH": "12th Pass",
  "ITI": "ITI / Vocational",
  "DIPLOMA": "Diploma",
  "GRADUATE": "Undergraduate",
  "PG": "Post Graduate",
};
const COMMON_SKILLS = [
  "Python", "JavaScript", "Communication", "Java", "SQL", "Excel",
  "Marketing", "Data Analysis", "HR", "Sales", "React", "Node.js"
];
const SECTORS = [
  "IT & Software", "Banking & Finance", "Healthcare", "Manufacturing",
  "Retail & E-Commerce", "Education", "Marketing & Sales"
];
const STATES = [
  "Maharashtra", "Karnataka", "Delhi", "Tamil Nadu", "Uttar Pradesh",
  "West Bengal", "Gujarat", "Rajasthan", "Madhya Pradesh", "Bihar"
];

function getToken() {
  if (typeof window !== "undefined") return localStorage.getItem("pmis_token");
  return null;
}

export function WizardFlow() {
  const router = useRouter();

  // Steps: 0=Aadhaar, 1=Upload Docs, 2=Education, 3=Skills, 4=Sectors, 5=Location, 6=Video
  const [step, setStep] = useState(0);
  const totalSteps = 6; // Steps 1-6 shown in progress
  const fileInputRef = useRef<HTMLInputElement>(null);
  const docInputRef = useRef<HTMLInputElement>(null);
  const videoInputRef = useRef<HTMLInputElement>(null);
  const [uploadedResumeName, setUploadedResumeName] = useState<string | null>(null);

  // Auth state synced with backend
  const [authStep, setAuthStep] = useState(1);
  const [authLoading, setAuthLoading] = useState(true);

  // Aadhaar form
  const [aadhaarZip, setAadhaarZip] = useState<File | null>(null);
  const [shareCode, setShareCode] = useState("");
  const [verifyingAadhaar, setVerifyingAadhaar] = useState(false);
  const [aadhaarError, setAadhaarError] = useState("");

  // Document upload
  const [uploadingDoc, setUploadingDoc] = useState(false);
  const [uploadedDocs, setUploadedDocs] = useState<any[]>([]);
  const [selectedDocType, setSelectedDocType] = useState("10th_marksheet");

  // Wizard form state
  const [educationLevel, setEducationLevel] = useState("");
  const [skills, setSkills] = useState<string[]>([]);
  const [sectorPreferences, setSectorPreferences] = useState<string[]>([]);
  const [stateName, setStateName] = useState("");
  const [locationPref, setLocationPref] = useState("HOME_STATE");

  // Video parsing state
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [uploadingVideo, setUploadingVideo] = useState(false);
  const [videoScores, setVideoScores] = useState<any>(null);
  const [videoProgress, setVideoProgress] = useState("");

  // Resume parsing
  const [isParsing, setIsParsing] = useState(false);
  const [parseSuccess, setParseSuccess] = useState(false);

  // On mount, check the user's current auth_step
  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push("/login");
      return;
    }

    fetch(`${API}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.json())
      .then((data) => {
        setAuthStep(data.auth_step || 1);
        // Jump to appropriate step based on auth level
        if (data.auth_step === 1) setStep(0);
        else if (data.auth_step === 2) setStep(1);
        else setStep(2);
      })
      .catch(() => router.push("/login"))
      .finally(() => setAuthLoading(false));
  }, []);

  // Fetch uploaded docs for step 1
  useEffect(() => {
    if (authStep >= 2) {
      const token = getToken();
      if (!token) return;
      fetch(`${API}/documents/my-documents`, {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((r) => r.json())
        .then((data) => setUploadedDocs(data.documents || []))
        .catch(() => {});
    }
  }, [authStep]);

  const toggleSelection = (item: string, list: string[], setList: (l: string[]) => void, max: number) => {
    if (list.includes(item)) setList(list.filter((i) => i !== item));
    else if (list.length < max) setList([...list, item]);
  };

  // STEP 0: Real Aadhaar offline XML verification
  const handleAadhaarVerify = async () => {
    setAadhaarError("");
    if (!aadhaarZip) {
      setAadhaarError("Please upload your Aadhaar XML ZIP file.");
      return;
    }
    if (shareCode.length !== 4 || !/^\d+$/.test(shareCode)) {
      setAadhaarError("Share code must be exactly 4 digits.");
      return;
    }

    setVerifyingAadhaar(true);
    try {
      const token = getToken();
      const formData = new FormData();
      formData.append("file", aadhaarZip);
      formData.append("share_code", shareCode);

      const res = await fetch(`${API}/digilocker/verify-aadhaar`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Verification failed");
      }

      setAuthStep(2);
      setStep(1);
    } catch (err: any) {
      setAadhaarError(err.message);
    } finally {
      setVerifyingAadhaar(false);
    }
  };

  // STEP 1: Real document upload
  const handleDocUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadingDoc(true);
    try {
      const token = getToken();
      const formData = new FormData();
      formData.append("file", file);
      formData.append("doc_type", selectedDocType);

      const res = await fetch(`${API}/documents/upload`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Upload failed");
      }

      // Refresh docs list
      const docsRes = await fetch(`${API}/documents/my-documents`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const docsData = await docsRes.json();
      setUploadedDocs(docsData.documents || []);
      setAuthStep(docsData.auth_step || authStep);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setUploadingDoc(false);
    }
  };

  // Resume upload (for skill extraction)
  const handleResumeUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsParsing(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch(`${API}/resume/parse`, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      if (data.data?.education_level && EDUCATION_LEVELS.includes(data.data.education_level)) {
        setEducationLevel(data.data.education_level);
      }
      if (data.data?.skills?.length > 0) {
        setSkills(data.data.skills.slice(0, 5));
      }
      setParseSuccess(true);
      setUploadedResumeName(file.name);
    } catch {
      alert("Failed to parse resume.");
    } finally {
      setIsParsing(false);
    }
  };

  const handleVideoUpload = async () => {
    if (!videoFile) return;
    setUploadingVideo(true);
    setVideoProgress("Uploading video...");
    try {
      const token = getToken();
      const formData = new FormData();
      formData.append("file", videoFile);
      
      setVideoProgress("Transcribing and analyzing with AI...");
      const res = await fetch(`${API}/candidates/upload-video`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Video analysis failed (${res.status})`);
      }
      
      const data = await res.json();
      setVideoScores(data.scores);
      setVideoProgress("");
    } catch (err: any) {
      console.error("Video upload error:", err);
      alert(err.message || "Something went wrong.");
      setVideoProgress("");
    } finally {
      setUploadingVideo(false);
    }
  };

  const handleNext = () => {
    if (step < totalSteps) setStep(step + 1);
    else router.push("/recommendations");
  };

  if (authLoading) {
    return (
      <div className="w-full max-w-2xl mx-auto space-y-6 relative z-10 pt-12">
        <Skeleton className="h-8 w-48 mx-auto" />
        <Skeleton className="h-[450px] w-full rounded-none border-2 border-gray-200" />
      </div>
    );
  }

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6 relative z-10">
      {/* Progress (visible for steps 1+) */}
      {step >= 1 && (
        <div className="space-y-2 mb-8">
          <h2 className="text-center font-bold text-muted-foreground text-xs uppercase tracking-widest">
            Phase {Math.max(step, 1)} // {totalSteps}
          </h2>
          <Progress value={(Math.max(step, 1) / totalSteps) * 100} className="w-full h-1 bg-gray-200" />
        </div>
      )}

      <Card className="border-2 border-black dark:border-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] dark:shadow-[8px_8px_0px_0px_rgba(255,255,255,1)] rounded-none relative min-h-[450px] flex flex-col bg-white dark:bg-[#0a0a0a]">
        <CardContent className="flex-1 px-4 sm:px-10 pt-10 pb-6">
          <AnimatePresence mode="wait">

            {/* STEP 0: AADHAAR VERIFICATION */}
            {step === 0 && (
              <motion.div key="s0" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, scale: 0.95 }} className="space-y-8">
                <div className="flex flex-col items-center text-center space-y-4">
                  <div className="bg-black dark:bg-white text-white dark:text-black p-4"><ShieldCheck size={48} strokeWidth={1.5} /></div>
                  <h3 className="text-3xl font-black uppercase tracking-tight dark:text-white">Offline Aadhaar KYC</h3>
                  <p className="text-muted-foreground max-w-md font-medium">
                    Upload your offline Aadhaar XML ZIP file from myaadhaar.uidai.gov.in. Your raw credentials are NEVER stored.
                  </p>
                </div>

                <div className="bg-blue-50 border-l-4 border-blue-500 p-4 text-xs font-bold text-blue-900 leading-relaxed">
                  <p className="mb-2 uppercase tracking-widest text-blue-700">How to get your Aadhaar XML file:</p>
                  <ol className="list-decimal pl-4 space-y-1">
                    <li>Go to myaadhaar.uidai.gov.in on your phone or laptop</li>
                    <li>Login with your Aadhaar number + OTP</li>
                    <li>Click "Offline e-KYC" → Create a 4-digit share code → "Download"</li>
                    <li>You will get a ZIP file. Upload that file below.</li>
                  </ol>
                </div>

                {aadhaarError && (
                  <div className="border-2 border-red-500 bg-red-50 p-3 text-sm font-bold text-red-700 flex items-center gap-2">
                    <AlertTriangle size={16} /> {aadhaarError}
                  </div>
                )}

                <div className="space-y-4">
                  <div>
                    <label className="text-xs font-black uppercase tracking-widest text-gray-500 mb-1 block">Aadhaar XML ZIP File</label>
                    <input
                      type="file"
                      accept=".zip"
                      onChange={(e) => setAadhaarZip(e.target.files?.[0] || null)}
                      className="w-full p-4 border-2 border-black dark:border-white focus:outline-none font-bold bg-white dark:bg-black dark:text-white"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-black uppercase tracking-widest text-gray-500 mb-1 block">4-Digit Share Code</label>
                    <input
                      type="text"
                      maxLength={4}
                      value={shareCode}
                      onChange={(e) => setShareCode(e.target.value.replace(/\D/g, ""))}
                      className="w-full p-4 border-2 border-black dark:border-white focus:outline-none font-bold text-center tracking-widest text-lg dark:text-white dark:bg-black"
                      placeholder="XXXX"
                    />
                  </div>
                </div>

                <Button
                  onClick={handleAadhaarVerify}
                  disabled={verifyingAadhaar}
                  className="w-full h-14 rounded-none bg-black dark:bg-white text-white dark:text-black font-black uppercase text-base border-2 border-black dark:border-white shadow-[4px_4px_0px_0px_rgba(0,0,0,0.2)] dark:shadow-[4px_4px_0px_0px_rgba(255,255,255,0.2)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none transition-all"
                >
                  {verifyingAadhaar ? "Verifying..." : <><Lock className="mr-2 h-5 w-5" /> Verify Identity</>}
                </Button>
              </motion.div>
            )}

            {/* STEP 1: DOCUMENT UPLOAD */}
            {step === 1 && (
              <motion.div key="s1" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-6">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-2xl font-black uppercase flex items-center gap-3 dark:text-white">
                      <FileText className="h-7 w-7" /> Upload Documents
                    </h3>
                    <p className="text-muted-foreground mt-2 font-medium dark:text-gray-400">
                      Upload your 10th, 12th marksheets or diploma. Admin will verify them against your Aadhaar name.
                    </p>
                  </div>
                  <div className="bg-black dark:bg-white text-white dark:text-black text-[10px] uppercase tracking-widest font-bold px-3 py-1 flex items-center gap-1">
                    <CheckCircle2 className="h-3 w-3" /> Aadhaar Done
                  </div>
                </div>

                <div className="space-y-3">
                  <label className="text-xs font-black uppercase tracking-widest text-gray-500 dark:text-gray-400 block">Document Type</label>
                  <select
                    value={selectedDocType}
                    onChange={(e) => setSelectedDocType(e.target.value)}
                    className="w-full p-3 border-2 border-black dark:border-white font-bold bg-white dark:bg-black dark:text-white"
                  >
                    <option value="10th_marksheet">10th Marksheet</option>
                    <option value="12th_marksheet">12th Marksheet</option>
                    <option value="diploma_certificate">Diploma Certificate</option>
                  </select>
                </div>

                <input type="file" accept=".pdf,.jpg,.jpeg,.png" className="hidden" ref={docInputRef} onChange={handleDocUpload} />
                <Button
                  onClick={() => docInputRef.current?.click()}
                  disabled={uploadingDoc}
                  variant="outline"
                  className="w-full h-14 rounded-none border-2 border-dashed border-black dark:border-white font-black uppercase bg-white dark:bg-black text-black dark:text-white hover:bg-gray-50 dark:hover:bg-gray-900 cursor-pointer"
                >
                  <Upload className="mr-2 h-5 w-5" />
                  {uploadingDoc ? "Uploading..." : "Upload File (PDF / Image)"}
                </Button>

                {/* Uploaded docs list */}
                {uploadedDocs.length > 0 && (
                  <div className="space-y-2 pt-4 border-t-2 border-gray-200 dark:border-gray-800">
                    <p className="text-xs font-black uppercase tracking-widest text-gray-500 dark:text-gray-400">Uploaded Documents</p>
                    {uploadedDocs.map((d: any) => (
                      <div key={d.id} className="flex items-center justify-between border-2 border-gray-200 dark:border-gray-700 p-3 bg-white dark:bg-black">
                        <span className="font-bold text-sm dark:text-white">{d.doc_type.replace(/_/g, " ")}</span>
                        <span className={`text-xs font-black uppercase px-2 py-1 ${
                          d.status === "APPROVED" ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300" :
                          d.status === "REJECTED" ? "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300" :
                          "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300"
                        }`}>
                          {d.status}
                        </span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Info message */}
                <div className="border-2 border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/50 p-4 text-xs text-gray-600 dark:text-gray-300 font-bold">
                  After uploading, an admin will review your documents. Once approved, you will be able to apply to internships.
                  You can proceed with profile setup while waiting for approval.
                </div>
              </motion.div>
            )}

            {/* STEP 2: EDUCATION */}
            {step === 2 && (
              <motion.div key="s2" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-8">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-2xl font-black uppercase flex items-center gap-3 dark:text-white">
                      <GraduationCap className="h-8 w-8" /> Academic Profile
                    </h3>
                    <p className="text-muted-foreground mt-2 font-medium dark:text-gray-400">Select your highest education level.</p>
                  </div>
                </div>

                {/* Resume AI parser */}
                <div className={`border-2 border-dashed p-5 flex flex-col items-center justify-center relative transition-colors ${uploadedResumeName ? 'bg-green-50/50 border-green-500 dark:bg-green-900/20 dark:border-green-600' : 'bg-gray-50 border-gray-300 dark:bg-black dark:border-gray-700'}`}>
                  {uploadedResumeName ? (
                    <CheckCircle2 className="h-6 w-6 text-green-600 dark:text-green-400 mb-2" />
                  ) : (
                    <Upload className="h-6 w-6 text-gray-400 dark:text-gray-500 mb-2" />
                  )}
                  
                  <h4 className="text-sm font-bold text-black dark:text-white mb-1">
                    {uploadedResumeName ? "Resume Extracted" : "Upload Resume (PDF)"}
                  </h4>
                  
                  <p className="text-xs text-gray-500 dark:text-gray-400 text-center mb-4 max-w-[250px]">
                    {uploadedResumeName 
                      ? `AI successfully parsed: ${uploadedResumeName}` 
                      : "Our AI will extract your skills and education from your resume."}
                  </p>
                  
                  <input type="file" accept=".pdf" className="hidden" ref={fileInputRef} onChange={handleResumeUpload} />
                  
                  <Button 
                    variant="outline" 
                    className={`rounded-none border-2 border-black dark:border-white font-bold text-xs h-9 cursor-pointer hover:-translate-y-0.5 transition-transform ${uploadedResumeName ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100 border-green-800 dark:border-green-400' : 'dark:text-white hover:bg-gray-100 dark:hover:bg-gray-900'}`}
                    onClick={() => fileInputRef.current?.click()} 
                    disabled={isParsing}
                  >
                    {isParsing ? "Scanning..." : uploadedResumeName ? "Replace Resume" : "Browse Files"}
                  </Button>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  {EDUCATION_LEVELS.map((level) => (
                    <div key={level} onClick={() => setEducationLevel(level)}
                      className={`cursor-pointer border-2 p-4 text-center font-bold transition-all ${
                        educationLevel === level ? "border-black bg-black text-white dark:bg-white dark:text-black dark:border-white" : "border-gray-200 text-gray-500 hover:border-black hover:text-black dark:hover:border-white dark:hover:text-white"
                      }`}
                    >{EDUCATION_LABELS[level] || level}</div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* STEP 3: SKILLS */}
            {step === 3 && (
              <motion.div key="s3" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-8">
                <div>
                  <h3 className="text-2xl font-black uppercase flex items-center gap-3 dark:text-white"><Lightbulb className="h-7 w-7" /> Skill Inventory</h3>
                  <p className="text-muted-foreground mt-2 font-medium">Select up to 5 core competencies.</p>
                </div>
                <div className="flex flex-wrap gap-3">
                  {COMMON_SKILLS.map((skill) => (
                    <div key={skill} onClick={() => toggleSelection(skill, skills, setSkills, 5)}
                      className={`cursor-pointer px-4 py-2 text-sm font-bold border-2 transition-all ${
                        skills.includes(skill) ? "border-black bg-black text-white dark:bg-white dark:text-black dark:border-white" : "border-gray-200 text-gray-600 dark:text-gray-400 hover:border-black dark:hover:border-white dark:hover:text-white"
                      }`}
                    >{skill}</div>
                  ))}
                </div>
                <div className="h-1 w-full bg-gray-100 dark:bg-gray-800"><div className="h-full bg-black dark:bg-white transition-all" style={{ width: `${(skills.length / 5) * 100}%` }} /></div>
              </motion.div>
            )}

            {/* STEP 4: SECTORS */}
            {step === 4 && (
              <motion.div key="s4" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-8">
                <div>
                  <h3 className="text-2xl font-black uppercase flex items-center gap-3 dark:text-white"><Building2 className="h-7 w-7" /> Industry Focus</h3>
                  <p className="text-muted-foreground mt-2 font-medium">Target your preferred sectors (up to 3).</p>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {SECTORS.map((sec) => (
                    <div key={sec} onClick={() => toggleSelection(sec, sectorPreferences, setSectorPreferences, 3)}
                      className={`cursor-pointer border-2 p-4 font-bold transition-all ${
                        sectorPreferences.includes(sec) ? "border-black bg-black text-white dark:bg-white dark:text-black dark:border-white shadow-[4px_4px_0px_0px_rgba(0,0,0,0.2)] dark:shadow-[4px_4px_0px_0px_rgba(255,255,255,0.2)]" : "border-gray-200 hover:border-black dark:hover:border-white dark:text-gray-400 dark:hover:text-white"
                      }`}
                    >{sec}</div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* STEP 5: LOCATION */}
            {step === 5 && (
              <motion.div key="s5" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-8">
                <div>
                  <h3 className="text-2xl font-black uppercase flex items-center gap-3 dark:text-white"><MapPin className="h-7 w-7" /> Logistics</h3>
                  <p className="text-muted-foreground mt-2 font-medium">Define your geographical constraints.</p>
                </div>
                <div className="space-y-3">
                  <p className="font-bold text-sm uppercase tracking-wide">Primary State</p>
                  <select className="w-full p-4 border-2 border-black dark:border-white focus:outline-none rounded-none bg-white dark:bg-black font-bold dark:text-white" value={stateName} onChange={(e) => setStateName(e.target.value)}>
                    <option value="" disabled>SELECT REGION</option>
                    {STATES.map((s) => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
                <div className="space-y-3 pt-6">
                  <p className="font-bold text-sm uppercase tracking-wide">Mobility Scope</p>
                  <div className="grid grid-cols-1 gap-3">
                    {(["HOME_STATE", "NEARBY", "PAN_INDIA"] as const).map((loc) => {
                      const labels: Record<string, string> = { HOME_STATE: "Strictly Home State", NEARBY: "Adjoining Regions", PAN_INDIA: "Anywhere in India" };
                      return (
                        <div key={loc} onClick={() => setLocationPref(loc)}
                          className={`cursor-pointer border-2 p-4 font-bold transition-all ${
                            locationPref === loc ? "border-black bg-black text-white dark:bg-white dark:text-black dark:border-white" : "border-gray-200 text-gray-500 hover:border-black hover:text-black dark:hover:border-white dark:hover:text-white"
                          }`}
                        >{labels[loc]}</div>
                      );
                    })}
                  </div>
                </div>
              </motion.div>
            )}

            {/* STEP 6: VIDEO INTRODUCTION */}
            {step === 6 && (
              <motion.div key="s6" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-6">
                <div>
                  <h3 className="text-2xl font-black uppercase flex items-center gap-3 dark:text-white">
                    <Camera className="h-7 w-7" /> Video Profile
                  </h3>
                  <p className="text-muted-foreground mt-2 font-medium dark:text-gray-400">
                    A short introduction boosts your matching score significantly. Optional but highly recommended.
                  </p>
                </div>

                {!videoScores ? (
                  <div className="space-y-6">
                    <div className="bg-gray-50 dark:bg-[#111] border-2 border-black dark:border-white p-4 text-left">
                      <p className="font-bold text-sm uppercase tracking-wide mb-2 dark:text-white">What to include (2-3 min)</p>
                      <ul className="text-sm space-y-2 font-medium text-gray-700 dark:text-gray-300 list-disc pl-5">
                        <li>Who you are and your educational background</li>
                        <li>Top 2-3 skills and your experience with them</li>
                        <li>What excites you about the industry</li>
                      </ul>
                    </div>

                    <input type="file" accept="video/mp4,video/webm,video/quicktime,audio/mp3,audio/wav" className="hidden" ref={videoInputRef} onChange={(e) => {
                      if (e.target.files) setVideoFile(e.target.files[0]);
                      setVideoScores(null);
                    }} />

                    <div className="flex flex-col gap-3">
                      <Button
                        onClick={() => videoInputRef.current?.click()}
                        disabled={uploadingVideo}
                        variant="outline"
                        className="w-full h-14 rounded-none border-2 border-dashed border-black dark:border-white font-black uppercase bg-white dark:bg-black text-black dark:text-white hover:bg-gray-50 dark:hover:bg-gray-900 transition-all justify-start px-6"
                      >
                        <Upload className="mr-3 h-5 w-5" />
                        {videoFile ? videoFile.name : "Select Video / Audio"}
                      </Button>

                      <Button
                        onClick={handleVideoUpload}
                        disabled={!videoFile || uploadingVideo}
                        className="w-full h-14 rounded-none bg-[#1d9e75] text-white font-black uppercase text-base border-2 border-black dark:border-white shadow-[4px_4px_0px_0px_rgba(0,0,0,0.2)] dark:shadow-[4px_4px_0px_0px_rgba(255,255,255,0.2)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all disabled:opacity-50 disabled:bg-gray-400"
                      >
                        {uploadingVideo ? videoProgress : "Upload & Analyze with AI"}
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-6 text-left">
                    <div className="flex items-center gap-4 bg-green-50 border-2 border-green-500 p-4">
                      <div className="bg-green-500 text-white p-3 font-black text-xl">
                        {videoScores.overall_score}
                      </div>
                      <div>
                        <p className="font-bold text-green-900">Analysis Complete</p>
                        <p className="text-xs font-bold uppercase tracking-widest text-green-700">Overall Communication Score</p>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div className="border-2 border-black dark:border-white p-4 text-center bg-white dark:bg-[#111]">
                        <p className="text-2xl font-black dark:text-white">{videoScores.confidence_score}</p>
                        <p className="text-[10px] font-bold uppercase tracking-widest text-gray-500">Confidence</p>
                      </div>
                      <div className="border-2 border-black dark:border-white p-4 text-center bg-white dark:bg-[#111]">
                        <p className="text-2xl font-black dark:text-white">{videoScores.clarity_score}</p>
                        <p className="text-[10px] font-bold uppercase tracking-widest text-gray-500">Clarity</p>
                      </div>
                    </div>

                    <div className="border-2 border-black dark:border-white p-4 bg-white dark:bg-[#111]">
                      <p className="font-bold text-xs uppercase tracking-widest mb-2 dark:text-white">Top Strength</p>
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300">{videoScores.top_strength}</p>
                    </div>

                    <div className="border-2 border-black dark:border-white p-4 bg-white dark:bg-[#111]">
                      <p className="font-bold text-xs uppercase tracking-widest mb-2 dark:text-white">AI Feedback</p>
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300">{videoScores.feedback}</p>
                    </div>
                  </div>
                )}
              </motion.div>
            )}

          </AnimatePresence>
        </CardContent>

        {/* NAVIGATION FOOTER */}
        {step >= 1 && (
          <CardFooter className="bg-white dark:bg-[#0a0a0a] border-t-2 border-black dark:border-white p-4 sm:px-8 mt-auto flex justify-between">
            <Button variant="outline" onClick={() => setStep(Math.max(1, step - 1))} className="w-24 rounded-none border-2 border-black dark:border-white font-bold hover:bg-gray-100 dark:hover:bg-gray-900 dark:text-white cursor-pointer">
              BACK
            </Button>
            <Button
              onClick={handleNext}
              className="w-32 rounded-none bg-black dark:bg-white text-white dark:text-black font-bold border-2 border-black dark:border-white shadow-[4px_4px_0px_0px_rgba(0,0,0,0.2)] dark:shadow-[4px_4px_0px_0px_rgba(255,255,255,0.2)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all cursor-pointer"
              disabled={
                (step === 2 && !educationLevel) ||
                (step === 3 && skills.length === 0) ||
                (step === 4 && sectorPreferences.length === 0) ||
                (step === 5 && (!stateName || !locationPref))
              }
            >
              {step === totalSteps ? "EXECUTE" : "NEXT"}
            </Button>
          </CardFooter>
        )}
      </Card>
    </div>
  );
}
