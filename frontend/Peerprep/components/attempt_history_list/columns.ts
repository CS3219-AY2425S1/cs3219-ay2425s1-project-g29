import type { ColumnDef } from "@tanstack/vue-table";
import { ArrowUpDown } from 'lucide-vue-next'
import { Button } from "@/components/ui/button";
import { RouterLink } from 'vue-router';

export const getColumns = (refreshData: () => void): ColumnDef[] => [
  {
    accessorKey: "index",
    header: ({ column }) => {
      return h(Button, {
        variant: 'ghost',
        onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
      }, () => ['Index', h(ArrowUpDown, { class: 'ml-1 h-4 w-4' })])
    },
  },
  {
    accessorKey: "questionTitle",
    header: ({ column }) => {
      return h(Button, {
        variant: 'ghost',
        onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
      }, () => ['Question Title', h(ArrowUpDown, { class: 'ml-1 h-4 w-4' })])
    },
    cell: ({ row }) => {  // Actually this is not needed
      // Assume each row has a `sessionId` or `attemptId` property you want to link to
      const sessionId = row.original.sessionId;
      return h(
        RouterLink,
        {
          to: {
            path: `/profile/attempt/${sessionId}`,
            class: 'text-blue-500 underline cursor-pointer' // Link styling
          }
        },
        { default: () => row.getValue('questionTitle') }
      );
    },
  },
  {
    accessorKey: "questionDifficulty",
    header: ({ column }) => {
      return h(Button, {
        variant: 'ghost',
        onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
      }, () => ['Question Difficulty', h(ArrowUpDown, { class: 'ml-1 h-4 w-4' })])
    },
  },
  {
    accessorKey: "questionCategory",
    header: ({ column }) => {
      return h(Button, {
        variant: 'ghost',
        onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
      }, () => ['Category', h(ArrowUpDown, { class: 'ml-1 h-4 w-4' })])
    },
  },
  {
    accessorKey: "dateTime",
    header: ({ column }) => {
      return h(Button, {
        variant: 'ghost',
        onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
      }, () => ['Date/Time', h(ArrowUpDown, { class: 'ml-1 h-4 w-4' })])
    },
  },
  {
    accessorKey: "matchedUser",
    header: ({ column }) => {
      return h(Button, {
        variant: 'ghost',
        onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
      }, () => ['Matched User', h(ArrowUpDown, { class: 'ml-1 h-4 w-4' })])
    },
  },
];
