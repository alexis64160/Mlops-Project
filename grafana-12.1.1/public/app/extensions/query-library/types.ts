import { DataQuery, DataSourceRef } from '@grafana/schema';

import { User } from './utils/types';

export type QueryTemplate = {
  query: DataQuery;
  datasourceName?: string;
  title?: string;
  description?: string;
  tags?: string[];
  isLocked?: boolean;
  isVisible?: boolean;
  queryText?: string;
  datasourceRef?: DataSourceRef | null;
  datasourceType?: string;
  createdAtTimestamp?: number;
  user?: User;
  uid?: string;
};

export type QueryTemplateRow = QueryTemplate & {
  index: string;
};
