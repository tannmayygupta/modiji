"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  ShieldCheck, FileText, GraduationCap, Lightbulb, Camera, Cpu,
  Building2, MapPin, IndianRupee, ChevronDown, CheckCircle2, ArrowUpRight,
} from "lucide-react";
import { STATES, SECTORS, EDUCATION_LEVELS, WIZARD_TOTAL_STEPS } from "@/lib/constants";

/* Shared reveal. Matches the wizard's motion budget: short fade + 20px rise,
   once, no loops. */
const reveal = {
  initial: { opacity: 0, y: 20 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-80px" },
  transition: { duration: 0.4, ease: "easeOut" as const },
};

/* Counts are read from the same arrays the wizard renders, so nothing here
   can claim a number the product doesn't actually offer. */
const STATS = [
  { value: `${STATES.length}`, label: "States & UTs" },
  { value: `${SECTORS.length}`, label: "Sectors" },
  { value: `${EDUCATION_LEVELS.length}`, label: "Education levels" },
  { value: `${WIZARD_TOTAL_STEPS}`, label: "Steps to finish" },
];

const STEPS = [
  {
    icon: ShieldCheck,
    title: "Verify your identity",
    body: "Download your offline e-KYC file from myaadhaar.uidai.gov.in and upload it with your 4-digit share code.",
  },
  {
    icon: FileText,
    title: "Upload your marksheets",
    body: "10th, 12th, diploma or degree. An administrator checks each one against the name on your Aadhaar record.",
  },
  {
    icon: GraduationCap,
    title: "Add your education",
    body: "Pick your highest qualification, or upload a resume and let the parser fill it in for you.",
  },
  {
    icon: Lightbulb,
    title: "Choose skills & sectors",
    body: "Up to 5 skills, up to 3 industries, and how far from home you're willing to work.",
  },
  {
    icon: Camera,
    title: "Record a short intro",
    body: "Two to three minutes about yourself. It's transcribed and scored for clarity and confidence.",
  },
  {
    icon: Cpu,
    title: "Get your matches",
    body: "Ranked internships with a match score, and the specific reasons behind every single one.",
  },
];

const CAPABILITIES = [
  {
    n: "01",
    title: "Your Aadhaar number is never stored",
    body: "Verification reads the UIDAI-signed offline XML you upload and checks the signature. We keep the result of that check — not the credential. There is no OTP flow to intercept and no number sitting in our database.",
  },
  {
    n: "02",
    title: "Documents are checked by a person",
    body: "Uploaded marksheets enter an admin review queue and are matched against your verified Aadhaar name before you can apply anywhere.",
  },
  {
    n: "03",
    title: "Every match explains itself",
    body: "Each recommendation lists which of your skills matched, which partly matched, and which are missing — plus location and sector reasoning.",
  },
  {
    n: "04",
    title: "Your intro video counts",
    body: "The audio is transcribed and scored for clarity and confidence. That score feeds into your ranking, so how you present yourself matters.",
  },
];

/* Grid dividers for the stats strip: 2 columns on mobile, 4 on desktop.
   Built so no two conflicting width utilities ever land on the same element
   (Tailwind resolves those by stylesheet order, not class order). */
function statCellBorders(i: number) {
  const cls: string[] = [];
  if (i % 2 === 1) cls.push("border-l-2");
  else if (i > 0) cls.push("md:border-l-2");
  if (i >= 2) cls.push("border-t-2 md:border-t-0");
  return cls.join(" ");
}

export default function Home() {
  return (
    <div className="w-full relative z-10">

      {/* ================================ HERO ================================ */}
      <section className="w-full px-4 sm:px-6 pt-16 pb-20 md:pt-24 md:pb-28">
        <div className="container max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-14 lg:gap-12 items-center">

          {/* ---- Left: the pitch ---- */}
          <div className="lg:col-span-7">
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="inline-flex items-center gap-2 nb-panel nb-shadow-sm px-4 py-2 mb-8"
            >
              <ShieldCheck size={14} className="text-black dark:text-white" />
              <span className="nb-label text-black dark:text-white">
                Ministry of Corporate Affairs
              </span>
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, ease: "easeOut" }}
              className="nb-h text-[clamp(2.5rem,8vw,5rem)] leading-[0.92] text-black dark:text-white"
            >
              Government
              <br />
              internships
              <br />
              <span className="nb-invert inline-block px-3 py-0.5 mt-2">
                matched to you
              </span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.25 }}
              className="mt-8 max-w-xl text-lg font-medium leading-relaxed text-gray-600 dark:text-gray-400"
            >
              Verify yourself once with offline Aadhaar e-KYC and upload your
              marksheets. We match you against verified internships across India
              and tell you, in plain words, why each one fits.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.35 }}
              className="mt-10 flex flex-col sm:flex-row gap-4"
            >
              <Link
                href="/login"
                className="nb-invert nb-shadow-sm nb-press h-14 px-8 border-2 border-black dark:border-white inline-flex items-center justify-center gap-2 font-black uppercase tracking-wide"
              >
                Start your application
                <ArrowUpRight className="h-5 w-5" />
              </Link>
              <Link
                href="#how"
                className="nb-panel nb-press h-14 px-8 inline-flex items-center justify-center gap-2 font-black uppercase tracking-wide text-black dark:text-white"
              >
                How it works
                <ChevronDown className="h-5 w-5" />
              </Link>
            </motion.div>

            <motion.ul
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.4, delay: 0.5 }}
              className="mt-10 flex flex-wrap gap-x-6 gap-y-2"
            >
              {[
                "Offline Aadhaar e-KYC",
                "Aadhaar number never stored",
                "Documents reviewed by an admin",
              ].map((item) => (
                <li key={item} className="flex items-center gap-2">
                  <CheckCircle2 size={14} className="text-green-600 dark:text-green-500 shrink-0" />
                  <span className="nb-label">{item}</span>
                </li>
              ))}
            </motion.ul>
          </div>

          {/* ---- Right: the actual product, not an abstraction ---- */}
          <div className="lg:col-span-5">
            <motion.div
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <p className="nb-label mb-3">Sample match</p>
              <SampleMatchCard />
            </motion.div>
          </div>
        </div>
      </section>

      {/* =============================== STATS =============================== */}
      <section className="w-full px-4 sm:px-6 pb-20 md:pb-28">
        <div className="container max-w-6xl mx-auto">
          <motion.dl {...reveal} className="nb-panel nb-shadow-lg grid grid-cols-2 md:grid-cols-4">
            {STATS.map((stat, i) => (
              <div
                key={stat.label}
                className={`p-6 sm:p-8 border-black dark:border-white ${statCellBorders(i)}`}
              >
                <dd className="nb-h text-4xl sm:text-5xl text-black dark:text-white">
                  {stat.value}
                </dd>
                <dt className="nb-label mt-2">{stat.label}</dt>
              </div>
            ))}
          </motion.dl>
        </div>
      </section>

      {/* ============================ HOW IT WORKS ============================ */}
      <section id="how" className="w-full px-4 sm:px-6 pb-20 md:pb-28 scroll-mt-24">
        <div className="container max-w-6xl mx-auto">
          <motion.div {...reveal} className="mb-12">
            <p className="nb-label mb-3">The process</p>
            <h2 className="nb-h text-3xl sm:text-4xl md:text-5xl text-black dark:text-white">
              Six steps, start to finish
            </h2>
            <p className="mt-4 max-w-2xl text-base font-medium text-gray-600 dark:text-gray-400">
              You can stop after any step and pick up where you left off. Nothing
              is lost between sessions.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {STEPS.map((step, i) => {
              const Icon = step.icon;
              return (
                <motion.div
                  key={step.title}
                  {...reveal}
                  transition={{ duration: 0.4, delay: (i % 3) * 0.08, ease: "easeOut" }}
                  className="nb-panel nb-shadow-md p-7 flex flex-col"
                >
                  <div className="flex items-start justify-between mb-6">
                    <div className="nb-invert p-3">
                      <Icon size={24} strokeWidth={2} />
                    </div>
                    <span className="nb-h text-4xl text-gray-300 dark:text-gray-700 leading-none" aria-hidden="true">
                      {String(i + 1).padStart(2, "0")}
                    </span>
                  </div>
                  <h3 className="nb-h text-lg mb-2 text-black dark:text-white">
                    {step.title}
                  </h3>
                  <p className="text-sm font-medium leading-relaxed text-gray-600 dark:text-gray-400">
                    {step.body}
                  </p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* =========================== WHAT YOU GET ============================ */}
      <section className="w-full px-4 sm:px-6 pb-20 md:pb-28">
        <div className="container max-w-6xl mx-auto">
          <motion.div {...reveal} className="mb-12">
            <p className="nb-label mb-3">What makes it different</p>
            <h2 className="nb-h text-3xl sm:text-4xl md:text-5xl text-black dark:text-white">
              Verified, not self-reported
            </h2>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {CAPABILITIES.map((cap, i) => (
              <motion.article
                key={cap.n}
                {...reveal}
                transition={{ duration: 0.4, delay: (i % 3) * 0.08, ease: "easeOut" }}
                className={`nb-panel nb-shadow-md p-8 ${i === 0 ? "lg:col-span-3" : ""}`}
              >
                <div className="flex items-baseline gap-4 mb-4">
                  <span className="nb-h text-2xl text-black dark:text-white shrink-0">
                    {cap.n}
                  </span>
                  <span className="flex-1 nb-rule" aria-hidden="true" />
                </div>
                <h3
                  className={`nb-h mb-3 text-black dark:text-white ${
                    i === 0 ? "text-2xl sm:text-3xl" : "text-xl"
                  }`}
                >
                  {cap.title}
                </h3>
                <p
                  className={`font-medium leading-relaxed text-gray-600 dark:text-gray-400 ${
                    i === 0 ? "text-base max-w-3xl" : "text-sm"
                  }`}
                >
                  {cap.body}
                </p>
              </motion.article>
            ))}
          </div>
        </div>
      </section>

      {/* ============================= FINAL CTA ============================== */}
      <section className="w-full nb-invert">
        <div className="container max-w-6xl mx-auto px-4 sm:px-6 py-20 md:py-24">
          <motion.div
            {...reveal}
            className="flex flex-col lg:flex-row lg:items-end justify-between gap-10"
          >
            <div>
              <h2 className="nb-h text-3xl sm:text-4xl md:text-5xl leading-[0.95] max-w-2xl">
                Ready when you are
              </h2>
              <p className="mt-4 text-base font-medium opacity-80 max-w-xl">
                All you need to begin is a mobile number. You can add your
                documents and video whenever you're ready.
              </p>
            </div>
            <Link
              href="/login"
              className="shrink-0 h-16 px-10 inline-flex items-center justify-center gap-2 bg-white text-black dark:bg-black dark:text-white border-2 border-white dark:border-black font-black uppercase tracking-wide text-lg nb-press"
            >
              Start now
              <ArrowUpRight className="h-5 w-5" />
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  );
}

/* ---------------------------------------------------------------------------
   A static, non-interactive replica of the real RecommendationCard. Same
   grammar as /recommendations — company line, verified badge, meta row, match
   ring, reasons — so the hero shows the product instead of an abstract graphic.
   Labelled "Sample match" above; every value here is illustrative.
--------------------------------------------------------------------------- */
function SampleMatchCard() {
  const MATCH = 92;

  return (
    <div className="nb-panel nb-shadow-lg overflow-hidden">
      <div className="flex flex-col sm:flex-row">

        <div className="flex-1 p-6">
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <span className="text-sm font-semibold text-blue-600 dark:text-blue-400">
              National Infrastructure Corp.
            </span>
            <span className="bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 text-[10px] font-bold px-2 py-0.5 flex items-center gap-1">
              <CheckCircle2 size={11} strokeWidth={3} />
              Govt Verified
            </span>
          </div>

          <h3 className="nb-h text-xl text-black dark:text-white leading-tight">
            Data Analyst Intern
          </h3>

          <div className="flex flex-wrap items-center gap-x-4 gap-y-2 mt-4">
            <span className="nb-label flex items-center gap-1.5">
              <Building2 size={14} /> IT &amp; Software
            </span>
            <span className="nb-label flex items-center gap-1.5">
              <MapPin size={14} /> Pune, Maharashtra
            </span>
            <span className="nb-label flex items-center gap-1.5">
              <IndianRupee size={14} /> 12,000/mo
            </span>
          </div>
        </div>

        <div className="w-full sm:w-44 bg-gray-50 dark:bg-[#111] border-t-2 sm:border-t-0 sm:border-l-2 border-black dark:border-white flex flex-col items-center justify-center p-6">
          <div className="relative w-20 h-20 mb-3">
            <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36" aria-hidden="true">
              <path
                className="text-gray-200 dark:text-gray-700"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke="currentColor"
                strokeWidth="3"
              />
              <motion.path
                className="text-blue-600 dark:text-blue-400"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke="currentColor"
                strokeWidth="3"
                strokeLinecap="round"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: MATCH / 100 }}
                transition={{ duration: 1.1, delay: 0.5, ease: "easeOut" }}
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-lg font-black text-black dark:text-white">
                {MATCH}%
              </span>
            </div>
          </div>
          <span className="nb-label text-center">Match score</span>
        </div>
      </div>

      {/* Reasons — the "Why this match?" panel, shown open */}
      <div className="border-t-2 border-black dark:border-white bg-gray-50 dark:bg-[#111] p-6">
        <p className="nb-label mb-4">Why this match</p>
        <ul className="space-y-2.5">
          {[
            "3 of your 5 skills are required for this role",
            "Located in your preferred home state",
            "Sector matches your first preference",
          ].map((reason) => (
            <li key={reason} className="flex items-start gap-3">
              <span className="nb-invert p-0.5 mt-0.5 shrink-0">
                <CheckCircle2 size={13} strokeWidth={2.5} />
              </span>
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                {reason}
              </span>
            </li>
          ))}
        </ul>

        <div className="flex flex-wrap gap-2 mt-5">
          <span className="px-2.5 py-1 bg-green-100 dark:bg-green-900/40 text-green-800 dark:text-green-300 text-xs font-bold">
            ✓ Python
          </span>
          <span className="px-2.5 py-1 bg-green-100 dark:bg-green-900/40 text-green-800 dark:text-green-300 text-xs font-bold">
            ✓ SQL
          </span>
          <span className="px-2.5 py-1 bg-yellow-100 dark:bg-yellow-900/40 text-yellow-800 dark:text-yellow-300 text-xs font-bold">
            ~ Power BI
          </span>
        </div>
      </div>
    </div>
  );
}
