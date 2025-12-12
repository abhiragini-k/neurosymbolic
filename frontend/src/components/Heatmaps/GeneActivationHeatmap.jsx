import { ArrowUp, ArrowDown, HelpCircle, AlertCircle, CheckCircle, XCircle } from "lucide-react";

const data = [
    { gene: "AMPK", drug: 1, disease: 1, match: 0.95 },
    { gene: "mTOR", drug: -1, disease: 1, match: 0.20 },
    { gene: "FOXO1", drug: 1, disease: -1, match: 0.10 },
];

const getMatchColor = (score) => {
    if (score >= 0.7) return "bg-green-100 text-green-700 border-green-200"; // Good
    if (score < 0.3) return "bg-red-100 text-red-700 border-red-200"; // Conflict
    return "bg-yellow-100 text-yellow-700 border-yellow-200"; // Partial
};

const getTrendIcon = (val) => {
    if (val === 1) return <div className="flex items-center text-green-600 font-medium"><ArrowUp className="w-4 h-4 mr-1" /> Up</div>;
    if (val === -1) return <div className="flex items-center text-red-600 font-medium"><ArrowDown className="w-4 h-4 mr-1" /> Down</div>;
    return <span className="text-gray-500">Neutral</span>;
};

const GeneActivationHeatmap = () => {
    return (
        <div className="rounded-xl border bg-card text-card-foreground shadow-sm h-full flex flex-col">
            <div className="p-6 pb-4">
                <h3 className="font-semibold leading-none tracking-tight">Gene Activation Match Heatmap</h3>
            </div>
            <div className="p-6 pt-0 flex-1">
                <div className="w-full">
                    {/* Header */}
                    <div className="grid grid-cols-4 gap-4 mb-4 text-xs font-medium text-muted-foreground uppercase tracking-wider text-center">
                        <div className="text-left font-bold">Gene</div>
                        <div>Drug Effect</div>
                        <div>Disease Sig.</div>
                        <div>Match Score</div>
                    </div>

                    {/* Rows */}
                    <div className="space-y-3">
                        {data.map((item, index) => (
                            <div key={index} className="grid grid-cols-4 gap-4 items-center text-sm p-3 rounded-lg border bg-muted/20 hover:bg-muted/40 transition-colors">
                                <div className="font-semibold text-left">{item.gene}</div>
                                <div className="flex justify-center">{getTrendIcon(item.drug)}</div>
                                <div className="flex justify-center">{getTrendIcon(item.disease)}</div>
                                <div className="flex justify-center">
                                    <div className={`px-3 py-1 rounded-full text-xs font-bold border ${getMatchColor(item.match)} shadow-sm min-w-[60px] text-center`}>
                                        {item.match.toFixed(2)}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Legend */}
                <div className="mt-6 flex flex-wrap justify-center gap-4 text-xs text-muted-foreground pt-4 border-t">
                    <div className="flex items-center gap-1.5">
                        <div className="w-2.5 h-2.5 rounded-full bg-green-500"></div> Good Match (≥ 0.7)
                    </div>
                    <div className="flex items-center gap-1.5">
                        <div className="w-2.5 h-2.5 rounded-full bg-yellow-500"></div> Partial (0.3-0.7)
                    </div>
                    <div className="flex items-center gap-1.5">
                        <div className="w-2.5 h-2.5 rounded-full bg-red-500"></div> Conflict (&lt; 0.3)
                    </div>
                </div>
            </div>
        </div>
    );
};

export default GeneActivationHeatmap;
