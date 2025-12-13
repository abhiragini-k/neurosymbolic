import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Header from "@/components/Header";
import PredictionSummary from "@/components/PredictionSummary";
import PredictionResults from "@/components/PredictionResults";
import api from "@/lib/api";
import { useToast } from "@/components/ui/use-toast";

const Analysis = () => {
    const [drug, setDrug] = useState("");
    const [disease, setDisease] = useState(""); // Kept for compatibility with PredictionSummary
    const [weight, setWeight] = useState(0.6);
    const [score, setScore] = useState(null); // Kept for compatibility
    const [predictions, setPredictions] = useState(null);
    const [loading, setLoading] = useState(false);

    const navigate = useNavigate();
    const { toast } = useToast();

    const handleAnalyze = async () => {
        if (!drug) {
            toast({
                title: "Error",
                description: "Please select or enter a drug name.",
                variant: "destructive",
            });
            return;
        }

        setLoading(true);
        try {
            const result = await api.predictDrug(drug);
            // Enrich predictions with compound_id for downstream use
            const enrichedPredictions = result.predicted.map(p => ({
                ...p,
                compound_id: result.drug_id
            }));
            setPredictions(enrichedPredictions);
            setScore(0.85); // Dummy score to show "Analysis Complete" state in summary if needed
        } catch (error) {
            console.error("Prediction failed:", error);
            toast({
                title: "Error",
                description: "Failed to fetch predictions. Please try again.",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    const handlePredictionSelect = (prediction) => {
        navigate('/analysis/detail', {
            state: {
                drug: drug,
                disease: prediction
            }
        });
    };

    return (
        <div className="min-h-screen bg-background">
            <Header />

            <div className="container py-8">
                <div className="mb-8">
                    <h1 className="text-4xl font-bold mb-2">Drug Repurposing Analysis</h1>
                    <p className="text-muted-foreground">
                        Analyze drug-disease pairs using neurosymbolic AI
                    </p>
                </div>

                <div className="grid gap-6 lg:grid-cols-12">
                    {/* Left Column - Prediction Inputs */}
                    <div className="lg:col-span-4">
                        <PredictionSummary
                            drug={drug}
                            disease={disease}
                            weight={weight}
                            score={score}
                            onDrugChange={setDrug}
                            onDiseaseChange={setDisease}
                            onWeightChange={(val) => setWeight(val[0])}
                            onAnalyze={handleAnalyze}
                        />
                    </div>

                    {/* Right Column - Results List */}
                    <div className="lg:col-span-8">
                        {loading ? (
                            <div className="h-full flex items-center justify-center rounded-xl border border-dashed border-muted-foreground/30 bg-muted/30 text-muted-foreground text-center p-6 min-h-[400px]">
                                <div className="flex flex-col items-center gap-2">
                                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                                    <p>Running R-GCN Model...</p>
                                </div>
                            </div>
                        ) : predictions ? (
                            <PredictionResults
                                predictions={predictions}
                                onSelect={handlePredictionSelect}
                            />
                        ) : (
                            <div className="h-full flex items-center justify-center rounded-xl border border-dashed border-muted-foreground/30 bg-muted/30 text-muted-foreground text-center p-6 min-h-[400px]">
                                <div className="max-w-md">
                                    <h3 className="text-lg font-semibold mb-2">Ready to Analyze</h3>
                                    <p>Select a drug from the left panel and click "Analyze" to see top candidate diseases for repurposing.</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Analysis;
