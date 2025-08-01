'use client';

import { useState } from 'react';
import PageLayout from '../components/PageLayout';

type FAQItem = {
  question: string;
  answer: string;
};

const faqs: FAQItem[] = [
  {
    question: 'What is Ayurveda?',
    answer: 'Ayurveda is a traditional system of medicine with historical roots in the Indian subcontinent. It emphasizes a holistic approach to health and wellness, focusing on balance between body, mind, and spirit.'
  },
  {
    question: 'Is Ayurveda scientifically proven?',
    answer: 'Many traditional Ayurvedic practices have been studied scientifically, with some showing promising results. However, not all aspects of Ayurveda have been thoroughly researched by modern scientific methods.'
  },
  {
    question: 'How can I get started with Ayurveda?',
    answer: 'A good way to start is by learning about your dosha (body type) and making small dietary and lifestyle changes based on Ayurvedic principles. Consulting with a qualified Ayurvedic practitioner is recommended for personalized guidance.'
  },
  {
    question: 'Is this information a substitute for medical advice?',
    answer: 'No, the information provided by our chatbot is for educational purposes only and should not be considered medical advice. Always consult with a qualified healthcare provider before making any changes to your health regimen.'
  }
];

export default function FAQPage() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const toggleFAQ = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <PageLayout
      title="Frequently Asked Questions"
      description="Find answers to common questions about Ayurveda and our platform."
    >
      <div className="space-y-4">
        {faqs.map((faq, index) => (
          <div key={index} className="bg-white rounded-lg shadow-md overflow-hidden">
            <button
              className="w-full px-6 py-4 text-left focus:outline-none"
              onClick={() => toggleFAQ(index)}
            >
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-ayurveda-dark">
                  {faq.question}
                </h3>
                <span className="text-ayurveda-green text-xl">
                  {openIndex === index ? '−' : '+'}
                </span>
              </div>
            </button>
            {openIndex === index && (
              <div className="px-6 pb-4 pt-0 text-ayurveda-dark/80">
                {faq.answer}
              </div>
            )}
          </div>
        ))}
        
        <div className="mt-8 text-center text-ayurveda-dark/80">
          <p>Have more questions? Feel free to <a href="/contact" className="text-ayurveda-green hover:underline">contact us</a>.</p>
        </div>
      </div>
    </PageLayout>
  );
}
