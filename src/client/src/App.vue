<script setup lang="ts">
import { onMounted, ref, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useSiteStore } from '@/stores/site';
import AppHeader from '@/components/layout/AppHeader.vue';
import AppNav from '@/components/layout/AppNav.vue';
import MobileNav from '@/components/layout/MobileNav.vue';
import { useTheme } from '@/composables/useTheme';
import { initSiteSlug } from '@/composables/useSiteDetection';
import { useMobileBarAutoHide } from '@/composables/useMobileBarAutoHide';

const route = useRoute();
const site = useSiteStore();
const { initTheme } = useTheme();
const { barsVisible } = useMobileBarAutoHide();
const navExpanded = ref(true);

function toggleNav() {
  navExpanded.value = !navExpanded.value;
}

const isMobile = computed(() => {
  if (typeof window === 'undefined') return false;
  return window.innerWidth <= 768;
});

const mainMargin = computed(() => {
  if (route.path === '/' || route.name === 'module') return '';
  return { marginLeft: '0' };
});

const footerMargin = computed(() => {
  if (route.path === '/' || route.name === 'module') return '';
  return { marginLeft: '0' };
});

onMounted(async () => {
  initSiteSlug();
  await Promise.all([site.loadColumns(), site.loadGlobalConfig()]);
  initTheme();
});
</script>

<template>
  <div>
    <AppHeader
      v-if="!route.meta.hideHeader"
      :class="{ 'mobile-hidden': isMobile && !barsVisible }"
    />
    <AppNav
      v-if="!route.meta.hideHeader && route.path !== '/' && route.name !== 'module' && route.name !== 'detail' && route.name !== 'info'"
      :expanded="navExpanded"
      @toggle="toggleNav"
    />
    <main :style="mainMargin">
      <router-view />
    </main>
    <MobileNav
      v-if="!route.meta.hideHeader && route.name === 'detail'"
      :class="{ 'mobile-hidden': isMobile && !barsVisible }"
    />
    <footer v-if="site.icp" class="footer" :style="footerMargin">
      <div class="footer-inner">
        <p class="footer-beian">{{ site.icp }}</p>
      </div>
    </footer>
  </div>
</template>
