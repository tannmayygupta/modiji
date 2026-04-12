"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { RecommendationCard } from "@/components/recommendations/RecommendationCard";
import { Skeleton } from "@/components/ui/skeleton";
import { Cpu, AlertTriangle } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

function getToken() {
  if (typeof window !== "undefined") return localStorage.getItem("pmis_token");
  return null;
}

export default function RecommendationsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [error, setError] = useState("");
  const [engineVersion, setEngineVersion] = useState("");

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push("/login");
      return;
    }

    const fetchRecommendations = async () => {
      try {
        const res = await fetch(`${API}/recommendations/?top_k=10`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.detail || "Failed to fetch recommendations");
        }

        const data = await res.json();
        setEngineVersion(data.engine_version || "");

        // Map backend response to card props
        const cards = (data.recommendations || []).map((rec: any, idx: number) => ({
          id: rec.id || rec.internship_id,
          companyName: rec.company_name,
          roleTitle: rec.role_title,
          sector: rec.sector,
          location: `${rec.city}, ${rec.state}`,
          stipend: rec.stipend_amount,
          matchPercentage: rec.match_percentage,
          badgeText: idx === 0 ? "High Priority Match" : "",
          explanation: rec.explanation ? {
            reasons: (rec.explanation.reasons || []).map((r: any) => ({ text: r.text })),
            skillAlignment: rec.explanation.skill_alignment || null,
          } : null,
        }));

        setRecommendations(cards);
      } catch (err: any) {
        console.error("Recommendation fetch error:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [router]);

  return (
    <div className="container px-4 py-12 max-w-4xl mx-auto relative z-10">
      <div className="mb-10 text-center sm:text-left flex flex-col sm:flex-row justify-between items-center border-b-2 border-black dark:border-white pb-6 bg-white/80 dark:bg-black/80 backdrop-blur-md p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)]">
        <div>
          <h1 className="text-4xl font-black uppercase tracking-tight text-black dark:text-white">
            Your Matches
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400 font-bold">
            Based on your profile, we found these opportunities for you.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 text-xs font-black tracking-widest text-white bg-black dark:bg-white dark:text-black px-4 py-2 flex items-center gap-2 border-2 border-transparent">
          <Cpu size={16} /> {engineVersion === "hybrid-v1" ? "ML Engine Active" : "Recommendation Engine"}
        </div>
      </div>

      {error && (
        <div className="mb-8 p-6 border-2 border-red-500 bg-red-50 dark:bg-red-900/20 flex items-start gap-4">
          <AlertTriangle className="text-red-500 mt-1 shrink-0" size={24} />
          <div>
            <p className="font-black uppercase text-red-800 dark:text-red-400">{error}</p>
            <p className="text-sm font-medium text-red-600 dark:text-red-300 mt-1">
              {error.includes("under review") 
                ? "Please check back later once an administrator has verified your credentials."
                : "Please complete your profile in the Wizard first, then return here."}
            </p>
          </div>
        </div>
      )}

      {loading ? (
        <div className="space-y-8">
          {[1, 2, 3].map(i => (
            <Skeleton key={i} className="w-full h-56 rounded-none border-2 border-gray-200 bg-white dark:bg-black" />
          ))}
        </div>
      ) : recommendations.length > 0 ? (
        <div className="space-y-6">
          {recommendations.map((data, idx) => (
            <RecommendationCard key={data.id === "None" ? idx : (data.id || idx)} {...data} />
          ))}
        </div>
      ) : !error ? (
        <div className="text-center py-20 border-2 border-dashed border-gray-300 dark:border-gray-700">
          <p className="font-black uppercase text-gray-500 text-lg">No recommendations found</p>
          <p className="text-sm font-medium text-gray-400 mt-2">Complete your profile wizard to get personalized matches.</p>
        </div>
      ) : null}
    </div>
  )
}
