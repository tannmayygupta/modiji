"use client";

import { useState, useEffect } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ShieldCheck, X, Check, FileText, User, AlertTriangle } from "lucide-react";

const API = "http://localhost:8000/api/v1";

interface QueueItem {
  document_id: string;
  doc_type: string;
  original_filename: string;
  uploaded_at: string;
  candidate_id: string;
  candidate_name: string;
  aadhaar_name: string | null;
  candidate_email: string;
  auth_step: number;
  ocr_extracted_name: string | null;
  ocr_confidence: number | null;
}

export default function AdminPanel() {
  const [queue, setQueue] = useState<QueueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>(null);
  const [reviewingId, setReviewingId] = useState<string | null>(null);

  const fetchQueue = async () => {
    try {
      const res = await fetch(`${API}/documents/admin/queue?status_filter=PENDING`);
      const data = await res.json();
      setQueue(data.queue || []);
    } catch (e) {
      console.error("Failed to load queue:", e);
    }
  };

  const fetchStats = async () => {
    try {
      const res = await fetch(`${API}/admin/stats`);
      const data = await res.json();
      setStats(data);
    } catch (e) {
      console.error("Failed to load stats:", e);
    }
  };

  useEffect(() => {
    Promise.all([fetchQueue(), fetchStats()]).finally(() => setLoading(false));
  }, []);

  const handleReview = async (documentId: string, action: "APPROVED" | "REJECTED") => {
    setReviewingId(documentId);
    try {
      const formData = new FormData();
      formData.append("action", action);
      formData.append("notes", action === "APPROVED" ? "Verified by admin" : "Document mismatch or unclear");
      formData.append("reviewer", "admin");

      await fetch(`${API}/documents/admin/review/${documentId}`, {
        method: "POST",
        body: formData,
      });

      // Refresh queue
      await fetchQueue();
    } catch (e) {
      console.error("Review failed:", e);
    } finally {
      setReviewingId(null);
    }
  };

  const nameMatch = (candidateName: string, aadhaarName: string | null): boolean => {
    if (!aadhaarName) return false;
    return candidateName.toLowerCase().trim() === aadhaarName.toLowerCase().trim();
  };

  return (
    <div className="container px-4 py-12 max-w-5xl mx-auto relative z-10">
      {/* Admin Header */}
      <div className="mb-10 border-b-2 border-black pb-6 bg-white/80 backdrop-blur-md p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
        <div className="flex items-center gap-3 mb-2">
          <ShieldCheck className="h-8 w-8" />
          <h1 className="text-4xl font-black uppercase tracking-tight">Admin Panel</h1>
        </div>
        <p className="text-gray-600 font-bold">
          Document Verification Queue — Review uploaded marksheets against Aadhaar-verified identities.
        </p>
      </div>

      {/* Quick Stats */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
          {[
            { label: "CANDIDATES", value: stats.total_candidates },
            { label: "INTERNSHIPS", value: stats.total_internships },
            { label: "APPLICATIONS", value: stats.total_applications },
            { label: "PENDING DOCS", value: queue.length },
          ].map((s) => (
            <div key={s.label} className="border-2 border-black p-4 bg-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
              <p className="text-xs font-black uppercase tracking-widest text-gray-500">{s.label}</p>
              <p className="text-3xl font-black mt-1">{s.value}</p>
            </div>
          ))}
        </div>
      )}

      {/* Verification Queue */}
      <h2 className="text-2xl font-black uppercase tracking-tight mb-6 flex items-center gap-2">
        <FileText className="h-6 w-6" /> Pending Review ({queue.length})
      </h2>

      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="w-full h-40 rounded-none border-2 border-gray-200" />
          ))}
        </div>
      ) : queue.length === 0 ? (
        <div className="border-2 border-dashed border-gray-300 p-16 text-center">
          <Check className="h-12 w-12 mx-auto text-gray-300 mb-4" />
          <p className="text-gray-500 font-bold uppercase tracking-widest">Queue Clear</p>
          <p className="text-gray-400 text-sm mt-2">No documents pending review.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {queue.map((item) => {
            const isNameMatch = nameMatch(item.candidate_name, item.aadhaar_name);
            return (
              <Card
                key={item.document_id}
                className="border-2 border-black rounded-none shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] bg-white"
              >
                <CardContent className="p-6">
                  <div className="flex flex-col md:flex-row justify-between gap-6">
                    {/* Left: Document Info */}
                    <div className="flex-1 space-y-4">
                      <div className="flex items-center gap-2">
                        <span className="bg-black text-white text-[10px] font-black uppercase tracking-widest px-3 py-1">
                          {item.doc_type.replace(/_/g, " ")}
                        </span>
                        <span className="text-xs text-gray-500 font-bold">{item.original_filename}</span>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                        {/* Candidate Name */}
                        <div className="border-2 border-gray-200 p-3">
                          <p className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-1">
                            <User className="inline h-3 w-3 mr-1" />Account Name
                          </p>
                          <p className="font-black text-lg">{item.candidate_name}</p>
                        </div>

                        {/* Aadhaar Name (for cross-check) */}
                        <div className={`border-2 p-3 ${isNameMatch ? "border-green-500 bg-green-50" : "border-red-500 bg-red-50"}`}>
                          <p className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-1">
                            <ShieldCheck className="inline h-3 w-3 mr-1" />Aadhaar Verified Name
                          </p>
                          <p className="font-black text-lg">{item.aadhaar_name || "NOT VERIFIED"}</p>
                          {isNameMatch ? (
                            <span className="text-xs font-bold text-green-700">Names match</span>
                          ) : (
                            <span className="text-xs font-bold text-red-700 flex items-center gap-1">
                              <AlertTriangle className="h-3 w-3" /> Names do NOT match — verify manually
                            </span>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-4 text-xs text-gray-500 font-bold">
                        <span>Email: {item.candidate_email}</span>
                        <span>Auth Step: {item.auth_step}/3</span>
                        <span>Uploaded: {item.uploaded_at ? new Date(item.uploaded_at).toLocaleDateString() : "N/A"}</span>
                      </div>

                      {/* View Document Button */}
                      <a
                        href={`${API}/documents/admin/document-file/${item.document_id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-block text-xs font-black uppercase tracking-widest border-2 border-black px-4 py-2 hover:bg-black hover:text-white transition-colors"
                      >
                        View Document
                      </a>
                    </div>

                    {/* Right: Action Buttons */}
                    <div className="flex flex-col gap-3 justify-center min-w-[160px]">
                      <Button
                        onClick={() => handleReview(item.document_id, "APPROVED")}
                        disabled={reviewingId === item.document_id}
                        className="rounded-none bg-black text-white font-black uppercase border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,0.2)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none transition-all h-12"
                      >
                        <Check className="mr-2 h-4 w-4" /> Approve
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => handleReview(item.document_id, "REJECTED")}
                        disabled={reviewingId === item.document_id}
                        className="rounded-none font-black uppercase border-2 border-black hover:bg-red-50 transition-all h-12"
                      >
                        <X className="mr-2 h-4 w-4" /> Reject
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
