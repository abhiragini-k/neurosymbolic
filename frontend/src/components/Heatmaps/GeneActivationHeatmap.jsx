import { useState, useEffect } from 'react';
import { ArrowUp, ArrowDown, HelpCircle, AlertCircle, CheckCircle, XCircle } from "lucide-react";

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

const GeneActivationHeatmap = ({ drugId, diseaseId }) => {
    const [rows, setRows] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!drugId || !diseaseId) return;

        setLoading(true);
        setError(null);
        console.log(`[GeneMatch] Fetching for ${drugId} -> ${diseaseId}`);
        const url = `http://localhost:8000/explainability/gene-match?drug_id=${encodeURIComponent(drugId)}&disease_id=${encodeURIComponent(diseaseId)}`;

        fetch(url)
            .then(res => {
                if (!res.ok) throw new Error("Network response was not ok");
                return res.json();
            })
            .then(json => {
                console.log("[GeneMatch] Data:", json);
                if (json && json.gene_matches) {
                    setRows(json.gene_matches);
                } else {
                    setRows([]);
                }
            })
            .catch(err => {
                console.error("[GeneMatch] Error:", err);
                setError(err.message);
            })
            .finally(() => setLoading(false));
    }, [drugId, diseaseId]);

    if (!drugId || !diseaseId) return <div className="p-4 border rounded">Select Drug & Disease</div>;
    if (loading) return <div className="p-4 border rounded bg-gray-50 animate-pulse">Loading Gene Matches...</div>;
    if (error) return <div className="p-4 border rounded text-red-500">Error: {error}</div>;
    if (rows.length === 0) return <div className="p-4 border rounded text-yellow-600">No gene data found.</div>;

    return (
        <div className="rounded-xl border bg-card text-card-foreground shadow-sm h-full flex flex-col">
            <div className="p-6 pb-4">
                <h3 className="font-semibold leading-none tracking-tight">Gene Activation Match Heatmap</h3>
            </div>
            <div className="p-6 pt-0 flex-1 overflow-auto max-h-[400px]">
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
                        {rows.map((item, index) => (
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
                <div className="mt-6 flex flex-wrap justify-center gap-4 text-xs text-muted-foreground pt-4 border-t sticky bottom-0 bg-background">
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

