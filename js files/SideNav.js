import React from 'react';
import { ImExit } from "react-icons/im";
import { FaGear } from "react-icons/fa6";
import { IoChatbubbles } from "react-icons/io5";
import { RiTeamFill } from "react-icons/ri";

// Nav bar setup
const SideNav = ({ setPage, onLogout }) => {
  return (
    <div className="fixed z-50 h-screen w-40 m-0 flex flex-col bg-sidenav-primary shadow-xl">
      <SideNavIcon icon={<RiTeamFill size="48" />} setPage={setPage} pageValue={"start"} />
      <SideNavIcon icon={<IoChatbubbles size="48" />} setPage={setPage} pageValue={"direct"} />
      <SideNavIcon icon={<FaGear size="48" />} setPage={setPage} pageValue={"settings"} />
      <BottomLeftIcon icon={<ImExit size="48" />} onLogout={onLogout} />
    </div>
  );
};

// Nav bar icons setup
const SideNavIcon = ({ icon, setPage, pageValue }) => {
  return (
    <div onClick={() => setPage(pageValue)} className='flex rounded-full items-center justify-center h-20 w-20 mt-10 mb-2 mx-auto bg-tertiary text-accent shadow-lg hover:bg-white hover:text-black transition-all duration-200 ease-linear cursor-pointer'>
      {icon}
    </div>
  );
}

// Logout icon setup
const BottomLeftIcon = ({ icon, onLogout }) => {
  return (
    <div onClick={onLogout} className='fixed bottom-10 left-10 flex rounded-full items-center justify-center h-20 w-20 shadow-lg bg-tertiary text-accent hover:bg-white hover:text-red-500 transition-all duration-300 ease-linear cursor-pointer'>
      {icon}
    </div>
  );
}

export default SideNav;
