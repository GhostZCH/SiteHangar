<script setup lang="ts">
import type { StatItem } from '@/types/content';
defineProps<{ items: StatItem[] }>();
</script>

<template>
  <div class="stats-row">
    <div
      v-for="(s, i) in items"
      :key="i"
      class="stat-item"
    >
      <div class="stat-value">{{ s.value }}</div>
      <div class="stat-label">{{ s.label }}</div>
    </div>
  </div>
</template>
