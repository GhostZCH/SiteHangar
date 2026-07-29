import type { ChartItem } from '@/types/content';

export function buildBarOption(c: ChartItem): any {
  return {
    title: c.title ? { text: c.title, left: 'center', textStyle: { fontSize: 14 } } : undefined,
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: c.xAxis || [] },
    yAxis: { type: 'value' },
    series: [
      {
        type: 'bar',
        data: c.data || [],
        itemStyle: { color: c.color || '#6366f1' },
        barWidth: '50%',
      },
    ],
  };
}
