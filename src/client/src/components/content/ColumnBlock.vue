<script setup lang="ts">
import type { ColumnBlock as ColumnBlockType } from '@/types/content';
import DescriptionBlock from './DescriptionBlock.vue';
import TableBlock from './TableBlock.vue';
import ListBlock from './ListBlock.vue';
import CardListBlock from './CardListBlock.vue';

defineProps<{ columns: ColumnBlockType[] }>();

function getColumnClass(count: number): string {
  const map: Record<number, string> = {
    1: 'columns-1',
    2: 'columns-2',
    3: 'columns-3',
    4: 'columns-4',
  };
  return map[count] || 'columns-1';
}
</script>

<template>
  <div class="column-layout" :class="getColumnClass(columns.length)">
    <div v-for="(col, idx) in columns" :key="idx" class="column-item">
      <DescriptionBlock v-if="col.items && col.items.length" :items="col.items" />
      <TableBlock v-if="col.tables && col.tables.length" :items="col.tables" />
      <ListBlock v-if="col.list" :list="col.list" />
      <CardListBlock v-if="col.cards && col.cards.length" :items="col.cards" />
    </div>
  </div>
</template>

<style scoped>
.column-layout {
  display: grid;
  gap: 32px;
  margin-top: 16px;
}

.columns-1 {
  grid-template-columns: 1fr;
}

.columns-2 {
  grid-template-columns: repeat(2, 1fr);
}

.columns-3 {
  grid-template-columns: repeat(3, 1fr);
}

.columns-4 {
  grid-template-columns: repeat(4, 1fr);
}

.column-item {
  padding: 0 16px;
  border-left: 1px solid var(--outline-variant);
}

.column-item:first-child {
  padding-left: 0;
  border-left: none;
}

.column-item:last-child {
  padding-right: 0;
}

@media (max-width: 768px) {
  .columns-2,
  .columns-3,
  .columns-4 {
    grid-template-columns: 1fr;
  }

  .column-item {
    padding: 16px 0;
    border-left: none;
    border-bottom: 1px solid var(--outline-variant);
  }

  .column-item:first-child {
    padding-top: 0;
  }

  .column-item:last-child {
    padding-bottom: 0;
    border-bottom: none;
  }
}
</style>
