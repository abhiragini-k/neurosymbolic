import Header from "@/components/Header";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const Documentation = () => {
    const steps = [
        {
            number: "01",
            title: "Data Collection",
            description: "Aggregate biomedical knowledge from multiple databases including DrugBank, DisGeNET, STRING, and PubMed. This creates a comprehensive knowledge graph of drug-protein-gene-disease relationships.",
            tags: ["Knowledge Graph", "Data Integration"],
        },
        {
            number: "02",
            title: "Graph Neural Network Training",
            description: "Train GNN models on the knowledge graph to learn embeddings that capture complex patterns in molecular structures and biological pathways. The model learns to predict drug-disease associations based on graph topology and node features.",
            tags: ["Deep Learning", "Graph Embeddings"],
        },
        {
            number: "03",
            title: "Symbolic Rule Extraction",
            description: "Extract logical rules and reasoning pathways from curated biomedical knowledge bases. These rules encode expert knowledge about drug mechanisms, disease pathways, and protein interactions.",
            tags: ["Logic Programming", "Knowledge Engineering"],
        },
        {
            number: "04",
            title: "Hybrid Inference",
            description: "Combine neural predictions with symbolic reasoning using a weighted aggregation strategy. The user-adjustable weight parameter controls the balance between pattern-based (neural) and rule-based (symbolic) reasoning.",
            tags: ["Neurosymbolic AI", "Ensemble Methods"],
        },
        {
            number: "05",
            title: "Explanation Generation",
            description: "Generate human-interpretable explanations by: (1) highlighting important subgraph patterns from the GNN, and (2) identifying the most confident logical reasoning chains from the symbolic component.",
            tags: ["Explainable AI", "Transparency"],
        },
        {
            number: "06",
            title: "Validation & Ranking",
            description: "Rank predictions by combined confidence scores. Top candidates are validated against literature and clinical trial databases. High-confidence predictions with strong explanations are prioritized for experimental validation.",
            tags: ["Validation", "Literature Mining"],
        },
    ];

    return (
        <div className="min-h-screen bg-background">
            <Header />

            <div className="container py-12 max-w-4xl">
                <h1 className="text-4xl font-bold mb-4">Documentation</h1>
                <p className="text-xl text-muted-foreground mb-12">
                    Step-by-step pipeline for neurosymbolic drug repurposing
                </p>

                <div className="space-y-6">
                    {steps.map((step, idx) => (
                        <Card key={idx} className="p-8 shadow-card hover:shadow-elevated transition-all">
                            <div className="flex gap-6">
                                <div className="flex-shrink-0">
                                    <div className="w-16 h-16 rounded-full bg-gradient-hero flex items-center justify-center text-white font-bold text-xl">
                                        {step.number}
                                    </div>
                                </div>

                                <div className="flex-1">
                                    <h2 className="text-2xl font-semibold mb-3">{step.title}</h2>
                                    <p className="text-muted-foreground leading-relaxed mb-4">
                                        {step.description}
                                    </p>
                                    <div className="flex flex-wrap gap-2">
                                        {step.tags.map((tag, tagIdx) => (
                                            <Badge key={tagIdx} variant="secondary">
                                                {tag}
                                            </Badge>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </Card>
                    ))}
                </div>

                <Card className="mt-12 p-8 shadow-card bg-gradient-card">
                    <h2 className="text-2xl font-semibold mb-4">Technical Stack</h2>
                    <div className="grid md:grid-cols-2 gap-6">
                        <div>
                            <h3 className="font-semibold mb-2 text-primary">Neural Components</h3>
                            <ul className="space-y-1 text-sm text-muted-foreground">
                                <li>• Graph Convolutional Networks (GCN)</li>
                                <li>• Graph Attention Networks (GAT)</li>
                                <li>• PyTorch Geometric</li>
                                <li>• Node2Vec embeddings</li>
                            </ul>
                        </div>
                        <div>
                            <h3 className="font-semibold mb-2 text-accent">Symbolic Components</h3>
                            <ul className="space-y-1 text-sm text-muted-foreground">
                                <li>• Prolog-based reasoning engine</li>
                                <li>• Knowledge graph querying (SPARQL)</li>
                                <li>• Pathway analysis algorithms</li>
                                <li>• Logic-based rule mining</li>
                            </ul>
                        </div>
                    </div>
                </Card>
            </div>
        </div>
    );
};

export default Documentation;
