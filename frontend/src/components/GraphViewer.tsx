import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Network, Pill, Activity, Dna, Microscope } from "lucide-react";
import { useState } from "react";

interface Node {
  id: string;
  label: string;
  type: "drug" | "protein" | "gene" | "disease" | "pathway";
  x: number;
  y: number;
  size: number;
}

interface Edge {
  from: string;
  to: string;
  weight: number;
}

const GraphViewer = () => {
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);

  const VIEWBOX_WIDTH = 140;
  const VIEWBOX_HEIGHT = 170;
  const GRAPH_PADDING_X = 6;
  const GRAPH_PADDING_TOP = 4;
  const GRAPH_PADDING_BOTTOM = 24;
  const NODE_SCALE = 0.18;
  const LABEL_WIDTH = 48;
  const LABEL_HEIGHT = 12;
  const BADGE_WIDTH = 40;
  const BADGE_HEIGHT = 10;
  const Y_MIN = 12;
  const Y_MAX = 98;
  const clamp = (value: number, min: number, max: number) =>
    Math.min(Math.max(value, min), max);

  const toViewBoxX = (percent: number) =>
    GRAPH_PADDING_X + (percent / 100) * (VIEWBOX_WIDTH - GRAPH_PADDING_X * 2);
  const toViewBoxY = (percent: number) =>
    GRAPH_PADDING_TOP +
    ((clamp(percent, Y_MIN, Y_MAX) - Y_MIN) / (Y_MAX - Y_MIN)) *
      (VIEWBOX_HEIGHT - GRAPH_PADDING_TOP - GRAPH_PADDING_BOTTOM);
  const getNodeRadius = (size: number) => (size / 2) * NODE_SCALE;

  // Define nodes with positions
  const nodes: Node[] = [
    // Center drug
    { id: "metformin", label: "Metformin", type: "drug", x: 50, y: 20, size: 60 },
    
    // Primary proteins
    { id: "ampk", label: "AMPK", type: "protein", x: 30, y: 45, size: 50 },
    { id: "mtor", label: "mTOR", type: "protein", x: 70, y: 45, size: 50 },
    
    // Genes
    { id: "glut4", label: "GLUT4", type: "gene", x: 20, y: 70, size: 45 },
    { id: "irs1", label: "IRS1", type: "gene", x: 50, y: 65, size: 45 },
    { id: "foxo1", label: "FOXO1", type: "gene", x: 80, y: 70, size: 45 },
    
    // Pathway
    { id: "pi3k", label: "PI3K Pathway", type: "pathway", x: 50, y: 85, size: 40 },
    
    // Target disease
    { id: "diabetes", label: "Type 2 Diabetes", type: "disease", x: 50, y: 100, size: 60 },
  ];

  // Define edges (connections)
  const edges: Edge[] = [
    { from: "metformin", to: "ampk", weight: 0.9 },
    { from: "metformin", to: "mtor", weight: 0.85 },
    { from: "ampk", to: "glut4", weight: 0.88 },
    { from: "ampk", to: "irs1", weight: 0.75 },
    { from: "mtor", to: "irs1", weight: 0.8 },
    { from: "mtor", to: "foxo1", weight: 0.82 },
    { from: "glut4", to: "pi3k", weight: 0.85 },
    { from: "irs1", to: "pi3k", weight: 0.9 },
    { from: "foxo1", to: "pi3k", weight: 0.78 },
    { from: "pi3k", to: "diabetes", weight: 0.92 },
  ];

  const getNodeColor = (type: string) => {
    switch (type) {
      case "drug": return "hsl(var(--drug-color))";
      case "disease": return "hsl(var(--disease-color))";
      case "protein": return "hsl(var(--protein-color))";
      case "gene": return "hsl(var(--accent))";
      case "pathway": return "hsl(var(--primary))";
      default: return "hsl(var(--muted))";
    }
  };

  const getNodeIcon = (type: string) => {
    switch (type) {
      case "drug": return Pill;
      case "protein": return Activity;
      case "gene": return Dna;
      case "pathway": return Network;
      case "disease": return Microscope;
      default: return Network;
    }
  };

  return (
    <Card className="p-6 shadow-card h-fit sticky top-20">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold">Knowledge Graph</h2>
        <Network className="h-5 w-5 text-muted-foreground" />
      </div>
      
      {/* Graph visualization */}
      <div
        className="relative w-full bg-gradient-to-br from-background via-muted/10 to-background rounded-lg border border-border overflow-hidden shadow-lg"
        style={{ paddingBottom: "105%" }}
      >
        <svg
          className="absolute inset-0 w-full h-full"
          viewBox={`0 0 ${VIEWBOX_WIDTH} ${VIEWBOX_HEIGHT}`}
          preserveAspectRatio="xMidYMid meet"
        >
          {/* Define gradients and filters */}
          <defs>
            <linearGradient id="edgeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity="0.6" />
              <stop offset="100%" stopColor="hsl(var(--accent))" stopOpacity="0.6" />
            </linearGradient>
            
            <linearGradient id="edgeGradientActive" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity="0.9" />
              <stop offset="50%" stopColor="hsl(var(--accent))" stopOpacity="0.9" />
              <stop offset="100%" stopColor="hsl(var(--drug-color))" stopOpacity="0.9" />
            </linearGradient>
            
            {/* Radial gradient for nodes */}
            <radialGradient id="nodeGradient">
              <stop offset="0%" stopColor="currentColor" stopOpacity="1" />
              <stop offset="100%" stopColor="currentColor" stopOpacity="0.8" />
            </radialGradient>
            
            {/* Glow filter */}
            <filter id="glow">
              <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
            
            {/* Strong glow for hover */}
            <filter id="strongGlow">
              <feGaussianBlur stdDeviation="5" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
            
            {/* Animated gradient for flow effect */}
            <linearGradient id="flowGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity="0">
                <animate attributeName="stop-opacity" values="0;1;0" dur="2s" repeatCount="indefinite" />
              </stop>
              <stop offset="50%" stopColor="hsl(var(--accent))" stopOpacity="0.8">
                <animate attributeName="offset" values="0;0.5;1" dur="2s" repeatCount="indefinite" />
              </stop>
              <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity="0">
                <animate attributeName="stop-opacity" values="0;1;0" dur="2s" repeatCount="indefinite" />
              </stop>
            </linearGradient>
          </defs>
          
          {/* Draw edges with curved paths */}
          {edges.map((edge, idx) => {
            const fromNode = nodes.find(n => n.id === edge.from);
            const toNode = nodes.find(n => n.id === edge.to);
            if (!fromNode || !toNode) return null;
            const from = {
              x: toViewBoxX(fromNode.x),
              y: toViewBoxY(fromNode.y),
            };
            const to = {
              x: toViewBoxX(toNode.x),
              y: toViewBoxY(toNode.y),
            };
            
            const isHighlighted = hoveredNode === edge.from || hoveredNode === edge.to;
            
            // Calculate control point for curved path
            const midX = (from.x + to.x) / 2;
            const midY = (from.y + to.y) / 2;
            const dx = to.x - from.x;
            const dy = to.y - from.y;
            const offset = 8; // Curve offset
            const controlX = midX - dy * offset / 100;
            const controlY = midY + dx * offset / 100;
            
            const pathD = `M ${from.x} ${from.y} Q ${controlX} ${controlY} ${to.x} ${to.y}`;
            
            return (
              <g key={idx}>
                {/* Shadow/glow layer */}
                {isHighlighted && (
                  <path
                    d={pathD}
                    stroke="hsl(var(--primary))"
                    strokeWidth="8"
                    strokeOpacity="0.2"
                    fill="none"
                    filter="url(#glow)"
                    className="transition-all duration-300"
                  />
                )}
                
                {/* Main path */}
                <path
                  d={pathD}
                  stroke={isHighlighted ? "url(#edgeGradientActive)" : "url(#edgeGradient)"}
                  strokeWidth={isHighlighted ? "3" : "2"}
                  strokeOpacity={isHighlighted ? "1" : "0.4"}
                  fill="none"
                  strokeLinecap="round"
                  className="transition-all duration-300"
                  style={{
                    filter: isHighlighted ? 'drop-shadow(0 0 4px hsl(var(--primary)))' : 'none'
                  }}
                />
                
                {/* Animated flow dots for highlighted edges */}
                {isHighlighted && (
                  <>
                    <circle r="3" fill="hsl(var(--primary))" filter="url(#glow)">
                      <animateMotion dur="2s" repeatCount="indefinite" path={pathD} />
                      <animate attributeName="opacity" values="0;1;0" dur="2s" repeatCount="indefinite" />
                    </circle>
                    <circle r="3" fill="hsl(var(--accent))" filter="url(#glow)">
                      <animateMotion dur="2s" repeatCount="indefinite" path={pathD} begin="0.5s" />
                      <animate attributeName="opacity" values="0;1;0" dur="2s" repeatCount="indefinite" begin="0.5s" />
                    </circle>
                  </>
                )}
                
                {/* Weight indicator */}
                {isHighlighted && (
                  <text
                    x={controlX}
                    y={controlY}
                    fill="hsl(var(--foreground))"
                    fontSize="5"
                    fontWeight="600"
                    textAnchor="middle"
                    className="animate-fade-in"
                    style={{
                      textShadow: '0 0 4px hsl(var(--background))',
                      filter: 'drop-shadow(0 1px 2px rgba(0,0,0,0.2))'
                    }}
                  >
                    {(edge.weight * 100).toFixed(0)}%
                  </text>
                )}
              </g>
            );
          })}
          
          {/* Draw nodes */}
          {nodes.map((node) => {
            const Icon = getNodeIcon(node.type);
            const isHovered = hoveredNode === node.id;
            const isConnected = edges.some(e => 
              (e.from === hoveredNode && e.to === node.id) || 
              (e.to === hoveredNode && e.from === node.id)
            );
            const shouldHighlight = isHovered || isConnected || !hoveredNode;
            const isKeyNode = node.type === "drug" || node.type === "disease";
            const viewX = toViewBoxX(node.x);
            const viewY = toViewBoxY(node.y);
            const radius = getNodeRadius(node.size);
            
            return (
              <g
                key={node.id}
                transform={`translate(${viewX}, ${viewY})`}
                onMouseEnter={() => setHoveredNode(node.id)}
                onMouseLeave={() => setHoveredNode(null)}
                className="cursor-pointer transition-all duration-300"
                filter={isHovered ? "url(#strongGlow)" : isKeyNode ? "url(#glow)" : undefined}
              >
                {/* Outer glow ring for key nodes */}
                {isKeyNode && (
                  <circle
                    r={radius + 6}
                    fill="none"
                    stroke={getNodeColor(node.type)}
                    strokeWidth="2"
                    strokeOpacity="0.3"
                    className="transition-all duration-300"
                  >
                    <animate
                      attributeName="r"
                      values={`${radius + 4};${radius + 10};${radius + 4}`}
                      dur="3s"
                      repeatCount="indefinite"
                    />
                    <animate
                      attributeName="stroke-opacity"
                      values="0.3;0.6;0.3"
                      dur="3s"
                      repeatCount="indefinite"
                    />
                  </circle>
                )}
                
                {/* Shadow circle */}
                <circle
                  r={radius}
                  fill="hsl(var(--foreground))"
                  opacity="0.1"
                  transform="translate(2, 2)"
                  className="transition-all duration-300"
                  style={{
                    transform: isHovered ? "translate(3px, 3px) scale(1.2)" : "translate(2px, 2px) scale(1)",
                  }}
                />
                
                {/* Main node circle with gradient */}
                <circle
                  r={radius}
                  fill={getNodeColor(node.type)}
                  opacity={shouldHighlight ? 1 : 0.3}
                  className="transition-all duration-300"
                  style={{
                    transform: isHovered ? "scale(1.2)" : "scale(1)",
                    transformOrigin: "center",
                    filter: isHovered ? 'brightness(1.2)' : 'brightness(1)'
                  }}
                />
                
                {/* Inner highlight circle */}
                <circle
                  r={Math.max(radius - 4, 2)}
                  fill="white"
                  opacity={isHovered ? 0.2 : 0.1}
                  className="transition-all duration-300"
                  style={{
                    transform: isHovered ? "scale(1.2)" : "scale(1)",
                    transformOrigin: "center",
                  }}
                />
                
                {/* Icon overlay */}
                <g transform={`translate(-6, -6)`}>
                  <foreignObject width="12" height="12">
                    <Icon className="h-3 w-3 text-white drop-shadow-lg" />
                  </foreignObject>
                </g>
                
                {/* Label with background */}
                {node.id === "pi3k" ? (
                  <g transform={`translate(${radius + 4}, 0)`}>
                    <rect
                      x={4}
                      y={-LABEL_HEIGHT / 2}
                      width={LABEL_WIDTH}
                      height={LABEL_HEIGHT}
                      fill="hsl(var(--background))"
                      opacity={isHovered ? 0.95 : 0.8}
                      rx="4"
                      className="transition-all duration-300"
                    />
                    <text
                      x={LABEL_WIDTH / 2 + 4}
                      y={-LABEL_HEIGHT / 2 + 8}
                      textAnchor="middle"
                      fill="hsl(var(--foreground))"
                      fontSize={isHovered ? "6" : "5.5"}
                      fontWeight={isHovered ? "700" : "500"}
                      opacity={shouldHighlight ? 1 : 0.6}
                      className="transition-all duration-300 select-none"
                      style={{
                        filter: 'drop-shadow(0 1px 2px rgba(0,0,0,0.1))'
                      }}
                    >
                      {node.label}
                    </text>
                  </g>
                ) : (
                  <g>
                    <rect
                      x={-LABEL_WIDTH / 2}
                      y={radius + 8}
                      width={LABEL_WIDTH}
                      height={LABEL_HEIGHT}
                      fill="hsl(var(--background))"
                      opacity={isHovered ? 0.95 : 0.8}
                      rx="4"
                      className="transition-all duration-300"
                    />
                    <text
                      y={radius + 15}
                      textAnchor="middle"
                      fill="hsl(var(--foreground))"
                      fontSize={isHovered ? "6" : "5.5"}
                      fontWeight={isHovered ? "700" : "500"}
                      opacity={shouldHighlight ? 1 : 0.5}
                      className="transition-all duration-300 select-none"
                      style={{
                        filter: 'drop-shadow(0 1px 2px rgba(0,0,0,0.1))'
                      }}
                    >
                      {node.label}
                    </text>
                  </g>
                )}
                
                {/* Type badge on hover */}
                {isHovered && (
                  <g className="animate-fade-in">
                    <rect
                      x={-BADGE_WIDTH / 2}
                      y={radius + 28}
                      width={BADGE_WIDTH}
                      height={BADGE_HEIGHT}
                      fill={getNodeColor(node.type)}
                      opacity="0.9"
                      rx="8"
                    />
                    <text
                      y={radius + 30}
                      textAnchor="middle"
                      fill="white"
                      fontSize="4.5"
                      fontWeight="600"
                    >
                      {node.type.toUpperCase()}
                    </text>
                  </g>
                )}
                
                {/* Pulse animation for hovered nodes */}
                {isHovered && (
                  <circle
                    r={radius}
                    fill="none"
                    stroke={getNodeColor(node.type)}
                    strokeWidth="2"
                    strokeOpacity="0"
                    className="transition-all duration-300"
                  >
                    <animate
                      attributeName="r"
                      values={`${radius};${radius + 12}`}
                      dur="1s"
                      repeatCount="indefinite"
                    />
                    <animate
                      attributeName="stroke-opacity"
                      values="0.8;0"
                      dur="1s"
                      repeatCount="indefinite"
                    />
                  </circle>
                )}
              </g>
            );
          })}
        </svg>
      </div>
      
      {/* Legend */}
      <div className="mt-6 space-y-3">
        <p className="text-sm font-medium mb-3">Legend:</p>
        <div className="grid grid-cols-2 gap-3">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-drug" />
            <span className="text-xs text-muted-foreground">Drug</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-disease" />
            <span className="text-xs text-muted-foreground">Disease</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-protein" />
            <span className="text-xs text-muted-foreground">Protein</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-accent" />
            <span className="text-xs text-muted-foreground">Gene</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-primary" />
            <span className="text-xs text-muted-foreground">Pathway</span>
          </div>
        </div>
        <p className="text-xs text-muted-foreground italic mt-4">
          Hover over nodes to explore connections and view relationship strengths
        </p>
      </div>
    </Card>
  );
};

export default GraphViewer;
