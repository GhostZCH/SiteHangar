<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useSiteStore } from '@/stores/site';

const route = useRoute();
const site = useSiteStore();

const columns = computed(() => site.columns);

function isActive(path: string): boolean {
  return route.path.startsWith(path);
}
</script>

<template>
  <nav class="hidden md:flex items-center gap-1 text-sm" style="margin-right: 8px;">
    <router-link
      v-for="c in columns"
      :key="c.slug"
      :to="'/' + c.slug"
      class="nav-item"
      style="padding: 6px 12px; font-size: 13px; min-width: 78px; text-align: center; justify-content: center;"
      :class="{ active: isActive('/' + c.slug) }"
    >
      {{ c.name }}
    </router-link>
    <router-link
      to="/info"
      class="nav-item"
      style="padding: 6px 12px; font-size: 13px; min-width: 78px; text-align: center; justify-content: center;"
      :class="{ active: route.path === '/info' }"
    >
      关于
    </router-link>
  </nav>
</template>
