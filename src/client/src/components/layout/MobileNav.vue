<script setup lang="ts">
import { usePageSections } from '@/composables/usePageSections';

const { pageSections, activeSectionId, scrollToSection } = usePageSections();
</script>

<template>
  <nav v-if="pageSections.length" class="mobile-nav-bar" aria-label="章节导航">
    <button
      v-for="item in pageSections"
      :key="item.id"
      class="mobile-nav-item"
      :class="{ active: activeSectionId === item.id }"
      @click="scrollToSection(item.id)"
    >
      {{ item.title.slice(0, 2) }}
    </button>
  </nav>
</template>
