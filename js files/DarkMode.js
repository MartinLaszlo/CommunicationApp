import React, { useState, useEffect } from 'react';
import "./DarkMode.css";

const DarkMode = () => {
    // Start theme based on localStorage or default to dark
    const [isDarkMode, setIsDarkMode] = useState(() => {
        const storedTheme = localStorage.getItem('theme');
        return storedTheme ? storedTheme === 'dark' : true;  // Default to dark mode
    });

    useEffect(() => {
        document.body.setAttribute('data-theme', isDarkMode ? 'dark' : 'light');
        localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    }, [isDarkMode]);

    // Function to switch theme
    const toggleTheme = () => {
        setIsDarkMode(!isDarkMode);
    };

    return (
        <div className='flex justify-center items-center'>
            <label htmlFor='darkmode-toggle' className='flex items-center cursor-pointer'>
                <div className='mr-3 font-medium'>Toggle Light/Dark Mode</div>
                <div className='relative'>
                    <input
                        type='checkbox'
                        id='darkmode-toggle'
                        className='sr-only' 
                        onChange={toggleTheme}
                        checked={!isDarkMode}
                    />
                    <div className={`w-10 h-4 bg-gray-400 rounded-full shadow-inner ${isDarkMode ? 'bg-gray-600' : 'bg-gray-400'}`}></div>
                    <div className={`dot absolute w-6 h-6 bg-white rounded-full shadow -left-1 -top-1 transition ${isDarkMode ? 'transform translate-x-full' : ''}`}></div>
                </div>
            </label>
        </div>
    );
};

export default DarkMode;
