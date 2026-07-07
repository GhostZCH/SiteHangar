<script setup lang="ts">
import { computed } from 'vue';
import type { PageData } from '@/types/content';

const props = defineProps<{ pageData: PageData }>();

const heroTags = computed<string[]>(() => {
  const tags = props.pageData.hero?.tags;
  if (!tags) return [];
  const arr = Array.isArray(tags) ? tags : [];
  return arr.filter((t: unknown) => typeof t === 'string' && t.trim().length > 0);
});

const heroTitle = computed(() => props.pageData.hero?.title || props.pageData.page?.title);
</script>

<template>
  <section class="hero">
    <div class="hero-inner">
      <div class="hero-content">
        <div class="hero-title-wrap">
          <h1 class="hero-title">{{ heroTitle }}</h1>
          <div v-if="heroTags.length" class="hero-tags">
            <span v-for="(t, i) in heroTags" :key="i" class="hero-tag">{{ t }}</span>
          </div>
        </div>
        <p v-if="pageData.introduction" class="hero-subtitle">{{ pageData.introduction }}</p>
        <div v-if="pageData.version || pageData.lastModified" class="hero-meta">
          <span v-if="pageData.version" class="hero-version">{{ pageData.version }}</span>
          <span v-if="pageData.lastModified" class="hero-lastmodified">{{ pageData.lastModified }}</span>
        </div>
      </div>
    </div>
  </section>
</template>
