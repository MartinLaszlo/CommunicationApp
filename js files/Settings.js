import React, { useState } from 'react';
import DarkMode from './DarkMode';

const Settings = () => {
  return (
    <div className='flex justify-center items-center h-screen'>
      <div className='bg-sidenav-primary rounded-3xl shadow-lg p-8 max-w-md'>
        <h2 className='text-3xl font-semibold mb-4'>Settings</h2>
        <div className='p-4 text-xl'>
          <DarkMode />
        </div>
      </div>
    </div>
  );
}

export default Settings;