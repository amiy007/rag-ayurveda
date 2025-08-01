'use client';

import PageLayout from '../components/PageLayout';

const testimonials = [
  {
    id: 1,
    name: 'Priya S.',
    role: 'Yoga Instructor',
    content: 'This platform has been a game-changer for my practice. The Ayurvedic insights have helped me create more personalized sessions for my students.',
    rating: 5
  },
  {
    id: 2,
    name: 'Rajesh K.',
    role: 'Health Enthusiast',
    content: 'I\'ve been exploring Ayurveda for years, and this is one of the most accessible resources I\'ve found. The information is well-researched and easy to understand.',
    rating: 5
  },
  {
    id: 3,
    name: 'Ananya M.',
    role: 'Nutritionist',
    content: 'I recommend this platform to all my clients who are interested in holistic health. The combination of traditional wisdom and modern science is impressive.',
    rating: 4
  },
  {
    id: 4,
    name: 'Vikram P.',
    role: 'New to Ayurveda',
    content: 'As someone new to Ayurveda, I found the platform very user-friendly. The explanations are clear and the remedies have been helpful for my wellness journey.',
    rating: 5
  }
];

export default function TestimonialsPage() {
  return (
    <PageLayout
      title="What People Are Saying"
      description="Read testimonials from our community about their experiences with Ayurveda and our platform."
    >
      <div className="grid gap-6 md:grid-cols-2">
        {testimonials.map((testimonial) => (
          <div key={testimonial.id} className="bg-white p-6 rounded-xl shadow-md">
            <div className="flex items-center mb-4">
              <div className="flex-shrink-0 bg-ayurveda-light w-12 h-12 rounded-full flex items-center justify-center text-2xl">
                {testimonial.name.charAt(0)}
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-ayurveda-dark">{testimonial.name}</h3>
                <p className="text-ayurveda-dark/60 text-sm">{testimonial.role}</p>
              </div>
            </div>
            <div className="text-ayurveda-dark/80 mb-3">
              {testimonial.content}
            </div>
            <div className="text-ayurveda-yellow">
              {[...Array(5)].map((_, i) => (
                <span key={i} className={i < testimonial.rating ? 'text-yellow-400' : 'text-gray-300'}>
                  ★
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-12 text-center">
        <p className="text-ayurveda-dark/80 mb-4">
          Would you like to share your experience with us?
        </p>
        <a
          href="/contact"
          className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-ayurveda-green hover:bg-ayurveda-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-ayurveda-green transition-colors"
        >
          Share Your Story
        </a>
      </div>
    </PageLayout>
  );
}
