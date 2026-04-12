"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { Moon, Sun, User, LogOut } from "lucide-react";

export function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const [hasToken, setHasToken] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    // 🔋 Background WAKE-UP ping for Render (Invisible to user)
    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
    const healthUrl = API_URL.includes("/api/v1") ? API_URL.replace("/api/v1", "/health") : `${API_URL}/health`;
    fetch(healthUrl).catch(() => {});

    // Check Auth
    setHasToken(!!localStorage.getItem("pmis_token"));
    
    // Check Theme
    const savedTheme = localStorage.getItem("pmis_theme");
    if (savedTheme === "dark" || (!savedTheme && document.documentElement.classList.contains("dark"))) {
      setIsDarkMode(true);
      document.documentElement.classList.add("dark");
    } else {
      setIsDarkMode(false);
      document.documentElement.classList.remove("dark");
    }
  }, [pathname]); // Re-run check when route changes

  const toggleTheme = () => {
    if (isDarkMode) {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("pmis_theme", "light");
      setIsDarkMode(false);
    } else {
      document.documentElement.classList.add("dark");
      localStorage.setItem("pmis_theme", "dark");
      setIsDarkMode(true);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("pmis_token");
    localStorage.removeItem("pmis_user_id");
    setHasToken(false);
    router.push("/");
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b-2 border-black dark:border-white bg-white/90 dark:bg-[#0a0a0a]/90 backdrop-blur supports-[backdrop-filter]:bg-white/60">
      <div className="container flex h-16 items-center px-4 max-w-6xl mx-auto">
        <Link href="/" className="flex items-center space-x-2">
          <svg className="w-8 h-8 text-black dark:text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2" />
            <path d="M18 14h-8" />
            <path d="M15 18h-5" />
            <path d="M10 6h8v4h-8V6Z" />
          </svg>
          <span className="font-black uppercase tracking-widest sm:inline-block text-black dark:text-white">PMIS Allocation</span>
        </Link>
        <div className="flex flex-1 items-center justify-end space-x-2 sm:space-x-4">
          <button 
            onClick={toggleTheme}
            className="p-2 border-2 border-black dark:border-white text-black dark:text-white hover:bg-black hover:text-white dark:hover:bg-white dark:hover:text-black transition-all"
            aria-label="Toggle Theme"
          >
            {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
          </button>
          
          <nav className="flex items-center space-x-2 sm:space-x-4">
            
            {hasToken ? (
              <>
                <Link href="/profile" className="text-xs font-black uppercase text-black dark:text-white hover:underline px-2 tracking-widest flex items-center gap-1">
                  <User size={14} className="hidden sm:inline" /> Profile
                </Link>
                <button onClick={handleLogout} className="bg-red-500 text-white text-xs font-black uppercase px-4 py-2 border-2 border-black hover:bg-white hover:text-red-500 hover:translate-x-[2px] hover:translate-y-[2px] shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none transition-all flex items-center gap-1">
                  <LogOut size={14} className="hidden sm:inline" /> Logout
                </button>
              </>
            ) : (
              <>
                <Link href="/login" className="text-xs font-black uppercase text-black dark:text-white hover:underline px-2 tracking-widest">
                  Login
                </Link>
                <Link href="/wizard" className="bg-black dark:bg-white text-white dark:text-black text-xs font-black uppercase px-6 py-2 sm:py-3 border-2 border-black dark:border-white hover:bg-white hover:text-black dark:hover:bg-black dark:hover:text-white hover:translate-x-[2px] hover:translate-y-[2px] shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)] hover:shadow-none transition-all">
                  Initialize
                </Link>
              </>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
}
