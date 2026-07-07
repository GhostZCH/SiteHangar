<script setup lang="ts">
import { computed, ref } from 'vue';
import { useDetailPageData } from '@/composables/usePageData';
import { usePageSections } from '@/composables/usePageSections';
import { useSiteStore } from '@/stores/site';
import DetailHero from '@/components/content/DetailHero.vue';
import DetailContent from '@/components/content/DetailContent.vue';
import PageLoading from '@/components/content/PageLoading.vue';
import PageError from '@/components/content/PageError.vue';
import NavList, { type NavItem } from '@/components/layout/NavList.vue';

const { data, loading, error } = useDetailPageData();
const sections = computed(() => data.value?.data.sections || []);
const { pageSections, activeSectionId, scrollToSection } = usePageSections(sections);

const site = useSiteStore();
const navExpanded = ref(true);

const navItems = computed<NavItem[]>(() => {
  if (sections.value.length) {
    return sections.value.map((s) => ({
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
    active: false,
    to: '/' + c.slug,
  }));
});

const navTitle = computed(() => (pageSections.value.length ? '目录' : '栏目'));

function toggleNav() {
  navExpanded.value = !navExpanded.value;
}
</script>

<template>
  <div>
    <PageLoading v-if="loading" />
    <PageError v-else-if="error" :message="error" />
    <div v-else-if="data" class="detail-page">
      <div class="detail-layout">
        <aside class="detail-nav" :class="{ expanded: navExpanded }">
          <NavList :title="navTitle" :items="navItems" :expanded="navExpanded" @click="scrollToSection" @action="toggleNav">
            <template #action-short>
              <span class="nav-toggle-icon">{{ navExpanded ? '«' : '»' }}</span>
            </template>
          </NavList>
        </aside>
        <div class="detail-main">
          <DetailHero :page-data="data.data" />
          <DetailContent :sections="sections" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.detail-page {
  display: flex;
  justify-content: center;
  padding: 0 24px;
}

.detail-layout {
  display: flex;
  gap: 0;
  width: 100%;
  max-width: 1400px;
  align-items: flex-start;
}

.detail-nav {
  width: var(--nav-width);
  flex-shrink: 0;
  background: transparent;
  border: none;
  border-right: 1px solid var(--outline-variant);
  border-radius: 0;
  padding: 16px 0 16px;
  height: fit-content;
  position: sticky;
  top: 72px;
  transition: width 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.detail-nav.expanded {
  width: var(--nav-expanded-width);
}

.detail-main {
  flex: 1;
  min-width: 0;
}

@media (max-width: 1024px) {
  .detail-page {
    padding: 0 16px;
  }
  .detail-layout {
    flex-direction: column;
  }
  .detail-nav {
    position: relative;
    top: 0;
    width: 100% !important;
  }
}
</style>
