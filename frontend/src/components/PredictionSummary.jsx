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



                {/* Weight slider removed as per user request */}

                <Button onClick={onAnalyze} className="w-full" size="lg">
                    <Play className="mr-2 h-4 w-4" />
                    Analyze
                </Button>

                {/* Score display removed as per user request */}
            </div>
        </Card>
    );
};

export default PredictionSummary;
