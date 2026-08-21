import Link from "next/link";
import { MapPin, Mail, Building2 } from "lucide-react";

// Server component on purpose: no hooks, no client JS, and the copyright year
// is rendered once on the server instead of risking a hydration mismatch.
const YEAR = new Date().getFullYear();

const PLATFORM_LINKS = [
  { label: "Start your application", href: "/login" },
  { label: "How it works", href: "/#how" },
  { label: "Your profile", href: "/profile" },
  { label: "Your matches", href: "/recommendations" },
];

export function Footer() {
  return (
    <footer className="w-full nb-rule bg-white dark:bg-[#0a0a0a] relative z-10 mt-auto">
      <div className="container max-w-6xl mx-auto px-4 sm:px-6 pt-16 pb-10">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-12 gap-10 lg:gap-8 mb-14">

          {/* Identity */}
          <div className="lg:col-span-5 space-y-5">
            <div className="flex items-center gap-3">
              <div className="nb-invert p-2">
                <Building2 className="h-5 w-5" />
              </div>
              <span className="flex flex-col leading-none">
                <span className="nb-h text-xl tracking-widest text-black dark:text-white">
                  Kaushalya
                </span>
                <span
                  className="nb-devanagari text-xs font-medium tracking-wide text-gray-600 dark:text-gray-400 mt-1"
                  lang="hi"
                >
                  कौशल्य
                </span>
              </span>
            </div>
            <p className="text-sm font-medium leading-relaxed text-gray-600 dark:text-gray-400 max-w-sm">
              The allocation engine for the PM Internship Scheme. Verify once,
              then get matched to government-verified internships with a plain
              explanation of why each one fits.
            </p>
          </div>

          {/* Platform */}
          <div className="lg:col-span-3">
            <h2 className="nb-label mb-5">Platform</h2>
            <ul className="space-y-3">
              {PLATFORM_LINKS.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm font-bold text-black dark:text-white hover:underline underline-offset-4 decoration-2"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact */}
          <div className="lg:col-span-4">
            <h2 className="nb-label mb-5">Contact</h2>
            <div className="space-y-4 text-sm font-medium text-gray-600 dark:text-gray-400">
              <div className="flex items-start gap-3">
                <MapPin size={18} className="shrink-0 mt-0.5 text-black dark:text-white" />
                <p>
                  Shastri Bhawan, Dr. Rajendra Prasad Road
                  <br />
                  New Delhi 110001, India
                </p>
              </div>
              <div className="flex items-center gap-3">
                <Mail size={18} className="shrink-0 text-black dark:text-white" />
                <a
                  href="mailto:support@pmis.gov.in"
                  className="font-bold text-black dark:text-white hover:underline underline-offset-4 decoration-2"
                >
                  support@pmis.gov.in
                </a>
              </div>
            </div>
          </div>
        </div>

        <div className="nb-rule pt-6 flex flex-col sm:flex-row justify-between items-center gap-4">
          <p className="nb-label normal-case tracking-normal">
            &copy; {YEAR} Ministry of Corporate Affairs, Government of India
          </p>
          <div className="flex items-center gap-2">
            <span
              aria-hidden="true"
              className="h-2 w-2 bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.9)]"
            />
            <span className="nb-label">Systems Operational</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
