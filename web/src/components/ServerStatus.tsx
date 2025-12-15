import React from 'react';

const ServerStatus = ({ data }: { data: any }) => {
    return (
        <div className="p-6 bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col items-center justify-center text-center">
            <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mb-4 text-3xl">
                ✓
            </div>
            <h2 className="text-xl font-bold text-gray-800 mb-2">{data.server || "Base Hiring MCP"}</h2>
            <p className="text-gray-500 mb-4">Version: <span className="font-mono bg-gray-100 px-2 py-0.5 rounded">{data.version}</span></p>
            <div className="flex items-center gap-2 px-4 py-2 bg-green-50 text-green-700 rounded-full border border-green-200">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                <span className="text-sm font-medium uppercase tracking-wide">{data.status}</span>
            </div>
        </div>
    );
};

export default ServerStatus;
