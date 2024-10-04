<script setup lang="ts" generic="TData, TValue">
import { getColumns } from '@/components/user_list/columns'; // Import getColumns instead of columns
import {
    FlexRender,
    getCoreRowModel,
    useVueTable,
} from '@tanstack/vue-table';

import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';

const props = defineProps<{
    data: TData[];
    refreshData: () => void; // Received from the parent
}>();

const columns = getColumns(props.refreshData);

const table = useVueTable({
    get data() { return props.data },
    get columns() { return columns }, // Use dynamically created columns
    getCoreRowModel: getCoreRowModel(),
});
</script>

<template>
    <div class="flex flex-col items-center justify-center gap-y-4">
        <div class="flex w-full items-center">
            <h2 class="text-lg font-semibold mx-auto">Users</h2>
        </div>
        <Table class="border rounded-md border-collapse">
            <TableHeader>
                <TableRow v-for="headerGroup in table.getHeaderGroups()" :key="headerGroup.id">
                    <TableHead v-for="header in headerGroup.headers" :key="header.id" class="border">
                        <FlexRender v-if="!header.isPlaceholder" :render="header.column.columnDef.header"
                            :props="header.getContext()" />
                    </TableHead>
                </TableRow>
            </TableHeader>
            <TableBody>
                <template v-if="table.getRowModel().rows?.length">
                    <TableRow v-for="row in table.getRowModel().rows" :key="row.id"
                        :data-state="row.getIsSelected() ? 'selected' : undefined">
                        <TableCell v-for="cell in row.getVisibleCells()" :key="cell.id" class="border">
                            <FlexRender :render="cell.column.columnDef.cell" :props="cell.getContext()" />
                        </TableCell>
                    </TableRow>
                </template>
                <template v-else>
                    <TableRow>
                        <TableCell :colspan="columns.length" class="h-24 text-center">
                            No results.
                        </TableCell>
                    </TableRow>
                </template>
            </TableBody>
        </Table>
    </div>
</template>
