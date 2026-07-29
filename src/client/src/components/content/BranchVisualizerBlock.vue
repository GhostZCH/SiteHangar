<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import type { BranchVisualizer } from '@/types/content';

const props = defineProps<{ viz: BranchVisualizer | BranchVisualizer[] }>();

const visualizers = computed(() => {
  return Array.isArray(props.viz) ? props.viz : [props.viz];
});

const mounted = ref(false);

onMounted(() => {
  mounted.value = true;
});

function colorByLevel(level: number) {
  if (level >= 5) return 'level-5';
  if (level >= 4) return 'level-4';
  if (level >= 3) return 'level-3';
  if (level >= 2) return 'level-2';
  if (level >= 1) return 'level-1';
  return 'level-0';
}

function getLevelLabel(level: number) {
  if (level >= 5) return '成熟完善';
  if (level >= 4) return '高度发展';
  if (level >= 3) return '显著发展';
  if (level >= 2) return '初步发展';
  if (level >= 1) return '萌芽阶段';
  return '尚未出现';
}
</script>

<template>
  <div v-for="(v, idx) in visualizers" :key="idx" class="branch-visualizer">
    <div class="branch-grid-wrapper">
      <!-- 表头：时期 -->
      <div class="branch-grid-header">
        <div class="branch-label-header"></div>
        <div v-for="(p, i) in v.periods" :key="i" class="branch-period-header">
          {{ p }}
        </div>
      </div>

      <!-- 数据行 -->
      <div
        v-for="(b, bi) in v.branches"
        :key="bi"
        class="branch-grid-row"
        :class="{ 'animate-in': mounted }"
        :style="{ animationDelay: `${bi * 0.15}s` }"
      >
        <div class="branch-name-cell">
          <div class="branch-name">{{ b.name }}</div>
        </div>
        <div
          v-for="(lv, i) in b.levels"
          :key="i"
          class="branch-grid-cell"
          :class="[colorByLevel(lv), lv >= 1 ? 'animate-cell' : 'no-animate', lv >= 1 ? 'has-content' : '', i === 0 ? 'first-cell' : '', i === b.levels.length - 1 ? 'last-cell' : '']"
          :style="{ animationDelay: `${bi * 0.15 + i * 0.08}s` }"
          :title="`${b.name} - ${v.periods[i]}: ${getLevelLabel(lv)}`"
        >
          <div v-if="lv >= 1" class="cell-content">{{ b.descriptions[i] }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.branch-visualizer {
  margin: 16px 0;
}

/* 颜色定义 */
.level-0 {
  background: var(--surface-variant);
  color: #000000;
}

.level-1 {
  background: color-mix(in srgb, var(--primary) 8%, var(--surface));
  color: #000000;
}

.level-2 {
  background: color-mix(in srgb, var(--primary) 18%, var(--surface));
  color: #000000;
}

.level-3 {
  background: color-mix(in srgb, var(--primary) 32%, var(--surface));
  color: #000000;
}

.level-4 {
  background: color-mix(in srgb, var(--primary) 32%, var(--surface));
  color: #000000;
}

.level-5 {
  background: color-mix(in srgb, var(--primary) 55%, var(--surface));
  color: #000000;
}

/* Grid 布局 */
.branch-grid-wrapper {
  overflow-x: auto;
  background: transparent;
  border: none;
  padding: 0;
}

.branch-grid-header {
  display: grid;
  grid-template-columns: 72px repeat(9, 1fr);
  gap: 0;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--outline-variant);
}

.branch-grid-row {
  display: grid;
  grid-template-columns: 72px repeat(9, 1fr);
  gap: 0;
  margin-bottom: 16px;
}

.branch-grid-row:last-child {
  margin-bottom: 0;
}

.branch-label-header {
  padding: 8px 4px;
  font-size: 12px;
  font-weight: 400;
  color: var(--on-surface-variant);
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.branch-period-header {
  padding: 8px 4px;
  font-size: 12px;
  font-weight: 400;
  color: var(--on-surface-variant);
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.branch-name-cell {
  padding: 4px 2px;
  min-height: 72px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  background: transparent;
  flex-shrink: 0;
}

.branch-name {
  width: 100%;
  font-size: 12px;
  font-weight: 400;
  color: var(--on-surface);
  text-align: left;
  line-height: 1.4;
  word-break: break-all;
  overflow-wrap: break-word;
  white-space: normal;
}

.branch-grid-cell {
  padding: 6px 4px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  border-radius: 0;
  overflow: hidden;
  min-width: 0;
}

/* 无内容的格子：立即可见，无动画无鼠标效果 */
.branch-grid-cell.no-animate {
  opacity: 1;
  transform: scale(1);
  cursor: default;
}

/* 有内容的格子：初始不可见，待动画 */
.branch-grid-cell.animate-cell {
  opacity: 0;
  transform: scale(0.9);
  cursor: pointer;
  animation: cellPopIn 0.4s ease forwards;
}

/* 左侧圆角 */
.branch-grid-cell.first-cell {
  border-radius: 8px 0 0 8px;
}

/* 右侧圆角 */
.branch-grid-cell.last-cell {
  border-radius: 0 8px 8px 0;
}

/* 鼠标悬停效果 - 只有有内容的格子 */
.branch-grid-cell.has-content:hover {
  transform: scale(1.05);
  filter: brightness(1.1);
  z-index: 1;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.cell-content {
  font-size: 11px;
  line-height: 1.4;
  text-align: center;
  color: inherit;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
}

/* 动画 */
@keyframes rowFadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes cellPopIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .branch-grid-header,
  .branch-grid-row {
    grid-template-columns: 48px repeat(9, 1fr);
  }

  .branch-grid-header {
    margin-bottom: 8px;
    padding-bottom: 4px;
  }

  .branch-grid-row {
    margin-bottom: 8px;
  }

  .branch-label-header,
  .branch-period-header {
    padding: 6px 2px;
    font-size: 10px;
  }

  .branch-name-cell {
    padding: 3px 1px;
    min-height: 56px;
  }

  .branch-name {
    font-size: 10px;
  }

  .branch-grid-cell {
    padding: 4px 2px;
    height: 56px;
  }

  .cell-content {
    font-size: 9px;
  }
}
</style>
