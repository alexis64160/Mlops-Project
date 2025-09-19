import { DataQuery } from '@grafana/schema';

import { TemplateQueryTemplate } from '../../api/clients/querylibrary/v0alpha1';

export type DataQueryTarget = {
  variables: object; // TODO: Detect variables in #86838
  properties: DataQuery;
};

export type DataQueryPartialSpec = Partial<TemplateQueryTemplate>;

export type QueryTemplate = {
  uid: string;
  title: string;
  description?: string;
  tags?: string[];
  isLocked?: boolean;
  isVisible?: boolean;
  targets: DataQuery[];
  createdAtTimestamp: number;
  user?: User;
};

export type AddQueryTemplateCommand = {
  title: string;
  description?: string;
  tags: string[];
  isVisible?: boolean;
  targets: DataQuery[];
  isLocked?: boolean;
};

export type EditQueryTemplateCommand = {
  uid: string;
  partialSpec: DataQueryPartialSpec;
};

export type DeleteQueryTemplateCommand = {
  uid: string;
};

export type User = {
  uid: string;
  displayName?: string;
  avatarUrl?: string;
};
