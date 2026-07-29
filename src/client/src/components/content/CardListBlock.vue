<script setup lang="ts">
import type { CardItem } from '@/types/content';
defineProps<{ items: CardItem[][] }>();
</script>

<template>
  <div v-for="(group, gi) in items" :key="gi" class="grid-3">
    <article v-for="(c, i) in group" :key="i" class="card">
      <div v-if="c.image" class="card-media" :style="{ backgroundImage: `url(${c.image})` }"></div>
      <div class="card-content">
        <h3 class="card-headline">{{ c.headline }}</h3>
        <p class="card-supporting">{{ c.supporting }}</p>
        <div v-if="c.detail?.length" class="detail-panel">
          <p v-for="(d, j) in c.detail" :key="j">{{ d }}</p>
        </div>
      </div>
    </article>
  </div>
</template>
