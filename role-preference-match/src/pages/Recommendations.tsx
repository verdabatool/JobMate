
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '@/components/Layout';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Briefcase,
  Building,
  ThumbsUp,
  MapPin,
  Users,
  Star,
  ArrowLeft,
  ExternalLink
} from 'lucide-react';

// Mock data for company recommendations
const mockCompanies = [
  {
    id: 1,
    name: "TechVision Inc",
    logo: "/placeholder.svg",
    description: "Leading tech company focused on innovative solutions in software development and artificial intelligence.",
    matchScore: 95,
    location: "San Francisco, CA",
    companySize: "500-1000 employees",
    companyType: "startup",
    industry: "Technology",
    reasons: [
      "Hiring for positions matching your job title",
      "Company culture aligns with your preferences",
      "Remote-friendly work environment"
    ],
    rating: 4.8
  },
  {
    id: 2,
    name: "Global Fintech Solutions",
    logo: "/placeholder.svg",
    description: "Financial technology company revolutionizing digital payments and banking experiences for consumers worldwide.",
    matchScore: 92,
    location: "New York, NY",
    companySize: "1000-5000 employees",
    companyType: "fintech",
    industry: "Finance Technology",
    reasons: [
      "Growing team in your area of expertise",
      "Strong benefits package",
      "Great career progression opportunities"
    ],
    rating: 4.5
  },
  {
    id: 3,
    name: "HealthTech Innovations",
    logo: "/placeholder.svg",
    description: "Healthcare technology provider focused on improving patient outcomes through data-driven solutions.",
    matchScore: 88,
    location: "Boston, MA",
    companySize: "100-500 employees",
    companyType: "healthtech",
    industry: "Healthcare Technology",
    reasons: [
      "Mission-driven organization",
      "Active hiring for your role",
      "Company values match your preferences"
    ],
    rating: 4.6
  },
  {
    id: 4,
    name: "EcoSolutions Corp",
    logo: "/placeholder.svg",
    description: "Sustainability-focused organization developing green technologies and environmental solutions.",
    matchScore: 85,
    location: "Seattle, WA",
    companySize: "100-500 employees",
    companyType: "sustainability",
    industry: "Environmental Technology",
    reasons: [
      "Values-aligned with your preferences",
      "Rapidly growing team",
      "Innovative work environment"
    ],
    rating: 4.4
  },
  {
    id: 5,
    name: "Remote Workspace",
    logo: "/placeholder.svg",
    description: "Fully distributed company providing digital infrastructure solutions to businesses globally.",
    matchScore: 82,
    location: "Remote (Global)",
    companySize: "100-500 employees",
    companyType: "remote-friendly",
    industry: "Business Services",
    reasons: [
      "100% remote-first company",
      "Flexible work arrangements",
      "International team"
    ],
    rating: 4.7
  },
];

const Recommendations = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useState<any>(null);
  const [companies, setCompanies] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    const params = sessionStorage.getItem('jobSearchParams');

    if (!params) {
      toast.error("Please provide your job preferences first");
      navigate('/input');
      return;
    }

    const parsed = JSON.parse(params);
    setSearchParams(parsed);
    setIsLoading(true);

    fetch('http://localhost:5005/recommendations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        job_title: parsed.jobTitle,
        preferences: parsed.preferences || "",
        top_n: 5
      })
    })
      .then(res => res.json())
      .then(data => {
        console.log("🔁 Backend returned:", data);
        if (data.recommendations) {
          setCompanies(data.recommendations);
        } else {
          toast.error("No recommendations found");
          setCompanies([]); // fallback
        }
        setIsLoading(false);
      })
      .catch(() => {
        toast.error("Failed to fetch recommendations");
        setIsLoading(false);
      });
  }, [navigate]);

  
  const handleRetry = () => {
    navigate('/input');
  };
  
  if (isLoading) {
    return (
      <Layout>
        <div className="container py-16">
          <div className="flex flex-col items-center justify-center min-h-[40vh]">
            <div className="animate-pulse space-y-4 text-center">
              <Briefcase size={48} className="mx-auto text-jobmate-teal animate-bounce" />
              <h2 className="text-2xl font-bold">Finding your perfect company matches...</h2>
              <p className="text-gray-500">Our AI is analyzing your preferences</p>
            </div>
          </div>
        </div>
      </Layout>
    );
  }
  
  return (
    <Layout>
      <div className="container py-12 px-4 md:px-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-bold">Your Company Matches</h1>
            {searchParams && (
              <p className="text-gray-500 mt-2">
                Based on your search for <span className="font-semibold">{searchParams.jobTitle}</span> at 
                <span className="font-semibold"> {companyTypes.find(t => t.value === searchParams.companyType)?.label || searchParams.companyType}</span> companies
              </p>
            )}
          </div>
          
          <Button variant="outline" onClick={handleRetry} className="flex items-center">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Refine Search
          </Button>
        </div>
        
        {companies.length === 0 ? (
          <div className="text-center py-16">
            <Building className="mx-auto mb-4 h-12 w-12 text-gray-400" />
            <h3 className="text-xl font-bold">No matches found</h3>
            <p className="text-gray-500 mb-6">Try adjusting your search criteria</p>
            <Button onClick={handleRetry}>Try Again</Button>
          </div>
        ) : (
          <div className="grid gap-6 lg:grid-cols-2 xl:grid-cols-3">
            {companies.map((company) => (
              <Card key={company.url}>
                <CardHeader>
                  <CardTitle>{company.job_title} at {company.company}</CardTitle>
                  <CardDescription className="text-sm text-gray-500">Match Score: {company.similarity_score}</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm">{company.snippet}</p>
                </CardContent>
                <CardFooter>
                  <a href={company.url} target="_blank" rel="noopener noreferrer">
                    <Button className="w-full bg-jobmate-teal text-white">
                      Apply Now
                      <ExternalLink className="ml-2 h-4 w-4" />
                    </Button>
                  </a>
                </CardFooter>
              </Card>

            ))}
          </div>
        )}
        
        <div className="mt-12 text-center">
          <p className="text-gray-500 mb-4">Not seeing what you're looking for?</p>
          <Button onClick={handleRetry} variant="outline" className="mx-auto">
            Try Different Preferences
          </Button>
        </div>
      </div>
    </Layout>
  );
};

// Company types for display purposes
const companyTypes = [
  { value: 'startup', label: 'Startup' },
  { value: 'corporate', label: 'Corporate' },
  { value: 'remote-friendly', label: 'Remote-friendly' },
  { value: 'fintech', label: 'Fintech' },
  { value: 'edtech', label: 'Edtech' },
  { value: 'healthtech', label: 'Healthtech' },
  { value: 'sustainability', label: 'Sustainability-focused' }
];

export default Recommendations;
