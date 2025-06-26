import React, { useEffect, useState } from 'react';
import io from 'socket.io-client';

const socket = io('http://localhost:5000');

const Algorithm = ({ studentId, moduleId }) => {
    const [isInQueue, setIsInQueue] = useState(false);
    const [groupStatus, setGroupStatus] = useState('Enter the queue if you are looking for a group. If you have already entered the queue previously and wish to exit it please click the button below twice.');

    useEffect(() => {
        // Setup socket listeners
        socket.on('group_formation_results', data => {
            if (data.module_ID === moduleId) {
                const foundGroup = data.groups.find(group => group.group.some(member => parseInt(member.studentId) === studentId));
                if (foundGroup) {
                    setIsInQueue(false); // Automatically update when in a group
                    setGroupStatus(`You are in a group. Group ID: ${foundGroup.group_id}`);
                }
            }
        });

        return () => {
            socket.off('group_formation_results');
        };
    }, [studentId, moduleId]);

    // Put user in the queue and tell them
    const enterQueue = () => {
        setIsInQueue(true);
        setGroupStatus('You are in the queue. Please check this page later to see if you are in a new group. If you wish to exit click the button below.');
        socket.emit('join_group_queue', { student_ID: studentId, module_ID: moduleId });
    };

    // Put user OUT of the queue and tell them
    const exitQueue = () => {
        if (isInQueue) {
            setIsInQueue(false);
            setGroupStatus('You have exited the queue. Enter again if you wish.');
            socket.emit('leave_group_queue', { student_ID: studentId, module_ID: moduleId });
        }
    };    

    // Group formation panel
    return (
        <div className='p-4 bg-tertiary rounded-3xl shadow mt-4 border border-2 border-accent'>
            <h2 className='text-2xl font-bold mb-2 text-text'>Group Formation Panel</h2>
            <p className='text-lg font-bold mb-2 text-info-txt'>{groupStatus}</p>
            <button
                className={`py-2 px-4 text-white rounded-3xl mb-4 ${isInQueue ? 'bg-red-500 hover:bg-white hover:text-black transition-all duration-200 ease-linear' : 'bg-accent hover:bg-white hover:text-black transition-all duration-200 ease-linear'}`}
                onClick={isInQueue ? exitQueue : enterQueue}>
                {isInQueue ? 'Exit Queue' : 'Enter Queue'}
            </button>
        </div>
    );
};

export default Algorithm;
