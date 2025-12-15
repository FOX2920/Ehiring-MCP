import React from 'react';
import { createRoot } from 'react-dom/client';
import JobDescription from './components/JobDescription';
import CandidateList from './components/CandidateList';
import InterviewSchedule from './components/InterviewSchedule';
import CandidateDetail from './components/CandidateDetail';
import OfferLetter from './components/OfferLetter';
import ServerStatus from './components/ServerStatus';
import FeedbackData from './components/FeedbackData';
import './index.css';

const App = () => {
    // Read tool output from window.openai
    const toolOutput = window.openai?.toolOutput;

    if (!toolOutput) {
        return (
            <div className="p-4 flex items-center justify-center h-full text-gray-500">
                Waiting for data...
            </div>
        );
    }

    // Determine which view to render based on the 'type' field in toolOutput
    switch (toolOutput.type) {
        case 'job_description':
            return <JobDescription data={toolOutput} />;
        case 'candidate_list':
            return <CandidateList data={toolOutput} />;
        case 'interview_schedule':
            return <InterviewSchedule data={toolOutput} />;
        case 'candidate_detail':
            return <CandidateDetail data={toolOutput} />;
        case 'offer_letter':
            return <OfferLetter data={toolOutput} />;
        case 'server_status':
            return <ServerStatus data={toolOutput} />;
        case 'feedback_data':
            return <FeedbackData data={toolOutput} />;
        default:
            return (
                <div className="p-4">
                    <h2 className="text-xl font-bold mb-2">Unknown Data Type</h2>
                    <pre className="bg-gray-100 p-4 rounded overflow-auto max-h-96 text-xs">
                        {JSON.stringify(toolOutput, null, 2)}
                    </pre>
                </div>
            );
    }
};

const container = document.getElementById('root');
if (container) {
    const root = createRoot(container);
    root.render(<App />);
}
