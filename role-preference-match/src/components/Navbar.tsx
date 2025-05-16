
import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Briefcase } from 'lucide-react';

const Navbar = () => {
  return (
    <header className="border-b border-border sticky top-0 z-50 bg-background/95 backdrop-blur-sm">
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center gap-2">
          <Briefcase className="h-6 w-6 text-jobmate-teal" />
          <Link to="/" className="text-xl font-bold text-jobmate-navy">
            JOB MATE
          </Link>
        </div>
        <nav className="hidden md:flex items-center space-x-6">
          <Link to="/" className="text-sm font-medium hover:text-jobmate-teal transition-colors">
            Home
          </Link>
          <Link to="/input" className="text-sm font-medium hover:text-jobmate-teal transition-colors">
            Find Companies
          </Link>
          <Link to="/about" className="text-sm font-medium hover:text-jobmate-teal transition-colors">
            About
          </Link>
          <Link to="/contact" className="text-sm font-medium hover:text-jobmate-teal transition-colors">
            Contact
          </Link>
        </nav>
        <div className="flex items-center gap-4">
          <Link to="/input">
            <Button variant="default" className="bg-jobmate-teal hover:bg-jobmate-teal/90">
              Get Started
            </Button>
          </Link>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
