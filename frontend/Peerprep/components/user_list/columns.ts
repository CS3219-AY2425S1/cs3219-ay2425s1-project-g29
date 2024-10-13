import { h } from "vue";
import type { ColumnDef } from "@tanstack/vue-table";
import type { User } from "~/types/User";

export const getColumns = (refreshData: () => void): ColumnDef<User>[] => [
  { accessorKey: "index", header: "Index" },
  { accessorKey: "displayName", header: "Display Name" },
  { accessorKey: "email", header: "Email" },
  { accessorKey: "uid", header: "User ID" },
  { accessorKey: "admin", header: "Admin" },
];
