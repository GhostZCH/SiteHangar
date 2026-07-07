<script setup lang="ts">
import type { TableItem } from '@/types/content';
defineProps<{ items: TableItem[] }>();
</script>

<template>
  <div class="space-y-6">
    <div v-for="(t, i) in items" :key="i" class="table-container">
      <table class="table">
        <thead>
          <tr>
            <th v-for="(h, j) in t.headers" :key="j">{{ h }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, r) in t.rows" :key="r">
            <td v-for="(cell, c) in row" :key="c">{{ cell }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
