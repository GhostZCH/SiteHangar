<script setup lang="ts">
import type { ListBlock } from '@/types/content';
defineProps<{ list: ListBlock }>();
</script>

<template>
  <div class="card p-6">
    <h3 v-if="list.title" class="text-lg font-semibold mb-4">{{ list.title }}</h3>
    <ul class="space-y-3">
      <li v-for="(it, i) in list.items" :key="i" class="flex gap-3">
        <span class="flex-shrink-0 w-6 h-6 rounded-full bg-primary-100 text-primary-700 text-xs font-semibold flex items-center justify-center">{{ it.icon }}</span>
        <div>
          <div class="font-medium" style="color: var(--on-surface);">{{ it.title }}</div>
          <div v-if="it.subtitle" class="text-sm" style="color: var(--on-surface-variant);">{{ it.subtitle }}</div>
        </div>
      </li>
    </ul>
  </div>
</template>
