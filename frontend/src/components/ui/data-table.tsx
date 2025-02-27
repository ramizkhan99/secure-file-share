import React from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

interface Column<T> {
    header: string;
    accessorKey: keyof T;
    additionalClass?: string;
    headerClasses?: string;
    cell?: (item: T) => React.ReactNode;
}

interface DataTableProps<T> {
    data: T[];
    columns: Column<T>[];
    isLoading?: boolean;
    error?: string;
}

export function DataTable<T>({ data, columns, isLoading, error }: DataTableProps<T>) {
    if (isLoading) {
        return <div className="text-center py-4">Loading...</div>;
    }

    if (error) {
        return <div className="text-red-500 text-center py-4">Error: {error}</div>;
    }

    return (
        <div className="rounded-md border">
            <Table>
                <TableHeader>
                    <TableRow>
                        {columns.map((column) => (
                            <TableHead key={String(column.accessorKey)} className={column.headerClasses}>
                                {column.header}
                            </TableHead>
                        ))}
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {data.map((item, rowIndex) => (
                        <TableRow key={rowIndex}>
                            {columns.map((column) => (
                                <TableCell key={String(column.accessorKey)} className={column.additionalClass}>
                                    {column.cell ? column.cell(item) : String(item[column.accessorKey])}
                                </TableCell>
                            ))}
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    );
}