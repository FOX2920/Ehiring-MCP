import React from 'react';

const CandidateDetail = ({ data }: { data: any }) => {
    // data is expected to be the 'openings' list from get_candidate_details_tool
    const openings = data.openings || [];

    if (!openings.length) {
        return <div className="p-4 text-red-500">No candidate details found.</div>;
    }

    return (
        <div className="p-4 space-y-8">
            {openings.map((opening: any, idx: number) => (
                <div key={idx} className="border-b pb-8 last:border-0">
                    <h2 className="text-2xl font-bold mb-6 text-gray-900 border-l-4 border-blue-500 pl-3">
                        {opening.opening_name || "Unknown Position"}
                    </h2>

                    <div className="space-y-6">
                        {opening.candidates.map((cand: any) => (
                            <div key={cand.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                                {/* Header */}
                                <div className="bg-gray-50 p-4 border-b border-gray-100 flex justify-between items-start">
                                    <div>
                                        <h3 className="text-xl font-bold text-gray-800">{cand.ten}</h3>
                                        <div className="text-sm text-gray-500 mt-1 flex flex-wrap gap-2">
                                            <span>{cand.email}</span>
                                            <span>•</span>
                                            <span>{cand.so_dien_thoai}</span>
                                            <span>•</span>
                                            <span className="bg-green-100 text-green-800 px-2 py-0.5 rounded-full text-xs font-medium">
                                                {cand.stage_name}
                                            </span>
                                        </div>
                                    </div>
                                    {cand.cv_url && (
                                        <a href={cand.cv_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                                            Open CV ↗
                                        </a>
                                    )}
                                </div>

                                <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-6">
                                    {/* Personal Info */}
                                    <div>
                                        <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Personal Info</h4>
                                        <dl className="space-y-1 text-sm">
                                            <div className="flex justify-between"><dt className="text-gray-600">DOB:</dt><dd>{cand.ngay_sinh}</dd></div>
                                            <div className="flex justify-between"><dt className="text-gray-600">Gender:</dt><dd>{cand.gioi_tinh}</dd></div>
                                            <div className="flex justify-between"><dt className="text-gray-600">Address:</dt><dd className="text-right truncate max-w-[200px]" title={cand.dia_chi_hien_tai}>{cand.dia_chi_hien_tai}</dd></div>
                                            <div className="flex justify-between"><dt className="text-gray-600">Source:</dt><dd>{cand.nguon_ung_vien}</dd></div>
                                        </dl>
                                    </div>

                                    {/* Test Results */}
                                    <div>
                                        <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Test Results</h4>
                                        {cand.test_results?.length ? (
                                            <div className="space-y-2">
                                                {cand.test_results.map((test: any, i: number) => (
                                                    <div key={i} className="bg-gray-50 p-2 rounded text-sm">
                                                        <div className="font-medium text-gray-700">{test.test_name}</div>
                                                        <div className="flex justify-between text-xs text-gray-500 mt-1">
                                                            <span>Score: <span className="font-bold text-gray-900">{test.score}</span></span>
                                                            <span>{test.time}</span>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        ) : (
                                            <p className="text-sm text-gray-400 italic">No test results available.</p>
                                        )}
                                    </div>
                                </div>

                                {/* Reviews */}
                                {cand.reviews?.length > 0 && (
                                    <div className="p-4 border-t border-gray-100">
                                        <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Reviews</h4>
                                        <div className="space-y-3">
                                            {cand.reviews.map((review: any, rIdx: number) => (
                                                <div key={rIdx} className="bg-yellow-50 p-3 rounded-r-lg border-l-2 border-yellow-400">
                                                    <div className="flex justify-between items-center mb-1">
                                                        <span className="font-bold text-gray-800 text-sm">{review.name}</span>
                                                        <span className="text-xs text-gray-500">{review.title}</span>
                                                    </div>
                                                    <p className="text-sm text-gray-700 whitespace-pre-wrap">{review.content}</p>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            ))}
        </div>
    );
};

export default CandidateDetail;
