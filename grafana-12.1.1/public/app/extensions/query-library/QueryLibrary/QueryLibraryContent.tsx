import { css } from '@emotion/css';
import { Fragment, useEffect, useState } from 'react';

import { GrafanaTheme2 } from '@grafana/data';
import { Trans, t } from '@grafana/i18n';
import { Box, Divider, EmptyState, ScrollContainer, Stack, useStyles2 } from '@grafana/ui';
import { attachSkeleton, SkeletonComponent } from '@grafana/ui/unstable';
import { generatedAPI } from 'app/extensions/api/clients/querylibrary/v0alpha1/endpoints.gen';

import { OnSelectQueryType } from '../../../features/explore/QueryLibrary/types';
import { QueryTemplateRow } from '../types';

import { QueryLibraryActions } from './QueryLibraryActions';
import { QueryLibraryDetails } from './QueryLibraryDetails';
import { QueryLibraryItem } from './QueryLibraryItem';

export interface QueryLibraryContentProps {
  isFiltered?: boolean;
  onSelectQuery: OnSelectQueryType;
  queryRows: QueryTemplateRow[];
}

function QueryLibraryContentComponent({ isFiltered, onSelectQuery, queryRows }: QueryLibraryContentProps) {
  const [isEditingQuery, setIsEditingQuery] = useState(false);
  const [selectedQueryRowIndex, setSelectedQueryRowIndex] = useState<number>(0);

  const isEmpty = queryRows.length === 0;
  const styles = useStyles2(getStyles);

  const { isSuccess, isFetching } = generatedAPI.endpoints.listQueryTemplate.useQueryState({});

  useEffect(() => {
    if (isSuccess && !isFetching) {
      setSelectedQueryRowIndex((prevState) => (queryRows[prevState] ? prevState : prevState - 1));
    }
  }, [queryRows, isSuccess, isFetching]);

  if (isEmpty) {
    // search miss
    return isFiltered ? (
      <EmptyState message={t('query-library.not-found.title', 'No results found')} variant="not-found">
        <Trans i18nKey="query-library.not-found.message">Try adjusting your search or filter criteria</Trans>
      </EmptyState>
    ) : (
      // true empty state
      <EmptyState
        message={t('query-library.empty-state.title', "You haven't saved any queries to the library yet")}
        variant="call-to-action"
      >
        <Trans i18nKey="query-library.empty-state.message">
          Start adding them from Explore or when editing a dashboard
        </Trans>
      </EmptyState>
    );
  }

  return (
    <Stack flex={1} gap={0} minHeight={0}>
      <Box display="flex" flex={1} minWidth={0}>
        <ScrollContainer>
          <Stack direction="column" gap={0} flex={1} minWidth={0} role="radiogroup">
            {queryRows.map((queryRow, index) => (
              <Fragment key={queryRow.uid}>
                <QueryLibraryItem
                  isSelected={queryRows[selectedQueryRowIndex]?.uid === queryRow.uid}
                  onSelectQueryRow={() => {
                    setSelectedQueryRowIndex(index);
                    setIsEditingQuery(false);
                  }}
                  queryRow={queryRow}
                />
                <Divider spacing={0} />
              </Fragment>
            ))}
          </Stack>
        </ScrollContainer>
      </Box>
      <Divider direction="vertical" spacing={0} />
      <Box display="flex" flex={2} minWidth={0}>
        <ScrollContainer>
          <Box
            direction="column"
            display="flex"
            flex={1}
            paddingBottom={0}
            paddingLeft={2}
            paddingRight={1}
            paddingTop={2}
          >
            {queryRows[selectedQueryRowIndex] && (
              <>
                <Box flex={1}>
                  <QueryLibraryDetails
                    query={queryRows[selectedQueryRowIndex]}
                    editingQuery={isEditingQuery}
                    setEditingQuery={setIsEditingQuery}
                  />
                </Box>
                <div className={styles.actions}>
                  <QueryLibraryActions
                    selectedQueryRow={queryRows[selectedQueryRowIndex]}
                    onSelectQuery={onSelectQuery}
                    isEditingQuery={isEditingQuery}
                  />
                </div>
              </>
            )}
          </Box>
        </ScrollContainer>
      </Box>
    </Stack>
  );
}

const QueryLibraryContentSkeleton: SkeletonComponent = ({ rootProps }) => {
  return (
    <Stack flex={1} gap={0} minHeight={0} {...rootProps}>
      <Box display="flex" flex={1} minWidth={0}>
        <Stack direction="column" flex={1} gap={0} minWidth={0}>
          {new Array(5).fill(0).map((_, index) => (
            <Fragment key={index}>
              <QueryLibraryItem.Skeleton />
              <Divider spacing={0} />
            </Fragment>
          ))}
        </Stack>
      </Box>
      <Divider direction="vertical" spacing={0} />
      <Box display="flex" flex={2} minWidth={0}>
        <Box
          direction="column"
          display="flex"
          flex={1}
          paddingBottom={0}
          paddingLeft={2}
          paddingRight={1}
          paddingTop={2}
        >
          <QueryLibraryDetails.Skeleton />
        </Box>
      </Box>
    </Stack>
  );
};

export const QueryLibraryContent = attachSkeleton(QueryLibraryContentComponent, QueryLibraryContentSkeleton);

const getStyles = (theme: GrafanaTheme2) => ({
  actions: css({
    background: theme.colors.background.primary,
    bottom: 0,
    padding: theme.spacing(1, 0),
    position: 'sticky',
    zIndex: 1,
  }),
});
