import { Dialog, DialogTrigger, DialogContent, DialogTitle, DialogDescription, DialogClose } from '@radix-ui/react-dialog';
import { Button } from '../../ui/button';
import React, { useState } from 'react';
import { useToast } from '@/hooks/use-toast';
import { useAppDispatch } from '@/store';
import { fetchFiles } from '@/store/slices';
import { Api } from '@/lib/api';

export const UploadFileDialog: React.FC = () => {
    const [file, setFile] = useState<File | null>(null);
    const [dialogOpen, setDialogOpen] = useState(false);
    const { toast } = useToast();
    const dispatch = useAppDispatch();

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files && event.target.files.length > 0) {
            setFile(event.target.files[0]);
        }
    };

    const handleClose = () => {
        setDialogOpen(false);
        dispatch(fetchFiles());
    }

    const handleFileUpload = async (event: React.FormEvent) => {
        event.preventDefault();
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await Api.post('files', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
                withCredentials: true,
            });
            if (response.status === 201) {
                toast({
                    title: 'File uploaded successfully.',
                });
                handleClose();
            }
        } catch (error) {
            if (error) {
                toast({
                    title: 'An error occurred while uploading the file.',
                    variant: 'destructive',
                });
            }
        }
    };

    return (
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
                <Button className="bg-blue-500 text-white hover:bg-blue-600">
                    Upload file
                </Button>
            </DialogTrigger>
            <DialogContent className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-20">
                <div className="bg-gray-800 p-6 rounded-lg shadow-lg max-w-md w-full">
                    <DialogTitle className="text-lg font-semibold text-white">Upload File</DialogTitle>
                    <DialogDescription className="mt-2 text-sm text-gray-400">
                        Select a file to upload.
                    </DialogDescription>
                    <form className="mt-4" onSubmit={handleFileUpload}>
                        <input type="file" onChange={handleFileChange} className="block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-gray-700 file:text-gray-300 hover:file:bg-gray-600" />
                        <div className="mt-4 flex justify-end">
                            <DialogClose asChild>
                                <Button className="bg-gray-600 text-white hover:bg-gray-700 mr-2">Cancel</Button>
                            </DialogClose>
                            <Button type="submit" className="bg-blue-500 text-white hover:bg-blue-600">Upload</Button>
                        </div>
                    </form>
                </div>
            </DialogContent>
        </Dialog>
    );
};