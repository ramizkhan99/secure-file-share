import React, { useState } from 'react';
import { Dialog, DialogTrigger, DialogContent, DialogTitle, DialogDescription, DialogClose } from '@radix-ui/react-dialog';
import { Button } from '@/components/ui/button';
import { Share2Icon, CopyIcon, CheckIcon } from 'lucide-react';
import { Api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { Input } from '@/components/ui/input';

interface ShareFileDialogProps {
    fileId: number;
    fileName: string;
}

export const ShareFileDialog: React.FC<ShareFileDialogProps> = ({ fileId, fileName }) => {
    const [shareLink, setShareLink] = useState<string>('');
    const [copied, setCopied] = useState(false);
    const { toast } = useToast();

    const handleShare = async () => {
        try {
            const response = await Api.get(`files/share?id=${fileId}`, {
                withCredentials: true,
            });

            if (response.data.success) {
                const shareId = response.data.data.id;
                const fullLink = `${window.location.origin}/files/shared/${shareId}`;
                setShareLink(fullLink);
            }
        } catch (error) {
            console.error('Error sharing file:', error);
            toast({
                title: 'Error sharing file',
                variant: 'destructive',
            });
        }
    };

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(shareLink);
            setCopied(true);
            toast({
                title: 'Link copied to clipboard',
            });
            setTimeout(() => setCopied(false), 2000);
        } catch (error) {
            console.error('Error copying to clipboard:', error);
            toast({
                title: 'Failed to copy link',
                variant: 'destructive',
            });
        }
    };

    return (
        <Dialog>
            <DialogTrigger asChild>
                <Button variant="ghost" size="icon" className="hover:bg-transparent">
                    <Share2Icon className="w-4 h-4 text-green-500 hover:text-green-400" />
                </Button>
            </DialogTrigger>
            <DialogContent className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
                <div className="bg-gray-800 p-6 rounded-lg shadow-lg max-w-md w-full">
                    <DialogTitle className="text-lg font-semibold text-white">Share File</DialogTitle>
                    <DialogDescription className="mt-2 text-sm text-gray-400">
                        {shareLink ? 'Copy the link below to share the file:' : `Generate a shareable link for "${fileName}"`}
                    </DialogDescription>
                    
                    {!shareLink ? (
                        <div className="mt-4 flex justify-end space-x-2">
                            <DialogClose asChild>
                                <Button variant="ghost" className="text-white hover:bg-gray-700">
                                    Cancel
                                </Button>
                            </DialogClose>
                            <Button onClick={handleShare} variant="default">
                                Generate Link
                            </Button>
                        </div>
                    ) : (
                        <div className="mt-4 space-y-4">
                            <div className="flex space-x-2">
                                <Input
                                    value={shareLink}
                                    readOnly
                                    className="bg-gray-700 text-white border-gray-600"
                                />
                                <Button
                                    onClick={handleCopy}
                                    variant="outline"
                                    size="icon"
                                    className="shrink-0"
                                >
                                    {copied ? (
                                        <CheckIcon className="w-4 h-4 text-green-500" />
                                    ) : (
                                        <CopyIcon className="w-4 h-4" />
                                    )}
                                </Button>
                            </div>
                            <div className="flex justify-end">
                                <DialogClose asChild>
                                    <Button variant="ghost" className="text-white hover:bg-gray-700">
                                        Close
                                    </Button>
                                </DialogClose>
                            </div>
                        </div>
                    )}
                </div>
            </DialogContent>
        </Dialog>
    );
}; 