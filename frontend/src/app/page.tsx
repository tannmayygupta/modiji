"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ShieldAlert, Fingerprint, Database, Sparkles, MapPin, Building2, Globe, Mail, Phone, ArrowUpRight, Code, Zap } from "lucide-react";
import { motion } from "framer-motion";

export default function Home() {
  return (
    <div className="flex flex-col items-center relative z-10 w-full overflow-hidden bg-[#fdfbf6] dark:bg-[#060608] text-[#111] dark:text-[#f0f0f0] transition-colors duration-500 font-sans">
      
      {/* ================= BACKGROUND ANIMATIONS ================= */}
      <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
        {/* Animated Orbs */}
        <motion.div 
          animate={{ y: [0, -80, 0], x: [0, 50, 0], scale: [1, 1.2, 1] }} 
          transition={{ duration: 14, repeat: Infinity, ease: "easeInOut" }}
          className="absolute -top-32 -left-32 w-[600px] h-[600px] bg-indigo-500/10 dark:bg-indigo-600/20 rounded-full blur-[120px]"
        />
        <motion.div 
          animate={{ y: [0, 100, 0], x: [0, -70, 0], scale: [1, 1.5, 1] }} 
          transition={{ duration: 18, repeat: Infinity, ease: "easeInOut", delay: 2 }}
          className="absolute top-40 -right-40 w-[700px] h-[700px] bg-purple-500/10 dark:bg-purple-800/20 rounded-full blur-[150px]"
        />
        <motion.div 
          animate={{ y: [0, -40, 0], x: [0, -40, 0] }} 
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut", delay: 1 }}
          className="absolute -bottom-40 left-1/3 w-[500px] h-[500px] bg-blue-500/10 dark:bg-blue-600/10 rounded-full blur-[120px]"
        />
        {/* Crisp Technical Grid */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:32px_32px]"></div>
      </div>

      {/* ================= ASYMMETRICAL HERO SECTION ================= */}
      <section className="w-full relative z-10 pt-32 pb-24 min-h-[90vh] flex items-center">
        <div className="container px-6 max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-16 items-center">
          
          {/* Left Hero Content */}
          <div className="lg:col-span-7 flex flex-col items-start space-y-8 text-left">
            <motion.div 
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, ease: "easeOut" }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-gray-200 dark:border-gray-800 bg-white/40 dark:bg-black/40 backdrop-blur-md text-xs font-bold uppercase tracking-[0.2em] shadow-sm"
            >
              <Sparkles size={14} className="text-indigo-500" /> Ministry of Corporate Affairs
            </motion.div>

            {/* Split Meeting Animation for Title */}
            <h1 className="text-5xl sm:text-6xl md:text-[5.5rem] font-black tracking-tighter leading-[0.9] flex flex-col overflow-visible">
              <div className="flex flex-wrap gap-x-2 sm:gap-x-4">
                <motion.span 
                  initial={{ opacity: 0, x: -150, filter: "blur(10px)" }} 
                  animate={{ opacity: 1, x: 0, filter: "blur(0px)" }} 
                  transition={{ duration: 1, type: "spring", bounce: 0.2 }}
                  className="inline-block"
                >
                  PM
                </motion.span>
                <motion.span 
                  initial={{ opacity: 0, x: 150, filter: "blur(10px)" }} 
                  animate={{ opacity: 1, x: 0, filter: "blur(0px)" }} 
                  transition={{ duration: 1, type: "spring", bounce: 0.2, delay: 0.1 }}
                  className="inline-block text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-400 dark:to-purple-400"
                >
                  INTERNSHIP
                </motion.span>
              </div>
              <motion.span 
                initial={{ opacity: 0, y: 50, filter: "blur(10px)" }} 
                animate={{ opacity: 1, y: 0, filter: "blur(0px)" }} 
                transition={{ duration: 1, type: "spring", bounce: 0.2, delay: 0.2 }}
                className="inline-block mt-2"
              >
                ALLOCATION
              </motion.span>
            </h1>
            
            <motion.p 
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 1, delay: 0.6 }}
              className="max-w-[550px] text-gray-600 dark:text-gray-400 md:text-xl font-medium leading-relaxed"
            >
              A high-precision matchmaking engine. Fusing secure Aadhaar SSO with real-time NLP skill extraction to route top talent into vetted enterprise infrastructure.
            </motion.p>
            
            <motion.div 
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.8 }}
              className="flex flex-col sm:flex-row gap-4 pt-4 w-full sm:w-auto"
            >
              <Link href="/wizard" className="w-full sm:w-auto">
                <Button size="lg" className="h-16 px-10 text-lg w-full font-bold rounded-2xl bg-black dark:bg-white text-white dark:text-black hover:scale-[1.02] active:scale-[0.98] transition-transform flex items-center justify-center gap-3">
                  Initialise Protocol <ArrowUpRight className="h-5 w-5" />
                </Button>
              </Link>
            </motion.div>
          </div>

          {/* Right Hero Interactive Graphic */}
          <div className="lg:col-span-5 relative hidden md:block">
            <motion.div 
              initial={{ opacity: 0, scale: 0.8, rotateY: 20 }} animate={{ opacity: 1, scale: 1, rotateY: 0 }} 
              transition={{ duration: 1.2, ease: "easeOut", delay: 0.4 }}
              className="relative w-full aspect-square max-w-md mx-auto"
            >
              {/* Glassmorphic Main Card */}
              <div className="absolute inset-0 bg-white/20 dark:bg-black/20 backdrop-blur-2xl border border-white/40 dark:border-white/10 rounded-[2rem] shadow-2xl p-8 flex flex-col justify-between overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/30 blur-[60px] rounded-full -translate-y-1/2 translate-x-1/3"></div>
                
                <div>
                  <div className="flex items-center justify-between mb-8">
                    <div className="h-12 w-12 rounded-2xl bg-indigo-100 dark:bg-indigo-900/50 flex items-center justify-center">
                      <Zap className="text-indigo-600 dark:text-indigo-400" />
                    </div>
                    <span className="px-3 py-1 rounded-full bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs font-bold">98.4% Match</span>
                  </div>
                  <h3 className="text-2xl font-black mb-2">Algorithm Active</h3>
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Processing real-time candidate NLP vectors across 4,200+ enterprise postings.</p>
                </div>

                <div className="space-y-4">
                  <div className="h-2 w-full bg-gray-200 dark:bg-gray-800 rounded-full overflow-hidden">
                    <motion.div initial={{ width: 0 }} animate={{ width: "100%" }} transition={{ duration: 2, delay: 1 }} className="h-full bg-indigo-600"></motion.div>
                  </div>
                  <div className="h-2 w-3/4 bg-gray-200 dark:bg-gray-800 rounded-full overflow-hidden">
                    <motion.div initial={{ width: 0 }} animate={{ width: "100%" }} transition={{ duration: 2, delay: 1.2 }} className="h-full bg-purple-600"></motion.div>
                  </div>
                </div>
              </div>

              {/* Floating Element 1 */}
              <motion.div 
                animate={{ y: [-10, 10, -10] }} transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
                className="absolute -right-12 top-12 p-4 bg-white/80 dark:bg-[#111]/80 backdrop-blur-lg border border-gray-100 dark:border-gray-800 rounded-2xl shadow-xl flex items-center gap-3"
              >
                <Database className="text-blue-500" />
                <div>
                  <p className="text-xs text-gray-500 font-bold uppercase">Data Source</p>
                  <p className="text-sm font-black">DigiLocker SSO</p>
                </div>
              </motion.div>

              {/* Floating Element 2 */}
              <motion.div 
                animate={{ y: [10, -10, 10] }} transition={{ duration: 7, repeat: Infinity, ease: "easeInOut" }}
                className="absolute -left-12 bottom-20 p-4 bg-white/80 dark:bg-[#111]/80 backdrop-blur-lg border border-gray-100 dark:border-gray-800 rounded-2xl shadow-xl flex items-center gap-3"
              >
                <Code className="text-purple-500" />
                <div>
                  <p className="text-xs text-gray-500 font-bold uppercase">Engine</p>
                  <p className="text-sm font-black">Hybrid Scoring</p>
                </div>
              </motion.div>
            </motion.div>
          </div>

        </div>
      </section>

      {/* ================= BENTO GRID FEATURES ================= */}
      <section className="w-full py-32 px-6 relative z-10">
        <div className="container max-w-7xl mx-auto">
          <div className="mb-16">
            <h2 className="text-4xl md:text-5xl font-black tracking-tight mb-4">Uncompromising Architecture.</h2>
            <p className="text-lg text-gray-500 font-medium max-w-xl">A complete departure from legacy systems. Engineered purely for speed, accuracy, and enterprise-grade scale.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-12 gap-6 auto-rows-[300px]">
            
            {/* Bento Block 1 - Large */}
            <motion.div 
              initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}
              className="md:col-span-8 group bg-white dark:bg-[#0c0c0c] border border-gray-200 dark:border-gray-800 rounded-[2rem] p-10 relative overflow-hidden hover:border-black dark:hover:border-white transition-colors duration-500 flex flex-col justify-end"
            >
              <div className="absolute top-0 right-0 p-8 opacity-0 group-hover:opacity-5 transition-opacity duration-700 pointer-events-none transform scale-150 -translate-y-10 translate-x-10">
                <Fingerprint className="w-full h-full" />
              </div>
              <div className="mb-auto">
                <div className="h-14 w-14 rounded-full bg-indigo-100 dark:bg-indigo-900/40 flex items-center justify-center">
                  <Fingerprint className="text-indigo-600 dark:text-indigo-400" size={28} />
                </div>
              </div>
              <div>
                <h3 className="text-3xl font-black mb-3">Absolute Verification</h3>
                <p className="text-gray-500 dark:text-gray-400 font-medium max-w-md">100% cryptographic certainty. Digilocker SSO auto-fetches authenticated Academic records, destroying any possibility of resume forgery.</p>
              </div>
            </motion.div>

            {/* Bento Block 2 - Tall */}
            <motion.div 
              initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6, delay: 0.1 }}
              className="md:col-span-4 md:row-span-2 group bg-zinc-900 dark:bg-[#111] border border-zinc-800 rounded-[2rem] p-10 relative overflow-hidden text-white flex flex-col justify-end"
            >
               <div className="absolute top-0 right-0 w-full h-[50%] bg-gradient-to-b from-indigo-500/20 to-transparent"></div>
               <div className="mb-auto">
                <div className="h-14 w-14 rounded-full bg-white/10 backdrop-blur-md flex items-center justify-center border border-white/20">
                  <ShieldAlert className="text-white" size={28} />
                </div>
              </div>
              <div>
                <h3 className="text-3xl font-black mb-3">AI Fraud Engine</h3>
                <p className="text-zinc-400 font-medium">NLP strictly analyzes corporate postings in real-time. Unrealistic stipends, spam matrices, or exploitation keywords are instantly segregated from the network.</p>
              </div>
            </motion.div>

            {/* Bento Block 3 - Medium */}
            <motion.div 
              initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6, delay: 0.2 }}
              className="md:col-span-4 group bg-white dark:bg-[#0c0c0c] border border-gray-200 dark:border-gray-800 rounded-[2rem] p-10 relative overflow-hidden hover:border-black dark:hover:border-white transition-colors duration-500 flex flex-col justify-end"
            >
              <div className="mb-auto">
                <div className="h-14 w-14 rounded-full bg-purple-100 dark:bg-purple-900/40 flex items-center justify-center">
                  <Database className="text-purple-600 dark:text-purple-400" size={28} />
                </div>
              </div>
              <div>
                <h3 className="text-2xl font-black mb-2">Hybrid ML</h3>
                <p className="text-gray-500 dark:text-gray-400 font-medium text-sm">Deep collaborative filtering maps user matrices into high-response probability roles.</p>
              </div>
            </motion.div>

            {/* Bento Block 4 - Medium */}
            <motion.div 
              initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6, delay: 0.3 }}
              className="md:col-span-4 group bg-indigo-50 dark:bg-indigo-950/20 border border-indigo-100 dark:border-indigo-900/50 rounded-[2rem] p-10 relative overflow-hidden flex flex-col justify-end"
            >
              <div className="mb-auto">
                <div className="h-14 w-14 rounded-full bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-600/30">
                  <ArrowUpRight className="text-white" size={28} />
                </div>
              </div>
              <div>
                <h3 className="text-2xl font-black mb-2 text-indigo-950 dark:text-indigo-100">Video Synthesis</h3>
                <p className="text-indigo-700/80 dark:text-indigo-300/80 font-medium text-sm">Automated Llama 3.3 speech-to-text pipeline analyzes your intro video for communication confidence boosting scores by up to 15%.</p>
              </div>
            </motion.div>

          </div>
        </div>
      </section>

      {/* ================= COMPREHENSIVE ELITE FOOTER ================= */}
      <footer className="w-full bg-white dark:bg-[#050505] border-t border-gray-200 dark:border-gray-800 pt-24 pb-12 relative z-10">
        <div className="container px-6 max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-16 mb-20">
            
            {/* Brand Logo & description */}
            <div className="lg:col-span-4 space-y-6">
              <div className="flex items-center gap-3 font-black text-2xl tracking-tighter">
                <div className="h-10 w-10 bg-black dark:bg-white rounded-lg flex items-center justify-center">
                  <Building2 className="text-white dark:text-black h-5 w-5" />
                </div>
                PMIS SUITE
              </div>
              <p className="text-gray-500 dark:text-gray-400 font-medium leading-relaxed max-w-sm">
                The fastest, most secure way to bridge the gap between fresh talent and top-tier corporate infrastructure. Built for the modern enterprise ecosystem.
              </p>
              <div className="flex items-center gap-3 pt-4">
                <div className="h-10 w-10 flex items-center justify-center rounded-full border border-gray-200 dark:border-gray-800 hover:border-indigo-500 hover:text-indigo-500 transition-colors cursor-pointer"><Globe size={18} /></div>
                <div className="h-10 w-10 flex items-center justify-center rounded-full border border-gray-200 dark:border-gray-800 hover:border-indigo-500 hover:text-indigo-500 transition-colors cursor-pointer"><Mail size={18} /></div>
                <div className="h-10 w-10 flex items-center justify-center rounded-full border border-gray-200 dark:border-gray-800 hover:border-indigo-500 hover:text-indigo-500 transition-colors cursor-pointer"><Phone size={18} /></div>
              </div>
            </div>

            {/* Platform Links */}
            <div className="lg:col-span-2 lg:col-start-7">
              <h4 className="font-bold mb-8 tracking-tight text-lg">Platform</h4>
              <ul className="space-y-4 font-medium text-gray-500 dark:text-gray-400">
                <li><a href="#" className="hover:text-black dark:hover:text-white transition-colors flex items-center gap-2 group">How it Works <ArrowUpRight size={14} className="opacity-0 group-hover:opacity-100 transition-all -translate-x-2 group-hover:translate-x-0"/></a></li>
                <li><a href="#" className="hover:text-black dark:hover:text-white transition-colors flex items-center gap-2 group">Applicant SSO <ArrowUpRight size={14} className="opacity-0 group-hover:opacity-100 transition-all -translate-x-2 group-hover:translate-x-0"/></a></li>
                <li><a href="#" className="hover:text-black dark:hover:text-white transition-colors flex items-center gap-2 group">Enterprise Console <ArrowUpRight size={14} className="opacity-0 group-hover:opacity-100 transition-all -translate-x-2 group-hover:translate-x-0"/></a></li>
                <li><a href="#" className="hover:text-black dark:hover:text-white transition-colors flex items-center gap-2 group">Neural Matching <ArrowUpRight size={14} className="opacity-0 group-hover:opacity-100 transition-all -translate-x-2 group-hover:translate-x-0"/></a></li>
              </ul>
            </div>

            {/* Contact */}
            <div className="lg:col-span-3">
              <h4 className="font-bold mb-8 tracking-tight text-lg">Communications</h4>
              <div className="space-y-6 font-medium text-gray-500 dark:text-gray-400">
                <div className="flex items-start gap-4">
                  <MapPin size={20} className="text-black dark:text-white shrink-0 mt-1" />
                  <p>Shastri Bhawan<br/>Dr. Rajendra Prasad Rd<br/>New Delhi, India</p>
                </div>
                <div className="flex items-center gap-4">
                  <Mail size={20} className="text-black dark:text-white shrink-0" />
                  <p>exec@pmis.gov.in</p>
                </div>
              </div>
            </div>

          </div>

          <div className="pt-8 border-t border-gray-200 dark:border-gray-800 flex flex-col md:flex-row justify-between items-center gap-4 text-sm font-medium text-gray-500 dark:text-gray-400">
            <p>© {new Date().getFullYear()} Ministry of Corporate Affairs Core.</p>
            <div className="flex gap-6">
              <span className="hover:text-black dark:hover:text-white cursor-pointer transition-colors">Privacy Paradigm</span>
              <span className="hover:text-black dark:hover:text-white cursor-pointer transition-colors">Terms of Service</span>
            </div>
            <div className="flex items-center gap-2">
               <div className="h-2 w-2 rounded-full bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.8)] animate-pulse"></div>
               Systems Operational
            </div>
          </div>
          
        </div>
      </footer>
    </div>
  );
}
