import { BeakerIcon, ShareIcon, CubeTransparentIcon, ScaleIcon, SparklesIcon } from "@heroicons/react/24/outline";

/**
 * ConfidenceBreakdown Component
 * Refined design with 2x2 grid, HeroIcons, and specific color themes.
 */
const ConfidenceBreakdown = () => {
    return (
        <div className="max-w-sm w-full bg-white shadow-sm rounded-xl border border-gray-200 p-5">
            {/* Header */}
            <div className="mb-4">
                <div className="flex items-center gap-2 mb-1">
                    <SparklesIcon className="w-5 h-5 text-blue-500" />
                    <h3 className="text-lg font-semibold text-gray-900 leading-tight">Confidence Breakdown</h3>
                </div>
                <p className="text-sm text-gray-500 font-medium ml-7">(Explainable AI)</p>
                <div className="mt-3 mb-4 flex items-center justify-between">
                    <span className="text-sm font-semibold text-slate-700">Overall Confidence: 0.72</span>
                    <div className="h-1 w-full ml-4 bg-sky-100 rounded-full"></div>
                </div>
            </div>

            {/* Grid Content */}
            <div className="grid grid-cols-2 gap-3">
                {/* Pathway Match - Blue */}
                <div className="bg-blue-50 rounded-lg p-3.5 space-y-2">
                    <div className="flex items-center justify-between text-blue-700">
                        <div className="flex items-center gap-1.5">
                            <BeakerIcon className="w-4 h-4" />
                            <span className="text-xs font-bold uppercase tracking-wide">Pathway</span>
                        </div>
                        <span className="text-xs font-bold">78%</span>
                    </div>
                    <div className="w-full bg-gray-200 h-1.5 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-500 rounded-full" style={{ width: '78%' }}></div>
                    </div>
                    <ul className="text-[10px] leading-tight text-blue-900 font-medium space-y-1 mt-1 pl-1">
                        <li>• MAPK Pathway</li>
                        <li>• TNF Signaling</li>
                    </ul>
                </div>

                {/* Gene Influence - Green */}
                <div className="bg-green-50 rounded-lg p-3.5 space-y-2">
                    <div className="flex items-center justify-between text-green-700">
                        <div className="flex items-center gap-1.5">
                            <ShareIcon className="w-4 h-4" />
                            <span className="text-xs font-bold uppercase tracking-wide">Gene Infl.</span>
                        </div>
                        <span className="text-xs font-bold">66%</span>
                    </div>
                    <div className="w-full bg-gray-200 h-1.5 rounded-full overflow-hidden">
                        <div className="h-full bg-green-500 rounded-full" style={{ width: '66%' }}></div>
                    </div>
                    <ul className="text-[10px] leading-tight text-green-900 font-medium space-y-1 mt-1 pl-1">
                        <li>• AMPK → TNF (0.92)</li>
                        <li>• AMPK → IL6 (0.88)</li>
                    </ul>
                </div>

                {/* Embedding Sim - Orange */}
                <div className="bg-orange-50 rounded-lg p-3.5 space-y-2">
                    <div className="flex items-center justify-between text-orange-700">
                        <div className="flex items-center gap-1.5">
                            <CubeTransparentIcon className="w-4 h-4" />
                            <span className="text-xs font-bold uppercase tracking-wide">Embedding</span>
                        </div>
                        <span className="text-xs font-bold">58%</span>
                    </div>
                    <div className="w-full bg-gray-200 h-1.5 rounded-full overflow-hidden">
                        <div className="h-full bg-orange-500 rounded-full" style={{ width: '58%' }}></div>
                    </div>
                    <ul className="text-[10px] leading-tight text-orange-900 font-medium space-y-1 mt-1 pl-1">
                        <li>• Metformin (0.82)</li>
                        <li>• Acarbose (0.71)</li>
                    </ul>
                </div>

                {/* Rule Based - Purple */}
                <div className="bg-purple-50 rounded-lg p-3.5 space-y-2">
                    <div className="flex items-center justify-between text-purple-700">
                        <div className="flex items-center gap-1.5">
                            <ScaleIcon className="w-4 h-4" />
                            <span className="text-xs font-bold uppercase tracking-wide">Rules</span>
                        </div>
                        <span className="text-xs font-bold">41%</span>
                    </div>
                    <div className="w-full bg-gray-200 h-1.5 rounded-full overflow-hidden">
                        <div className="h-full bg-purple-500 rounded-full" style={{ width: '41%' }}></div>
                    </div>
                    <ul className="text-[10px] leading-tight text-purple-900 font-medium space-y-1 mt-1 pl-1">
                        <li>✔ Downregulates IL6</li>
                        <li>✔ Anti-inflammatory sim.</li>
                    </ul>
                </div>
            </div>
        </div>
    );
};

export default ConfidenceBreakdown;
