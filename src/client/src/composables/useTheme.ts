import { ref } from 'vue';

export type ThemeName = 'default' | 'warm' | 'cold' | 'night' | 'glass' | 'eye-care' | '3d';

const STORAGE_KEY = 'sitehangar-theme';
const currentTheme = ref<ThemeName>('default');

export function useTheme() {
  function setTheme(theme: ThemeName) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);
    currentTheme.value = theme;
  }

  function initTheme() {
    const saved = localStorage.getItem(STORAGE_KEY) as ThemeName | null;
    const theme = saved || 'default';
    setTheme(theme);
  }

  function getCurrentTheme(): ThemeName {
    return currentTheme.value;
  }

  return {
    currentTheme,
    setTheme,
    initTheme,
    getCurrentTheme,
  };
}
