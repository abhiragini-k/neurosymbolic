import { Link, useLocation } from "react-router-dom";
import { Brain } from "lucide-react";
import { cn } from "@/lib/utils";

const Header = () => {
  const location = useLocation();
  
  const isActive = (path: string) => location.pathname === path;
  
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/60">
      <div className="container flex h-16 items-center justify-between">
        <Link to="/" className="flex items-center gap-2 text-xl font-bold">
          <Brain className="h-6 w-6 text-primary" />
          <span className="bg-gradient-hero bg-clip-text text-transparent">
            Neurosymbolic
          </span>
        </Link>
        
        <nav className="hidden md:flex items-center gap-6">
          <Link
            to="/"
            className={cn(
              "text-sm font-medium transition-colors hover:text-primary",
              isActive("/") ? "text-primary" : "text-muted-foreground"
            )}
          >
            Home
          </Link>
          <Link
            to="/analysis"
            className={cn(
              "text-sm font-medium transition-colors hover:text-primary",
              isActive("/analysis") ? "text-primary" : "text-muted-foreground"
            )}
          >
            Analysis
          </Link>
          <Link
            to="/results"
            className={cn(
              "text-sm font-medium transition-colors hover:text-primary",
              isActive("/results") ? "text-primary" : "text-muted-foreground"
            )}
          >
            Results
          </Link>
          <Link
            to="/documentation"
            className={cn(
              "text-sm font-medium transition-colors hover:text-primary",
              isActive("/documentation") ? "text-primary" : "text-muted-foreground"
            )}
          >
            Documentation
          </Link>
          <Link
            to="/about"
            className={cn(
              "text-sm font-medium transition-colors hover:text-primary",
              isActive("/about") ? "text-primary" : "text-muted-foreground"
            )}
          >
            About
          </Link>
        </nav>
      </div>
    </header>
  );
};

export default Header;
