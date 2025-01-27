import { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '@/store';
import { fetchUsers } from '@/store/slices/users-list.slice';
import { Badge } from '@/components/ui/badge';
import { DataTable } from '@/components/ui/data-table';

interface User {
    username: string;
    email: string;
    role: "admin" | "user";
    isMFAEnabled: boolean;
}

export function UsersList() {
    const dispatch = useAppDispatch();
    const { users, isPending, error } = useAppSelector((state) => state.usersList);

    useEffect(() => {
        dispatch(fetchUsers());
    }, [dispatch]);

    const columns = [
        {
            header: "Username",
            accessorKey: "username" as keyof User,
        },
        {
            header: "Email",
            accessorKey: "email" as keyof User,
        },
        {
            header: "Role",
            accessorKey: "role" as keyof User,
            cell: (user: User) => (
                <Badge variant={user.role === 'admin' ? 'default' : 'secondary'}>
                    {user.role}
                </Badge>
            ),
        },
        {
            header: "MFA Status",
            accessorKey: "isMFAEnabled" as keyof User,
            cell: (user: User) => (
                <Badge variant={user.isMFAEnabled ? 'success' : 'destructive'}>
                    {user.isMFAEnabled ? 'Enabled' : 'Disabled'}
                </Badge>
            ),
        },
    ];

    return (
        <div className="container mx-auto py-10">
            <h2 className="text-2xl font-bold mb-4">Users</h2>
            <DataTable
                data={users}
                columns={columns}
                isLoading={isPending}
                error={error}
            />
        </div>
    );
} 