import { initializeApp } from 'firebase/app';
import { getAuth, RecaptchaVerifier, signInWithPhoneNumber, ConfirmationResult } from 'firebase/auth';

const firebaseConfig = {
  apiKey:            process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain:        process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId:         process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket:     process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId:             process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

// Initialize Firebase only if config is provided
const app = firebaseConfig.apiKey ? initializeApp(firebaseConfig) : null;
export const auth = app ? getAuth(app) : null;

let recaptchaVerifier: RecaptchaVerifier | null = null;

export function setupRecaptcha(containerId: string) {
  if (!auth) throw new Error('Firebase missing config');
  recaptchaVerifier = new RecaptchaVerifier(auth, containerId, { size: 'invisible' });
  return recaptchaVerifier;
}

export async function sendOTP(phoneNumber: string): Promise<any> {
  // phoneNumber must be in E.164 format: +91XXXXXXXXXX
  if (!auth) {
    console.warn("MOCK FIREBASE: No config found. Simulating OTP sent to " + phoneNumber);
    return { isMock: true, verify: () => "simulated_token_" + phoneNumber };
  }
  if (!recaptchaVerifier) throw new Error('Recaptcha not initialized');
  return signInWithPhoneNumber(auth, phoneNumber, recaptchaVerifier);
}

export async function verifyOTP(
  confirmationResult: any,
  otp: string
): Promise<string> {
  if (confirmationResult.isMock) {
    console.warn("MOCK FIREBASE: Simulating OTP verification for " + otp);
    if (otp !== "123456") throw new Error("Mock OTP must be 123456");
    return confirmationResult.verify();
  }
  const result = await confirmationResult.confirm(otp);
  return result.user.getIdToken();
}
