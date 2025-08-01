'use client';

import PageLayout from '../components/PageLayout';

export default function AboutPage() {
  return (
    <PageLayout
      title="About Us"
      description="Learn about our mission to make Ayurvedic wisdom accessible to everyone."
    >
      <div className="space-y-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-bold text-ayurveda-dark mb-4">Our Mission</h2>
          <p className="text-ayurveda-dark/80 mb-4">
            We are dedicated to making the ancient wisdom of Ayurveda accessible to everyone. 
            Our platform combines traditional knowledge with modern technology to provide 
            personalized health insights and natural remedies.
          </p>
          
          <h2 className="text-2xl font-bold text-ayurveda-dark mt-8 mb-4">Our Values</h2>
          <ul className="space-y-3 text-ayurveda-dark/80">
            <li>• Holistic approach to health and wellness</li>
            <li>• Evidence-based traditional medicine</li>
            <li>• Accessible and easy-to-understand information</li>
            <li>• Respect for ancient wisdom with modern application</li>
          </ul>
        </div>
      </div>
    </PageLayout>
  );
}
