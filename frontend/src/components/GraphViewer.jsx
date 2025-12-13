import { Card } from "@/components/ui/card";
import { Network } from "lucide-react";
import CytoscapeComponent from 'react-cytoscapejs';
import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';

// Register the dagre extension
cytoscape.use(dagre);

const GraphViewer = ({ data }) => {
    // SVG Icons (Data URIs) - ViewBox adjusted for padding/centering (50% size = -12 -12 48 48, 60% size = -8 -8 40 40)
    const pillIcon = 'data:image/svg+xml;utf8,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-12 -12 48 48" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="7" width="18" height="10" rx="5" transform="rotate(-45 12 12)" /><line x1="8" y1="12" x2="16" y2="12" transform="rotate(-45 12 12)" /></svg>');
    const microscopeIcon = 'data:image/svg+xml;utf8,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-12 -12 48 48" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 18h8"/><path d="M3 22h18"/><path d="M14 22a7 7 0 1 0 0-14h-1"/><rect x="9" y="14" width="6" height="6" rx="2"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="12" y1="11" x2="12" y2="5"/></svg>');
    const activityIcon = 'data:image/svg+xml;utf8,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-8 -8 40 40" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12" /></svg>');
    const dnaIcon = 'data:image/svg+xml;utf8,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-8 -8 40 40" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 15c6.667-6 13.333 0 20-6"/><path d="M9 22c1.798-1.998 2.518-3.995 2.807-5.993"/><path d="M15 2c-1.798 1.998-2.518 3.995-2.807 5.993"/><path d="M17 17c-1.798 1.998-2.518 3.995-2.807 5.993"/><path d="M11 7c1.798-1.998 2.518-3.995 2.807-5.993"/></svg>');
    const networkIcon = 'data:image/svg+xml;utf8,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-8 -8 40 40" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>');

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
        spacingFactor: 0.8, // Compact layout
        ranker: 'network-simplex',
        rankSep: 60, // Reduced vertical separation
        nodeSep: 40,  // Reduced horizontal separation
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
                'color': '#1e293b', // slate-800 (Dark text for light bg)
                'text-outline-width': 0,
                'background-color': '#64748b', // slate-500
                'width': 50,
                'height': 50,
                'font-size': 14, // Increased font size
                'font-weight': 'bold',
                'border-width': 2,
                'border-color': '#ffffff',
                'border-opacity': 0.8,
                // Animation transitions
                'transition-property': 'background-color, border-color, width, height', // Removed shadow props
                'transition-duration': '0.4s',
                'transition-timing-function': 'spring(500, 15)', // Bouncy spring effect
                'overlay-opacity': 0 // Start invisible
            }
        },
        // Hover State (if supported by input device)
        {
            selector: 'node:active',
            style: {
                'overlay-padding': 10,
                'overlay-opacity': 0.2,
                'overlay-color': '#ffffff', // White flash
                'transition-duration': '0.1s'
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
                'font-size': 16,
                'text-margin-y': 10,
                // 'shadow-blur': 10,
                // 'shadow-color': '#ef4444',
                // 'shadow-opacity': 0.5,
                'background-image': pillIcon,
                'background-fit': 'cover'
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
                'font-size': 16,
                'text-margin-y': 10,
                // 'shadow-blur': 10,
                // 'shadow-color': '#3b82f6',
                // 'shadow-opacity': 0.5,
                'background-image': microscopeIcon,
                'background-fit': 'cover'
            }
        },
        // Gene/Protein Nodes (Green/Teal - Middle)
        {
            selector: 'node[type="Gene"]',
            style: {
                'background-color': '#10b981', // Emerald-500
                'border-color': '#6ee7b7',
                'width': 55,
                'height': 55,
                'background-image': activityIcon,
                'background-fit': 'cover'
            }
        },
        {
            selector: 'node[type="Protein"]',
            style: {
                'background-color': '#06b6d4', // Cyan-500
                'border-color': '#67e8f9',
                'width': 55,
                'height': 55,
                'background-image': dnaIcon,
                'background-fit': 'cover'
            }
        },
        {
            selector: 'node[type="Pathway"]',
            style: {
                'background-color': '#f59e0b', // Amber-500
                'border-color': '#fcd34d',
                'width': 50,
                'height': 50,
                'background-image': networkIcon,
                'background-fit': 'cover'
            }
        },
        // Edges
        {
            selector: 'edge',
            style: {
                'width': 3,
                'line-color': '#64748b', // slate-500 (Darker for visibility)
                'target-arrow-color': '#64748b',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier',
                'arrow-scale': 1.2,
                'opacity': 0.6
            }
        },
        // Highlighted/Selected (Glow Effect)
        {
            selector: ':selected',
            style: {
                'border-width': 4,
                'border-color': '#ffffff', // White border (no black outline)
                // 'shadow-blur': 30, // Invalid in React/Browser context if leaked
                // 'shadow-color': '#fbbf24', 
                // 'shadow-opacity': 0.8,
                'width': 85,
                'height': 85,
                'z-index': 999
            }
        },
        // Hover State (Glow on Mouse Over)
        {
            selector: '.hovered',
            style: {
                'border-width': 4,
                'border-color': '#ffffff', // White border
                // 'shadow-blur': 50, 
                // 'shadow-color': '#fbbf24', 
                // 'shadow-opacity': 1, 
                'width': 100, // Larger pop
                'height': 100,
                'z-index': 999,
                'transition-duration': '0.4s'
            }
        }
    ];

    return (
        <Card className="p-6 shadow-card h-fit sticky top-20">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold">Knowledge Graph</h2>
                <Network className="h-5 w-5 text-muted-foreground" />
            </div>

            <div className="relative w-full h-[600px] bg-white rounded-lg border border-border overflow-hidden shadow-lg">
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

                        // Hover Effects
                        cy.on('mouseover', 'node', (e) => {
                            const node = e.target;
                            node.addClass('hovered');
                            // Optional: Change cursor
                            document.body.style.cursor = 'pointer';
                        });

                        cy.on('mouseout', 'node', (e) => {
                            const node = e.target;
                            node.removeClass('hovered');
                            document.body.style.cursor = 'default';
                        });
                    }}
                />

                {/* Legend Overlay */}
                <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-sm p-4 rounded-lg border shadow-sm z-10 max-w-[200px]">
                    <p className="text-sm font-medium mb-2">Legend</p>
                    <div className="space-y-2">
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
                </div>
            </div>
        </Card>
    );
};

export default GraphViewer;
