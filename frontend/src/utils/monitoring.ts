/** Lightweight client-side monitoring helpers. */

type MetricRecord = {
  name: string;
  value: number;
  timestamp: number;
};

const metrics: MetricRecord[] = [];

export const recordMetric = (name: string, value: number) => {
  metrics.push({ name, value, timestamp: Date.now() });
};

export const getMetricsSummary = () => {
  const summary: Record<string, { count: number; average: number }> = {};
  metrics.forEach((metric) => {
    const entry = summary[metric.name] ?? { count: 0, average: 0 };
    entry.count += 1;
    entry.average = entry.average + (metric.value - entry.average) / entry.count;
    summary[metric.name] = entry;
  });
  return summary;
};

export const resetMetrics = () => {
  metrics.length = 0;
};
