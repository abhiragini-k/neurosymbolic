import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, Cell, CartesianGrid } from "recharts";

const data = [
    { pathway: "AMPK Pathway", influence: 0.92 },
    { pathway: "mTOR Pathway", influence: 0.73 },
    { pathway: "PI3K Pathway", influence: 0.60 },
    { pathway: "GLUT4 Regulation", influence: 0.35 },
    { pathway: "Inflammation Pathway", influence: 0.20 },
];

const getColor = (influence) => {
    if (influence >= 0.8) return "#8B0000"; // Dark Red
    if (influence >= 0.6) return "#FFA500"; // Orange
    if (influence >= 0.4) return "#FFD700"; // Yellow (Gold for better visibility)
    if (influence >= 0.2) return "#87CEEB"; // Light Blue
    return "#0000FF"; // Blue
};

const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        return (
            <div className="bg-background border rounded-lg p-3 shadow-lg">
                <p className="font-semibold">{label}</p>
                <p className="text-sm">Influence: {payload[0].value}</p>
            </div>
        );
    }
    return null;
};

const PathwayInfluenceHeatmap = ({ data }) => {
    // Use dynamic data or fallback to empty array
    // Expecting data to have a 'pathway_influence' property
    const heatmapData = data?.pathway_influence || [];

    return (
        <div className="rounded-xl border bg-card text-card-foreground shadow-sm h-full">
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
