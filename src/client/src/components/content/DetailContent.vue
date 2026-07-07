<script setup lang="ts">
import type { Section } from '@/types/content';
import SectionRenderer from './SectionRenderer.vue';

const props = defineProps<{ sections: Section[] }>();
</script>

<template>
  <div class="content">
    <div class="content-inner">
      <div v-if="sections.length" class="space-y-12">
        <SectionRenderer v-for="(s, idx) in sections" :key="s.id" :section="s" :index="idx" />
      </div>
      <div v-else class="card p-8 text-center" style="color: var(--on-surface-variant);">
        该页面暂无章节内容
      </div>
    </div>
  </div>
</template>
