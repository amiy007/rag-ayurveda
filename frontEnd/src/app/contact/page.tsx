'use client';

import PageLayout from '../components/PageLayout';

export default function ContactPage() {
  return (
    <PageLayout
      title="Contact Us"
      description="Get in touch with our team for questions or feedback."
    >
      <div className="space-y-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-bold text-ayurveda-dark mb-4">Get In Touch</h2>
          <p className="text-ayurveda-dark/80 mb-6">
            We&apos;d love to hear from you! Whether you have questions about Ayurveda, 
            feedback about our platform, or just want to say hello, please reach out.
          </p>
          
          <div className="mt-8 space-y-4">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-ayurveda-light p-3 rounded-full">
                <span className="text-ayurveda-dark text-xl">✉️</span>
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-ayurveda-dark">Email Us</h3>
                <p className="text-ayurveda-dark/80">contact@ayurvedabot.example.com</p>
              </div>
            </div>
            
            <div className="pt-4">
              <p className="text-ayurveda-dark/80">
                We typically respond to all inquiries within 24-48 hours.
              </p>
            </div>
          </div>
        </div>
      </div>
    </PageLayout>
  );
}
