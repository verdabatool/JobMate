
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '@/components/Layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { 
  Select, 
  SelectContent, 
  SelectGroup, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { toast } from 'sonner';
import { 
  Briefcase,
  Building,
  ArrowRight
} from 'lucide-react';

// Company types for selection
const companyTypes = [
  { value: 'startup', label: 'Startup' },
  { value: 'corporate', label: 'Corporate' },
  { value: 'remote-friendly', label: 'Remote-friendly' },
  { value: 'fintech', label: 'Fintech' },
  { value: 'edtech', label: 'Edtech' },
  { value: 'healthtech', label: 'Healthtech' },
  { value: 'sustainability', label: 'Sustainability-focused' }
];

const UserInput = () => {
  const navigate = useNavigate();
  const [jobTitle, setJobTitle] = useState('');
  const [companyType, setCompanyType] = useState('');
  const [preferences, setPreferences] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!jobTitle) {
      toast.error("Please enter a job title");
      return;
    }
    
    // if (!companyType) {
    //   toast.error("Please select a company type");
    //   return;
    // }
    
    setIsLoading(true);
    
    // Simulate API call with a timeout
    setTimeout(() => {
      // Store the form data in sessionStorage to pass to the recommendations page
      sessionStorage.setItem('jobSearchParams', JSON.stringify({
        jobTitle,
        companyType,
        preferences
      }));
      
      setIsLoading(false);
      navigate('/recommendations');
    }, 1500);
  };
  
  return (
    <Layout>
      <div className="container max-w-5xl py-12 px-4 md:px-6">
        <Card className="border shadow-lg">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl md:text-3xl font-bold">Find Your Ideal Company</CardTitle>
            <CardDescription className="text-lg text-gray-500">
              Tell us about your preferences and we'll match you with the perfect companies
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <Briefcase className="h-5 w-5 text-jobmate-teal" />
                    <Label htmlFor="job-title" className="text-lg">Job Title or Role</Label>
                  </div>
                  <Input
                    id="job-title"
                    placeholder="e.g., Software Engineer, Marketing Manager, UX Designer"
                    value={jobTitle}
                    onChange={(e) => setJobTitle(e.target.value)}
                    className="w-full"
                    required
                  />
                </div>
                {/*                 
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <Building className="h-5 w-5 text-jobmate-teal" />
                    <Label htmlFor="company-type" className="text-lg">Company Type</Label>
                  </div>
                  <Select value={companyType} onValueChange={setCompanyType}>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select company type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectGroup>
                        {companyTypes.map((type) => (
                          <SelectItem key={type.value} value={type.value}>
                            {type.label}
                          </SelectItem>
                        ))}
                      </SelectGroup>
                    </SelectContent>
                  </Select>
                </div> */}
                
                <div className="space-y-2">
                  <Label htmlFor="preferences" className="text-lg">Culture & Environment Preferences (Optional)</Label>
                  <Textarea
                    id="preferences"
                    placeholder="Describe any company culture, values, or environment preferences you're looking for..."
                    value={preferences}
                    onChange={(e) => setPreferences(e.target.value)}
                    className="min-h-[120px] w-full"
                  />
                </div>
              </div>
              
              <div className="flex justify-center">
                <Button 
                  type="submit" 
                  className="bg-jobmate-teal hover:bg-jobmate-teal/90 text-white px-8 py-6 text-lg"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <>
                      <span className="animate-pulse">Finding matches</span>
                      <span className="ml-2">...</span>
                    </>
                  ) : (
                    <>
                      Find Companies
                      <ArrowRight className="ml-2 h-5 w-5" />
                    </>
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
        
        <div className="mt-12 bg-jobmate-lightgray p-6 rounded-lg">
          <h3 className="text-xl font-bold mb-4">How Your Data Helps Us Find Matches</h3>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded shadow-sm">
              <h4 className="font-semibold mb-2">Job Title Analysis</h4>
              <p className="text-sm text-gray-600">We match your desired role with companies hiring for similar positions.</p>
            </div>
            <div className="bg-white p-4 rounded shadow-sm">
              <h4 className="font-semibold mb-2">Company Type Filtering</h4>
              <p className="text-sm text-gray-600">We narrow down to organizations that match your preferred company style.</p>
            </div>
            <div className="bg-white p-4 rounded shadow-sm">
              <h4 className="font-semibold mb-2">Culture Matching</h4>
              <p className="text-sm text-gray-600">Your preferences help us identify companies with compatible cultures.</p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default UserInput;
