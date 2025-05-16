
import React, { useState } from 'react';
import Layout from '@/components/Layout';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import {
  Mail,
  Phone,
  MessageCircle,
  Send
} from 'lucide-react';

const Contact = () => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // Validate form
    if (!formData.name || !formData.email || !formData.message) {
      toast.error("Please fill in all required fields");
      setIsSubmitting(false);
      return;
    }
    
    // Simulate form submission
    setTimeout(() => {
      toast.success("Message sent successfully! We'll be in touch soon.");
      setFormData({
        name: '',
        email: '',
        subject: '',
        message: ''
      });
      setIsSubmitting(false);
    }, 1500);
  };
  
  return (
    <Layout>
      <div className="container py-12 px-4 md:px-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-3xl font-bold md:text-4xl mb-4">Contact Us</h1>
            <p className="text-xl text-gray-600">
              Have a question or feedback? We'd love to hear from you.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="md:col-span-1 space-y-8">
              <div>
                <h3 className="text-lg font-semibold mb-4">Get in Touch</h3>
                <p className="text-gray-600 mb-6">
                  Our team is ready to answer your questions and help you get the most out of JOB MATE.
                </p>
                
                <div className="space-y-4">
                  <div className="flex items-center">
                    <div className="bg-jobmate-teal/10 p-2 rounded-full mr-4">
                      <Mail className="h-5 w-5 text-jobmate-teal" />
                    </div>
                    <div>
                      <p className="text-sm font-medium">Email Us</p>
                      <p className="text-sm text-gray-600">hello@jobmate.com</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center">
                    <div className="bg-jobmate-teal/10 p-2 rounded-full mr-4">
                      <Phone className="h-5 w-5 text-jobmate-teal" />
                    </div>
                    <div>
                      <p className="text-sm font-medium">Call Us</p>
                      <p className="text-sm text-gray-600">+1 (555) 123-4567</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center">
                    <div className="bg-jobmate-teal/10 p-2 rounded-full mr-4">
                      <MessageCircle className="h-5 w-5 text-jobmate-teal" />
                    </div>
                    <div>
                      <p className="text-sm font-medium">Live Chat</p>
                      <p className="text-sm text-gray-600">Available 9am-5pm EST</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold mb-4">Office Location</h3>
                <p className="text-gray-600 mb-2">
                  JOB MATE Headquarters<br />
                  123 AI Avenue<br />
                  San Francisco, CA 94105
                </p>
              </div>
            </div>
            
            <div className="md:col-span-2 bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-semibold mb-6">Send Us a Message</h3>
              
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid gap-6 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="name">Full Name <span className="text-red-500">*</span></Label>
                    <Input 
                      id="name"
                      name="name" 
                      placeholder="Your name" 
                      value={formData.name} 
                      onChange={handleChange}
                      required
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="email">Email <span className="text-red-500">*</span></Label>
                    <Input 
                      id="email"
                      name="email" 
                      type="email" 
                      placeholder="your@email.com" 
                      value={formData.email} 
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="subject">Subject</Label>
                  <Input 
                    id="subject"
                    name="subject" 
                    placeholder="What's this regarding?" 
                    value={formData.subject} 
                    onChange={handleChange}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="message">Message <span className="text-red-500">*</span></Label>
                  <Textarea 
                    id="message"
                    name="message" 
                    placeholder="How can we help you?" 
                    className="min-h-[150px]" 
                    value={formData.message} 
                    onChange={handleChange}
                    required
                  />
                </div>
                
                <Button 
                  type="submit" 
                  className="bg-jobmate-teal hover:bg-jobmate-teal/90 w-full flex items-center justify-center"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? (
                    <span className="flex items-center">
                      Sending... <span className="animate-pulse ml-1">●</span>
                    </span>
                  ) : (
                    <span className="flex items-center">
                      Send Message <Send className="ml-2 h-4 w-4" />
                    </span>
                  )}
                </Button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Contact;
