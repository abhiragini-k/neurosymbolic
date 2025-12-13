import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Brain, Network, ArrowRight } from "lucide-react";

const ExplanationPanel = ({ neuralScore, symbolicScore, reasoningChains }) => {
    return (
        <div className="space-y-6">
            <h2 className="text-2xl font-bold">Explanation</h2>

            {/* Neural Explanation Removed */}

            {/* Symbolic Explanation */}
            <Card className="p-6 shadow-card">
                <div className="flex items-center gap-3 mb-4">
                    <div className="inline-flex rounded-lg bg-accent/10 p-2">
                        <Network className="h-5 w-5 text-accent" />
                    </div>
                    <div className="flex-1">
                        <h3 className="text-lg font-semibold">Symbolic Explanation</h3>
                        <div className="flex items-center gap-2 mt-1">
                            <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-accent transition-all duration-500"
                                    style={{ width: `${symbolicScore * 100}%` }}
                                />
                            </div>
                            <span className="text-sm font-medium">{(symbolicScore * 100).toFixed(1)}%</span>
                        </div>
                    </div>
                </div>

                <div className="space-y-4 mt-4">
                    <p className="text-sm font-medium text-foreground">Top Reasoning Chains:</p>
                    {reasoningChains.map((chain, idx) => (
                        <div key={idx} className="space-y-2 p-3 bg-muted/50 rounded-lg">
                            <div className="flex flex-wrap items-center gap-2">
                                {chain.pathway.map((node, nodeIdx) => (
                                    <div key={nodeIdx} className="flex items-center gap-2">
                                        <Badge
                                            variant="outline"
                                            className={
                                                nodeIdx === 0
                                                    ? "bg-drug/10 text-drug border-drug/20"
                                                    : nodeIdx === chain.pathway.length - 1
                                                        ? "bg-disease/10 text-disease border-disease/20"
                                                        : "bg-protein/10 text-protein border-protein/20"
                                            }
                                        >
                                            {node}
                                        </Badge>
                                        {nodeIdx < chain.pathway.length - 1 && (
                                            <ArrowRight className="h-3 w-3 text-muted-foreground" />
                                        )}
                                    </div>
                                ))}
                            </div>

                            {/* Display Pathways/Edges if available */}
                            {chain.edges && chain.edges.length > 0 && (
                                <div className="pl-2 border-l-2 border-primary/20 mt-2">
                                    <p className="text-xs font-semibold text-muted-foreground mb-1">Pathways involved:</p>
                                    <div className="flex flex-wrap gap-1">
                                        {chain.edges.map((edge, edgeIdx) => (
                                            <Badge key={edgeIdx} variant="secondary" className="text-[10px] h-5">
                                                {edge}
                                            </Badge>
                                        ))}
                                    </div>
                                </div>
                            )}

                            <div className="flex items-center justify-between mt-2">
                                <span className="text-xs text-muted-foreground">Pathway {idx + 1}</span>
                                <Badge variant="secondary" className="text-xs">
                                    {(chain.confidence * 100).toFixed(0)}% confidence
                                </Badge>
                            </div>
                        </div>
                    ))}
                </div>
            </Card>
        </div>
    );
};

export default ExplanationPanel;
