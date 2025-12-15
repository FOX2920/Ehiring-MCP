import React from 'react';

const OfferLetter = ({ data }: { data: any }) => {
    if (!data.success) {
        return <div className="p-4 text-red-500">{data.message || "Failed to retrieve offer letter."}</div>;
    }

    return (
        <div className="p-6 max-w-3xl mx-auto bg-white shadow-lg rounded-lg border border-gray-200">
            <div className="border-b pb-4 mb-6">
                <h1 className="text-2xl font-bold text-gray-900 mb-1">Offer Letter</h1>
                <div className="flex justify-between items-end">
                    <div>
                        <p className="text-gray-600">Candidate: <span className="font-semibold text-gray-800">{data.candidate_name}</span></p>
                        <p className="text-gray-600">Position: <span className="font-semibold text-gray-800">{data.opening_name}</span></p>
                    </div>
                    {data.candidate_similarity_score && (
                        <div className="text-xs text-gray-400">Match score: {data.candidate_similarity_score.toFixed(2)}</div>
                    )}
                </div>
            </div>

            <div className="prose max-w-none text-gray-800 whitespace-pre-wrap font-serif leading-relaxed bg-gray-50 p-6 rounded shadow-inner">
                {data.test_result?.test_content || "Offer content not available."}
            </div>

            <div className="mt-6 pt-4 border-t text-sm text-gray-500 flex justify-between">
                <span>Source: {data.test_result?.test_name}</span>
                <span>Retrieved via Google Sheet</span>
            </div>
        </div>
    );
};

export default OfferLetter;
