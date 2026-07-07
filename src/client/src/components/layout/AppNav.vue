<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useSiteStore } from '@/stores/site';
import { usePageSections } from '@/composables/usePageSections';
import NavList, { type NavItem } from './NavList.vue';

const props = defineProps<{ expanded: boolean }>();
const emit = defineEmits<{ toggle: [] }>();

const route = useRoute();
const site = useSiteStore();
const { pageSections, activeSectionId, scrollToSection } = usePageSections();

const currentPath = computed(() => route.path);

const navItems = computed<NavItem[]>(() => {
  if (pageSections.value.length) {
    return pageSections.value.map((s) => ({
        id: s.id,
        title: s.title,
        subtitle: s.subtitle,
        short: s.title.slice(0, 2),
        active: activeSectionId.value === s.id,
      }));
  }

  return site.columns.map((c) => ({
    id: c.slug,
    title: c.name,
    subtitle: c.description || undefined,
    short: c.name.slice(0, 2),
    active: currentPath.value.startsWith('/' + c.slug),
    to: '/' + c.slug,
  }));
});

const navTitle = computed(() => (pageSections.value.length ? '目录' : '栏目'));
</script>

<template>
  <aside class="nav-drawer" :class="{ expanded: props.expanded }">
    <div class="nav-items">
      <NavList :title="navTitle" :items="navItems" :expanded="props.expanded" @click="scrollToSection" @action="emit('toggle')">
        <template #action-short>
          <span class="nav-toggle-icon">{{ props.expanded ? '«' : '»' }}</span>
        </template>
      </NavList>
    </div>
  </aside>
</template>
