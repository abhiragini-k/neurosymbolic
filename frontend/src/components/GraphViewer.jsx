import { Card } from "@/components/ui/card";
import { Network } from "lucide-react";
import CytoscapeComponent from 'react-cytoscapejs';
import cytoscape from 'cytoscape';

const GraphViewer = ({ data }) => {
    // Combine nodes and edges into elements
    const elements = [
        ...(data?.nodes || []),
        ...(data?.edges || [])
    ];

    const layout = {
        name: 'cose',
        animate: true,
        animationDuration: 500,
        nodeDimensionsIncludeLabels: true,
        padding: 20,
        randomize: false, // Keep deterministic if possible, or true for fresh layout
        componentSpacing: 100,
        nodeRepulsion: 400000,
        edgeElasticity: 100,
        nestingFactor: 5,
    };

    const stylesheet = [
        {
            selector: 'node',
            style: {
                'label': 'data(label)',
                'text-valign': 'center',
                'text-halign': 'center',
                'color': '#ffffff',
                'text-outline-width': 2,
                'text-outline-color': '#000000',
                'background-color': '#666',
                'width': 40,
                'height': 40,
                'font-size': 10
            }
        },
        {
            selector: 'node[type="Drug"]',
            style: {
                'background-color': '#F472B6', // Pink-400 (approx for drug)
                'text-outline-color': '#831843'
            }
        },
        {
            selector: 'node[type="Disease"]',
            style: {
                'background-color': '#60A5FA', // Blue-400
                'text-outline-color': '#1E3A8A'
            }
        },
        {
            selector: 'node[type="Gene"]',
            style: {
                'background-color': '#A78BFA', // Purple-400
                'text-outline-color': '#4C1D95'
            }
        },
        {
            selector: 'node[type="Protein"]',
            style: {
                'background-color': '#34D399', // Emerald-400
                'text-outline-color': '#064E3B'
            }
        },
        {
            selector: 'node[type="Pathway"]',
            style: {
                'background-color': '#FBBF24', // Amber-400
                'text-outline-color': '#78350F'
            }
        },
        {
            selector: 'edge',
            style: {
                'width': 2,
                'line-color': '#94a3b8',
                'target-arrow-color': '#94a3b8',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier',
                'label': 'data(label)',
                'font-size': 8,
                'text-rotation': 'autorotate',
                'text-background-color': '#ffffff',
                'text-background-opacity': 0.8,
                'text-background-padding': 2
            }
        },
        {
            selector: ':selected',
            style: {
                'border-width': 4,
                'border-color': '#ffffff'
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
                        // Optional: You can use cy here to bind events
                        cy.on('tap', 'node', (evt) => {
                            const node = evt.target;
                            console.log('Tapped node ' + node.id());
                        });
                    }}
                />
            </div>

            {/* Legend */}
            <div className="mt-6 space-y-3">
                <p className="text-sm font-medium mb-3">Legend:</p>
                <div className="grid grid-cols-2 gap-3">
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-[#F472B6]" />
                        <span className="text-xs text-muted-foreground">Drug</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-[#60A5FA]" />
                        <span className="text-xs text-muted-foreground">Disease</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-[#34D399]" />
                        <span className="text-xs text-muted-foreground">Protein</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-[#A78BFA]" />
                        <span className="text-xs text-muted-foreground">Gene</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-[#FBBF24]" />
                        <span className="text-xs text-muted-foreground">Pathway</span>
                    </div>
                </div>
                <p className="text-xs text-muted-foreground italic mt-4">
                    Interactive Graph: Zoom, Pan, and Drag nodes.
                </p>
            </div>
        </Card>
    );
};

export default GraphViewer;
