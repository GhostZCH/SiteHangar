<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useTheme, type ThemeName } from '@/composables/useTheme';

const props = defineProps<{
  currentTheme: ThemeName;
}>();

const emit = defineEmits<{
  select: [theme: ThemeName];
}>();

const showThemeMenu = ref(false);

const themes: { key: ThemeName; label: string }[] = [
  { key: 'default', label: '默认' },
  { key: 'warm', label: '暖色' },
  { key: 'cold', label: '冷色' },
  { key: 'night', label: '夜间' },
  { key: 'glass', label: '毛玻璃' },
  { key: 'eye-care', label: '护眼' },
  { key: '3d', label: '3D' },
];

function toggleThemeMenu(e: Event) {
  e.stopPropagation();
  showThemeMenu.value = !showThemeMenu.value;
}

function closeThemeMenu() {
  showThemeMenu.value = false;
}

function selectTheme(theme: ThemeName) {
  emit('select', theme);
  showThemeMenu.value = false;
}

onMounted(() => {
  window.addEventListener('click', closeThemeMenu);
});

onBeforeUnmount(() => {
  window.removeEventListener('click', closeThemeMenu);
});
</script>

<template>
  <div class="theme-switcher">
    <button class="icon-btn" @click="toggleThemeMenu" title="切换主题">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="5"/>
        <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
      </svg>
    </button>
    <div class="theme-menu" :class="{ show: showThemeMenu }">
      <button
        v-for="t in themes"
        :key="t.key"
        class="theme-option"
        :class="{ active: currentTheme === t.key }"
        :data-theme="t.key"
        @click="selectTheme(t.key)"
      >
        <span class="theme-dot"></span>
        <span>{{ t.label }}</span>
      </button>
    </div>
  </div>
</template>
