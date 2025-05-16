
import { useLocation, Link } from "react-router-dom";
import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Briefcase } from "lucide-react";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname
    );
  }, [location.pathname]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 px-4">
      <Briefcase className="h-16 w-16 text-jobmate-teal mb-6" />
      <h1 className="text-5xl font-bold mb-4">404</h1>
      <p className="text-xl text-gray-600 mb-6 text-center">Oops! We couldn't find the page you're looking for</p>
      <p className="text-gray-500 mb-8 max-w-md text-center">
        The page you're looking for doesn't exist or has been moved.
      </p>
      <div className="flex flex-col sm:flex-row gap-4">
        <Link to="/">
          <Button className="bg-jobmate-teal hover:bg-jobmate-teal/90">
            Return to Home
          </Button>
        </Link>
        <Link to="/input">
          <Button variant="outline">
            Find Companies
          </Button>
        </Link>
      </div>
    </div>
  );
};

export default NotFound;
