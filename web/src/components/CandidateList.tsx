import React from 'react';

const CandidateList = ({ data }: { data: any }) => {
    const candidates = data.candidates || [];

    if (!candidates.length) {
        return (
            <div className="p-4">
                <h2 className="text-xl font-bold mb-2">Candidates for {data.opening_name || "Unknown"}</h2>
                <p className="text-gray-500">{data.message || "No candidates found."}</p>
            </div>
        );
    }

    return (
        <div className="p-4">
            <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-800">Candidates</h2>
                <p className="text-gray-600">Position: <span className="font-semibold">{data.opening_name}</span> ({candidates.length})</p>
            </div>

            <div className="grid gap-4">
                {candidates.map((candidate: any) => (
                    <div key={candidate.id} className="bg-white p-4 rounded-lg shadow border border-gray-200 flex flex-col md:flex-row justify-between items-start md:items-center hover:bg-gray-50 transition-colors">
                        <div className="flex-1">
                            <h3 className="text-lg font-bold text-blue-600">{candidate.name}</h3>
                            <div className="text-sm text-gray-600 mt-1">
                                <p>📧 {candidate.email || "N/A"} • 📞 {candidate.phone || "N/A"}</p>
                                <p>Current Stage: <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">{candidate.stage_name || "Unknown"}</span></p>
                            </div>
                        </div>

                        <div className="mt-4 md:mt-0 flex gap-2">
                            {candidate.cv_url && (
                                <a
                                    href={candidate.cv_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 text-sm font-medium"
                                >
                                    View CV
                                </a>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default CandidateList;
