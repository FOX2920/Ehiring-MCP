import React, { useState } from 'react';

const FeedbackData = ({ data }: { data: any }) => {
    const [expandedQuestion, setExpandedQuestion] = useState<string | null>(null);

    if (!data.success || !data.data) {
        return <div className="p-4 text-red-500">{data.message || "No feedback data found."}</div>;
    }

    const questions = Object.keys(data.data);

    return (
        <div className="p-4">
            <h2 className="text-2xl font-bold mb-2 text-gray-800">Feedback Analysis</h2>
            <p className="text-gray-600 mb-6">{data.message}</p>

            <div className="space-y-4">
                {questions.map((question, idx) => {
                    const answers = data.data[question];
                    const candidateNames = Object.keys(answers);
                    const isExpanded = expandedQuestion === question;

                    return (
                        <div key={idx} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                            <button
                                onClick={() => setExpandedQuestion(isExpanded ? null : question)}
                                className="w-full text-left p-4 bg-gray-50 hover:bg-gray-100 transition-colors flex justify-between items-start"
                            >
                                <div className="font-semibold text-gray-800 pr-4">{question}</div>
                                <span className="text-xs font-medium bg-blue-100 text-blue-800 px-2 py-1 rounded-full whitespace-nowrap">
                                    {candidateNames.length} answers
                                </span>
                            </button>

                            {isExpanded && (
                                <div className="divide-y divide-gray-100">
                                    {candidateNames.map((name, cIdx) => (
                                        <div key={cIdx} className="p-4 hover:bg-amber-50/30">
                                            <div className="text-sm font-bold text-gray-700 mb-1">{name}</div>
                                            <div className="text-gray-600 text-sm italic border-l-2 border-gray-300 pl-3">
                                                "{answers[name]}"
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default FeedbackData;
