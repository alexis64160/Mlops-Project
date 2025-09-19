import { Trans, t } from '@grafana/i18n';
import { getAppEvents } from '@grafana/runtime';
import { Button, IconButton, Stack } from '@grafana/ui';
import { useQueryLibraryContext } from 'app/features/explore/QueryLibrary/QueryLibraryContext';

import { notifyApp } from '../../../core/actions';
import { createSuccessNotification } from '../../../core/copy/appNotification';
import { OnSelectQueryType } from '../../../features/explore/QueryLibrary/types';
import { dispatch } from '../../../store/store';
import { ShowConfirmModalEvent } from '../../../types/events';
import {
  useDeleteQueryTemplateMutation,
  useUpdateQueryTemplateMutation,
} from '../../api/clients/querylibrary/v0alpha1';
import { QueryLibraryInteractions } from '../QueryLibraryAnalyticsEvents';
import { selectors } from '../e2e-selectors/selectors';
import { QueryTemplateRow } from '../types';
import { canEditQuery } from '../utils/identity';

export interface QueryLibraryActionsProps {
  onSelectQuery: OnSelectQueryType;
  selectedQueryRow: QueryTemplateRow;
  isEditingQuery: boolean;
}
export function QueryLibraryActions({ onSelectQuery, selectedQueryRow, isEditingQuery }: QueryLibraryActionsProps) {
  const [deleteQueryTemplate] = useDeleteQueryTemplateMutation();
  const [editQueryTemplate] = useUpdateQueryTemplateMutation();
  const { openAddQueryModal } = useQueryLibraryContext();
  const { isLocked } = selectedQueryRow;

  const onDeleteQuery = (queryUid: string) => {
    const performDelete = async (queryUid: string) => {
      await deleteQueryTemplate({
        name: queryUid,
      }).unwrap();
      dispatch(notifyApp(createSuccessNotification(t('query-library.notifications.query-deleted', 'Query deleted'))));
      QueryLibraryInteractions.deleteQueryClicked();
    };

    getAppEvents().publish(
      new ShowConfirmModalEvent({
        title: t('query-library.delete-modal.title', 'Delete query'),
        text: t(
          'query-library.delete-modal.body-text',
          "You're about to remove this query from the query library. This action cannot be undone. Do you want to continue?"
        ),
        yesText: t('query-library.delete-modal.confirm-button', 'Delete query'),
        icon: 'trash-alt',
        onConfirm: () => performDelete(queryUid),
      })
    );
  };

  const onDuplicateQuery = () => {
    openAddQueryModal(selectedQueryRow.query, {
      title: `${selectedQueryRow.title} ${t('query-library.actions.duplicate-query-title-copy', 'Copy')}`,
      isDuplicating: true,
    });
    QueryLibraryInteractions.duplicateQueryClicked();
  };

  const handleLockToggle = () => {
    if (!selectedQueryRow.uid) {
      return;
    }
    QueryLibraryInteractions.lockQueryClicked(!isLocked);
    return editQueryTemplate({
      name: selectedQueryRow.uid || '',
      patch: {
        spec: {
          isLocked: !isLocked,
        },
      },
    });
  };

  return (
    <Stack wrap="wrap" justifyContent="space-between">
      <Stack wrap="wrap" justifyContent="flex-start">
        <IconButton
          data-testid={selectors.components.queryLibraryDrawer.delete}
          variant="secondary"
          name="trash-alt"
          onClick={() => onDeleteQuery(selectedQueryRow.uid ?? '')}
          tooltip={t('query-library.actions.delete-query-button', 'Delete query')}
          disabled={selectedQueryRow.isLocked || !canEditQuery(selectedQueryRow)}
        />
        <IconButton
          data-testid={selectors.components.queryLibraryDrawer.lock}
          variant={isLocked ? 'primary' : 'secondary'}
          name={isLocked ? 'lock' : 'unlock'}
          onClick={handleLockToggle}
          tooltip={
            isLocked
              ? t('query-library.actions.unlock-query-button', 'Unlock query')
              : t('query-library.actions.lock-query-button', 'Lock query')
          }
          disabled={!canEditQuery(selectedQueryRow) || isEditingQuery}
        />
        <IconButton
          data-testid={selectors.components.queryLibraryDrawer.duplicate}
          variant="secondary"
          name="copy"
          onClick={onDuplicateQuery}
          tooltip={t('query-library.actions.duplicate-query-button', 'Duplicate query')}
        />
      </Stack>

      <Button
        data-testid={selectors.components.queryLibraryDrawer.confirm}
        onClick={() => onSelectQuery(selectedQueryRow.query)}
      >
        <Trans i18nKey="query-library.actions.select-query-button">Select query</Trans>
      </Button>
    </Stack>
  );
}
