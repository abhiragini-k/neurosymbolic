import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";
import Index from "./pages/Index";
import Analysis from "./pages/Analysis";
import AnalysisDetail from "./pages/AnalysisDetail";
import EvidencePage from "./pages/EvidencePage";
import About from "./pages/About";
import Documentation from "./pages/Documentation";
import Results from "./pages/Results";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
    <QueryClientProvider client={queryClient}>
        <TooltipProvider>
            <Toaster />
            <Sonner />
            <AuthProvider>
                <BrowserRouter>
                    <Routes>
                        <Route path="/login" element={<Login />} />

                        <Route element={<ProtectedRoute />}>
                            <Route path="/" element={<Index />} />
                            <Route path="/analysis" element={<Analysis />} />
                            <Route path="/analysis/detail" element={<AnalysisDetail />} />
                            <Route path="/evidence/:diseaseId" element={<EvidencePage />} />
                            <Route path="/results" element={<Results />} />
                            <Route path="/documentation" element={<Documentation />} />
                            <Route path="/about" element={<About />} />
                        </Route>

                        {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
                        <Route path="*" element={<NotFound />} />
                    </Routes>
                </BrowserRouter>
            </AuthProvider>
        </TooltipProvider>
    </QueryClientProvider>
);

export default App;
