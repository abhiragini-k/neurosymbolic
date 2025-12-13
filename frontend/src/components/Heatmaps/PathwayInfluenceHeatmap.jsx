import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, Cell, CartesianGrid } from "recharts";

const getColor = (influence) => {
    if (influence >= 0.8) return "#8B0000"; // Dark Red
    if (influence >= 0.6) return "#FFA500"; // Orange
    if (influence >= 0.4) return "#FFD700"; // Yellow
    if (influence >= 0.2) return "#87CEEB"; // Light Blue
    return "#0000FF"; // Blue
};

const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        return (
            <div className="bg-white border rounded p-2 shadow-lg text-black">
                <p className="font-bold">{label}</p>
                <p>Influence: {payload[0].value}</p>
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

        const url = `http://localhost:8000/explainability/pathway?drug_id=${encodeURIComponent(drugId)}&disease_id=${encodeURIComponent(diseaseId)}`;
        console.log("[Heatmap] URL:", url);

        fetch(url)
            .then(res => {
                if (!res.ok) throw new Error("Network response was not ok");
                return res.json();
            })
            .then(json => {
                console.log("[Heatmap] Data:", json);
                if (json && json.pathway_influence) {
                    setData(json.pathway_influence);
                } else {
                    setData([]);
                }
            })
            .catch(err => {
                console.error("[Heatmap] Error:", err);
                setError(err.message);
            })
            .finally(() => setLoading(false));
    }, [drugId, diseaseId]);

    // Render States
    if (!drugId || !diseaseId) return <div className="p-4 border rounded">Select Drug & Disease</div>;
    if (loading) return <div className="p-4 border rounded bg-gray-50 animate-pulse">Loading Influence Data...</div>;
    if (error) return <div className="p-4 border rounded text-red-500">Error: {error}</div>;
    if (data.length === 0) return <div className="p-4 border rounded text-yellow-600">No pathway data found.</div>;

    return (
        <div className="rounded-xl border bg-card text-card-foreground shadow-sm h-full flex flex-col">
            <div className="p-6 pb-2">
                <h3 className="font-semibold leading-none tracking-tight">Pathway Influence Heatmap</h3>
            </div>
            <div className="p-4 flex-1 min-h-[300px]">
                {/* 
                    Using 99% width/height to avoid resize loop.
                    Removed sophisticated layout props to ensure basic rendering first.
                */}
                <ResponsiveContainer width="99%" height={300}>
                    <BarChart
                        layout="vertical"
                        data={data}
                        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                        <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                        <XAxis type="number" domain={[0, 1.1]} />
                        <YAxis
                            type="category"
                            dataKey="pathway"
                            width={150}
                            interval={0}
                            tick={{ fontSize: 11 }}
                        />
                        <Tooltip content={<CustomTooltip />} />
                        <Bar dataKey="influence" barSize={20}>
                            {data.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={getColor(entry.influence)} />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default PathwayInfluenceHeatmap;

