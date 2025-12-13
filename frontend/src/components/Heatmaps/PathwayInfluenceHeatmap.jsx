import api from "@/lib/api";

import { useState, useEffect } from 'react';
import { ResponsiveContainer, BarChart, CartesianGrid, XAxis, YAxis, Tooltip, Legend, Bar, Cell } from 'recharts';

const getColor = (influence) => {
    if (influence >= 0.8) return "#8B0000";
    if (influence >= 0.6) return "#FFA500";
    if (influence >= 0.4) return "#FFD700";
    if (influence >= 0.2) return "#87CEEB";
    return "#0000FF";
};

const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        return (
            <div className="bg-white p-2 border border-gray-200 shadow-sm rounded text-xs">
                <p className="font-semibold">{label}</p>
                <p>Influence: {payload[0].value.toFixed(3)}</p>
            </div>
        );
    }
    return null;
};

const PathwayInfluenceHeatmap = ({ drugId, diseaseId }) => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!drugId || !diseaseId) return;

        console.log(`[Heatmap] Fetching for ${drugId} -> ${diseaseId}`);
        setLoading(true);
        setError(null);

        const fetchInfluence = async () => {
            try {
                const response = await api.get(`/api/explainability/pathway`, {
                    params: { drug_id: drugId, disease_id: diseaseId }
                });
                console.log("[Heatmap] Data:", response.data);
                if (response.data && Array.isArray(response.data.pathway_influence)) {
                    // Filter out invalid entries to prevent Recharts crash
                    const validData = response.data.pathway_influence.filter(item => item && item.pathway && typeof item.influence === 'number');
                    setData(validData);
                } else {
                    setData([]);
                }
            } catch (err) {
                console.error("[Heatmap] Error:", err);
                setError(err.message || "Failed to fetch data");
            } finally {
                setLoading(false);
            }
        };

        fetchInfluence();
    }, [drugId, diseaseId]);

    // Render States
    if (!drugId || !diseaseId) return <div className="p-4 border rounded">Select Drug & Disease</div>;
    if (loading) return <div className="p-4 border rounded bg-gray-50 animate-pulse">Loading Influence Data...</div>;
    if (error) return <div className="p-4 border rounded text-red-500">Error: {error}</div>;
    if (data.length === 0) return <div className="p-4 border rounded text-yellow-600">No pathway data found.</div>;

    const heatmapData = data;

    return (
        <div className="rounded-xl border bg-card text-card-foreground shadow-sm h-full flex flex-col">
            <div className="p-6 pb-2">
                <h3 className="font-semibold leading-none tracking-tight">Pathway Influence Heatmap</h3>
            </div>
            <div className="p-6 pt-0 h-[300px] w-full">
                {heatmapData.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                            layout="vertical"
                            data={heatmapData}
                            margin={{ top: 20, right: 30, left: 40, bottom: 5 }}
                        >
                            <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                            <XAxis type="number" domain={[0, 1]} hide />
                            <YAxis
                                type="category"
                                dataKey="pathway"
                                width={140}
                                tick={{ fontSize: 12 }}
                            // stroke="#888"
                            />
                            <Tooltip content={<CustomTooltip />} cursor={{ fill: "transparent" }} />
                            <Legend
                                content={() => (
                                    <div className="flex flex-wrap justify-center gap-2 mt-2 text-xs">
                                        <div className="flex items-center gap-1"><span className="w-3 h-3 block" style={{ background: "#8B0000" }}></span>≥ 0.8</div>
                                        <div className="flex items-center gap-1"><span className="w-3 h-3 block" style={{ background: "#FFA500" }}></span>0.6-0.8</div>
                                        <div className="flex items-center gap-1"><span className="w-3 h-3 block" style={{ background: "#FFD700" }}></span>0.4-0.6</div>
                                        <div className="flex items-center gap-1"><span className="w-3 h-3 block" style={{ background: "#87CEEB" }}></span>0.2-0.4</div>
                                        <div className="flex items-center gap-1"><span className="w-3 h-3 block" style={{ background: "#0000FF" }}></span>&lt; 0.2</div>
                                    </div>
                                )}
                            />
                            <Bar dataKey="influence" radius={[0, 4, 4, 0]} barSize={32}>
                                {heatmapData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={getColor(entry.influence)} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                ) : (
                    <div className="flex items-center justify-center h-full text-muted-foreground">
                        No pathway influence data available
                    </div>
                )}
            </div>
        </div>
    );
};

export default PathwayInfluenceHeatmap;
