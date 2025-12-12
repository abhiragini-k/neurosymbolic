import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Brain, Network, TrendingUp, Shield } from "lucide-react";
import Header from "@/components/Header";
import Background3D from "@/components/Background3D";

const Index = () => {
    return (
        <div className="min-h-screen relative">
            <Background3D />
            <div className="relative z-10">
                <Header />

                {/* Hero Section */}
                <section className="relative overflow-hidden py-20 md:py-32">
                    <div className="container relative z-10">
                        <div className="mx-auto max-w-3xl text-center">
                            <h1 className="mb-6 text-5xl font-bold tracking-tight md:text-6xl lg:text-7xl text-slate-900">
                                <span className="bg-gradient-hero bg-clip-text text-transparent">
                                    Neurosymbolic
                                </span>
                                <br />
                                Drug Repurposing
                            </h1>
                            <p className="mb-8 text-xl text-slate-600 md:text-2xl">
                                Explainable AI for discovering new therapeutic uses for existing drugs
                            </p>
                            <p className="mb-10 text-lg text-slate-500">
                                Combining Graph Neural Networks + Logical Reasoning for transparent drug discovery
                            </p>
                            <Link to="/analysis">
                                <Button size="lg" className="shadow-elevated text-lg px-8 py-6">
                                    <Brain className="mr-2 h-5 w-5" />
                                    Launch Analysis Tool
                                </Button>
                            </Link>
                        </div>
                    </div>
                </section>

                {/* Features Section */}
                <section className="py-16 md:py-24 bg-transparent">
                    <div className="container">
                        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
                            <Card className="p-6 shadow-card hover:shadow-elevated transition-all bg-white/80 backdrop-blur-sm border-slate-200">
                                <div className="mb-4 inline-flex rounded-lg bg-primary/10 p-3">
                                    <Brain className="h-6 w-6 text-primary" />
                                </div>
                                <h3 className="mb-2 text-xl font-semibold text-slate-900">Neural Networks</h3>
                                <p className="text-slate-600">
                                    Deep learning models analyze complex patterns in biomedical data
                                </p>
                            </Card>

                            <Card className="p-6 shadow-card hover:shadow-elevated transition-all bg-white/80 backdrop-blur-sm border-slate-200">
                                <div className="mb-4 inline-flex rounded-lg bg-accent/10 p-3">
                                    <Network className="h-6 w-6 text-accent" />
                                </div>
                                <h3 className="mb-2 text-xl font-semibold text-slate-900">Symbolic Reasoning</h3>
                                <p className="text-slate-600">
                                    Logic-based reasoning provides interpretable decision pathways
                                </p>
                            </Card>

                            <Card className="p-6 shadow-card hover:shadow-elevated transition-all bg-white/80 backdrop-blur-sm border-slate-200">
                                <div className="mb-4 inline-flex rounded-lg bg-drug/10 p-3">
                                    <TrendingUp className="h-6 w-6 text-drug" />
                                </div>
                                <h3 className="mb-2 text-xl font-semibold text-slate-900">Novel Predictions</h3>
                                <p className="text-slate-600">
                                    Discover unexpected therapeutic opportunities from existing drugs
                                </p>
                            </Card>

                            <Card className="p-6 shadow-card hover:shadow-elevated transition-all bg-white/80 backdrop-blur-sm border-slate-200">
                                <div className="mb-4 inline-flex rounded-lg bg-disease/10 p-3">
                                    <Shield className="h-6 w-6 text-disease" />
                                </div>
                                <h3 className="mb-2 text-xl font-semibold text-slate-900">Explainable AI</h3>
                                <p className="text-slate-600">
                                    Transparent reasoning chains build trust in predictions
                                </p>
                            </Card>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    );
};

export default Index;
