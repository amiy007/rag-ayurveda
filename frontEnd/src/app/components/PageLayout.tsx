import { ReactNode } from 'react';
import Head from 'next/head';
import Link from 'next/link';

type PageLayoutProps = {
  title: string;
  description: string;
  children: ReactNode;
};

export default function PageLayout({ title, description, children }: PageLayoutProps) {
  return (
    <>
      <Head>
        <title>{`${title} | Ayurveda Remedy Bot`}</title>
        <meta name="description" content={description} />
      </Head>
      <div className="min-h-screen pt-20 pb-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center">
            <h1 className="text-4xl font-extrabold text-ayurveda-dark sm:text-5xl sm:tracking-tight lg:text-6xl">
              {title}
            </h1>
            <p className="max-w-xl mt-5 mx-auto text-xl text-ayurveda-dark/80">
              {description}
            </p>
          </div>
          
          <div className="mt-12 bg-white/90 backdrop-blur-sm rounded-2xl shadow-xl p-6 sm:p-8">
            {children}
          </div>
          
          <div className="mt-12 text-center">
            <p className="text-ayurveda-dark/80">
              This page is under construction. Please check back later for updates!
            </p>
            <Link
              href="/"
              className="mt-4 inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-ayurveda-green hover:bg-ayurveda-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-ayurveda-green transition-colors"
            >
              ← Back to Home
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}
