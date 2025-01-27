import { NavigationMenu, NavigationMenuList, NavigationMenuItem, NavigationMenuLink } from '@radix-ui/react-navigation-menu';
import React from 'react';
import { Link } from 'react-router-dom';
import { useAppSelector } from '@/store';
import { selectIsAdmin } from '@/store/slices/user.slice';
import ProfileDropdown from '@/components/profile-dropdown/profile-dropdown.component';

const Navbar: React.FC = () => {
    const isAdmin = useAppSelector(selectIsAdmin);

    return (
        <NavigationMenu className="w-full min-w-full top-0 left-0 bg-gray-900 bg-opacity-70 backdrop-blur-md shadow-md fixed">
            <NavigationMenuList className="flex justify-between items-center p-4">
                <div className="left flex items-center space-x-4">
                    <NavigationMenuItem>
                        <Link to="/home">
                            <NavigationMenuLink className="text-lg font-semibold text-white hover:text-gray-400">
                                Home
                            </NavigationMenuLink>
                        </Link>
                    </NavigationMenuItem>
                    {isAdmin && (
                        <>
                            <NavigationMenuItem>
                                <Link to="/users">
                                    <NavigationMenuLink className="text-lg font-semibold text-white hover:text-gray-400">
                                        Users
                                    </NavigationMenuLink>
                                </Link>
                            </NavigationMenuItem>
                            <NavigationMenuItem>
                                <Link to="/docs">
                                    <NavigationMenuLink className="text-lg font-semibold text-white hover:text-gray-400">
                                        Documentation
                                    </NavigationMenuLink>
                                </Link>
                            </NavigationMenuItem>
                        </>
                    )}
                </div>
                <div className="right flex items-center space-x-4">
                    <NavigationMenuItem>
                        <ProfileDropdown />
                    </NavigationMenuItem>
                </div>
            </NavigationMenuList>
        </NavigationMenu>
    );
};

export default Navbar;