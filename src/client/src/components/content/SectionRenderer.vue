<script setup lang="ts">
import type { Section, ContentBlock } from '@/types/content';
import DescriptionBlock from './DescriptionBlock.vue';
import StatsBlock from './StatsBlock.vue';
import TableBlock from './TableBlock.vue';
import CardListBlock from './CardListBlock.vue';
import ChartBlock from './ChartBlock.vue';
import TimelineBlock from './TimelineBlock.vue';
import ListBlock from './ListBlock.vue';
import ChipsBlock from './ChipsBlock.vue';
import BranchVisualizerBlock from './BranchVisualizerBlock.vue';
import SubSectionBlock from './SubSectionBlock.vue';
import ColumnBlock from './ColumnBlock.vue';

const props = defineProps<{ section: Section; index: number }>();

function renderBlock(block: ContentBlock) {
  switch (block.type) {
    case 'description':
      return { component: DescriptionBlock, props: { items: block.data }, show: true };
    case 'stats':
      return { component: StatsBlock, props: { items: block.data }, show: true };
    case 'tables':
      return { component: TableBlock, props: { items: [block.data] }, show: true };
    case 'cards':
      return { component: CardListBlock, props: { items: [block.data] }, show: true };
    case 'charts':
      return { component: ChartBlock, props: { items: block.data }, show: true };
    case 'list':
      return { component: ListBlock, props: { list: block.data }, show: true };
    case 'chips':
      return { component: ChipsBlock, props: { items: block.data }, show: true };
    case 'branchVisualizer':
      return { component: BranchVisualizerBlock, props: { viz: block.data }, show: true };
    case 'timeline':
      return { component: TimelineBlock, props: { timeline: block.data }, show: true };
    default:
      return { component: null, props: {}, show: false };
  }
}
</script>

<template>
  <section
    :id="section.id"
    class="section scroll-mt-20"
    :data-subtitle="section.subtitle"
  >
    <header class="section-header">
      <span class="section-num">{{ String(index + 1).padStart(2, '0') }}</span>
      <div class="section-title-wrap">
        <h2 class="section-title">{{ section.title }}</h2>
        <p v-if="section.subtitle" class="section-subtitle">{{ section.subtitle }}</p>
      </div>
    </header>

    <div v-if="section.content" class="space-y-6">
      <!-- 优先使用 blocks 顺序渲染 -->
      <template v-if="section.content.blocks && section.content.blocks.length">
        <template v-for="(block, bi) in section.content.blocks" :key="bi">
          <DescriptionBlock v-if="block.type === 'description'" :items="block.data" />
          <StatsBlock v-if="block.type === 'stats'" :items="block.data" />
          <TableBlock v-if="block.type === 'tables'" :items="[block.data]" />
          <CardListBlock v-if="block.type === 'cards'" :items="[block.data]" />
          <ChartBlock v-if="block.type === 'charts'" :items="block.data" />
          <ListBlock v-if="block.type === 'list'" :list="block.data" />
          <ChipsBlock v-if="block.type === 'chips'" :items="block.data" />
          <BranchVisualizerBlock v-if="block.type === 'branchVisualizer'" :viz="block.data" />
          <TimelineBlock v-if="block.type === 'timeline'" :timeline="block.data" />
        </template>
      </template>
      <!-- 兼容旧数据：回退到原有分组渲染 -->
      <template v-else>
        <DescriptionBlock v-if="section.content.description" :items="section.content.description" />
        <StatsBlock v-if="section.content.stats" :items="section.content.stats" />
        <TableBlock v-if="section.content.tables" :items="section.content.tables" />
        <CardListBlock v-if="section.content.cards" :items="section.content.cards" />
        <ChartBlock v-if="section.content.charts" :items="section.content.charts" />
        <ListBlock v-if="section.content.list" :list="section.content.list" />
        <ChipsBlock v-if="section.content.chips" :items="section.content.chips" />
        <BranchVisualizerBlock v-if="section.content.branchVisualizer" :viz="section.content.branchVisualizer" />
        <TimelineBlock v-if="section.content.timeline" :timeline="section.content.timeline" />
      </template>
      <ColumnBlock v-if="section.content.columns" :columns="section.content.columns" />
      <SubSectionBlock
        v-for="(sub, idx) in section.content.subsections"
        :key="idx"
        :subsection="sub"
        :index="idx"
      />
    </div>
  </section>
</template>
