import React from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft, ExternalLink, Search, BookOpen, FlaskConical } from "lucide-react";

const EvidencePage = () => {
    const { diseaseId } = useParams();
    const navigate = useNavigate();
    const location = useLocation();

    // Get params from state or fallback
    const { drug, diseaseName } = location.state || {};

    if (!drug || !diseaseName) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen bg-background text-foreground p-6">
                <h2 className="text-xl font-bold mb-2">Context Missing</h2>
                <p className="text-muted-foreground mb-6">Please start from the Analysis page.</p>
                <Button onClick={() => navigate('/analysis')} variant="outline">
                    <ArrowLeft className="mr-2 h-4 w-4" /> Go Back
                </Button>
            </div>
        );
    }

    const queries = [
        {
            title: "Mechanism of Action",
            query: `${drug} ${diseaseName} mechanism of action`,
            icon: <FlaskConical className="h-5 w-5 text-purple-600" />,
            desc: "Understand the biological pathways and interactions."
        },
        {
            title: "Clinical Studies",
            query: `${drug} ${diseaseName} clinical trial results`,
            icon: <BookOpen className="h-5 w-5 text-blue-600" />,
            desc: "Review recent clinical trial outcomes and findings."
        },
        {
            title: "Therapeutic Efficacy",
            query: `${drug} treatment efficacy for ${diseaseName}`,
            icon: <Search className="h-5 w-5 text-green-600" />,
            desc: "Evaluate effectiveness and treatment potential."
        },
        {
            title: "Side Effects & Toxicity",
            query: `${drug} side effects in ${diseaseName} patients`,
            icon: <ExternalLink className="h-5 w-5 text-red-600" />,
            desc: "Investigate potential adverse effects/contraindications."
        }
    ];

    const openSearch = (query, site = 'google') => {
        let url = "";
        if (site === 'scholar') {
            url = `https://scholar.google.com/scholar?q=${encodeURIComponent(query)}`;
        } else if (site === 'pubmed') {
            url = `https://pubmed.ncbi.nlm.nih.gov/?term=${encodeURIComponent(query)}`;
        } else {
            url = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
        }
        window.open(url, '_blank');
    };

    return (
        <div className="min-h-screen bg-background text-foreground p-6 lg:p-10">
            {/* Header */}
            <div className="max-w-4xl mx-auto mb-8">
                <Button
                    variant="ghost"
                    className="mb-4 pl-0 hover:bg-transparent hover:text-primary"
                    onClick={() => navigate(-1)}
                >
                    <ArrowLeft className="mr-2 h-4 w-4" /> Back to Analysis
                </Button>

                <div className="flex flex-col gap-2">
                    <h1 className="text-3xl font-bold tracking-tight">Research Evidence</h1>
                    <p className="text-muted-foreground">
                        Direct access to external research and clinical studies for <span className="text-primary font-semibold">{drug}</span> + <span className="text-primary font-semibold">{diseaseName}</span>.
                    </p>
                </div>
            </div>

            {/* Content Grid */}
            <div className="max-w-4xl mx-auto grid gap-4">
                {queries.map((item, idx) => (
                    <Card key={idx} className="bg-card border-border hover:border-sidebar-accent transition-colors shadow-sm">
                        <CardHeader className="pb-3">
                            <div className="flex items-start gap-4">
                                <div className="p-2 bg-muted rounded-lg border border-border">
                                    {item.icon}
                                </div>
                                <div className="flex-1">
                                    <CardTitle className="text-lg text-foreground">{item.title}</CardTitle>
                                    <CardDescription className="text-muted-foreground mt-1">{item.desc}</CardDescription>
                                </div>
                            </div>
                        </CardHeader>
                        <CardContent>
                            <div className="flex flex-wrap gap-2 pt-2">
                                <Button
                                    size="sm"
                                    variant="secondary"
                                    className="bg-secondary text-secondary-foreground hover:bg-secondary/80"
                                    onClick={() => openSearch(item.query, 'google')}
                                >
                                    <Search className="mr-2 h-3 w-3" /> Google Search
                                </Button>
                                <Button
                                    size="sm"
                                    variant="secondary"
                                    className="bg-secondary text-secondary-foreground hover:bg-secondary/80"
                                    onClick={() => openSearch(item.query, 'scholar')}
                                >
                                    <BookOpen className="mr-2 h-3 w-3" /> Google Scholar
                                </Button>
                                <Button
                                    size="sm"
                                    variant="secondary"
                                    className="bg-secondary text-secondary-foreground hover:bg-secondary/80"
                                    onClick={() => openSearch(item.query, 'pubmed')}
                                >
                                    <FlaskConical className="mr-2 h-3 w-3" /> PubMed
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>
            <div className="max-w-4xl mx-auto mt-8 text-center text-sm text-muted-foreground">
                <p>Click on the buttons above to open research results in a new tab.</p>
            </div>
        </div>
    );
};

export default EvidencePage;
