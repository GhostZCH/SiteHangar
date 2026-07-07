import type { ChartItem } from '@/types/content';
import { buildBarOption } from './BarChartOption';
import { buildPieOption } from './PieChartOption';
import { buildLineOption } from './LineChartOption';
import { buildChinaMapOption } from './ChinaMapOption';

export function buildOption(c: ChartItem): any {
  switch (c.type) {
    case 'bar':
      return buildBarOption(c);
    case 'pie':
      return buildPieOption(c);
    case 'line':
      return buildLineOption(c);
    case 'chinaMap':
      return buildChinaMapOption(c);
    default:
      return {};
  }
}
