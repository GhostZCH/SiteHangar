<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import mermaid from 'mermaid';

const props = defineProps<{ code: string }>();
const containerRef = ref<HTMLDivElement>();
const rendered = ref('');

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  securityLevel: 'loose',
});

async function render() {
  if (!containerRef.value || !props.code.trim()) return;
  try {
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
