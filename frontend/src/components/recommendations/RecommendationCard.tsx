"use client";

import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { motion, AnimatePresence } from "framer-motion";
import { Building2, MapPin, IndianRupee, ChevronDown, CheckCircle2 } from "lucide-react";

export function RecommendationCard({ 
  companyName, 
  roleTitle, 
  sector, 
  location, 
  matchPercentage,
  badgeText = "",
  stipend,
  explanation
}: any) {
  const [expanded, setExpanded] = useState(false);

  return (
    <Card className="w-full border-2 border-black rounded-none shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-all bg-white overflow-hidden">
      <CardContent className="p-0">
        <div className="flex flex-col sm:flex-row">
          
          <div className="flex-1 p-6 sm:p-8 relative">
            {badgeText && (
              <span className="absolute top-4 right-4 border-2 border-black bg-black text-white text-[10px] uppercase tracking-widest font-bold px-3 py-1">
                {badgeText}
              </span>
            )}
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm font-semibold text-blue-600">{companyName}</span>
              <span className="bg-blue-100 text-blue-700 text-[10px] font-bold px-2 py-0.5 rounded-sm flex items-center">
                <svg className="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Govt Verified
              </span>
            </div>
            <h3 className="text-2xl font-black uppercase text-black leading-tight">{roleTitle}</h3>
            
            <div className="flex items-center gap-6 mt-4 text-sm font-bold text-gray-600 uppercase tracking-wide">
              <span className="flex items-center gap-1.5"><Building2 size={16} /> {sector}</span>
              <span className="flex items-center gap-1.5"><MapPin size={16} /> {location}</span>
              {stipend && <span className="flex items-center gap-1.5"><IndianRupee size={16} /> {stipend}/mo</span>}
            </div>

            <div className="mt-8 flex gap-4">
              <Button onClick={() => alert("Applying...")} className="bg-black hover:bg-gray-800 text-white rounded-none font-bold uppercase border-2 border-black px-8">Apply Now</Button>
              <Button variant="outline" onClick={() => alert("Saved!")} className="rounded-none font-bold uppercase border-2 border-black hover:bg-gray-100">Save</Button>
            </div>
          </div>

          <div className="w-full sm:w-56 bg-gray-50 flex flex-col items-center justify-center p-8 border-t-2 sm:border-t-0 sm:border-l-2 border-black">
            <div className="relative w-24 h-24 mb-3">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                <path
                  className="text-slate-200"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="3"
                />
                <path
                  className="text-blue-600"
                  strokeDasharray={`${matchPercentage}, 100`}
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="3"
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-xl font-bold text-slate-900">{matchPercentage}%</span>
              </div>
            </div>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-widest">Match Score</span>
            
            <button 
              onClick={() => setExpanded(!expanded)}
              className="mt-6 text-xs font-black text-black uppercase tracking-widest hover:underline flex items-center gap-1"
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
              className="bg-gray-50 border-t-2 border-black"
            >
              <div className="p-6 sm:p-8">
                <h4 className="font-black text-lg text-black uppercase tracking-tight mb-6">How you fit this role</h4>
                <div className="grid gap-4">
                  {explanation?.reasons?.map((reason: any, idx: number) => (
                    <div key={idx} className="flex items-start gap-4">
                      <div className="mt-0.5 bg-black text-white p-1 rounded-sm">
                         <CheckCircle2 size={16} strokeWidth={2} />
                      </div>
                      <p className="text-sm font-medium text-gray-800 leading-relaxed">{reason.text}</p>
                    </div>
                  ))}
                </div>

                {explanation?.skillAlignment && (
                  <div className="mt-6">
                    <h5 className="font-bold text-sm text-slate-800 mb-3">Skill Alignment</h5>
                    <div className="flex flex-wrap gap-2">
                      {explanation.skillAlignment.matched?.map((s: string) => (
                        <span key={s} className="px-3 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded-md flex items-center gap-1">✓ {s}</span>
                      ))}
                      {explanation.skillAlignment.partial?.map((s: string) => (
                        <span key={s} className="px-3 py-1 bg-yellow-100 text-yellow-800 text-xs font-semibold rounded-md flex items-center gap-1">~ {s}</span>
                      ))}
                      {explanation.skillAlignment.missing?.map((s: string) => (
                        <span key={s} className="px-3 py-1 bg-red-50 text-red-700 text-xs font-semibold rounded-md flex items-center gap-1">× {s}</span>
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
