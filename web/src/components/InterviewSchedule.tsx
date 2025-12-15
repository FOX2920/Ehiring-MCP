import React from 'react';
import { Interview } from '../types';

const InterviewSchedule = ({ data }: { data: any }) => {
    const interviews: Interview[] = data.interviews || [];

    if (!interviews.length) {
        return <div className="p-4 text-gray-500">No interviews found.</div>;
    }

    // Sort interviews by date/time
    const sortedInterviews = [...interviews].sort((a, b) =>
        new Date(a.time_dt).getTime() - new Date(b.time_dt).getTime()
    );

    return (
        <div className="p-4">
            <h2 className="text-2xl font-bold mb-4 text-gray-800">Interview Schedule</h2>
            <div className="overflow-x-auto">
                <table className="min-w-full bg-white border border-gray-200 shadow-sm rounded-lg overflow-hidden">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="py-3 px-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Time</th>
                            <th className="py-3 px-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Candidate</th>
                            <th className="py-3 px-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Position</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                        {sortedInterviews.map((interview) => {
                            const date = new Date(interview.time_dt);
                            const dateStr = date.toLocaleDateString('vi-VN', { weekday: 'short', day: '2-digit', month: '2-digit' });
                            const timeStr = date.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });

                            return (
                                <tr key={interview.id} className="hover:bg-gray-50 transition-colors">
                                    <td className="py-3 px-4 whitespace-nowrap">
                                        <div className="text-sm font-bold text-gray-900">{timeStr}</div>
                                        <div className="text-xs text-gray-500">{dateStr}</div>
                                    </td>
                                    <td className="py-3 px-4 whitespace-nowrap">
                                        <div className="text-sm font-medium text-blue-600">{interview.candidate_name}</div>
                                    </td>
                                    <td className="py-3 px-4">
                                        <div className="text-sm text-gray-700 truncate max-w-[200px]" title={interview.opening_name}>{interview.opening_name}</div>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
            <div className="mt-4 text-sm text-gray-500 text-right">
                Total interviews: {interviews.length}
            </div>
        </div>
    );
};

export default InterviewSchedule;
