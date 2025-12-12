import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import { Play } from "lucide-react";

interface PredictionSummaryProps {
  drug: string;
  disease: string;
  weight: number;
  score: number | null;
  onDrugChange: (value: string) => void;
  onDiseaseChange: (value: string) => void;
  onWeightChange: (value: number[]) => void;
  onAnalyze: () => void;
}

const PredictionSummary = ({
  drug,
  disease,
  weight,
  score,
  onDrugChange,
  onDiseaseChange,
  onWeightChange,
  onAnalyze,
}: PredictionSummaryProps) => {
  const getConfidenceLevel = (score: number) => {
    if (score >= 0.7) return { label: "High", color: "text-protein" };
    if (score >= 0.4) return { label: "Medium", color: "text-accent" };
    return { label: "Low", color: "text-muted-foreground" };
  };

  const confidence = score !== null ? getConfidenceLevel(score) : null;

  return (
    <Card className="p-6 shadow-card h-fit sticky top-20">
      <h2 className="mb-6 text-2xl font-bold">Prediction Summary</h2>
      
      <div className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="drug">Select Drug</Label>
          <Select value={drug} onValueChange={onDrugChange}>
            <SelectTrigger id="drug">
              <SelectValue placeholder="Choose a drug" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="metformin">Metformin</SelectItem>
              <SelectItem value="aspirin">Aspirin</SelectItem>
              <SelectItem value="ibuprofen">Ibuprofen</SelectItem>
              <SelectItem value="atorvastatin">Atorvastatin</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="disease">Select Disease</Label>
          <Select value={disease} onValueChange={onDiseaseChange}>
            <SelectTrigger id="disease">
              <SelectValue placeholder="Choose a disease" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="diabetes">Type 2 Diabetes</SelectItem>
              <SelectItem value="alzheimers">Alzheimer's Disease</SelectItem>
              <SelectItem value="cancer">Cancer</SelectItem>
              <SelectItem value="cardiovascular">Cardiovascular Disease</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div className="space-y-3">
          <div className="flex justify-between">
            <Label>Neural vs Symbolic Weight</Label>
            <span className="text-sm text-muted-foreground">{weight.toFixed(1)}</span>
          </div>
          <Slider
            value={[weight]}
            onValueChange={onWeightChange}
            min={0}
            max={1}
            step={0.1}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>Neural</span>
            <span>Symbolic</span>
          </div>
        </div>
        
        <Button onClick={onAnalyze} className="w-full" size="lg">
          <Play className="mr-2 h-4 w-4" />
          Analyze
        </Button>
        
        {score !== null && (
          <div className="mt-8 pt-6 border-t space-y-4">
            <div className="flex flex-col items-center">
              <div className="relative w-32 h-32">
                <svg className="w-full h-full transform -rotate-90">
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke="currentColor"
                    strokeWidth="8"
                    fill="none"
                    className="text-muted"
                  />
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke="currentColor"
                    strokeWidth="8"
                    fill="none"
                    strokeDasharray={`${2 * Math.PI * 56}`}
                    strokeDashoffset={`${2 * Math.PI * 56 * (1 - score)}`}
                    className="text-primary transition-all duration-1000"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-3xl font-bold">{score.toFixed(2)}</div>
                    <div className="text-xs text-muted-foreground">Score</div>
                  </div>
                </div>
              </div>
              
              {confidence && (
                <div className="mt-4 text-center">
                  <div className={`text-lg font-semibold ${confidence.color}`}>
                    {confidence.label} Confidence
                  </div>
                  <p className="text-sm text-muted-foreground mt-2">
                    This prediction shows {confidence.label.toLowerCase()} potential for therapeutic efficacy
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};

export default PredictionSummary;
