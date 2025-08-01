'use client';

import PageLayout from '../components/PageLayout';

export default function ResourcesPage() {
  return (
    <PageLayout
      title="Ayurveda Resources"
      description="Discover helpful resources to learn more about Ayurveda and holistic health."
    >
      <div className="space-y-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-bold text-ayurveda-dark mb-4">Coming Soon: Resource Library</h2>
          <p className="text-ayurveda-dark/80 mb-4">
            We&apos;re compiling a comprehensive collection of Ayurveda resources including:
          </p>
          <ul className="list-disc pl-5 space-y-2 text-ayurveda-dark/80">
            <li>Recommended books on Ayurveda</li>
            <li>Guided meditation and yoga practices</li>
            <li>Seasonal eating guides</li>
            <li>Herbal remedy references</li>
            <li>Self-care routines</li>
          </ul>
          <p className="mt-4 text-ayurveda-dark/80">
            Check back soon for our curated collection of resources to support your Ayurvedic journey.
          </p>
        </div>
      </div>
    </PageLayout>
  );
}
