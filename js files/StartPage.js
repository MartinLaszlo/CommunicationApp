import axios from 'axios';
import React, { useEffect, useState } from 'react';
import Chat from './Chat';
import Algorithm from './Algorithm';

const StartPage = () => {
  const [user, setUser] = useState({});
  const [program, setProgram] = useState(null);
  const [modules, setModules] = useState([]);
  const [selectedModuleId, setSelectedModuleId] = useState(null);
  const [channels, setChannels] = useState([]);
  const [selectedChannelId, setSelectedChannelId] = useState(null);

  const API_BASE_URL = 'http://localhost:5000';

  const ApiService = {
    getPrograms: () => axios.get(`${API_BASE_URL}/programs`),
    getModulesByProgramId: (programId) => axios.get(`${API_BASE_URL}/programs/${programId}/modules`).then(response => response.data),
    getChannelsByModuleId: (moduleId, userId, userRole) => axios.get(`${API_BASE_URL}/modules/${moduleId}/channels`, { params: { user_id: userId, user_role: userRole } }),
    getAllUsers: () => axios.get(`${API_BASE_URL}/users`).then(response => response.data),
  };

  useEffect(() => {
    const loggedInUser = JSON.parse(localStorage.getItem('user'));
    setUser(loggedInUser);
    // Get user's program
    if (loggedInUser?.program_ID) {
      ApiService.getPrograms().then(response => {
        const userProgram = response.data.find(p => p.program_ID === loggedInUser.program_ID);
        setProgram(userProgram);
      }).catch(error => console.error('Failed to fetch programs', error));
      // Get program's modules
      ApiService.getModulesByProgramId(loggedInUser.program_ID)
        .then(data => {
          setModules(data);
        })
        .catch(error => console.error('Error fetching modules:', error));
    }
  }, []);

  // Get channels for each module
  useEffect(() => {
    if (selectedModuleId && user.id && user.role) {
      ApiService.getChannelsByModuleId(selectedModuleId, user.id, user.role)
        .then(response => {
          setChannels(response.data || []);  
        })
        .catch(error => {
          console.error('Error fetching channels:', error);
          setChannels([]);
        });
    }
  }, [selectedModuleId, user.id, user.role]); 

  const handleModuleClick = moduleId => {
    setSelectedModuleId(moduleId);
    setSelectedChannelId(null); // Reset channel selection when switching modules
  };

  const handleChannelSelection = e => {
    setSelectedChannelId(e.target.value);
  };

  // Channels dropdwon menu
  const renderChannelsDropdown = () => (
    <select onChange={handleChannelSelection} value={selectedChannelId || ''} className='p-2 rounded-3xl w-full border border-accent border-2 bg-tertiary text-center text-text text-lg'>
      <option value="" >Select a Channel</option>
      {channels.map(channel => (
        <option key={channel.channel_ID} value={channel.channel_ID}>
          {channel.channel_name}
        </option>
      ))}
    </select>
  );

  return (
    <div className='grid grid-cols-12 pl-12 gap-7 p-4 h-[calc(100vh)] bg-gradient-to-b from-background to-background-secondary'>
      <div className='col-start-2 col-span-3 m-0 p-4 flex flex-col text-text bg-primary shadow-lg rounded-3xl overflow-hidden'>
        <h1 className="bg-tertiary text-lg font-bold text-text shadow-2xl rounded-3xl px-8 pt-6 pb-8 mb-4 border border-2 border-accent"> 
          Logged in as [{user.role === 'staff' ? 'Staff' : 'Student'}] {user.name}
          {program && <h2>Program: {program.program_name}</h2>}
        </h1>
        <div className='text-center text-2xl mt-3 font-bold mb-4'>Modules</div>
        <div className='bg-tertiary overflow-y-auto border-2 rounded-3xl border-accent text-white' style={{ maxHeight: '250px' }}>
          {modules.map(module => (
            <button
              key={module.module_ID}
              onClick={() => handleModuleClick(module.module_ID)}
              className='text-lg active:bg-button-sec active:text-black focus:bg-button-sec focus:text-black z-50 shadow-lg my-2 py-1 px-3 flex items-center justify-center bg-secondary hover:bg-white hover:text-black rounded-full transition-all duration-200 ease-linear cursor-pointer'
              style={{ margin: '10px auto', width: '95%' }}>
              {module.module_name}
            </button>
          ))}
        </div>
        {selectedModuleId && <div className='mt-4 text-center'>{renderChannelsDropdown()}</div>}
        {selectedModuleId && user.role !== 'staff' && <Algorithm moduleId={selectedModuleId} studentId={user.id}/>}
      </div>
      <div className='col-start-5 col-span-8 m-0 flex flex-col text-white gap-7 mr-6 text-text'>
        <div className='bg-primary h-1/8 flex items-center justify-center p-4 rounded-3xl text-text'>
          <h1 className='text-5xl font-bold'>
            <a style={{ textDecoration: 'none', color: 'var(--color-text)'}}>{selectedChannelId ? channels.find(ch => ch.channel_ID.toString() === selectedChannelId)?.channel_name : 'Select a channel'} 
            </a>
          </h1>
        </div>
        <div className='bg-primary h-full rounded-3xl overflow-y-auto p-4 text-text'>
          {selectedChannelId ? (
            <Chat channelId={selectedChannelId} />
          ) : (
            <div className='text-center text-text text-2xl font-bold'>Select a module and a channel to view chat</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StartPage;
