import { t } from '@grafana/i18n';
import { Drawer, Icon, Stack, Text, Tooltip } from '@grafana/ui';

import { OnSelectQueryType } from '../../features/explore/QueryLibrary/types';

import { QueryLibrary } from './QueryLibrary/QueryLibrary';

type Props = {
  isOpen: boolean;
  // List of datasource names to filter query templates by
  activeDatasources: string[];
  close: () => void;
  onSelectQuery: OnSelectQueryType;
};

export const QUERY_LIBRARY_LOCAL_STORAGE_KEYS = {
  explore: {
    newButton: 'grafana.explore.query-library.newButton',
  },
};

/**
 * Drawer with query library feature. Handles its own state and should be included in some top level component.
 */
export function QueryLibraryDrawer({ isOpen, activeDatasources, close, onSelectQuery }: Props) {
  return (
    isOpen && (
      <Drawer
        title={
          <Stack alignItems="center">
            <Text element="h3">{t('query-library.drawer.title', 'Query library')}</Text>
            <Tooltip
              placement="right"
              content={t(`query-library.drawer.tooltip`, 'Right now, each organization can save up to 1000 queries')}
            >
              <Icon name="info-circle" />
            </Tooltip>
          </Stack>
        }
        onClose={close}
        scrollableContent={false}
      >
        <QueryLibrary activeDatasources={activeDatasources} onSelectQuery={onSelectQuery} />
      </Drawer>
    )
  );
}
