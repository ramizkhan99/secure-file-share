import Navbar from '@/components/navbar/navbar';
import { UsersList } from '@/components/users-list/users-list.component';
import { useAppSelector } from '@/store';
import { selectIsAdmin } from '@/store/slices/user.slice';
import { Navigate } from 'react-router-dom';

export function UsersPage() {
    const isAdmin = useAppSelector(selectIsAdmin);

    if (!isAdmin) {
        return <Navigate to="/home" replace />;
    }

    return (
        <>
            <Navbar />
            <div className="users-page">
                <UsersList />
            </div>
        </>
    );
} 