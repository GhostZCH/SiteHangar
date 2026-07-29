<script setup lang="ts">
import type { ChipItem } from '@/types/content';
defineProps<{ items: ChipItem[] }>();
</script>

<template>
  <div class="chips-container">
    <span
      v-for="(c, i) in items"
      :key="i"
      class="chip"
      :class="c.accent ? 'chip-accent' : 'chip-default'"
    >
      {{ c.label }}
    </span>
  </div>
</template>

<style scoped>
.chips-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 4px 0;
}

.chip {
  display: inline-flex;
  align-items: center;
  padding: 6px 16px;
  border-radius: 9999px;
  font-size: 13px;
  font-weight: 500;
  line-height: 1.4;
  transition: all 0.2s ease;
  cursor: default;
  border: 1px solid transparent;
}

.chip-default {
  background: var(--surface-variant);
  color: var(--on-surface-variant);
  border-color: var(--outline-variant);
}

.chip-default:hover {
  background: var(--surface);
  border-color: var(--outline);
}

.chip-accent {
  background: var(--accent);
  color: var(--on-accent);
  border-color: var(--accent);
}

.chip-accent:hover {
  opacity: 0.9;
}
</style>
