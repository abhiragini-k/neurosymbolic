import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import Header from "@/components/Header";
import ExplanationPanel from "@/components/ExplanationPanel";
import GraphViewer from "@/components/GraphViewer";
import PathwayInfluenceHeatmap from "@/components/Heatmaps/PathwayInfluenceHeatmap";
import GeneActivationHeatmap from "@/components/Heatmaps/GeneActivationHeatmap";
import ConfidenceBreakdown from "@/components/ConfidenceBreakdown";
import api from "@/lib/api";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";

const AnalysisDetail = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { drug, disease } = location.state || {};

    const [loading, setLoading] = useState(true);
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!drug || !disease) {
            navigate('/analysis');
            return;
        }

        const fetchData = async () => {
            try {
                setLoading(true);
                // Use the GET endpoint we created: /analysis/{drug_id}/{disease_id}
                // disease object comes from location.state and should have compound_id and disease_id
                // Pass names explicitly to ensure backend uses the correct text for Polo Agent
                // Fallback to disease.compound_name if drug state is missing (e.g. direct nav or reload)
                const drugNameParam = encodeURIComponent(drug || disease.compound_name || "");
                const diseaseNameParam = encodeURIComponent(disease.disease_name || "");
                const response = await api.get(`/api/analysis/${disease.compound_id}/${disease.disease_id}?drug_name=${drugNameParam}&disease_name=${diseaseNameParam}`);
                setData(response.data);
            } catch (err) {
                console.error("Analysis failed:", err);
                setError("Failed to load analysis data.");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [drug, disease, navigate]);

    if (loading) {
        return (
            <div className="min-h-screen bg-background">
                <Header />
                <div className="container py-8 flex items-center justify-center h-[80vh]">
                    <div className="text-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
                        <p className="text-lg text-muted-foreground">Generating Neurosymbolic Analysis...</p>
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-background">
                <Header />
                <div className="container py-8">
                    <Button variant="ghost" onClick={() => navigate('/analysis')} className="mb-4">
                        <ArrowLeft className="mr-2 h-4 w-4" /> Back to Predictions
                    </Button>
                    <div className="text-center text-destructive p-8 border rounded-lg bg-destructive/10">
                        {error}
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-background">
            <Header />

            <div className="container py-8">
                <div className="mb-8 flex items-center gap-4">
                    <Button variant="outline" size="icon" onClick={() => navigate('/analysis')}>
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                    <div>
                        <h1 className="text-3xl font-bold">Analysis: {drug} + {disease.disease_name}</h1>
                        <p className="text-muted-foreground">
                            Neurosymbolic explanation and pathway analysis
                        </p>
                    </div>
                </div>

                <div className="grid gap-6 lg:grid-cols-12">
                    {/* Knowledge Graph */}
                    <div className="lg:col-span-7">
                        <GraphViewer data={data?.graph} />
                    </div>

                    {/* Explanation */}
                    <div className="lg:col-span-5 space-y-6">
                        <ExplanationPanel
                            neuralScore={data?.neural_score || 0.8} // Fallback for demo
                            symbolicScore={data?.symbolic_score || 0.7}
                            reasoningChains={data?.reasoning_chains || []}
                        />

                        {/* Symbolic Rules Display */}
                        <div className="p-6 shadow-sm border rounded-xl bg-card text-card-foreground border-l-4 border-l-primary">
                            <h3 className="font-semibold mb-3">Symbolic Rules</h3>
                            <div className="space-y-2 text-sm text-muted-foreground">
                                {data?.symbolic_rules && data.symbolic_rules.length > 0 ? (
                                    data.symbolic_rules.map((rule, idx) => (
                                        <div key={idx} className="p-2 bg-muted/50 rounded border border-muted">
                                            {rule}
                                        </div>
                                    ))
                                ) : (
                                    <p className="italic">No specific symbolic rules generated for this pair.</p>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Heatmaps Row */}
                    <div className="lg:col-span-12">
                        <div className="flex flex-col lg:flex-row gap-6 pt-6">
                            <ConfidenceBreakdown score={disease.score} />
                            <div className="flex-1 grid gap-6 md:grid-cols-2">
                                <PathwayInfluenceHeatmap />
                                <GeneActivationHeatmap />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AnalysisDetail;
