"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { User, FileText, CheckCircle2, XCircle, Clock, Save, BrainCircuit, ExternalLink, Briefcase, Upload, Edit3 } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

function getToken() {
  if (typeof window !== "undefined") return localStorage.getItem("pmis_token");
  return null;
}

export default function ProfilePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<any>(null);
  const [documents, setDocuments] = useState<any[]>([]);
  const [isUpdating, setIsUpdating] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");
  const [updateError, setUpdateError] = useState("");
  const [fetchError, setFetchError] = useState("");
  const [uploadingVideo, setUploadingVideo] = useState(false);
  const [videoProgress, setVideoProgress] = useState("");
  const [appliedJobs, setAppliedJobs] = useState<any[]>([]);
  const [savedJobs, setSavedJobs] = useState<any[]>([]);

  const [formData, setFormData] = useState({
    name: "",
    phone: "",
    state: "",
    district: "",
  });

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push("/login");
      return;
    }

    // Fetch Profile
    const fetchProfile = async () => {
      try {
        const res = await fetch(`${API}/candidates/me`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (!res.ok) throw new Error();
        const data = await res.json();
        setProfile(data);
        setFormData({
          name: data.name || "",
          phone: data.phone || "",
          state: data.state || "",
          district: data.district || "",
        });
      } catch (err: any) {
        setFetchError("Could not load your profile. Please refresh or login again.");
      }
    };

    // Fetch Documents
    const fetchDocs = async () => {
      try {
        const res = await fetch(`${API}/documents/my-documents`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setDocuments(data.documents || []);
        }
      } catch (err) { }
    };

    // Fetch Applied & Saved
    const fetchInteractions = async () => {
      try {
        const [appliedRes, savedRes] = await Promise.all([
          fetch(`${API}/interactions/applied`, { headers: { Authorization: `Bearer ${token}` } }),
          fetch(`${API}/interactions/saved`, { headers: { Authorization: `Bearer ${token}` } })
        ]);

        if (appliedRes.ok) {
          const data = await appliedRes.json();
          setAppliedJobs(data.internships || []);
        }
        if (savedRes.ok) {
          const data = await savedRes.json();
          setSavedJobs(data.internships || []);
        }
      } catch (err) { }
    };

    Promise.all([fetchProfile(), fetchDocs(), fetchInteractions()]).finally(() => setLoading(false));
  }, [router]);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsUpdating(true);
    setSuccessMsg("");
    setUpdateError("");

    try {
      const token = getToken();
      const res = await fetch(`${API}/candidates/me`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(formData),
      });

      if (res.ok) {
        setSuccessMsg("Profile updated successfully!");
        setTimeout(() => setSuccessMsg(""), 3000);
      }
    } catch {
      setUpdateError("Failed to update profile. Please try again.");
    } finally {
      setIsUpdating(false);
    }
  };

  const handleVideoReupload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadingVideo(true);
    setVideoProgress("Uploading & Analyzing...");
    try {
      const token = getToken();
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${API}/candidates/upload-video`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      if (!res.ok) throw new Error("Video upload failed");

      // Reload profile to fetch new scores
      window.location.reload();
    } catch (err: any) {
      alert(err.message || "Something went wrong.");
    } finally {
      setUploadingVideo(false);
      setVideoProgress("");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="font-black uppercase tracking-widest animate-pulse dark:text-white">Loading Profile...</p>
      </div>
    );
  }

  if (fetchError) {
    return (
      <div className="min-h-screen flex flex-col gap-4 items-center justify-center p-4 text-center">
        <p className="text-xl font-black uppercase text-red-500">{fetchError}</p>
        <Button onClick={() => window.location.reload()} className="bg-black text-white dark:bg-white dark:text-black">Try Again</Button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-12 space-y-8 relative z-10">
      <div className="flex items-center gap-3 mb-8">
        <div className="bg-black dark:bg-white text-white dark:text-black p-3">
          <User size={32} strokeWidth={2.5} />
        </div>
        <div>
          <h1 className="text-3xl font-black uppercase tracking-tight text-black dark:text-white">Candidate Profile</h1>
          <p className="text-sm font-bold text-gray-500 uppercase tracking-widest">Manage your information & documents</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

        {/* Profile Settings */}
        <Card className="border-2 border-black dark:border-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] dark:shadow-[8px_8px_0px_0px_rgba(255,255,255,1)] rounded-none bg-white dark:bg-[#0a0a0a]">
          <CardContent className="p-8">
            <h2 className="text-xl font-black uppercase border-b-2 border-black dark:border-white pb-3 mb-6 flex items-center gap-2 dark:text-white">
              Personal Information
            </h2>

            {successMsg && (
              <div className="mb-4 p-3 bg-green-50 dark:bg-green-900/30 border-2 border-green-500 text-green-700 dark:text-green-400 text-xs font-bold uppercase tracking-wide">
                ✓ {successMsg}
              </div>
            )}
            {updateError && (
              <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/30 border-2 border-red-500 text-red-700 dark:text-red-400 text-xs font-bold uppercase tracking-wide">
                ! {updateError}
              </div>
            )}

            <form onSubmit={handleUpdate} className="space-y-4">
              <div>
                <label className="text-xs font-black uppercase tracking-widest text-gray-500 dark:text-gray-400 block mb-1">Full Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={e => setFormData({ ...formData, name: e.target.value })}
                  className="w-full p-3 border-2 border-dashed border-black dark:border-white dark:text-white bg-transparent focus:border-solid font-bold uppercase"
                />
              </div>

              <div>
                <label className="text-xs font-black uppercase tracking-widest text-gray-500 dark:text-gray-400 block mb-1">Phone Number</label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={e => setFormData({ ...formData, phone: e.target.value })}
                  className="w-full p-3 border-2 border-dashed border-black dark:border-white dark:text-white bg-transparent focus:border-solid font-bold uppercase"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-black uppercase tracking-widest text-gray-500 dark:text-gray-400 block mb-1">State</label>
                  <input
                    type="text"
                    value={formData.state}
                    onChange={e => setFormData({ ...formData, state: e.target.value })}
                    className="w-full p-3 border-2 border-dashed border-black dark:border-white dark:text-white bg-transparent focus:border-solid font-bold uppercase"
                  />
                </div>
                <div>
                  <label className="text-xs font-black uppercase tracking-widest text-gray-500 dark:text-gray-400 block mb-1">District</label>
                  <input
                    type="text"
                    value={formData.district}
                    onChange={e => setFormData({ ...formData, district: e.target.value })}
                    className="w-full p-3 border-2 border-dashed border-black dark:border-white dark:text-white bg-transparent focus:border-solid font-bold uppercase"
                  />
                </div>
              </div>

              <Button
                type="submit"
                disabled={isUpdating}
                className="w-full h-12 mt-4 rounded-none bg-black dark:bg-white text-white dark:text-black font-black uppercase border-2 flex items-center justify-center border-black dark:border-white shadow-[4px_4px_0px_0px_rgba(0,0,0,0.2)] dark:shadow-[4px_4px_0px_0px_rgba(255,255,255,0.2)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none transition-all"
              >
                <Save className="mr-2 h-4 w-4" /> {isUpdating ? "Saving..." : "Save Changes"}
              </Button>
            </form>

            <div className="mt-8 border-t-2 border-dashed border-gray-200 dark:border-gray-800 pt-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-black uppercase tracking-widest text-gray-500 dark:text-gray-400">ML Profile Context</h3>
                <Button variant="outline" size="sm" onClick={() => router.push("/wizard")} className="h-8 rounded-none border-black dark:border-white font-bold text-[10px] uppercase dark:text-white hover:bg-gray-100 dark:hover:bg-gray-900 border-2">
                  <Edit3 className="mr-2 h-3 w-3" /> Re-run Wizard
                </Button>
              </div>

              <div className="space-y-4">
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-1">Education Level</p>
                  <p className="font-bold text-sm dark:text-white uppercase">{profile?.education_level || "Not Set"}</p>
                </div>
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-1">Extracted Skills</p>
                  <div className="flex flex-wrap gap-2">
                    {profile?.skills?.length > 0 ? profile.skills.map((s: string, idx: number) => (
                      <span key={idx} className="text-xs font-bold uppercase px-2 py-1 bg-black text-white dark:bg-white dark:text-black">{s}</span>
                    )) : <span className="text-xs font-bold text-gray-500">No skills mapped</span>}
                  </div>
                </div>
              </div>
            </div>

          </CardContent>
        </Card>

        {/* Document Status */}
        <Card className="border-2 border-black dark:border-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] dark:shadow-[8px_8px_0px_0px_rgba(255,255,255,1)] rounded-none bg-white dark:bg-[#0a0a0a] h-fit">
          <CardContent className="p-8">
            <h2 className="text-xl font-black uppercase border-b-2 border-black dark:border-white pb-3 mb-6 flex items-center gap-2 dark:text-white">
              Document Status
            </h2>

            {documents.length === 0 ? (
              <div className="text-center p-6 border-2 border-dashed border-gray-300 dark:border-gray-700">
                <FileText className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <p className="text-sm font-bold text-gray-500">No documents uploaded yet.</p>
                <Button
                  onClick={() => router.push("/wizard")}
                  variant="outline"
                  className="mt-4 rounded-none border-2 border-black dark:border-white dark:text-white font-black uppercase hover:bg-gray-100 dark:hover:bg-gray-900"
                >
                  Go to Wizard
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {documents.map((doc: any) => (
                  <div key={doc.id} className="p-4 border-2 border-black dark:border-white bg-gray-50 dark:bg-black/50">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-black uppercase text-sm dark:text-white">
                          {doc.doc_type.replace(/_/g, " ")}
                        </p>
                        <p className="text-[10px] uppercase font-bold text-gray-500 mt-1 truncate max-w-[150px]">
                          {doc.original_filename}
                        </p>
                      </div>
                      <div className={`flex items-center gap-1 text-xs font-black uppercase px-2 py-1 border-2 ${doc.status === "APPROVED" ? "bg-green-100 text-green-800 border-green-800" :
                        doc.status === "REJECTED" ? "bg-red-100 text-red-800 border-red-800" :
                          "bg-yellow-100 text-yellow-800 border-yellow-800"
                        }`}>
                        {doc.status === "APPROVED" && <CheckCircle2 size={12} />}
                        {doc.status === "REJECTED" && <XCircle size={12} />}
                        {doc.status === "PENDING" && <Clock size={12} />}
                        {doc.status}
                      </div>
                    </div>
                    {doc.reviewer_notes && (
                      <div className="mt-3 p-2 bg-white dark:bg-black border-2 border-dashed border-gray-300 dark:border-gray-700 text-xs font-bold text-gray-600 dark:text-gray-400">
                        <span className="uppercase text-black dark:text-white">Admin Note:</span> {doc.reviewer_notes}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {profile?.auth_step >= 3 && (
              <div className="mt-6 p-4 bg-black dark:bg-white text-white dark:text-black">
                <p className="font-black uppercase text-center text-sm">
                  ✓ Profile Fully Verified
                </p>
                <p className="text-center text-xs font-medium mt-1">
                  You are eligible for recommendations.
                </p>
              </div>
            )}

          </CardContent>
        </Card>

      </div>

      {(profile?.video_uploaded || profile?.auth_step >= 3) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

          {/* AI Assessment Card */}
          {profile?.video_uploaded && (
            <Card className="border-2 border-black dark:border-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] dark:shadow-[8px_8px_0px_0px_rgba(255,255,255,1)] rounded-none bg-white dark:bg-[#0a0a0a] h-fit">
              <CardContent className="p-8">
                <h2 className="text-xl font-black uppercase border-b-2 border-black dark:border-white pb-3 mb-6 flex items-center gap-2 dark:text-white">
                  <BrainCircuit className="h-6 w-6" /> AI Assessment
                </h2>
                <div className="space-y-4">
                  <div className="flex items-center gap-4 bg-green-50 border-2 border-green-500 p-4">
                    <div className="bg-green-500 text-white p-3 font-black text-xl">
                      {profile?.video_overall_score || 0}
                    </div>
                    <div>
                      <p className="font-bold text-green-900">Communication Score</p>
                      <p className="text-xs font-bold uppercase tracking-widest text-green-700">Analyzed by Llama 3.3</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="border-2 border-black dark:border-white p-4 text-center dark:bg-[#111]">
                      <p className="text-2xl font-black dark:text-white">{profile?.video_conf_score || 0}</p>
                      <p className="text-[10px] font-bold uppercase tracking-widest text-gray-500">Confidence</p>
                    </div>
                    <div className="border-2 border-black dark:border-white p-4 text-center dark:bg-[#111]">
                      <p className="text-2xl font-black dark:text-white">{profile?.video_clarity_score || 0}</p>
                      <p className="text-[10px] font-bold uppercase tracking-widest text-gray-500">Clarity</p>
                    </div>
                  </div>

                  {profile?.video_url && (
                    <div className="flex flex-col gap-2 mt-4">
                      <a href={profile.video_url} target="_blank" rel="noreferrer" className="flex items-center justify-center gap-2 w-full p-3 border-2 border-black dark:border-white font-bold text-xs uppercase hover:bg-black hover:text-white dark:hover:bg-white dark:hover:text-black transition-colors dark:text-white cursor-pointer">
                        <ExternalLink size={16} /> Watch Submitted Video
                      </a>

                      <div className="relative w-full">
                        <input type="file" accept="video/*" className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" onChange={handleVideoReupload} disabled={uploadingVideo} />
                        <Button disabled={uploadingVideo} className="flex items-center justify-center gap-2 w-full p-3 border-2 border-dashed border-black dark:border-white bg-transparent font-bold text-xs uppercase hover:bg-gray-50 dark:hover:bg-[#111] transition-colors dark:text-gray-300 rounded-none h-11 text-black">
                          <Upload size={16} /> {uploadingVideo ? videoProgress : "Re-Upload Intro Video"}
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Saved & Applied Internships */}
          {profile?.auth_step >= 3 && (
            <div className="space-y-8 h-fit">
              <Card className="border-2 border-black dark:border-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] dark:shadow-[8px_8px_0px_0px_rgba(255,255,255,1)] rounded-none bg-white dark:bg-[#0a0a0a]">
                <CardContent className="p-8">
                  <h2 className="text-xl font-black uppercase border-b-2 border-black dark:border-white pb-3 mb-6 flex items-center gap-2 dark:text-white">
                    <Briefcase className="h-6 w-6" /> Applied Internships
                  </h2>
                  {appliedJobs.length === 0 ? (
                    <div className="text-center p-6 border-2 border-dashed border-gray-300 dark:border-gray-700">
                      <p className="text-sm font-bold text-gray-500 mb-2">No internship applications yet.</p>
                      <Button onClick={() => router.push("/recommendations")} variant="outline" className="mt-4 rounded-none border-2 border-black dark:text-white dark:border-white font-black uppercase hover:bg-gray-100 dark:hover:bg-[#111]">
                        Browse Internships
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {appliedJobs.map((job) => (
                        <div key={`applied-${job.id}`} className="border-2 border-black dark:border-white p-4">
                          <p className="font-bold text-sm text-blue-600 dark:text-blue-400">{job.company_name}</p>
                          <p className="font-black uppercase text-black dark:text-white">{job.role_title}</p>
                          <p className="text-[10px] font-bold text-gray-500 mt-1 uppercase tracking-widest">{job.city}, {job.state}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card className="border-2 border-black dark:border-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] dark:shadow-[8px_8px_0px_0px_rgba(255,255,255,1)] rounded-none bg-white dark:bg-[#0a0a0a]">
                <CardContent className="p-8">
                  <h2 className="text-xl font-black uppercase border-b-2 border-black dark:border-white pb-3 mb-6 flex items-center gap-2 dark:text-white">
                    <Save className="h-6 w-6" /> Saved Internships
                  </h2>
                  {savedJobs.length === 0 ? (
                    <div className="text-center p-6 border-2 border-dashed border-gray-300 dark:border-gray-700">
                      <p className="text-sm font-bold text-gray-500">No saved internships.</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {savedJobs.map((job) => (
                        <div key={`saved-${job.id}`} className="border-2 border-black dark:border-white p-4">
                          <p className="font-bold text-sm text-blue-600 dark:text-blue-400">{job.company_name}</p>
                          <p className="font-black uppercase text-black dark:text-white">{job.role_title}</p>
                          <div className="flex gap-4 mt-1">
                            <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">{job.city}, {job.state}</p>
                            <p className="text-[10px] font-bold text-green-600 uppercase tracking-widest">₹{job.stipend_amount}/mo</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          )}

        </div>
      )}
    </div>
  );
}
