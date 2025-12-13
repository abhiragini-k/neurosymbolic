import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ArrowLeft, ExternalLink, FileText, Loader2, AlertCircle } from "lucide-react";
import axios from 'axios';

const EvidencePage = () => {
    const { diseaseId } = useParams();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [data, setData] = useState(null);

    useEffect(() => {
        const fetchEvidence = async () => {
            try {
                setLoading(true);
                // Using the endpoint identified: /predict/diseases/{disease_id}/candidates
                const response = await axios.get(`http://127.0.0.1:8000/predict/diseases/${diseaseId}/candidates`);
                setData(response.data);
            } catch (err) {
                console.error("Failed to fetch evidence:", err);
                setError("Failed to load evidence data. Please try again later.");
            } finally {
                setLoading(false);
            }
        };

        if (diseaseId) {
            fetchEvidence();
        }
    }, [diseaseId]);

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen bg-slate-950 text-slate-50">
                <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
                <p className="text-muted-foreground">Loading evidence data...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen bg-slate-950 text-slate-50 p-6">
                <AlertCircle className="h-12 w-12 text-destructive mb-4" />
                <h2 className="text-xl font-bold mb-2">Error</h2>
                <p className="text-muted-foreground mb-6">{error}</p>
                <Button onClick={() => navigate(-1)} variant="outline">
                    <ArrowLeft className="mr-2 h-4 w-4" /> Go Back
                </Button>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-950 text-slate-50 p-6 lg:p-10">
            {/* Header */}
            <div className="max-w-7xl mx-auto mb-8">
                <Button
                    variant="ghost"
                    className="mb-4 pl-0 hover:bg-transparent hover:text-primary"
                    onClick={() => navigate(-1)}
                >
                    <ArrowLeft className="mr-2 h-4 w-4" /> Back to Analysis
                </Button>

                <div className="flex flex-col gap-2">
                    <h1 className="text-3xl font-bold tracking-tight">Evidence Analysis</h1>
                    <p className="text-muted-foreground">
                        Top drug candidates for <span className="text-primary font-semibold">{data?.disease_name}</span> based on AI predictions and literature evidence.
                    </p>
                </div>
            </div>

            {/* Content Grid */}
            <div className="max-w-7xl mx-auto grid gap-6 lg:grid-cols-2 xl:grid-cols-3">
                {data?.candidates?.map((candidate) => (
                    <Card key={candidate.drug_id} className="bg-slate-900 border-slate-800 flex flex-col h-full">
                        <CardHeader className="pb-3">
                            <div className="flex justify-between items-start">
                                <div>
                                    <CardTitle className="text-xl text-primary">{candidate.drug_name}</CardTitle>
                                    <CardDescription className="mt-1">Rank #{candidate.rank}</CardDescription>
                                </div>
                                <Badge variant="secondary" className="bg-slate-800 text-slate-300">
                                    Score: {candidate.score.toFixed(4)}
                                </Badge>
                            </div>
                        </CardHeader>

                        <CardContent className="flex-1 flex flex-col gap-4">
                            {/* AI Summary */}
                            <div className="bg-slate-950/50 p-3 rounded-md border border-slate-800">
                                <h4 className="text-sm font-semibold mb-2 flex items-center gap-2">
                                    <FileText className="h-3 w-3 text-blue-400" /> AI Summary
                                </h4>
                                <p className="text-sm text-slate-300 leading-relaxed">
                                    {candidate.summary?.overall_summary || "No summary available."}
                                </p>
                            </div>

                            {/* Key Points */}
                            {candidate.summary?.points && candidate.summary.points.length > 0 && (
                                <div className="space-y-2">
                                    <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Key Findings</h4>
                                    <ul className="text-sm space-y-1 list-disc list-inside text-slate-400">
                                        {candidate.summary.points.slice(0, 3).map((point, idx) => (
                                            <li key={idx} className="line-clamp-2">{point}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            <div className="mt-auto pt-4">
                                <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">References</h4>
                                <ScrollArea className="h-24 w-full rounded-md border border-slate-800 bg-slate-950 p-2">
                                    {candidate.papers && candidate.papers.length > 0 ? (
                                        <div className="space-y-2">
                                            {candidate.papers.map((paper, idx) => (
                                                <a
                                                    key={idx}
                                                    href={paper.url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="block text-xs text-blue-400 hover:text-blue-300 hover:underline truncate"
                                                >
                                                    <ExternalLink className="h-3 w-3 inline mr-1" />
                                                    {paper.title}
                                                </a>
                                            ))}
                                        </div>
                                    ) : (
                                        <p className="text-xs text-muted-foreground italic">No papers found.</p>
                                    )}
                                </ScrollArea>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    );
};

export default EvidencePage;
