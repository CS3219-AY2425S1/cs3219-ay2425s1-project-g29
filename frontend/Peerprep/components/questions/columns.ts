import { h } from "vue";
import type { ColumnDef } from "@tanstack/vue-table";
import { ArrowUpDown } from 'lucide-vue-next';
import { Button } from "@/components/ui/button";
import type { Question } from "~/types/Question";
import QuestionTableDropDown from "./QuestionTableDropDown.vue";

const difficultyOrder = ['easy', 'medium', 'hard'];

export const getColumns = (refreshData: () => void): ColumnDef<Question>[] => [
  { 
    accessorKey: "index", 
    header: ({ column }) => {
      return h(Button, {
        variant: 'ghost',
        onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
      }, () => ['Idx', h(ArrowUpDown, { class: 'ml-1 h-4 w-4' })])
    },
  },
  { 
    accessorKey: "title", 
    header: ({ column }) => {
      return h(Button, {
        variant: 'ghost',
        onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
      }, () => ['Title', h(ArrowUpDown, { class: 'ml-1 h-4 w-4' })])
    },
  },
  { 
    accessorKey: "description", 
    header: "Description", 
  },
  { 
    accessorKey: "category", 
    header: ({ column }) => {
      return h(Button, {
        variant: 'ghost',
        onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
      }, () => ['Category', h(ArrowUpDown, { class: 'ml-1 h-4 w-4' })])
    }, 
  },
  { 
    accessorKey: "difficulty", 
    header: ({ column }) => {
      return h(Button, {
        variant: 'ghost',
        onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
      }, () => ['Difficulty', h(ArrowUpDown, { class: 'ml-1 h-4 w-4' })])
    }, 
    sortingFn: (a, b) => {
      const aValue = a.original.difficulty;
      const bValue = b.original.difficulty;
      return difficultyOrder.indexOf(aValue) - difficultyOrder.indexOf(bValue);
    }
  },
  {
    id: "actions",
    enableHiding: false,
    cell: ({ row }) => {
      const question = row.original;

      return h(
        "div",
        { class: "relative" },
        h(QuestionTableDropDown, {
          question,
          onRefresh: refreshData // Use the passed refreshData function
        })
      );
    },
  },
];
