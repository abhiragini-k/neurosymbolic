import { Card } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, Loader2 } from "lucide-react";
import { useState } from "react";
import GraphViewer from "./GraphViewer";
import ConfidenceBreakdown from "./ConfidenceBreakdown";
import GeneActivationHeatmap from "./Heatmaps/GeneActivationHeatmap";
import PathwayInfluenceHeatmap from "./Heatmaps/PathwayInfluenceHeatmap";
import api from "@/lib/api";

const PredictionResults = ({ predictions, onSelect }) => {
    const [selectedDisease, setSelectedDisease] = useState(null);
    const [analysisData, setAnalysisData] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleSelect = (pred) => {
        onSelect(pred);
    };

    const getConfidenceBadge = (score) => {
        if (score >= 0.7) return <Badge className="bg-protein text-white">High</Badge>;
        if (score >= 0.4) return <Badge className="bg-accent text-white">Medium</Badge>;
        return <Badge variant="secondary">Low</Badge>;
    };

    return (
        <div className="space-y-6">
            <Card className="shadow-card overflow-hidden">
                <div className="p-6 border-b">
                    <h2 className="text-2xl font-bold">Top Predicted Diseases</h2>
                    <p className="text-muted-foreground">Select a disease to view detailed analysis</p>
                </div>
                <div className="overflow-x-auto">
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead className="w-16">Rank</TableHead>
                                <TableHead>Disease</TableHead>
                                <TableHead className="text-center">Score</TableHead>
                                <TableHead className="text-center">Confidence</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {predictions.map((pred, index) => (
                                <TableRow
                                    key={pred.disease_id}
                                    className={`cursor-pointer transition-colors ${selectedDisease?.disease_id === pred.disease_id ? "bg-muted" : "hover:bg-muted/50"}`}
                                    onClick={() => handleSelect(pred)}
                                >
                                    <TableCell className="font-bold">
                                        <div className="flex items-center gap-2">
                                            {index < 3 && <TrendingUp className="h-4 w-4 text-primary" />}
                                            {index + 1}
                                        </div>
                                    </TableCell>
                                    <TableCell className="font-medium">{pred.disease_name}</TableCell>
                                    <TableCell className="text-center">
                                        <span className="font-bold text-primary">{pred.score}</span>
                                    </TableCell>
                                    <TableCell className="text-center">{getConfidenceBadge(pred.score)}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </div>
            </Card>

            {selectedDisease && (
                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    <div className="flex items-center justify-between">
                        <h2 className="text-2xl font-bold">Analysis for {selectedDisease.disease_name}</h2>
                        {loading && <Loader2 className="h-6 w-6 animate-spin text-primary" />}
                    </div>

                    {analysisData && !loading && (
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                            <div className="lg:col-span-2 space-y-6">
                                <GraphViewer data={analysisData} />
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <GeneActivationHeatmap data={analysisData} />
                                    <PathwayInfluenceHeatmap data={analysisData} />
                                </div>
                            </div>
                            <div className="space-y-6">
                                <ConfidenceBreakdown score={selectedDisease.score} data={analysisData} />

                                {/* Symbolic Rules Display */}
                                <Card className="p-6 shadow-sm border-l-4 border-l-primary">
                                    <h3 className="font-semibold mb-3">Symbolic Rules</h3>
                                    <div className="space-y-2 text-sm text-muted-foreground">
                                        {analysisData.symbolic_rules ? (
                                            analysisData.symbolic_rules.map((rule, idx) => (
                                                <div key={idx} className="p-2 bg-muted/50 rounded">
                                                    {rule}
                                                </div>
                                            ))
                                        ) : (
                                            <p>No symbolic rules generated.</p>
                                        )}
                                    </div>
                                </Card>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default PredictionResults;
