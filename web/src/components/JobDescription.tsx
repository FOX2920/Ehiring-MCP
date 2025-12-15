import React from 'react';

const JobDescription = ({ data }: { data: any }) => {
    if (!data || !data.job_description) {
        // Check if we have a list of openings instead (from "not found" fallback)
        if (data.openings) {
            return (
                <div className="p-4">
                    <h2 className="text-xl font-bold mb-4 text-red-600">{data.message || "Job Description Not Found"}</h2>
                    <p className="mb-2">Did you mean one of these active openings?</p>
                    <ul className="list-disc pl-5">
                        {data.openings.map((op: any) => (
                            <li key={op.id} className="mb-1">
                                <span className="font-medium">{op.name}</span> (ID: {op.id})
                            </li>
                        ))}
                    </ul>
                </div>
            );
        }
        return <div className="p-4 text-red-500">{data.message || "No job description data available."}</div>;
    }

    return (
        <div className="p-6 bg-white rounded-lg shadow-md max-w-4xl mx-auto">
            <h1 className="text-2xl font-bold mb-4 text-gray-800">{data.opening_name}</h1>
            <div className="mb-4 text-sm text-gray-500">
                <span className="mr-4">ID: {data.opening_id}</span>
                {data.stages && (
                    <span>Stages: {data.stages.join(' → ')}</span>
                )}
            </div>

            <div className="prose max-w-none">
                <h3 className="text-lg font-semibold mb-2 text-gray-700">Job Description</h3>
                <div className="whitespace-pre-wrap text-gray-600 bg-gray-50 p-4 rounded border border-gray-200">
                    {data.job_description}
                </div>
            </div>
        </div>
    );
};

export default JobDescription;
