"use client";

import { useState, useEffect } from "react";
import { RecommendationCard } from "@/components/recommendations/RecommendationCard";
import { Skeleton } from "@/components/ui/skeleton";
import { Cpu } from "lucide-react";

// Mock data to simulate API response since the backend isn't linked yet
const mockData = [
  {
    id: "1",
    companyName: "Tata Consultancy Services",
    roleTitle: "Software Developer Intern",
    sector: "IT & Software",
    location: "Mumbai, Maharashtra",
    stipend: 5000,
    matchPercentage: 92,
    badgeText: "High Priority Match",
    explanation: {
      reasons: [
        { text: "Your B.Tech degree meets the educational requirements perfectly." },
        { text: "3 of your skills match exactly: React, Node.js, and TypeScript." },
        { text: "You are within the preferred home state location." }
      ],
      skillAlignment: {
        matched: ["React", "Node.js", "TypeScript"],
        partial: ["Database Management"],
        missing: ["AWS"]
      }
    }
  },
  {
    id: "2",
    companyName: "Persistent Systems",
    roleTitle: "Frontend Engineering Intern",
    sector: "IT & Software",
    location: "Pune, Maharashtra",
    stipend: 5000,
    matchPercentage: 85,
    explanation: {
      reasons: [
        { text: "Strong match with frontend core skills (React, JavaScript)." },
        { text: "Your graduation timeline aligns with the internship duration." },
      ],
      skillAlignment: {
        matched: ["React", "CSS", "JavaScript"],
        partial: [],
        missing: ["Jira", "GraphQL"]
      }
    }
  },
  {
    id: "3",
    companyName: "HDFC Bank",
    roleTitle: "Digital Products Intern",
    sector: "Banking & Finance",
    location: "Mumbai, Maharashtra",
    stipend: 6000,
    matchPercentage: 78,
    explanation: {
      reasons: [
        { text: "Matches your secondary sector interest." },
        { text: "Affirmative action boost applied for diversity representation." },
      ],
      skillAlignment: {
        matched: ["Communication", "Data Analysis"],
        partial: ["Excel"],
        missing: ["Financial Modeling"]
      }
    }
  }
];

export default function RecommendationsPage() {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading to mimic API call
    const timer = setTimeout(() => {
      setLoading(false);
    }, 1500);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="container px-4 py-12 max-w-4xl mx-auto relative z-10">
      <div className="mb-10 text-center sm:text-left flex flex-col sm:flex-row justify-between items-center border-b-2 border-black pb-6 bg-white/80 backdrop-blur-md p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
        <div>
          <h1 className="text-4xl font-black uppercase tracking-tight text-black">
            Your Matches
          </h1>
          <p className="mt-2 text-gray-600 font-bold">
            Based on your profile, we found these opportunities for you.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 text-xs font-black tracking-widest text-white bg-black px-4 py-2 flex items-center gap-2 border-2 border-transparent">
          <Cpu size={16} /> NLP Engine Active
        </div>
      </div>

      {loading ? (
        <div className="space-y-8">
          {[1, 2, 3].map(i => (
            <Skeleton key={i} className="w-full h-56 rounded-none border-2 border-gray-200 bg-white" />
          ))}
        </div>
      ) : (
        <div className="space-y-6">
          {mockData.map((data) => (
            <RecommendationCard key={data.id} {...data} />
          ))}
        </div>
      )}
    </div>
  )
}
