<script setup lang="ts" generic="TData, TValue">
import { getColumns } from '@/components/attempt_history_list/columns'; // Import getColumns instead of columns
import {
    FlexRender,
    getCoreRowModel,
    getFilteredRowModel,
    getSortedRowModel,
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
}>();

const columns = getColumns(props.refreshData);

const table = useVueTable({
    get data() { return props.data },
    get columns() { return columns }, // Use dynamically created columns
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
});
</script>

<template>
    <div class="flex flex-col items-left justify-center gap-y-4">
        <div class="items-left expand">
            <Input class="max-w-sm" placeholder="Filter Matched User..."
                :model-value="table.getColumn('matchedUser')?.getFilterValue() as string"
                @update:model-value=" table.getColumn('matchedUser')?.setFilterValue($event)" />
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
                            <template v-if="cell.column.id === 'questionTitle'">
                                <!-- Apply the RouterLink with custom styling -->
                                <RouterLink :to="{ path: `/profile/attempt/${row.original.sessionId}` }"
                                    class="text-blue-600 underline cursor-pointer">
                                    {{ cell.getValue() }}
                                </RouterLink>
                            </template>
                            <template v-else>
                                <FlexRender :render="cell.column.columnDef.cell" :props="cell.getContext()" />
                            </template>
                        </TableCell>
                    </TableRow>
                </template>
                <template v-else>
                    <TableRow>
                        <TableCell :colspan="columns.length" class="h-24 text-center">
                            No attempts found.
                        </TableCell>
                    </TableRow>
                </template>
            </TableBody>
        </Table>
    </div>
</template>
