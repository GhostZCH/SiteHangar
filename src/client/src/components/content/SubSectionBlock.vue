<script setup lang="ts">
import type { SubSection } from '@/types/content';
import DescriptionBlock from './DescriptionBlock.vue';
import StatsBlock from './StatsBlock.vue';
import TableBlock from './TableBlock.vue';
import CardListBlock from './CardListBlock.vue';
import ChartBlock from './ChartBlock.vue';
import ListBlock from './ListBlock.vue';
import ChipsBlock from './ChipsBlock.vue';
import TimelineBlock from './TimelineBlock.vue';
import BranchVisualizerBlock from './BranchVisualizerBlock.vue';
import TreeBlock from './TreeBlock.vue';
import ColumnBlock from './ColumnBlock.vue';

defineProps<{ subsection: SubSection; index: number }>();
</script>

<template>
  <div class="subsection">
    <h3 class="subsection-title">
      <span class="subsection-num">{{ index + 1 }}</span>
      {{ subsection.title }}
    </h3>
    <div v-if="subsection.content" class="space-y-6">
      <!-- 分栏是独立整体布局，存在分栏时只渲染分栏，避免与 blocks/聚合字段重复 -->
      <template v-if="subsection.content.columns && subsection.content.columns.length">
        <ColumnBlock :columns="subsection.content.columns" />
      </template>
      <template v-else>
        <!-- 使用 blocks 顺序渲染 -->
        <template v-for="(block, bi) in subsection.content.blocks" :key="bi">
          <DescriptionBlock v-if="block.type === 'description'" :items="block.data" />
          <StatsBlock v-if="block.type === 'stats'" :items="block.data" />
          <TableBlock v-if="block.type === 'tables'" :items="[block.data]" />
          <CardListBlock v-if="block.type === 'cards'" :items="[block.data]" />
          <ChartBlock v-if="block.type === 'charts'" :items="block.data" />
          <ListBlock v-if="block.type === 'list'" :list="block.data" />
          <ChipsBlock v-if="block.type === 'chips'" :items="block.data" />
          <TimelineBlock v-if="block.type === 'timeline'" :timeline="block.data" />
          <BranchVisualizerBlock v-if="block.type === 'branchVisualizer'" :viz="block.data" />
          <TreeBlock v-if="block.type === 'tree'" :data="block.data" />
        </template>
      </template>
    </div>
  </div>
</template>
