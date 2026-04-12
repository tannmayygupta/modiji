"use client";

import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { motion, AnimatePresence } from "framer-motion";
import { Building2, MapPin, IndianRupee, ChevronDown, CheckCircle2, Info } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

function getToken() {
  if (typeof window !== "undefined") return localStorage.getItem("pmis_token");
  return null;
}

export function RecommendationCard({
  id,
  internshipId,
  companyName,
  roleTitle,
  sector,
  location,
  matchPercentage,
  badgeText = "",
  stipend,
  explanation,
}: any) {
  const [expanded, setExpanded] = useState(false);
  const [applied, setApplied] = useState(false);
  const [saved, setSaved] = useState(false);

  const logInteraction = async (action: "APPLY" | "SAVE" | "VIEW") => {
    const token = getToken();
    if (!token) return;
    try {
      await fetch(`${API}/interactions/`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ internship_id: internshipId || id, action }),
      });
    } catch { /* non-blocking */ }
  };

  const handleApply = () => {
    if (!getToken()) { alert("Please login to apply."); return; }
    setApplied(true);
    logInteraction("APPLY");
  };

  const handleSave = () => {
    setSaved(true);
    logInteraction("SAVE");
  };

  return (
    <Card className="w-full border-2 border-black dark:border-white rounded-none shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] dark:shadow-[6px_6px_0px_0px_rgba(255,255,255,0.5)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-all bg-white dark:bg-[#0a0a0a] overflow-hidden">
      <CardContent className="p-0">
        <div className="flex flex-col sm:flex-row">

          <div className="flex-1 p-6 sm:p-8 relative">
            {badgeText && (
              <span className="absolute top-4 right-4 border-2 border-black dark:border-white bg-black dark:bg-white text-white dark:text-black text-[10px] uppercase tracking-widest font-bold px-3 py-1">
                {badgeText}
              </span>
            )}
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm font-semibold text-blue-600 dark:text-blue-400">{companyName}</span>
              <span className="bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 text-[10px] font-bold px-2 py-0.5 rounded-sm flex items-center">
                <svg className="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Govt Verified
              </span>
            </div>
            <h3 className="text-2xl font-black uppercase text-black dark:text-white leading-tight">{roleTitle}</h3>

            <div className="flex flex-wrap items-center gap-4 mt-4 text-sm font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wide">
              <span className="flex items-center gap-1.5"><Building2 size={16} /> {sector}</span>
              <span className="flex items-center gap-1.5"><MapPin size={16} /> {location}</span>
              {stipend && <span className="flex items-center gap-1.5"><IndianRupee size={16} /> {stipend.toLocaleString("en-IN")}/mo</span>}
            </div>

            <div className="mt-8 flex gap-4">
              <Button
                onClick={handleApply}
                disabled={applied}
                className="bg-black dark:bg-white hover:bg-gray-800 dark:hover:bg-gray-200 text-white dark:text-black rounded-none font-bold uppercase border-2 border-black dark:border-white px-8"
              >
                {applied ? "✓ Applied" : "Apply Now"}
              </Button>
              <Button
                variant="outline"
                onClick={handleSave}
                disabled={saved}
                className="rounded-none font-bold uppercase border-2 border-black dark:border-white text-black dark:text-white hover:bg-gray-100 dark:hover:bg-gray-900"
              >
                {saved ? "✓ Saved" : "Save"}
              </Button>
            </div>
          </div>

          <div className="w-full sm:w-56 bg-gray-50 dark:bg-[#111] flex flex-col items-center justify-center p-8 border-t-2 sm:border-t-0 sm:border-l-2 border-black dark:border-white">
            <div className="relative w-24 h-24 mb-3">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                <path
                  className="text-slate-200 dark:text-slate-700"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="3"
                />
                <path
                  className="text-blue-600 dark:text-blue-400"
                  strokeDasharray={`${matchPercentage}, 100`}
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="3"
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-xl font-bold text-slate-900 dark:text-white">{matchPercentage}%</span>
              </div>
            </div>
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-widest">Match Score</span>

            <button
              onClick={() => { setExpanded(!expanded); logInteraction("VIEW"); }}
              className="mt-6 text-xs font-black text-black dark:text-white uppercase tracking-widest hover:underline flex items-center gap-1"
            >
              WHY THIS MATCH?
              <motion.div animate={{ rotate: expanded ? 180 : 0 }}>
                <ChevronDown size={14} strokeWidth={3} />
              </motion.div>
            </button>
          </div>
        </div>

        <AnimatePresence>
          {expanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="bg-gray-50 dark:bg-[#111] border-t-2 border-black dark:border-white"
            >
              <div className="p-6 sm:p-8">
                <h4 className="font-black text-lg text-black dark:text-white uppercase tracking-tight mb-6">How you fit this role</h4>
                <div className="grid gap-4">
                  {explanation?.reasons?.map((reason: any, idx: number) => (
                    <div key={idx} className="flex items-start gap-4">
                      <div className={`mt-0.5 p-1 rounded-sm ${reason.category === 'fallback' ? 'bg-blue-500' : 'bg-black dark:bg-white'} text-white dark:text-black`}>
                        {reason.category === 'fallback' ? <Info size={16} strokeWidth={2} /> : <CheckCircle2 size={16} strokeWidth={2} />}
                      </div>
                      <p className="text-sm font-medium text-gray-800 dark:text-gray-200 leading-relaxed">{reason.text}</p>
                    </div>
                  ))}
                  {(!explanation?.reasons || explanation.reasons.length === 0) && (
                    <p className="text-sm font-medium text-gray-500">Great match based on your overall profile.</p>
                  )}
                </div>

                {explanation?.skillAlignment && (
                  <div className="mt-6">
                    <h5 className="font-bold text-sm text-slate-800 dark:text-slate-200 mb-3">Skill Alignment</h5>
                    <div className="flex flex-wrap gap-2">
                      {explanation.skillAlignment.matched?.map((s: string) => (
                        <span key={s} className="px-3 py-1 bg-green-100 dark:bg-green-900/40 text-green-800 dark:text-green-300 text-xs font-semibold rounded-md flex items-center gap-1">✓ {s}</span>
                      ))}
                      {explanation.skillAlignment.partial?.map((s: string) => (
                        <span key={s} className="px-3 py-1 bg-yellow-100 dark:bg-yellow-900/40 text-yellow-800 dark:text-yellow-300 text-xs font-semibold rounded-md flex items-center gap-1">~ {s}</span>
                      ))}
                      {explanation.skillAlignment.missing?.map((s: string) => (
                        <span key={s} className="px-3 py-1 bg-red-50 dark:bg-red-900/40 text-red-700 dark:text-red-300 text-xs font-semibold rounded-md flex items-center gap-1">× {s}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </CardContent>
    </Card>
  );
}
