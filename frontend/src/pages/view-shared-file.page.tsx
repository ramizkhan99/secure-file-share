import React, { useEffect, useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { Api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import localForage from 'localforage';
import { Button } from '@/components/ui/button';

const ViewSharedFilePage: React.FC = () => {
    const { shareId } = useParams<{ shareId: string }>();
    const [fileData, setFileData] = useState<{ content: string; type: string } | null>(null);
    const { toast } = useToast();
    const iframeRef = useRef<HTMLIFrameElement>(null);

    useEffect(() => {
        const cacheKey = `shared-file-${shareId}`;

        const fetchFileData = async () => {
            try {
                const response = await Api.get(`files/shared/${shareId}`, {
                    withCredentials: true,
                    responseType: 'blob',
                });

                const reader = new FileReader();
                reader.onload = () => {
                    const newFileData = {
                        content: reader.result as string,
                        type: response.headers['content-type'],
                    };
                    setFileData(newFileData);

                    // Cache the data in IndexedDB (using localForage)
                    localForage.setItem(cacheKey, newFileData).catch((err) => {
                        console.error('Error caching file data:', err);
                    });
                };
                reader.onerror = () => {
                    toast({
                        title: 'Error processing file',
                        description: 'Failed to convert file to a viewable format.',
                        variant: 'destructive',
                    });
                };
                reader.readAsDataURL(response.data);
            } catch (error: unknown) {
                toast({
                    title: 'Error viewing file',
                    description: (error instanceof Error) ? error.message : 'An unknown error occurred',
                    variant: 'destructive',
                });
            }
        };

        // Check IndexedDB for cached data
        localForage.getItem(cacheKey).then((cachedData: unknown) => {
            if (cachedData) {
                setFileData(cachedData as { content: string; type: string });
            } else {
                fetchFileData();
            }
        }).catch((err: unknown) => {
            console.error('Error retrieving cached data:', err);
            fetchFileData(); // Fetch the file if there's an error with IndexedDB
        });

        return () => {
            if (fileData) {
                URL.revokeObjectURL(fileData.content);
            }
        };
    }, [shareId, toast]); // Added toast to the dependency array

    useEffect(() => {
        if (fileData && iframeRef.current) {
            iframeRef.current.srcdoc = `
        <html>
          <head>
            <style>
              body { margin: 0; overflow: hidden; }
              .document-container { width: 100%; height: 100vh; display: flex; justify-content: center; align-items: center; }
              .document-container > * { max-width: 100%; max-height: 100%; }
            </style>
          </head>
          <body>
            <div class="document-container">
              ${fileData.type.startsWith('image/') ? `<img src="${fileData.content}" alt="Shared File" />` : ''}
              ${fileData.type === 'application/pdf' ? `<embed src="${fileData.content}" type="application/pdf" width="100%" height="100%" />` : ''}
              ${fileData.type.startsWith('video/') ? `<video controls width="100%"><source src="${fileData.content}" type="${fileData.type}">Your browser does not support the video tag.</video>` : ''}
              ${fileData.type.startsWith('audio/') ? `<audio controls><source src="${fileData.content}" type="${fileData.type}">Your browser does not support the audio element.</audio>` : ''}
              ${!['image/', 'application/pdf', 'video/', 'audio/'].some(prefix => fileData.type.startsWith(prefix)) ? `<div>Unsupported file type.</div>` : ''}
            </div>
          </body>
        </html>
      `;
        }
    }, [fileData]); // Added fileData to dependency array

    return (
        <div className="flex flex-col items-center justify-center min-h-screen p-4">
            <h1 className="text-2xl font-bold mb-4">View Shared File</h1>
            <div className="flex-grow mt-4 overflow-auto w-full">
                <iframe ref={iframeRef} className="w-full h-full doc-viewer" style={{ minHeight: '80vh' }} />
            </div>
            <div className="mt-4 flex justify-end">
                <Button onClick={() => window.history.back()} className="bg-gray-600 text-white hover:bg-gray-700 mr-2">Back</Button>
            </div>
        </div>
    );
};

export { ViewSharedFilePage };