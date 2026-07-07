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
      <!-- 优先使用 blocks 顺序渲染 -->
      <template v-if="subsection.content.blocks && subsection.content.blocks.length">
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
        </template>
      </template>
      <!-- 兼容旧数据：回退到原有分组渲染 -->
      <template v-else>
        <DescriptionBlock v-if="subsection.content.description" :items="subsection.content.description" />
        <StatsBlock v-if="subsection.content.stats" :items="subsection.content.stats" />
        <TableBlock v-if="subsection.content.tables" :items="subsection.content.tables" />
        <CardListBlock v-if="subsection.content.cards" :items="subsection.content.cards" />
        <ChartBlock v-if="subsection.content.charts" :items="subsection.content.charts" />
        <ListBlock v-if="subsection.content.list" :list="subsection.content.list" />
        <ChipsBlock v-if="subsection.content.chips" :items="subsection.content.chips" />
        <TimelineBlock v-if="subsection.content.timeline" :timeline="subsection.content.timeline" />
        <BranchVisualizerBlock v-if="subsection.content.branchVisualizer" :viz="subsection.content.branchVisualizer" />
      </template>
      <ColumnBlock v-if="subsection.content.columns" :columns="subsection.content.columns" />
    </div>
  </div>
</template>
