/**
 * 后端管理接口返回的数据结构
 */

export interface SiteDomain {
  id: number;
  hostname: string;
  siteSlug: string;
  primary: boolean;
  note: string | null;
  createdAt: string;
}

export interface Column {
  id: number;
  siteSlug: string;
  slug: string;
  name: string;
  description: string | null;
  icon: string | null;
  order: number;
  enabled: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface PageVersion {
  id: number;
  pageId: number;
  version: string;
  changelog: string | null;
  createdAt: string;
}

export interface Page {
  id: number;
  moduleId: number;
  slug: string;
  title: string;
  description: string | null;
  heroTitle: string | null;
  heroTags: string | null; // JSON
  type: 'home' | 'category' | 'detail';
  status: 'draft' | 'published';
  currentVersion: string | null;
  order: number;
  versions?: PageVersion[];
  module?: Pick<Column, 'slug' | 'siteSlug' | 'name'>;
  _count?: { versions: number };
  createdAt: string;
  updatedAt: string;
}

export interface Config {
  id: 1;
  adminPassword: string;
  siteName: string;
  siteDescription: string | null;
  updatedAt: string;
}
