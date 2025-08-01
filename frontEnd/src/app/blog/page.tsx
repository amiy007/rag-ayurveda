'use client';

import PageLayout from '../components/PageLayout';

export default function BlogPage() {
  return (
    <PageLayout
      title="Ayurveda Blog"
      description="Explore our collection of articles on Ayurveda, natural remedies, and holistic health."
    >
      <div className="space-y-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-bold text-ayurveda-dark mb-2">Coming Soon: Ayurveda Blog</h2>
          <p className="text-ayurveda-dark/80">
            Our blog is currently under development. We&apos;re working hard to bring you insightful articles
            about Ayurveda, natural remedies, and holistic health practices. Check back soon for updates!
          </p>
        </div>
      </div>
    </PageLayout>
  );
}
