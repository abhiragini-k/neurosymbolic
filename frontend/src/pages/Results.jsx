import Header from "@/components/Header";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { TrendingUp } from "lucide-react";

const Results = () => {
    const predictions = [
        {
            rank: 1,
            drug: "Metformin",
            disease: "Alzheimer's Disease",
            score: 0.89,
            confidence: "High",
            mechanism: "AMPK activation → neuroprotection",
        },
        {
            rank: 2,
            drug: "Aspirin",
            disease: "Colorectal Cancer",
            score: 0.84,
            confidence: "High",
            mechanism: "COX-2 inhibition → reduced inflammation",
        },
        {
            rank: 3,
            drug: "Atorvastatin",
            disease: "Parkinson's Disease",
            score: 0.79,
            confidence: "Medium",
            mechanism: "Cholesterol reduction → neuroprotection",
        },
        {
            rank: 4,
            drug: "Ibuprofen",
            disease: "Alzheimer's Disease",
            score: 0.76,
            confidence: "Medium",
            mechanism: "Anti-inflammatory → amyloid reduction",
        },
        {
            rank: 5,
            drug: "Metformin",
            disease: "Cancer",
            score: 0.72,
            confidence: "Medium",
            mechanism: "mTOR inhibition → cell cycle arrest",
        },
        {
            rank: 6,
            drug: "Aspirin",
            disease: "Cardiovascular Disease",
            score: 0.68,
            confidence: "Medium",
            mechanism: "Platelet inhibition → thrombosis prevention",
        },
        {
            rank: 7,
            drug: "Sildenafil",
            disease: "Pulmonary Hypertension",
            score: 0.65,
            confidence: "Medium",
            mechanism: "PDE5 inhibition → vasodilation",
        },
        {
            rank: 8,
            drug: "Thalidomide",
            disease: "Multiple Myeloma",
            score: 0.61,
            confidence: "Low",
            mechanism: "Immunomodulation → tumor suppression",
        },
        {
            rank: 9,
            drug: "Rapamycin",
            disease: "Aging",
            score: 0.58,
            confidence: "Low",
            mechanism: "mTOR inhibition → longevity pathways",
        },
        {
            rank: 10,
            drug: "Valproic Acid",
            disease: "Cancer",
            score: 0.55,
            confidence: "Low",
            mechanism: "HDAC inhibition → epigenetic regulation",
        },
    ];

    const getConfidenceBadge = (confidence) => {
        if (confidence === "High") return <Badge className="bg-protein text-white">High</Badge>;
        if (confidence === "Medium") return <Badge className="bg-accent text-white">Medium</Badge>;
        return <Badge variant="secondary">Low</Badge>;
    };

    return (
        <div className="min-h-screen bg-background">
            <Header />

            <div className="container py-12">
                <div className="mb-8">
                    <h1 className="text-4xl font-bold mb-4">Top Predictions</h1>
                    <p className="text-xl text-muted-foreground">
                        Novel drug repurposing candidates ranked by confidence score
                    </p>
                </div>

                <Card className="shadow-card overflow-hidden">
                    <div className="overflow-x-auto">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead className="w-16">Rank</TableHead>
                                    <TableHead>Drug</TableHead>
                                    <TableHead>Disease</TableHead>
                                    <TableHead className="text-center">Score</TableHead>
                                    <TableHead className="text-center">Confidence</TableHead>
                                    <TableHead>Mechanism</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {predictions.map((pred) => (
                                    <TableRow key={pred.rank} className="hover:bg-muted/50 transition-colors">
                                        <TableCell className="font-bold">
                                            <div className="flex items-center gap-2">
                                                {pred.rank <= 3 && <TrendingUp className="h-4 w-4 text-primary" />}
                                                {pred.rank}
                                            </div>
                                        </TableCell>
                                        <TableCell className="font-medium">{pred.drug}</TableCell>
                                        <TableCell>{pred.disease}</TableCell>
                                        <TableCell className="text-center">
                                            <span className="font-bold text-primary">{pred.score.toFixed(2)}</span>
                                        </TableCell>
                                        <TableCell className="text-center">{getConfidenceBadge(pred.confidence)}</TableCell>
                                        <TableCell className="text-sm text-muted-foreground">{pred.mechanism}</TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </div>
                </Card>

                <Card className="mt-8 p-6 shadow-card bg-secondary/30">
                    <h2 className="text-xl font-semibold mb-3">Interpretation Guide</h2>
                    <div className="space-y-2 text-sm text-muted-foreground">
                        <p>
                            <strong>Score:</strong> Combined confidence from neural and symbolic components (0-1 scale)
                        </p>
                        <p>
                            <strong>High confidence (≥0.70):</strong> Strong evidence from both neural patterns and logical reasoning
                        </p>
                        <p>
                            <strong>Medium confidence (0.40-0.69):</strong> Moderate support, requires further validation
                        </p>
                        <p>
                            <strong>Low confidence (&lt;0.40):</strong> Preliminary finding, needs substantial additional evidence
                        </p>
                    </div>
                </Card>
            </div>
        </div>
    );
};

export default Results;
