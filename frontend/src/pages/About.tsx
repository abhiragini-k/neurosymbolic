import Header from "@/components/Header";
import { Card } from "@/components/ui/card";
import { Brain, Network, Lightbulb, Target } from "lucide-react";

const About = () => {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <div className="container py-12 max-w-4xl">
        <h1 className="text-4xl font-bold mb-4">About Neurosymbolic AI</h1>
        <p className="text-xl text-muted-foreground mb-12">
          Understanding the fusion of neural networks and symbolic reasoning
        </p>
        
        <div className="space-y-8">
          <Card className="p-8 shadow-card">
            <div className="flex items-start gap-4">
              <div className="inline-flex rounded-lg bg-primary/10 p-3 mt-1">
                <Brain className="h-6 w-6 text-primary" />
              </div>
              <div className="flex-1">
                <h2 className="text-2xl font-semibold mb-3">What is Neurosymbolic AI?</h2>
                <p className="text-muted-foreground leading-relaxed">
                  Neurosymbolic AI combines the pattern recognition power of neural networks 
                  with the logical reasoning capabilities of symbolic AI. This hybrid approach 
                  enables both high accuracy and interpretability—critical for biomedical applications 
                  where understanding the "why" behind predictions is as important as the predictions themselves.
                </p>
              </div>
            </div>
          </Card>
          
          <Card className="p-8 shadow-card">
            <div className="flex items-start gap-4">
              <div className="inline-flex rounded-lg bg-accent/10 p-3 mt-1">
                <Network className="h-6 w-6 text-accent" />
              </div>
              <div className="flex-1">
                <h2 className="text-2xl font-semibold mb-3">The Neural Component</h2>
                <p className="text-muted-foreground leading-relaxed mb-4">
                  Graph Neural Networks (GNNs) analyze the complex relationships between drugs, 
                  proteins, genes, and diseases. They learn patterns from vast amounts of biomedical 
                  data, capturing subtle similarities that might not be obvious to human researchers.
                </p>
                <ul className="space-y-2 text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>Processes molecular structures and interaction networks</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>Identifies complex patterns in high-dimensional data</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>Learns from millions of drug-disease relationships</span>
                  </li>
                </ul>
              </div>
            </div>
          </Card>
          
          <Card className="p-8 shadow-card">
            <div className="flex items-start gap-4">
              <div className="inline-flex rounded-lg bg-disease p-3 mt-1">
                <Lightbulb className="h-6 w-6 text-white" />
              </div>
              <div className="flex-1">
                <h2 className="text-2xl font-semibold mb-3">The Symbolic Component</h2>
                <p className="text-muted-foreground leading-relaxed mb-4">
                  Logic-based reasoning systems use curated biomedical knowledge to construct 
                  explicit reasoning chains. This provides transparency and allows domain experts 
                  to validate and understand the system's conclusions.
                </p>
                <ul className="space-y-2 text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <span className="text-accent mt-1">•</span>
                    <span>Applies formal logic rules to biological pathways</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-accent mt-1">•</span>
                    <span>Generates interpretable reasoning chains</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-accent mt-1">•</span>
                    <span>Incorporates expert knowledge and constraints</span>
                  </li>
                </ul>
              </div>
            </div>
          </Card>
          
          <Card className="p-8 shadow-card">
            <div className="flex items-start gap-4">
              <div className="inline-flex rounded-lg bg-protein p-3 mt-1">
                <Target className="h-6 w-6 text-white" />
              </div>
              <div className="flex-1">
                <h2 className="text-2xl font-semibold mb-3">Drug Repurposing Application</h2>
                <p className="text-muted-foreground leading-relaxed">
                  Finding new uses for existing drugs can dramatically reduce development time 
                  and costs. Our neurosymbolic approach identifies promising drug-disease pairs 
                  while providing the scientific reasoning to support experimental validation. 
                  This transparency accelerates the path from computational prediction to clinical trials.
                </p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default About;
