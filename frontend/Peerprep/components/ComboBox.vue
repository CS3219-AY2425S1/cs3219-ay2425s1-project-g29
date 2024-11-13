<script setup lang="ts">
import { Check, ChevronsUpDown } from 'lucide-vue-next'
import { ref, computed } from 'vue'
import { cn } from '@/lib/utils'

const props = defineProps<{
  data: { value: string; label: string }[]
  modelValue: string
}>()

const emit = defineEmits(['update:modelValue'])

const open = ref(false)

const selectedLabel = computed(() => {
  const selected = props.data.find((item) => item.value === props.modelValue)
  return selected ? selected.label : 'Select category ...'
})

function selectCategory(value: string) {
  emit('update:modelValue', value)
  open.value = false
}
</script>

<template>
  <Popover v-model:open="open">
    <PopoverTrigger as-child>
      <Button variant="outline" role="combobox" :aria-expanded="open" class="w-[200px] justify-between">
        {{ selectedLabel }}
        <ChevronsUpDown class="ml-2 h-4 w-4 shrink-0 opacity-50" />
      </Button>
    </PopoverTrigger>
    <PopoverContent class="w-[200px] p-0">
      <Command>
        <CommandInput class="h-9" placeholder="Search category ..." />
        <CommandEmpty>No item found.</CommandEmpty>
        <CommandList>
          <CommandGroup>
            <CommandItem
              v-for="item in props.data"
              :key="item.value"
              :value="item.value"
              @select="() => selectCategory(item.value)"
            >
              <Check
                :class="cn(
                  'mr-2 h-4 w-4',
                  props.modelValue === item.value ? 'opacity-100' : 'opacity-0'
                )"
              />
              {{ item.label }}
            </CommandItem>
          </CommandGroup>
        </CommandList>
      </Command>
    </PopoverContent>
  </Popover>
</template>