"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Smartphone, Lock, Phone, Moon, Sun, Terminal } from "lucide-react";
import { setupRecaptcha, sendOTP, verifyOTP } from "../../firebase";
import type { ConfirmationResult } from "firebase/auth";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
const IS_DEV = process.env.NODE_ENV === "development";
const DEV_OTP = "123456";

export default function LoginPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [confirmationResult, setConfirmationResult] = useState<ConfirmationResult | null>(null);

  useEffect(() => {
    // Only init Recaptcha in production (Firebase is active)
    if (!IS_DEV && !window.recaptchaVerifier) {
      try {
        window.recaptchaVerifier = setupRecaptcha("recaptcha-container");
      } catch (err) {
        console.warn("Firebase not configured yet.");
      }
    }
  }, []);

  // ─────────────────────────────────────────────
  // DEV BYPASS: No Firebase needed
  // Any phone + OTP "123456" → directly hit backend
  // ─────────────────────────────────────────────
  const handleDevSendOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (phone.length !== 10) {
      setError("Enter a valid 10-digit mobile number.");
      return;
    }
    // Simulate OTP sent instantly
    setOtpSent(true);
  };

  const handleDevVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (otp !== DEV_OTP) {
        throw new Error(`Dev Mode: OTP must be ${DEV_OTP}`);
      }

      // Call backend with a mock dev token
      const res = await fetch(`${API}/auth/verify-phone`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          firebase_id_token: `dev_bypass_token_${phone}`,
          phone: `+91${phone}`,
        }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Backend error during dev login.");
      }

      const data = await res.json();
      localStorage.setItem("pmis_token", data.access_token);
      localStorage.setItem("pmis_user_id", data.user_id);
      router.push("/wizard");
    } catch (err: any) {
      setError(err.message || "Dev login failed.");
    } finally {
      setLoading(false);
    }
  };

  // ─────────────────────────────────────────────
  // PRODUCTION: Real Firebase OTP
  // ─────────────────────────────────────────────
  const handleSendOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (phone.length !== 10) throw new Error("Enter a valid 10-digit mobile number.");
      const confResult = await sendOTP(`+91${phone}`);
      setConfirmationResult(confResult as any);
      setOtpSent(true);
    } catch (err: any) {
      setError(err.message || "Failed to send OTP.");
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (!confirmationResult) throw new Error("No pending OTP.");
      if (otp.length < 6) throw new Error("Enter the 6-digit OTP.");

      const firebaseIdToken = await verifyOTP(confirmationResult, otp);

      const res = await fetch(`${API}/auth/verify-phone`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ firebase_id_token: firebaseIdToken, phone: `+91${phone}` }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Backend auth failed.");
      }

      const data = await res.json();
      localStorage.setItem("pmis_token", data.access_token);
      localStorage.setItem("pmis_user_id", data.user_id);
      router.push("/wizard");
    } catch (err: any) {
      setError(err.message || "Invalid OTP code");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center px-4 relative z-10 w-full">
      {/* Dev Mode Banner */}
      {IS_DEV && (
        <div className="w-full max-w-md mb-4 border-2 border-yellow-500 bg-yellow-50 dark:bg-yellow-900/30 p-3 flex items-start gap-3">
          <Terminal size={16} className="text-yellow-600 dark:text-yellow-400 mt-0.5 shrink-0" />
          <div>
            <p className="text-xs font-black uppercase text-yellow-700 dark:text-yellow-400 tracking-widest">
              Dev Mode Active
            </p>
            <p className="text-xs text-yellow-600 dark:text-yellow-500 mt-0.5">
              Firebase bypassed. Use any phone + OTP <strong>123456</strong> to login instantly.
            </p>
          </div>
        </div>
      )}

      <Card className="w-full max-w-md border-2 border-black dark:border-white rounded-none shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] dark:shadow-[8px_8px_0px_0px_rgba(255,255,255,1)] bg-white dark:bg-[#0a0a0a]">
        <CardContent className="p-8">
          <div className="flex items-center gap-3 mb-8">
            <div className="bg-black dark:bg-white text-white dark:text-black p-3 rounded-none">
              <Smartphone size={24} />
            </div>
            <div>
              <h1 className="text-2xl font-black uppercase tracking-tight text-black dark:text-white">
                Mobile Verification
              </h1>
              <p className="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-widest">
                PM Internship Scheme
              </p>
            </div>
          </div>

          {error && (
            <div className="border-2 border-red-500 bg-red-50 dark:bg-red-900/20 p-3 mb-6 text-sm font-bold text-red-700 dark:text-red-400">
              {error}
            </div>
          )}

          {!otpSent ? (
            <form onSubmit={IS_DEV ? handleDevSendOTP : handleSendOTP} className="space-y-4">
              <div>
                <label className="text-xs font-black uppercase tracking-widest text-gray-500 dark:text-gray-400 mb-1 block">
                  10-Digit Mobile Number
                </label>
                <div className="flex relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none border-r-2 border-black dark:border-white pr-2 my-[2px]">
                    <span className="text-gray-500 dark:text-gray-400 sm:text-sm font-black">+91</span>
                  </div>
                  <input
                    type="tel"
                    maxLength={10}
                    value={phone}
                    onChange={(e) => setPhone(e.target.value.replace(/\D/g, ""))}
                    required
                    className="w-full p-4 pl-16 border-2 border-black dark:border-white dark:text-white focus:outline-none font-black tracking-widest text-lg bg-white dark:bg-black"
                    placeholder="XXXXXXXXXX"
                  />
                </div>
              </div>

              {/* Recaptcha only loads in production */}
              {!IS_DEV && <div id="recaptcha-container"></div>}

              <Button
                type="submit"
                disabled={loading || phone.length !== 10}
                className="w-full h-14 rounded-none bg-black dark:bg-white text-white dark:text-black font-black uppercase text-base border-2 border-black dark:border-white shadow-[4px_4px_0px_0px_rgba(0,0,0,0.2)] dark:shadow-[4px_4px_0px_0px_rgba(255,255,255,0.2)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none transition-all mt-6"
              >
                {loading ? "Requesting..." : <><Phone className="mr-2 h-5 w-5" /> {IS_DEV ? "Continue (Dev Mode)" : "Send Security OTP"}</>}
              </Button>
            </form>
          ) : (
            <form onSubmit={IS_DEV ? handleDevVerifyOTP : handleVerifyOTP} className="space-y-4">
              <div className="bg-green-50 dark:bg-green-900/20 border-2 border-green-500 p-3 mb-4 text-xs font-bold text-green-700 dark:text-green-300">
                {IS_DEV ? `[DEV] Enter 123456 to authenticate as +91 ${phone}` : `OTP sent to +91 ${phone}`}
              </div>

              <div>
                <label className="text-xs font-black uppercase tracking-widest text-gray-500 dark:text-gray-400 mb-1 block">
                  Enter 6-Digit OTP
                </label>
                <input
                  type="text"
                  maxLength={6}
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))}
                  required
                  autoFocus
                  className="w-full p-4 border-2 border-black dark:border-white dark:text-white focus:outline-none font-black text-center tracking-widest text-2xl bg-white dark:bg-black"
                  placeholder="------"
                />
              </div>

              <Button
                type="submit"
                disabled={loading || otp.length !== 6}
                className="w-full h-14 rounded-none bg-black dark:bg-white text-white dark:text-black font-black uppercase text-base border-2 border-black dark:border-white shadow-[4px_4px_0px_0px_rgba(0,0,0,0.2)] dark:shadow-[4px_4px_0px_0px_rgba(255,255,255,0.2)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none transition-all mt-6"
              >
                {loading ? "Verifying..." : <><Lock className="mr-2 h-5 w-5" /> Authenticate & Access</>}
              </Button>

              <button
                type="button"
                onClick={() => { setOtpSent(false); setOtp(""); setError(""); }}
                className="w-full mt-4 text-xs font-black uppercase tracking-widest text-gray-500 dark:text-gray-400 hover:text-black dark:hover:text-white hover:underline"
              >
                Change Mobile Number
              </button>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
