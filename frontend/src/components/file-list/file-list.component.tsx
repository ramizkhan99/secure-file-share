import { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '@/store';
import { fetchFiles } from '@/store/slices/file.slice';
import { DownloadIcon } from 'lucide-react';
import { Api } from '@/lib/api';
import { DeleteFileDialog, UploadFileDialog, ShareFileDialog, ViewFileDialog } from '../dialogs';
import { DataTable } from '@/components/ui/data-table';
import { Button } from '@/components/ui/button';

interface File {
    id: number;
    filename: string;
    uploaded_at: string;
    size: number;
    type: string;
    owner?: string;
}

export function FileList() {
    const dispatch = useAppDispatch();
    const { files, isPending, error } = useAppSelector((state) => state.file);

    useEffect(() => {
        dispatch(fetchFiles());
    }, [dispatch]);

    async function handleFileDownload(id: number, filename: string) {
        try {
            const response = await Api.get(`files?id=${id}`, {
                withCredentials: true,
                responseType: 'blob',
            });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error('Error downloading file:', error);
        }
    }

    function bytesToSize(bytes: number) {
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        if (bytes === 0) return 'n/a';
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        if (i === 0) return `${bytes} ${sizes[i]}`;
        return `${(bytes / (1024 ** i)).toFixed(1)} ${sizes[i]}`;
    }

    const columns = [
        {
            header: "Name",
            accessorKey: "filename" as keyof File,
        },
        {
            header: "Size",
            accessorKey: "size" as keyof File,
            cell: (file: File) => bytesToSize(file.size),
        },
        {
            header: "Type",
            accessorKey: "type" as keyof File,
        },
        {
            header: "Owner",
            accessorKey: "owner" as keyof File,
        },
        {
            header: "Actions",
            headerClasses: "text-center",
            accessorKey: "id" as keyof File,
            cell: (file: File) => (
                <div className="flex items-center justify-center space-x-2">
                    <Button
                        variant="ghost"
                        size="icon"
                        className="hover:bg-transparent"
                        onClick={() => handleFileDownload(file.id, file.filename)}
                    >
                        <DownloadIcon className="w-4 h-4 text-blue-500 hover:text-blue-400" />
                    </Button>
                    <ShareFileDialog fileId={file.id} fileName={file.filename} />
                    <DeleteFileDialog fileId={file.id} fileName={file.filename} />
                    <ViewFileDialog fileId={file.id} fileName={file.filename} />
                </div>
            ),
        },
    ];

    return (
        <div className="container mx-auto py-10">
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold">Files</h2>
                <UploadFileDialog />
            </div>
            <DataTable
                data={files}
                columns={columns}
                isLoading={isPending}
                error={error}
            />
        </div>
    );
}