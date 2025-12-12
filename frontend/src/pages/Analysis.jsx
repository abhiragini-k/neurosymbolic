import { useState } from "react";
import Header from "@/components/Header";
import PredictionSummary from "@/components/PredictionSummary";
import ExplanationPanel from "@/components/ExplanationPanel";
import GraphViewer from "@/components/GraphViewer";
import PathwayInfluenceHeatmap from "@/components/Heatmaps/PathwayInfluenceHeatmap";
import GeneActivationHeatmap from "@/components/Heatmaps/GeneActivationHeatmap";

const Analysis = () => {
    const [drug, setDrug] = useState("");
    const [disease, setDisease] = useState("");
    const [weight, setWeight] = useState(0.6);
    const [score, setScore] = useState(null);
    const [neuralScore, setNeuralScore] = useState(0);
    const [symbolicScore, setSymbolicScore] = useState(0);
    const [reasoningChains, setReasoningChains] = useState([]);

    const handleAnalyze = () => {
        // Simulate analysis with dummy data
        const baseScore = 0.3 + Math.random() * 0.6;
        setScore(baseScore);

        const neural = weight * baseScore + (Math.random() * 0.1);
        const symbolic = (1 - weight) * baseScore + (Math.random() * 0.1);

        setNeuralScore(Math.min(neural, 1));
        setSymbolicScore(Math.min(symbolic, 1));

        // Generate dummy reasoning chains
        const chains = [
            {
                pathway: [drug || "Drug", "Protein AMPK", "Gene GLUT4", disease || "Disease"],
                confidence: 0.85 + Math.random() * 0.1,
            },
            {
                pathway: [drug || "Drug", "Protein mTOR", "Gene IRS1", "Pathway PI3K", disease || "Disease"],
                confidence: 0.75 + Math.random() * 0.1,
            },
            {
                pathway: [drug || "Drug", "Protein SIRT1", "Gene FOXO1", disease || "Disease"],
                confidence: 0.65 + Math.random() * 0.1,
            },
        ];

        setReasoningChains(chains);
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
                    {/* Left Column - Prediction */}
                    <div className="lg:col-span-3">
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

                    {/* Middle Column - Knowledge Graph */}
                    <div className="lg:col-span-5">
                        {score !== null ? (
                            <GraphViewer />
                        ) : (
                            <div className="h-full flex items-center justify-center rounded-xl border border-dashed border-muted-foreground/30 bg-muted/30 text-muted-foreground text-center p-6">
                                Click Analyze to generate and display the knowledge graph
                            </div>
                        )}
                    </div>

                    {/* Right Column - Explanation */}
                    <div className="lg:col-span-4">
                        {score !== null ? (
                            <ExplanationPanel
                                neuralScore={neuralScore}
                                symbolicScore={symbolicScore}
                                reasoningChains={reasoningChains}
                            />
                        ) : (
                            <div className="flex items-center justify-center h-full">
                                <p className="text-muted-foreground text-center">
                                    Select a drug and disease, then click Analyze to see results
                                </p>
                            </div>
                        )}
                    </div>

                    {/* Heatmaps Row */}
                    <div className="lg:col-span-9 lg:col-start-4">
                        {score !== null && (
                            <div className="grid gap-6 md:grid-cols-2">
                                <PathwayInfluenceHeatmap />
                                <GeneActivationHeatmap />
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Analysis;
