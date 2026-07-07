/**
 * EXMD（extended markdown）内容数据结构
 * 与 server/src/routes/render.routes.ts 返回结构对应
 */

export interface SiteInfo {
  slug: string;
}

export interface ColumnInfo {
  slug: string;
  name?: string;
}

export interface PageInfo {
  slug: string;
  title?: string;
}

export interface RenderResponse {
  site: SiteInfo;
  column?: ColumnInfo;
  page?: PageInfo;
  type: 'home' | 'category' | 'detail' | 'info';
  data: PageData;
}

export interface PageData {
  // 详情页结构
  page?: {
    title: string;
    description: string;
  };
  hero?: {
    title: string;
    tags: string[];
    brand_name?: string;
    subtitle?: string;
  };
  version?: string;
  lastModified?: string;
  introduction?: string;
  sections?: Section[];

  // 分类页结构
  recent?: RecentItem[];
  categories?: CategoryNode[];

  // 首页结构
  modules?: ModuleCard[];
}

export interface Section {
  id: string;
  title: string;
  subtitle?: string;
  type?: 'mixed' | 'text';
  content?: SectionContent;
}

export interface ContentBlock {
  type: 'description' | 'stats' | 'tables' | 'cards' | 'charts' | 'list' | 'chips' | 'branchVisualizer' | 'timeline';
  data: any;
}

export interface SectionContent {
  description?: string[];
  stats?: StatItem[];
  tables?: TableItem[];
  cards?: CardItem[][];
  charts?: ChartItem[];
  list?: ListBlock;
  chips?: ChipItem[];
  branchVisualizer?: BranchVisualizer;
  timeline?: TimelineBlock;
  subsections?: SubSection[];
  columns?: ColumnBlock[];
  blocks?: ContentBlock[];
}

export interface SubSection {
  title: string;
  content?: SubSectionContent;
}

export interface SubSectionContent {
  description?: string[];
  stats?: StatItem[];
  tables?: TableItem[];
  cards?: CardItem[][];
  charts?: ChartItem[];
  list?: ListBlock;
  chips?: ChipItem[];
  timeline?: TimelineBlock | TimelineBlock[];
  branchVisualizer?: BranchVisualizer | BranchVisualizer[];
  columns?: ColumnBlock[];
  blocks?: ContentBlock[];
}

export interface ColumnBlock {
  items?: string[];
  tables?: TableItem[];
  list?: ListBlock;
  cards?: CardItem[];
}

export interface StatItem {
  value: string;
  label: string;
}

export interface TableItem {
  headers: string[];
  rows: string[][];
}

export interface CardItem {
  headline: string;
  supporting: string;
  detail?: string[];
  image?: string;
}

export interface ChartItem {
  type: 'bar' | 'pie' | 'chinaMap' | 'line';
  id: string;
  title?: string;
  subType?: 'donut' | 'normal';
  xAxis?: string[];
  data?: number[];
  color?: string;
  // 饼图
  data2?: { value: number; name: string; color?: string }[];
}

export interface ListBlock {
  title: string;
  items: { icon: string; title: string; subtitle: string }[];
}

export interface ChipItem {
  label: string;
  accent?: boolean;
}

export interface BranchVisualizer {
  periods: string[];
  branches: {
    name: string;
    levels: number[];
    descriptions: string[];
  }[];
}

export interface TimelineBlock {
  title: string;
  items: {
    date: string;
    title: string;
    subtitle?: string;
    description?: (string | string[])[];
    image?: string;
  }[];
}

export interface RecentItem {
  title: string;
  subtitle?: string;
  desc?: string;
  link: string;
}

export interface CategoryNode {
  name: string;
  subCategories?: {
    name: string;
    links: { title: string; url: string }[];
  }[];
  links?: { title: string; url: string }[];
}

export interface ModuleCard {
  id: string;
  title: string;
  subtitle?: string;
  description?: string;
  image?: string;
  link: string;
  color?: string;
}
