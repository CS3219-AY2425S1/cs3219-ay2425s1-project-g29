<script setup lang="ts">
import { Check, ChevronsUpDown } from 'lucide-vue-next'

import { ref } from 'vue'
import { cn } from '@/lib/utils'


const { data } = defineProps<{
    data: { value: string; label: string }[],
}>()

const open = ref(false)
const value = ref('')
const selectedCategory = defineModel()
</script>

<template>
    <Popover v-model:open="open">
        <PopoverTrigger as-child>
            <Button variant="outline" role="combobox" :aria-expanded="open" class="w-[200px] justify-between">
                {{ selectedCategory
                    ? data.find((item) => item.value === selectedCategory)?.label
                    : "Select category ..." }}
                <ChevronsUpDown class="ml-2 h-4 w-4 shrink-0 opacity-50" />
            </Button>
        </PopoverTrigger>
        <PopoverContent class="w-[200px] p-0">
            <Command>
                <CommandInput class="h-9" placeholder="Search category ..." />
                <CommandEmpty>No item found.</CommandEmpty>
                <CommandList>
                    <CommandGroup>
                        <CommandItem v-for="item in data" :key="item.value" :value="item.value" @select="(ev) => {
                            if (typeof ev.detail.value === 'string') {
                                selectedCategory = ev.detail.value
                            }
                            open = false
                        }">
                            {{ item.label }}
                            <Check :class="cn(
                                'ml-auto h-4 w-4',
                                selectedCategory === item.value ? 'opacity-100' : 'opacity-0',
                            )" />
                        </CommandItem>
                    </CommandGroup>
                </CommandList>
            </Command>
        </PopoverContent>
    </Popover>
</template>