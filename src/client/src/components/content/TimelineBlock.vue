<script setup lang="ts">
import { computed } from 'vue';
import type { TimelineBlock } from '@/types/content';

const props = defineProps<{ timeline: TimelineBlock | TimelineBlock[] }>();

const timelines = computed(() => {
  return Array.isArray(props.timeline) ? props.timeline : [props.timeline];
});

type DescItem = string | string[];

function isStringArray(item: DescItem): item is string[] {
  return Array.isArray(item);
}
</script>

<template>
  <div v-for="(tl, idx) in timelines" :key="idx" class="card p-6">
    <h3 v-if="tl.title" class="text-lg font-semibold mb-6">{{ tl.title }}</h3>
    <ol class="timeline">
      <li v-for="(it, i) in tl.items" :key="i" class="timeline-item">
        <span class="timeline-dot"></span>
        <div class="timeline-content">
          <time class="timeline-date">{{ it.date }}</time>
          <h4 class="timeline-title">{{ it.title }}</h4>
          <p v-if="it.subtitle" class="timeline-subtitle">{{ it.subtitle }}</p>
          <img v-if="it.image" :src="it.image" :alt="it.title" class="mt-2 rounded max-w-md" />
          <div v-if="it.description" class="timeline-desc">
            <template v-for="(d, j) in it.description" :key="j">
              <!-- 字符串：主条目 -->
              <div v-if="!isStringArray(d)" class="timeline-desc-item">
                <span class="timeline-main-dot"></span>
                <span class="timeline-desc-text">{{ d }}</span>
              </div>
              <!-- 数组：主条目 + 子条目列表 -->
              <template v-else>
                <div class="timeline-desc-item">
                  <span class="timeline-main-dot"></span>
                  <span class="timeline-desc-text">{{ d[0] }}</span>
                </div>
                <div v-for="(sub, k) in d.slice(1)" :key="k" class="timeline-desc-item timeline-desc-sub">
                  <span class="timeline-sub-dot"></span>
                  <span class="timeline-desc-text">{{ sub }}</span>
                </div>
              </template>
            </template>
          </div>
        </div>
      </li>
    </ol>
  </div>
</template>
