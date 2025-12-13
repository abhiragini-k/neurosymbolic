import { Card } from "@/components/ui/card";
import { Network } from "lucide-react";
import CytoscapeComponent from 'react-cytoscapejs';
import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';

// Register the dagre extension
cytoscape.use(dagre);

const GraphViewer = ({ data }) => {
    // Combine nodes and edges into elements
    const elements = [
        ...(data?.nodes || []),
        ...(data?.edges || [])
    ];

    const layout = {
        name: 'dagre',
        rankDir: 'TB', // Top to Bottom
        animate: true,
        animationDuration: 800,
        nodeDimensionsIncludeLabels: true,
        padding: 30,
        spacingFactor: 1.5, // Spread nodes out more
        ranker: 'network-simplex',
        rankSep: 100, // Vertical separation
        nodeSep: 80,  // Horizontal separation
    };

    const stylesheet = [
        // Default Node Style
        {
            selector: 'node',
            style: {
                'label': 'data(label)',
                'text-valign': 'bottom',
                'text-halign': 'center',
                'text-margin-y': 8,
                'color': '#cbd5e1', // slate-300
                'text-outline-width': 0,
                'background-color': '#64748b', // slate-500
                'width': 50,
                'height': 50,
                'font-size': 12,
                'font-weight': 'bold',
                'border-width': 2,
                'border-color': '#ffffff',
                'border-opacity': 0.8
            }
        },
        // Drug Node (Red/Pink - Top)
        {
            selector: 'node[type="Drug"]',
            style: {
                'background-color': '#ef4444', // Red-500
                'border-color': '#fca5a5', // Red-300
                'border-width': 4,
                'width': 70,
                'height': 70,
                'font-size': 14,
                'text-margin-y': 10,
                'shadow-blur': 10,
                'shadow-color': '#ef4444',
                'shadow-opacity': 0.5
            }
        },
        // Disease Node (Blue - Bottom)
        {
            selector: 'node[type="Disease"]',
            style: {
                'background-color': '#3b82f6', // Blue-500
                'border-color': '#93c5fd', // Blue-300
                'border-width': 4,
                'width': 70,
                'height': 70,
                'font-size': 14,
                'text-margin-y': 10,
                'shadow-blur': 10,
                'shadow-color': '#3b82f6',
                'shadow-opacity': 0.5
            }
        },
        // Gene/Protein Nodes (Green/Teal - Middle)
        {
            selector: 'node[type="Gene"]',
            style: {
                'background-color': '#10b981', // Emerald-500
                'border-color': '#6ee7b7',
                'width': 55,
                'height': 55
            }
        },
        {
            selector: 'node[type="Protein"]',
            style: {
                'background-color': '#06b6d4', // Cyan-500
                'border-color': '#67e8f9',
                'width': 55,
                'height': 55
            }
        },
        {
            selector: 'node[type="Pathway"]',
            style: {
                'background-color': '#f59e0b', // Amber-500
                'border-color': '#fcd34d',
                'width': 50,
                'height': 50
            }
        },
        // Edges
        {
            selector: 'edge',
            style: {
                'width': 3,
                'line-color': '#94a3b8', // slate-400
                'target-arrow-color': '#94a3b8',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier',
                'arrow-scale': 1.2,
                'opacity': 0.6
            }
        },
        // Highlighted/Selected
        {
            selector: ':selected',
            style: {
                'border-width': 4,
                'border-color': '#ffffff',
                'shadow-blur': 20,
                'shadow-color': '#ffffff',
                'shadow-opacity': 0.8
            }
        }
    ];

    return (
        <Card className="p-6 shadow-card h-fit sticky top-20">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold">Knowledge Graph</h2>
                <Network className="h-5 w-5 text-muted-foreground" />
            </div>

            <div className="relative w-full h-[600px] bg-slate-950 rounded-lg border border-border overflow-hidden shadow-lg">
                <CytoscapeComponent
                    elements={elements}
                    style={{ width: '100%', height: '100%' }}
                    stylesheet={stylesheet}
                    layout={layout}
                    cy={(cy) => {
                        // Center the graph after layout
                        cy.on('layoutstop', () => {
                            cy.fit(undefined, 50); // Fit with 50px padding
                        });
                    }}
                />
            </div>

            {/* Legend */}
            <div className="mt-6 space-y-3">
                <p className="text-sm font-medium mb-3">Legend:</p>
                <div className="grid grid-cols-2 gap-3">
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-[#ef4444]" />
                        <span className="text-xs text-muted-foreground">Drug (Source)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-[#3b82f6]" />
                        <span className="text-xs text-muted-foreground">Disease (Target)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-[#10b981]" />
                        <span className="text-xs text-muted-foreground">Gene</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-[#06b6d4]" />
                        <span className="text-xs text-muted-foreground">Protein</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-[#f59e0b]" />
                        <span className="text-xs text-muted-foreground">Pathway</span>
                    </div>
                </div>
                <p className="text-xs text-muted-foreground italic mt-4">
                    Layout: Hierarchical (Drug &rarr; Disease). Drag nodes to rearrange.
                </p>
            </div>
        </Card>
    );
};

export default GraphViewer;
