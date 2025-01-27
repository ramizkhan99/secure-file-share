import React from 'react';
import { Dialog, DialogTrigger, DialogContent, DialogTitle, DialogDescription, DialogClose } from '@radix-ui/react-dialog';
import { useAppDispatch } from '@/store';
import { fetchFiles } from '@/store/slices/file.slice';
import { Api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Trash2Icon } from 'lucide-react';

interface DeleteFileDialogProps {
    fileId: number;
    fileName: string;
}

export const DeleteFileDialog: React.FC<DeleteFileDialogProps> = ({ fileId, fileName }) => {
    const dispatch = useAppDispatch();

    const handleFileDelete = async () => {
        try {
            await Api.delete(`files/?id=${fileId}`, {
                withCredentials: true,
            });
            dispatch(fetchFiles());
        } catch (error) {
            console.error('Error deleting file:', error);
        }
    };

    return (
        <Dialog>
            <DialogTrigger asChild>
                <Button variant="ghost" size="icon" className="hover:bg-transparent">
                    <Trash2Icon className="w-4 h-4 text-red-500 hover:text-red-400" />
                </Button>
            </DialogTrigger>
            <DialogContent className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
                <div className="bg-gray-800 p-6 rounded-lg shadow-lg max-w-md w-full">
                    <DialogTitle className="text-lg font-semibold text-white">Delete File</DialogTitle>
                    <DialogDescription className="mt-2 text-sm text-gray-400">
                        Are you sure you want to delete the file "{fileName}"? This action cannot be undone.
                    </DialogDescription>
                    <div className="mt-4 flex justify-end space-x-2">
                        <DialogClose asChild>
                            <Button variant="ghost" className="text-white hover:bg-gray-700">Cancel</Button>
                        </DialogClose>
                        <Button onClick={handleFileDelete} variant="destructive">Delete</Button>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
};