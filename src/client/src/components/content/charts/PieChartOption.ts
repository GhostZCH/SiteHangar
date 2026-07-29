import type { ChartItem } from '@/types/content';

export function buildPieOption(c: ChartItem): any {
  return {
    title: c.title ? { text: c.title, left: 'center', textStyle: { fontSize: 14 } } : undefined,
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [
      {
        type: 'pie',
        radius: c.subType === 'donut' ? ['40%', '70%'] : '60%',
        data: c.data2 || [],
      },
    ],
  };
}
