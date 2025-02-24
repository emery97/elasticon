import React from 'react';

const Credits: React.FC = () => {
  return (
    <>
    <div className="rounded-sm border border-stroke bg-white p-4 shadow-default dark:border-strokedark dark:bg-boxdark w-full h-full flex flex-col cursor-pointer">
      <div className="flex flex-col flex-grow">
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
          Missing Person Finder. Want to find traces of a missing person on the internet? Just enter their name and we will use elasticsearch to return any results found!
        </p>

        <div className="flex justify-between w-full mb-1 mt-5">
          <h4 className="text-title-md font-bold text-black dark:text-white">
            Credits
          </h4>
        </div>
        <h6 className="text-md font-bold text-black dark:text-white">
          This project was developed using the following technologies:
        </h6>
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
          <a href="https://tailadmin.com/react" target="_blank" rel="noopener" className="text-primary dark:text-white underline placeholder:underline">TailAdmin React Admin Template</a> - A modern admin dashboard template that is built with React, Tailwind CSS, and Redux.
        </p>
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
          <a href="https://reactjs.org/" target="_blank" rel="noopener" className="text-primary dark:text-white underline placeholder:underline">React.js</a> - A JavaScript library for building user interfaces.
        </p>
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
          <a href="https://nodejs.org/" target="_blank" rel="noopener" className="text-primary dark:text-white underline placeholder:underline">Node.js</a> - A JavaScript runtime built on Chrome's V8 JavaScript engine.
        </p>
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
          <a href="https://expressjs.com/" target="_blank" rel="noopener" className="text-primary dark:text-white underline placeholder:underline">Express.js</a> - A minimal and flexible Node.js web application framework.
        </p>
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
          <a href="https://www.mongodb.com/cloud/atlas" target="_blank" rel="noopener" className="text-primary dark:text-white underline placeholder:underline">MongoDB Atlas</a> - A fully-managed cloud database service.
        </p>
      </div>
    </div>
    </>
  );
};

export default Credits;
