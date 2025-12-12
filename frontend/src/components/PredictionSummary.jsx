import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import { Play } from "lucide-react";

const PredictionSummary = ({
    drug,
    disease,
    weight,
    score,
    onDrugChange,
    onDiseaseChange,
    onWeightChange,
    onAnalyze,
}) => {
    const getConfidenceLevel = (score) => {
        if (score >= 0.7) return { label: "High", color: "text-protein" };
        if (score >= 0.4) return { label: "Medium", color: "text-accent" };
        return { label: "Low", color: "text-muted-foreground" };
    };

    const confidence = score !== null ? getConfidenceLevel(score) : null;

    return (
        <Card className="p-6 shadow-card h-fit sticky top-20">
            <h2 className="mb-6 text-2xl font-bold">Prediction Summary</h2>

            <div className="space-y-6">
                <div className="space-y-4">
                    <div className="space-y-2">
                        <Label htmlFor="search-drug" className="text-lg font-semibold">Search a Drug</Label>
                        <Input
                            id="search-drug"
                            placeholder="Type a drug name..."
                            value={drug}
                            onChange={(e) => onDrugChange(e.target.value)}
                        />
                    </div>

                    <div className="space-y-2">
                        <Label className="text-lg font-semibold">Categories of Drug</Label>
                        <Accordion type="single" collapsible className="w-full">
                            <AccordionItem value="antibiotics">
                                <AccordionTrigger className="text-sm font-normal py-2">Antibiotics</AccordionTrigger>
                                <AccordionContent>
                                    <div className="flex flex-col space-y-1">
                                        {["Amoxicillin", "Ciprofloxacin", "Azithromycin", "Doxycycline", "Cephalexin"].map((d) => (
                                            <button
                                                key={d}
                                                className={`text-left text-sm py-1 px-2 hover:bg-accent hover:text-accent-foreground rounded-sm ${drug === d ? "bg-accent text-accent-foreground font-medium" : ""}`}
                                                onClick={() => onDrugChange(d)}
                                            >
                                                {d}
                                            </button>
                                        ))}
                                    </div>
                                </AccordionContent>
                            </AccordionItem>
                            <AccordionItem value="antivirals">
                                <AccordionTrigger className="text-sm font-normal py-2">Antivirals</AccordionTrigger>
                                <AccordionContent>
                                    <div className="flex flex-col space-y-1">
                                        {["Acyclovir", "Oseltamivir", "Zidovudine (AZT)", "Ribavirin", "Remdesivir"].map((d) => (
                                            <button
                                                key={d}
                                                className={`text-left text-sm py-1 px-2 hover:bg-accent hover:text-accent-foreground rounded-sm ${drug === d ? "bg-accent text-accent-foreground font-medium" : ""}`}
                                                onClick={() => onDrugChange(d)}
                                            >
                                                {d}
                                            </button>
                                        ))}
                                    </div>
                                </AccordionContent>
                            </AccordionItem>
                            <AccordionItem value="anticancer">
                                <AccordionTrigger className="text-sm font-normal py-2">Anticancer</AccordionTrigger>
                                <AccordionContent>
                                    <div className="flex flex-col space-y-1">
                                        {["Doxorubicin", "Methotrexate", "Cisplatin", "Paclitaxel", "Imatinib"].map((d) => (
                                            <button
                                                key={d}
                                                className={`text-left text-sm py-1 px-2 hover:bg-accent hover:text-accent-foreground rounded-sm ${drug === d ? "bg-accent text-accent-foreground font-medium" : ""}`}
                                                onClick={() => onDrugChange(d)}
                                            >
                                                {d}
                                            </button>
                                        ))}
                                    </div>
                                </AccordionContent>
                            </AccordionItem>
                            <AccordionItem value="pain">
                                <AccordionTrigger className="text-sm font-normal py-2">Pain & Inflammation</AccordionTrigger>
                                <AccordionContent>
                                    <div className="flex flex-col space-y-1">
                                        {["Ibuprofen", "Paracetamol", "Aspirin", "Diclofenac", "Celecoxib"].map((d) => (
                                            <button
                                                key={d}
                                                className={`text-left text-sm py-1 px-2 hover:bg-accent hover:text-accent-foreground rounded-sm ${drug === d ? "bg-accent text-accent-foreground font-medium" : ""}`}
                                                onClick={() => onDrugChange(d)}
                                            >
                                                {d}
                                            </button>
                                        ))}
                                    </div>
                                </AccordionContent>
                            </AccordionItem>
                            <AccordionItem value="neurological">
                                <AccordionTrigger className="text-sm font-normal py-2">Neurological drugs</AccordionTrigger>
                                <AccordionContent>
                                    <div className="flex flex-col space-y-1">
                                        {["Sertraline", "Donepezil", "Levodopa", "Diazepam", "Carbamazepine"].map((d) => (
                                            <button
                                                key={d}
                                                className={`text-left text-sm py-1 px-2 hover:bg-accent hover:text-accent-foreground rounded-sm ${drug === d ? "bg-accent text-accent-foreground font-medium" : ""}`}
                                                onClick={() => onDrugChange(d)}
                                            >
                                                {d}
                                            </button>
                                        ))}
                                    </div>
                                </AccordionContent>
                            </AccordionItem>
                            <AccordionItem value="metabolic">
                                <AccordionTrigger className="text-sm font-normal py-2">Metabolic disorders</AccordionTrigger>
                                <AccordionContent>
                                    <div className="flex flex-col space-y-1">
                                        {["Metformin", "Insulin", "Glipizide", "Levothyroxine", "Pioglitazone"].map((d) => (
                                            <button
                                                key={d}
                                                className={`text-left text-sm py-1 px-2 hover:bg-accent hover:text-accent-foreground rounded-sm ${drug === d ? "bg-accent text-accent-foreground font-medium" : ""}`}
                                                onClick={() => onDrugChange(d)}
                                            >
                                                {d}
                                            </button>
                                        ))}
                                    </div>
                                </AccordionContent>
                            </AccordionItem>
                        </Accordion>
                    </div>
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
