<script setup lang="ts">
defineProps<{ code: string }>();

function parseTree(text: string) {
  const lines = text.trim().split('\n').filter(l => l.trim());
  return lines.map(line => {
    // 计算缩进级别
    const match = line.match(/^(\s*)/);
    const indent = match ? match[1].length : 0;
    const level = Math.floor(indent / 2);
    // 去掉树状符号
    const content = line.trim().replace(/^[├└│├──└──\s]+/, '').trim();
    return { level, content };
  }).filter(item => item.content);
}
</script>

<template>
  <div class="tree-block card p-4">
    <div v-for="(item, i) in parseTree(code)" :key="i" class="tree-line" :style="{ paddingLeft: item.level * 20 + 'px' }">
      <span class="tree-node"></span>
      <span class="tree-text">{{ item.content }}</span>
    </div>
  </div>
</template>

<style scoped>
.tree-block {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 14px;
}

.tree-line {
  display: flex;
  align-items: center;
  padding: 4px 0;
  color: var(--on-surface);
}

.tree-node {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent);
  margin-right: 8px;
  flex-shrink: 0;
}

.tree-text {
  color: var(--on-surface);
}
</style>
