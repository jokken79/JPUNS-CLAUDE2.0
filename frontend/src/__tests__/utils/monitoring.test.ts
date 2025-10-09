import { getMetricsSummary, recordMetric, resetMetrics } from '../../utils/monitoring';

describe('monitoring utilities', () => {
  afterEach(() => {
    resetMetrics();
  });

  it('aggregates metrics correctly', () => {
    recordMetric('render', 10);
    recordMetric('render', 20);
    const summary = getMetricsSummary();
    expect(summary.render.count).toBe(2);
    expect(summary.render.average).toBeCloseTo(15);
  });
});
