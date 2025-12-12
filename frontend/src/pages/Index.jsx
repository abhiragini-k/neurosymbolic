import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Brain, Network, TrendingUp, Shield } from "lucide-react";
import Header from "@/components/Header";

const Index = () => {
    return (
        <div className="min-h-screen bg-background">
            <Header />

            {/* Hero Section */}
            <section className="relative overflow-hidden py-20 md:py-32">
                <div className="container relative z-10">
                    <div className="mx-auto max-w-3xl text-center">
                        <h1 className="mb-6 text-5xl font-bold tracking-tight md:text-6xl lg:text-7xl">
                            <span className="bg-gradient-hero bg-clip-text text-transparent">
                                Neurosymbolic
                            </span>
                            <br />
                            Drug Repurposing
                        </h1>
                        <p className="mb-8 text-xl text-muted-foreground md:text-2xl">
                            Explainable AI for discovering new therapeutic uses for existing drugs
                        </p>
                        <p className="mb-10 text-lg text-muted-foreground">
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

                {/* Background decoration */}
                <div className="absolute inset-0 -z-10 overflow-hidden">
                    <div className="absolute -top-1/2 left-1/2 h-96 w-96 -translate-x-1/2 rounded-full bg-primary/10 blur-3xl" />
                    <div className="absolute top-1/2 right-0 h-96 w-96 translate-x-1/2 rounded-full bg-accent/10 blur-3xl" />
                </div>
            </section>

            {/* Features Section */}
            <section className="py-16 md:py-24 bg-muted/30">
                <div className="container">
                    <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
                        <Card className="p-6 shadow-card hover:shadow-elevated transition-all">
                            <div className="mb-4 inline-flex rounded-lg bg-primary/10 p-3">
                                <Brain className="h-6 w-6 text-primary" />
                            </div>
                            <h3 className="mb-2 text-xl font-semibold">Neural Networks</h3>
                            <p className="text-muted-foreground">
                                Deep learning models analyze complex patterns in biomedical data
                            </p>
                        </Card>

                        <Card className="p-6 shadow-card hover:shadow-elevated transition-all">
                            <div className="mb-4 inline-flex rounded-lg bg-accent/10 p-3">
                                <Network className="h-6 w-6 text-accent" />
                            </div>
                            <h3 className="mb-2 text-xl font-semibold">Symbolic Reasoning</h3>
                            <p className="text-muted-foreground">
                                Logic-based reasoning provides interpretable decision pathways
                            </p>
                        </Card>

                        <Card className="p-6 shadow-card hover:shadow-elevated transition-all">
                            <div className="mb-4 inline-flex rounded-lg bg-drug p-3">
                                <TrendingUp className="h-6 w-6 text-white" />
                            </div>
                            <h3 className="mb-2 text-xl font-semibold">Novel Predictions</h3>
                            <p className="text-muted-foreground">
                                Discover unexpected therapeutic opportunities from existing drugs
                            </p>
                        </Card>

                        <Card className="p-6 shadow-card hover:shadow-elevated transition-all">
                            <div className="mb-4 inline-flex rounded-lg bg-disease p-3">
                                <Shield className="h-6 w-6 text-white" />
                            </div>
                            <h3 className="mb-2 text-xl font-semibold">Explainable AI</h3>
                            <p className="text-muted-foreground">
                                Transparent reasoning chains build trust in predictions
                            </p>
                        </Card>
                    </div>
                </div>
            </section>
        </div>
    );
};

export default Index;
