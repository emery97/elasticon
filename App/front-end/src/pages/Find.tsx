import React from 'react';
import PersonSearch from '../components/Find/PersonSearch';

const Credits: React.FC = () => {
  return (
    <>
    <div className="rounded-sm border border-stroke bg-white p-4 shadow-default dark:border-strokedark dark:bg-boxdark w-full h-full flex flex-col cursor-pointer">
      <div className="flex flex-col flex-grow">
        <PersonSearch></PersonSearch>
      </div>
    </div>
    </>
  );
};

export default Credits;
