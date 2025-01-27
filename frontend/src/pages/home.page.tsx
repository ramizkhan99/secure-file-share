import { FileList } from '@/components/file-list';
import Navbar from '@/components/navbar/navbar';
import React from 'react';

const HomePage: React.FC = () => {
    return (
        <div className="min-h-screen min-w-full">
            <Navbar />
            <div className="container mx-auto mt-8">
                <FileList />
            </div>
        </div>
    );
};

export { HomePage };
