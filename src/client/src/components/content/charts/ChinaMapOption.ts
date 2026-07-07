import type { ChartItem } from '@/types/content';

export function buildChinaMapOption(c: ChartItem): any {
  // 中国地图暂未实现，返回空配置
  return {
    title: c.title ? { text: c.title, left: 'center', textStyle: { fontSize: 14 } } : undefined,
  };
}
