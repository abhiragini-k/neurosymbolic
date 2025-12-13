import api from "@/lib/api";

import { useState, useEffect } from 'react';
import { SparklesIcon, BeakerIcon, ShareIcon, CubeTransparentIcon, ScaleIcon } from '@heroicons/react/24/outline';

const ConfidenceBreakdown = ({ drugId, diseaseId }) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showDetails, setShowDetails] = useState(false);

    useEffect(() => {
        const fetchData = async () => {
            if (!drugId || !diseaseId) {
                setLoading(false);
                return;
            }

            setLoading(true);
            try {
                const res = await api.get(`/api/analysis/confidence-breakdown`, {
                    params: { drug_id: drugId, disease_id: diseaseId }
                });
                setData(res.data);
                setError(null);
            } catch (err) {
                console.error("Failed to fetch confidence breakdown", err);
                setError("Failed to load data");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [drugId, diseaseId]);

    if (loading) return (
        <div className="max-w-sm w-full bg-white shadow-sm rounded-xl border border-gray-200 p-5 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
            <div className="grid grid-cols-2 gap-3">
                <div className="h-24 bg-gray-100 rounded-lg"></div>
                <div className="h-24 bg-gray-100 rounded-lg"></div>
                <div className="h-24 bg-gray-100 rounded-lg"></div>
                <div className="h-24 bg-gray-100 rounded-lg"></div>
            </div>
        </div>
    );

    if (error) return (
        <div className="max-w-sm w-full bg-red-50 shadow-sm rounded-xl border border-red-200 p-5 text-red-600 text-sm">
            {error}
        </div>
    );

    if (!data || !data.averages) return null;

    const { pathway, gene_influence, embedding_similarity, rule_mining, final_confidence } = data.averages;
    // Normalized values for bars
    const normalized = data.normalized || {};
    const norm_pathway = normalized.pathway || 0;
    const norm_gene = normalized.gene_influence || 0;
    const norm_emb = normalized.embedding_similarity || 0;
    const norm_rule = normalized.rule_mining || 0;

    const { pathways, gene_influence: genes_detailed, similar_drugs, rules } = data.details || {};

    const toggleDetail = (key) => {
        setShowDetails(prev => ({ ...prev, [key]: !prev[key] }));
    };

    // Derived scores for display if needed, defaulting to raw values or normalized
    const pathwayScore = norm_pathway;
    const geneScore = norm_gene;
    const embeddingScore = norm_emb;
    const ruleScore = norm_rule;

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
                    <span className="text-sm font-semibold text-slate-700">Overall Confidence: {final_confidence}%</span>
                    <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-500" style={{ width: `${Math.min(final_confidence, 100)}%` }}></div>
                    </div>
                </div>
            </div>

            {/* Grid Content */}
            <div className="grid grid-cols-2 gap-3 mb-4">
                {/* Pathway Match - Blue */}
                <div className="bg-blue-50 rounded-lg p-3.5 space-y-2 col-span-2 sm:col-span-1">
                    <div className="flex items-center justify-between text-blue-700">
                        <div className="flex items-center gap-1.5">
                            <BeakerIcon className="w-4 h-4" />
                            <span className="text-xs font-bold uppercase tracking-wide">Pathway</span>
                        </div>
                        <span className="text-xs font-bold">{Math.round(pathway * 100)}% (Raw)</span>
                    </div>
                    <div className="w-full bg-gray-200 h-1.5 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-500 rounded-full" style={{ width: `${norm_pathway * 100}%` }}></div>
                    </div>
                    <button onClick={() => toggleDetail('pathway')} className="text-[10px] text-blue-600 underline">
                        {showDetails.pathway ? "Less" : "More Details"}
                    </button>
                    {showDetails.pathway && (
                        <ul className="text-xs space-y-1.5 text-gray-600 mt-2 bg-white p-2 rounded border border-blue-100">
                            {pathways && pathways.length > 0 ? pathways.map((p, i) => (
                                <li key={i} className="pl-2 border-l-2 border-blue-300">{p.path}</li>
                            )) : <li className="italic text-gray-400">No specific pathways.</li>}
                        </ul>
                    )}
                </div>

                {/* Gene Influence - Green */}
                <div className="bg-green-50 rounded-lg p-3.5 space-y-2 col-span-2 sm:col-span-1">
                    <div className="flex items-center justify-between text-green-700">
                        <div className="flex items-center gap-1.5">
                            <ShareIcon className="w-4 h-4" />
                            <span className="text-xs font-bold uppercase tracking-wide">Gene Infl.</span>
                        </div>
                        <span className="text-xs font-bold">{Math.round(gene_influence * 100)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 h-1.5 rounded-full overflow-hidden">
                        <div className="h-full bg-green-500 rounded-full" style={{ width: `${norm_gene * 100}%` }}></div>
                    </div>
                    <button onClick={() => toggleDetail('gene')} className="text-[10px] text-green-600 underline">
                        {showDetails.gene ? "Less" : "More Details"}
                    </button>
                    {showDetails.gene && (
                        <div className="flex flex-wrap gap-1.5 mt-2 bg-white p-2 rounded border border-green-100">
                            {genes_detailed && genes_detailed.length > 0 ? genes_detailed.map((g, i) => (
                                <span key={i} className="px-1.5 py-0.5 bg-green-100 text-green-800 rounded text-[10px]">
                                    {g.name}
                                </span>
                            )) : <span className="italic text-gray-400 text-xs">None.</span>}
                        </div>
                    )}
                </div>

                {/* Embedding Sim - Orange */}
                <div className="bg-orange-50 rounded-lg p-3.5 space-y-2 col-span-2 sm:col-span-1">
                    <div className="flex items-center justify-between text-orange-700">
                        <div className="flex items-center gap-1.5">
                            <CubeTransparentIcon className="w-4 h-4" />
                            <span className="text-xs font-bold uppercase tracking-wide">Embedding</span>
                        </div>
                        <span className="text-xs font-bold">{Math.round(embedding_similarity * 100)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 h-1.5 rounded-full overflow-hidden">
                        <div className="h-full bg-orange-500 rounded-full" style={{ width: `${norm_emb * 100}%` }}></div>
                    </div>
                    <button onClick={() => toggleDetail('emb')} className="text-[10px] text-orange-600 underline">
                        {showDetails.emb ? "Less" : "More Details"}
                    </button>
                    {showDetails.emb && (
                        <ul className="text-xs space-y-1 text-gray-600 mt-2 bg-white p-2 rounded border border-orange-100">
                            {similar_drugs && similar_drugs.length > 0 ? similar_drugs.map((d, i) => (
                                d && d.name ? (
                                    <li key={i} className="flex justify-between">
                                        <span>{d.name}</span>
                                        <span className="text-gray-400">{(d.score * 100).toFixed(0)}%</span>
                                    </li>
                                ) : null
                            )) : <li className="italic text-gray-400">None.</li>}
                        </ul>
                    )}
                </div>

                {/* Rule Based - Purple */}
                <div className="bg-purple-50 rounded-lg p-3.5 space-y-2 col-span-2 sm:col-span-1">
                    <div className="flex items-center justify-between text-purple-700">
                        <div className="flex items-center gap-1.5">
                            <ScaleIcon className="w-4 h-4" />
                            <span className="text-xs font-bold uppercase tracking-wide">Rules</span>
                        </div>
                        <span className="text-xs font-bold">{Math.round(rule_mining * 100)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 h-1.5 rounded-full overflow-hidden">
                        <div className="h-full bg-purple-500 rounded-full" style={{ width: `${norm_rule * 100}%` }}></div>
                    </div>
                    <button onClick={() => toggleDetail('rule')} className="text-[10px] text-purple-600 underline">
                        {showDetails.rule ? "Less" : "More Details"}
                    </button>
                    {showDetails.rule && (
                        <ul className="text-xs space-y-1 text-gray-600 mt-2 bg-white p-2 rounded border border-purple-100">
                            {rules && rules.length > 0 ? rules.map((r, i) => (
                                <li key={i}>✔ {r.name}</li>
                            )) : <li className="italic text-gray-400">None.</li>}
                        </ul>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ConfidenceBreakdown;
