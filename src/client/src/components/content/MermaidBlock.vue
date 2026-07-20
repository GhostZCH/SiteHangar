<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';

const props = defineProps<{ code: string }>();
const containerRef = ref<HTMLDivElement>();
const rendered = ref('');

// mermaid 懒加载：首次渲染时动态 import，避免拖慢首屏
type Mermaid = typeof import('mermaid').default;
let mermaidPromise: Promise<Mermaid> | null = null;

function loadMermaid(): Promise<Mermaid> {
  if (!mermaidPromise) {
    mermaidPromise = import('mermaid').then((mod) => {
      const mermaid = mod.default;
      mermaid.initialize({
        startOnLoad: false,
        theme: 'dark',
        securityLevel: 'loose',
      });
      return mermaid;
    });
  }
  return mermaidPromise;
}

async function render() {
  if (!containerRef.value || !props.code.trim()) return;
  try {
    const mermaid = await loadMermaid();
    const id = 'mermaid-' + Math.random().toString(36).slice(2);
    const { svg } = await mermaid.render(id, props.code.trim());
    rendered.value = svg;
  } catch (e) {
    console.error('Mermaid render error:', e);
    rendered.value = `<pre class="text-red-400">${props.code}</pre>`;
  }
}

onMounted(render);
watch(() => props.code, render);
</script>

<template>
  <div ref="containerRef" class="mermaid-block card p-4 overflow-x-auto">
    <div v-html="rendered" />
  </div>
</template>

<style scoped>
.mermaid-block :deep(svg) {
  max-width: 100%;
  height: auto;
  margin: 0 auto;
  display: block;
}
</style>
