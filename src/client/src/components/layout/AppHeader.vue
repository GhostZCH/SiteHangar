<script setup lang="ts">
import { computed, ref, onMounted, onBeforeUnmount } from 'vue';
import { useRoute } from 'vue-router';
import { useSiteStore } from '@/stores/site';
import { useTheme, type ThemeName } from '@/composables/useTheme';
import ThemeSwitcher from './ThemeSwitcher.vue';
import HeaderNav from './HeaderNav.vue';

const route = useRoute();
const site = useSiteStore();
const { currentTheme, setTheme } = useTheme();

const showSiteLabel = computed(() => site.siteSlug);
const siteTitle = computed(() => site.siteTitle || 'SiteHanger');

function selectTheme(theme: ThemeName) {
  setTheme(theme);
}
</script>

<template>
  <header class="appbar">
    <div class="appbar-inner">
      <div class="appbar-brand">
        <router-link to="/" class="appbar-logo">
          <svg viewBox="0 0 48 48" stroke="currentColor" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round">
            <path d="M15.5 9L7 14V24V34L15.5 39L24 44L32.5001 39L41 34V24V14L32.5001 9L24 4L15.5 9Z"/>
            <path d="M24 4L24 24"/>
            <path d="M41 34L24 24"/>
            <path d="M7 34L24 24"/>
          </svg>
        </router-link>
        <span class="appbar-title">{{ siteTitle }}</span>
      </div>

      <div class="appbar-actions">
        <HeaderNav />
        <ThemeSwitcher :current-theme="currentTheme" @select="selectTheme" />
      </div>
    </div>
  </header>
</template>
