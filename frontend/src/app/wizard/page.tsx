import { WizardFlow } from "@/components/wizard/WizardFlow"

export default function WizardPage() {
  return (
    <div className="container px-4 py-12 md:py-24 max-w-5xl mx-auto">
      <div className="mb-10 text-center">
        <h1 className="text-3xl font-extrabold tracking-tight sm:text-4xl text-gray-900 dark:text-white">
          Tell us about yourself
        </h1>
        <p className="mt-4 text-lg text-gray-500 dark:text-gray-400 max-w-2xl mx-auto">
          Complete this short profile so our AI can match you with the best-fit internship opportunities.
        </p>
      </div>
      <WizardFlow />
    </div>
  )
}
