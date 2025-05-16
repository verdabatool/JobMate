
import React from 'react';
import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';
import Layout from '@/components/Layout';
import { 
  Briefcase, 
  Building, 
  CheckCircle, 
  Search, 
  ArrowRight, 
  Users,
  ThumbsUp
} from 'lucide-react';

const Index = () => {
  return (
    <Layout>
      {/* Hero Section */}
      <section className="py-16 md:py-24">
        <div className="container px-4 md:px-6">
          <div className="grid gap-6 lg:grid-cols-2 lg:gap-12 items-center">
            <div className="flex flex-col justify-center space-y-4 animate-fade-in">
              <div className="space-y-2">
                <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl">
                  Find Your Perfect <span className="gradient-text">Company Match</span>
                </h1>
                <p className="max-w-[600px] text-gray-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                  JOB MATE uses AI to help you discover companies that align perfectly with your desired role and workplace preferences.
                </p>
              </div>
              <div className="flex flex-col gap-2 min-[400px]:flex-row">
                <Link to="/input">
                  <Button className="bg-jobmate-teal hover:bg-jobmate-teal/90 text-white">
                    Get Started
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
                <Link to="/about">
                  <Button variant="outline">
                    Learn More
                  </Button>
                </Link>
              </div>
              <div className="flex items-center space-x-4 text-sm">
                <div className="flex items-center">
                  <CheckCircle className="mr-1 h-4 w-4 text-jobmate-teal" />
                  <span>850K+ Jobs</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="mr-1 h-4 w-4 text-jobmate-teal" />
                  <span>AI-Powered</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="mr-1 h-4 w-4 text-jobmate-teal" />
                  <span>Free to Use</span>
                </div>
              </div>
            </div>
            <div className="flex items-center justify-center animate-fade-in">
              <div className="rounded-xl bg-gradient-to-r from-jobmate-teal/20 to-jobmate-purple/20 p-8">
                <img
                  src="https://images.unsplash.com/photo-1519389950473-47ba0277781c?ixlib=rb-4.0.3"
                  alt="People using laptops"
                  className="mx-auto aspect-video rounded-xl object-cover w-full max-w-md shadow-xl"
                />
              </div>
            </div>
          </div>
        </div>
      </section>
      
      {/* How It Works */}
      <section className="py-16 bg-jobmate-lightgray">
        <div className="container px-4 md:px-6">
          <div className="flex flex-col items-center justify-center space-y-4 text-center">
            <div className="space-y-2">
              <div className="inline-block rounded-lg bg-jobmate-teal/10 px-3 py-1 text-sm text-jobmate-teal">
                How It Works
              </div>
              <h2 className="text-3xl font-bold tracking-tighter md:text-4xl">
                Simple Steps to Find Your Ideal Company
              </h2>
              <p className="max-w-[900px] text-gray-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                Our AI-powered platform makes finding your perfect company match easy and intuitive.
              </p>
            </div>
          </div>
          <div className="mx-auto grid max-w-5xl gap-6 py-12 md:grid-cols-3">
            <div className="flex flex-col items-center space-y-4 rounded-lg border p-6 shadow-sm">
              <div className="rounded-full bg-jobmate-teal p-3 text-white">
                <Briefcase className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold">Enter Your Job Role</h3>
              <p className="text-gray-500 text-center">
                Tell us about your desired job title or role and your experience level.
              </p>
            </div>
            <div className="flex flex-col items-center space-y-4 rounded-lg border p-6 shadow-sm">
              <div className="rounded-full bg-jobmate-teal p-3 text-white">
                <Building className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold">Specify Preferences</h3>
              <p className="text-gray-500 text-center">
                Select the type of company you want to work for and culture preferences.
              </p>
            </div>
            <div className="flex flex-col items-center space-y-4 rounded-lg border p-6 shadow-sm">
              <div className="rounded-full bg-jobmate-teal p-3 text-white">
                <ThumbsUp className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold">Get Recommendations</h3>
              <p className="text-gray-500 text-center">
                Receive AI-powered company recommendations that match your criteria.
              </p>
            </div>
          </div>
          <div className="flex justify-center">
            <Link to="/input">
              <Button className="bg-jobmate-teal hover:bg-jobmate-teal/90">
                Start Your Search
                <Search className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>
      
      {/* Features */}
      <section className="py-16">
        <div className="container px-4 md:px-6">
          <div className="flex flex-col items-center justify-center space-y-4 text-center">
            <div className="space-y-2">
              <div className="inline-block rounded-lg bg-jobmate-teal/10 px-3 py-1 text-sm text-jobmate-teal">
                Features
              </div>
              <h2 className="text-3xl font-bold tracking-tighter md:text-4xl">Powered by Advanced Technology</h2>
              <p className="max-w-[900px] text-gray-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                JOB MATE leverages cutting-edge AI to provide accurate and personalized recommendations.
              </p>
            </div>
          </div>
          <div className="grid gap-6 py-12 lg:grid-cols-2 lg:gap-12">
            <img
              src="https://images.unsplash.com/photo-1498050108023-c5249f4df085?ixlib=rb-4.0.3"
              alt="AI Technology"
              className="mx-auto aspect-video rounded-xl object-cover shadow-xl"
            />
            <div className="flex flex-col justify-center space-y-4">
              <ul className="grid gap-6">
                <li className="flex items-start gap-4">
                  <div className="rounded-full bg-jobmate-teal/10 p-1">
                    <Users className="h-6 w-6 text-jobmate-teal" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold">Personalized Matching</h3>
                    <p className="text-gray-500">
                      Our recommendation engine understands your unique preferences and career goals.
                    </p>
                  </div>
                </li>
                <li className="flex items-start gap-4">
                  <div className="rounded-full bg-jobmate-teal/10 p-1">
                    <Search className="h-6 w-6 text-jobmate-teal" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold">Vast Database</h3>
                    <p className="text-gray-500">
                      Access to 850K+ job listings with detailed company information and insights.
                    </p>
                  </div>
                </li>
                <li className="flex items-start gap-4">
                  <div className="rounded-full bg-jobmate-teal/10 p-1">
                    <CheckCircle className="h-6 w-6 text-jobmate-teal" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold">Smart Filtering</h3>
                    <p className="text-gray-500">
                      Intelligent filters that consider company culture, size, industry, and more.
                    </p>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>
      
      {/* CTA Section */}
      <section className="py-16 bg-jobmate-navy text-white">
        <div className="container px-4 md:px-6">
          <div className="grid gap-6 lg:grid-cols-2 lg:gap-12 items-center">
            <div className="space-y-4">
              <h2 className="text-3xl font-bold tracking-tighter md:text-4xl">
                Ready to Find Your Dream Company?
              </h2>
              <p className="text-gray-300 md:text-xl/relaxed">
                Start your search now and let our AI-powered platform match you with companies that align with your career goals and preferences.
              </p>
            </div>
            <div className="flex flex-col gap-2 min-[400px]:flex-row justify-center lg:justify-end">
              <Link to="/input">
                <Button className="bg-jobmate-teal hover:bg-jobmate-teal/90 text-white">
                  Get Started Now
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link to="/about">
                <Button variant="outline" className="border-white text-white hover:bg-white hover:text-jobmate-navy">
                  Learn More
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default Index;
