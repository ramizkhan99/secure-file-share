import { Dialog, DialogTrigger, DialogContent, DialogTitle, DialogDescription, DialogClose } from '@radix-ui/react-dialog';
import { Button } from '../../ui/button';
import React, { useState, useEffect, useRef } from 'react';
import { useToast } from '@/hooks/use-toast';
import { Api } from '@/lib/api';
import localForage from 'localforage';

interface ViewFileDialogProps {
    fileId: number;
    fileName: string;
}

export const ViewFileDialog: React.FC<ViewFileDialogProps> = ({ fileId, fileName }) => {
    const [fileData, setFileData] = useState<{ content: string; type: string } | null>(null);
    const [dialogOpen, setDialogOpen] = useState(false);
    const { toast } = useToast();
    const iframeRef = useRef<HTMLIFrameElement>(null);

    useEffect(() => {
        const cacheKey = `file-${fileId}`;

        const fetchFileData = async () => {
            try {
                const response = await Api.get(`files?id=${fileId}`, {
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

                    setDialogOpen(true);
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

        if (dialogOpen) {
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
        }

        return () => {
            if (fileData) {
                URL.revokeObjectURL(fileData.content);
            }
        };
    }, [dialogOpen, fileId, toast]); // Added toast to the dependency array

    const handleOpen = async () => {
        setDialogOpen(true);
    };

    const handleClose = () => {
        setDialogOpen(false);
        setFileData(null);
    };

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
              ${fileData.type.startsWith('image/') ? `<img src="${fileData.content}" alt="${fileName}" />` : ''}
              ${fileData.type === 'application/pdf' ? `<embed src="${fileData.content}" type="application/pdf" width="100%" height="100%" />` : ''}
              ${fileData.type.startsWith('video/') ? `<video controls width="100%"><source src="${fileData.content}" type="${fileData.type}">Your browser does not support the video tag.</video>` : ''}
              ${fileData.type.startsWith('audio/') ? `<audio controls><source src="${fileData.content}" type="${fileData.type}">Your browser does not support the audio element.</audio>` : ''}
              ${!['image/', 'application/pdf', 'video/', 'audio/'].some(prefix => fileData.type.startsWith(prefix)) ? `<div>Unsupported file type. <a href="${fileData.content}" download="${fileName}">Download</a></div>` : ''}
            </div>
          </body>
        </html>
      `;
        }
    }, [fileData, fileName]); // Added fileName to dependency array

    return (
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
                <Button onClick={handleOpen} className="bg-blue-500 text-white hover:bg-blue-600">
                    View File
                </Button>
            </DialogTrigger>
            <DialogContent className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-20">
                <div className="bg-gray-800 p-6 rounded-lg shadow-lg max-w-3xl w-full h-full flex flex-col">
                    <DialogTitle className="text-lg font-semibold text-white">View File</DialogTitle>
                    <DialogDescription className="mt-2 text-sm text-gray-400">
                        {fileName}
                    </DialogDescription>
                    <div className="flex-grow mt-4 overflow-auto">
                        <iframe ref={iframeRef} className="w-full h-full" />
                    </div>
                    <div className="mt-4 flex justify-end">
                        <DialogClose asChild>
                            <Button onClick={handleClose} className="bg-gray-600 text-white hover:bg-gray-700 mr-2">Close</Button>
                        </DialogClose>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
};