import { useLocalStorage } from 'react-use';

import { t } from '@grafana/i18n';
import { DataQuery } from '@grafana/schema';
import { Badge } from '@grafana/ui';
import { QueryOperationAction } from 'app/core/components/QueryOperationRow/QueryOperationAction';
import { useQueryLibraryContext } from 'app/features/explore/QueryLibrary/QueryLibraryContext';

import { QUERY_LIBRARY_LOCAL_STORAGE_KEYS } from './QueryLibraryDrawer';
import { selectors } from './e2e-selectors/selectors';

interface Props {
  query: DataQuery;
}

export function SaveQueryButton({ query }: Props) {
  const { openAddQueryModal } = useQueryLibraryContext();

  const [showQueryLibraryBadgeButton, setShowQueryLibraryBadgeButton] = useLocalStorage(
    QUERY_LIBRARY_LOCAL_STORAGE_KEYS.explore.newButton,
    true
  );

  return showQueryLibraryBadgeButton ? (
    <Badge
      data-testid={selectors.components.saveQueryButton.button}
      text={t('query-operation.header.save-to-query-library-new', 'New: Save to query library')}
      icon="save"
      color="blue"
      onClick={() => {
        openAddQueryModal(query);
        setShowQueryLibraryBadgeButton(false);
      }}
      style={{ cursor: 'pointer' }}
    />
  ) : (
    <QueryOperationAction
      dataTestId={selectors.components.saveQueryButton.button}
      title={t('query-operation.header.save-to-query-library', 'Save to query library')}
      icon="save"
      onClick={() => {
        openAddQueryModal(query);
      }}
    />
  );
}
