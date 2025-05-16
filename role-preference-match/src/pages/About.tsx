
import React from 'react';
import Layout from '@/components/Layout';
import { 
  Building, 
  Users, 
  Database, 
  Code, 
  ChartBar
} from 'lucide-react';

const About = () => {
  return (
    <Layout>
      <div className="container py-12 px-4 md:px-6">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-3xl font-bold md:text-4xl mb-4">About JOB MATE</h1>
            <p className="text-xl text-gray-600">
              Transforming how job seekers find their ideal company matches through AI-powered recommendations.
            </p>
          </div>
          
          <div className="prose prose-lg max-w-none">
            <div className="mb-8">
              <h2 className="text-2xl font-bold mb-4">Our Mission</h2>
              <p className="text-gray-600">
                At JOB MATE, we believe finding the right company is just as important as finding the right role. 
                Our mission is to help job seekers discover companies that truly align with their career goals, 
                values, and workplace preferences, creating better matches that lead to more fulfilling careers.
              </p>
            </div>
            
            <div className="mb-8">
              <h2 className="text-2xl font-bold mb-4">How It Works</h2>
              <p className="text-gray-600 mb-6">
                JOB MATE leverages advanced machine learning and natural language processing to match job seekers 
                with companies based on multiple dimensions of compatibility. Here's what powers our platform:
              </p>
              
              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-jobmate-lightgray rounded-lg p-6">
                  <div className="flex items-center mb-3">
                    <Database className="h-5 w-5 text-jobmate-teal mr-2" />
                    <h3 className="font-semibold">Extensive Data</h3>
                  </div>
                  <p className="text-gray-600 text-sm">
                    Our platform analyzes data from over 850,000 job listings, company profiles, 
                    and employee reviews to build comprehensive company profiles.
                  </p>
                </div>
                
                <div className="bg-jobmate-lightgray rounded-lg p-6">
                  <div className="flex items-center mb-3">
                    <Code className="h-5 w-5 text-jobmate-teal mr-2" />
                    <h3 className="font-semibold">Recommendation Engine</h3>
                  </div>
                  <p className="text-gray-600 text-sm">
                    We use advanced semantic matching algorithms and natural language processing 
                    to understand both explicit and implicit job preferences.
                  </p>
                </div>
              </div>
            </div>
            
            <div className="mb-8">
              <h2 className="text-2xl font-bold mb-4">Our Team</h2>
              <p className="text-gray-600 mb-6">
                JOB MATE was founded by a team of data scientists, HR professionals, and career coaches 
                who recognized the need for a more sophisticated approach to job matching.
              </p>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="w-24 h-24 bg-jobmate-navy/10 rounded-full mx-auto mb-3 flex items-center justify-center">
                    <Users className="h-12 w-12 text-jobmate-teal" />
                  </div>
                  <h4 className="font-bold">Data Science Team</h4>
                  <p className="text-sm text-gray-600">Building and refining our recommendation algorithms</p>
                </div>
                
                <div className="text-center">
                  <div className="w-24 h-24 bg-jobmate-navy/10 rounded-full mx-auto mb-3 flex items-center justify-center">
                    <Building className="h-12 w-12 text-jobmate-teal" />
                  </div>
                  <h4 className="font-bold">HR Specialists</h4>
                  <p className="text-sm text-gray-600">Ensuring our matches reflect real-world hiring practices</p>
                </div>
                
                <div className="text-center">
                  <div className="w-24 h-24 bg-jobmate-navy/10 rounded-full mx-auto mb-3 flex items-center justify-center">
                    <ChartBar className="h-12 w-12 text-jobmate-teal" />
                  </div>
                  <h4 className="font-bold">Product Team</h4>
                  <p className="text-sm text-gray-600">Creating an intuitive, helpful user experience</p>
                </div>
              </div>
            </div>
            
            <div>
              <h2 className="text-2xl font-bold mb-4">Our Commitment</h2>
              <p className="text-gray-600">
                We're committed to continuously improving our platform through user feedback, 
                additional data sources, and refinements to our matching algorithms. 
                Our goal is to make JOB MATE the most accurate and helpful tool for finding 
                not just a job, but a workplace where you can truly thrive.
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default About;
