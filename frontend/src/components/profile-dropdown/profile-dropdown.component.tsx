import React, { useEffect } from 'react';
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem } from '@radix-ui/react-dropdown-menu';
import { UserIcon, LogOutIcon, SettingsIcon } from 'lucide-react';
import { useAppDispatch, useAppSelector } from "@/store";
import { logoutUser } from "@/store/slices/user.slice";
import { useToast } from '@/hooks/use-toast';
import { useNavigate } from 'react-router-dom';

const ProfileDropdown: React.FC = () => {
    const dispatch = useAppDispatch();
    const { toast } = useToast();
    const { isLogoutSuccess } = useAppSelector((state) => state.user)
    const navigate = useNavigate();

    const handleLogout = () => {
        dispatch(logoutUser());
    };

    useEffect(() => {
        if (isLogoutSuccess) {
            toast({
                title: 'Logged Out Successfully!'
            });
            navigate('/');
        }
    }, [isLogoutSuccess, toast, navigate]);

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <UserIcon className="w-6 h-6 mr-16 cursor-pointer" />
            </DropdownMenuTrigger>
            <DropdownMenuContent className="bg-gray-800 text-white rounded-md shadow-lg mt-2 w-48">
                <DropdownMenuItem className="flex items-center space-x-2 p-2 hover:bg-gray-700 rounded-md transition-colors duration-200">
                    <SettingsIcon className="w-4 h-4" />
                    <span>Settings</span>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleLogout} className="flex items-center space-x-2 p-2 hover:bg-gray-700 rounded-md transition-colors duration-200">
                    <LogOutIcon className="w-4 h-4" />
                    <span>Logout</span>
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    );
};

export default ProfileDropdown;