import { css } from '@emotion/css';
import { useId, useMemo, useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import Skeleton from 'react-loading-skeleton';

import { dateTime, GrafanaTheme2 } from '@grafana/data';
import { Trans, t } from '@grafana/i18n';
import {
  Avatar,
  Box,
  Button,
  Checkbox,
  Field,
  IconButton,
  Input,
  Spinner,
  Stack,
  TagsInput,
  Text,
  useStyles2,
} from '@grafana/ui';
import { attachSkeleton, SkeletonComponent } from '@grafana/ui/unstable';
import { generatedAPI } from 'app/extensions/api/clients/querylibrary/v0alpha1/endpoints.gen';
import icnDatasourceSvg from 'img/icn-datasource.svg';

import { useUpdateQueryTemplateMutation } from '../../api/clients/querylibrary/v0alpha1';
import { QueryLibraryInteractions, dirtyFieldsToAnalyticsObject } from '../QueryLibraryAnalyticsEvents';
import { QueryTemplateRow } from '../types';
import { canEditQuery } from '../utils/identity';
import { EditQueryTemplateCommand } from '../utils/types';
import { useDatasource } from '../utils/useDatasource';

export type QueryDetails = {
  title: string;
  description: string;
  isVisible: boolean;
  tags: string[];
};

export interface QueryDetailsProps {
  query: QueryTemplateRow;
  editingQuery: boolean;
  setEditingQuery: (editingQuery: boolean) => void;
}

function QueryLibraryDetailsComponent({ query, editingQuery, setEditingQuery }: QueryDetailsProps) {
  const { isFetching } = generatedAPI.endpoints.listQueryTemplate.useQueryState({});
  const datasourceApi = useDatasource(query.datasourceRef);
  const formattedTime = dateTime(query.createdAtTimestamp).toLocaleString();
  const { isLocked } = query;

  const AUTHOR_ID = useId();
  const DATASOURCE_ID = useId();
  const DESCRIPTION_ID = useId();
  const DATE_ADDED_ID = useId();
  const IS_VISIBLE_ID = useId();
  const TITLE_INPUT_ID = useId();
  const TAGS_ID = 'tags';
  const styles = useStyles2(getStyles);

  const {
    control,
    register,
    handleSubmit,
    reset,
    formState: { dirtyFields, isDirty },
  } = useForm<QueryDetails>({
    defaultValues: {
      title: query.title,
      description: query.description,
      isVisible: query.isVisible,
    },
  });

  // Resets React Form Hook with new default values when selecting new query in library
  useEffect(() => {
    reset({
      title: query.title,
      description: query.description,
      isVisible: query.isVisible,
      tags: query.tags ?? [],
    });
  }, [query, reset]);

  const [editQueryTemplate] = useUpdateQueryTemplateMutation();

  const handleEditQueryTemplate = (editQueryTemplateCommand: EditQueryTemplateCommand) => {
    return editQueryTemplate({
      name: editQueryTemplateCommand.uid,
      patch: {
        spec: editQueryTemplateCommand.partialSpec,
      },
    });
  };

  const onSubmit = async (data: QueryDetails) => {
    setEditingQuery(false);
    QueryLibraryInteractions.saveEditClicked(dirtyFieldsToAnalyticsObject(dirtyFields));
    if (query?.uid) {
      handleEditQueryTemplate({ uid: query.uid, partialSpec: { ...data } });
    }
  };

  const editButton = useMemo(() => {
    if (!editingQuery) {
      return (
        <IconButton
          onClick={() => {
            QueryLibraryInteractions.editQueryClicked();
            setEditingQuery(true);
          }}
          name="pen"
          disabled={isLocked || !canEditQuery(query)}
          tooltip={t('query-library.query-details.edit-button', 'Edit query')}
        />
      );
    }
    return null;
  }, [editingQuery, isLocked, setEditingQuery, query]);

  const saveAndCancelButtons = useMemo(() => {
    if (editingQuery) {
      return (
        <Box display="flex" gap={1} alignItems="center">
          <Button variant="primary" type="submit" disabled={!isDirty}>
            <Trans i18nKey="explore.query-library.save">Save</Trans>
          </Button>
          <Button
            variant="secondary"
            onClick={() => {
              reset({
                title: query.title,
                description: query.description,
                isVisible: query.isVisible,
                tags: query.tags ?? [],
              });
              QueryLibraryInteractions.cancelEditClicked();
              setEditingQuery(false);
            }}
          >
            <Trans i18nKey="explore.query-library.cancel">Cancel</Trans>
          </Button>
        </Box>
      );
    }
    return null;
  }, [editingQuery, isDirty, setEditingQuery, reset, query]);

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Box minWidth={0}>
        <Box
          display="flex"
          gap={1}
          alignItems="center"
          justifyContent="space-between"
          marginBottom={editingQuery ? 0 : 2}
        >
          <Stack gap={1} alignItems="center" minWidth={0} flex={1}>
            <img
              className={styles.logo}
              src={datasourceApi?.meta.info.logos.small || icnDatasourceSvg}
              alt={datasourceApi?.type}
            />
            {editingQuery ? (
              <Box flex={1} marginBottom={2}>
                <Field label={t('query-library.query-details.title', 'Title')} noMargin>
                  <Stack direction="row">
                    <Input data-testid="query-title-input" id={TITLE_INPUT_ID} {...register('title')} />
                    {saveAndCancelButtons}
                  </Stack>
                </Field>
              </Box>
            ) : (
              <Text variant="h5" truncate>
                {query.title ?? ''}
              </Text>
            )}
          </Stack>
          {isFetching && <Spinner />}
          {editButton}
        </Box>
        <code className={styles.query}>{query.queryText}</code>
        <Field label={t('query-library.query-details.datasource', 'Data source')}>
          <Input readOnly id={DATASOURCE_ID} value={query.datasourceName} />
        </Field>
        <Field label={t('query-library.query-details.description', 'Description')}>
          <Input id={DESCRIPTION_ID} readOnly={!editingQuery} {...register('description')} />
        </Field>
        <Field label={t('query-library.query-details.tags', 'Tags')} htmlFor={TAGS_ID}>
          <Controller
            name={TAGS_ID}
            control={control}
            defaultValue={query.tags ?? []}
            render={({ field: { ref, value, onChange, ...field } }) => {
              return (
                <TagsInput
                  {...field}
                  id={TAGS_ID}
                  disabled={!editingQuery}
                  autoColors={false}
                  onChange={(tags) => {
                    onChange(Array.from(new Set(tags)).sort());
                  }}
                  tags={value ? Array.from(value) : []}
                />
              );
            }}
          />
        </Field>
        <Field label={t('query-library.query-details.author', 'Author')}>
          <Input
            readOnly
            id={AUTHOR_ID}
            prefix={
              <Box marginRight={0.5}>
                <Avatar
                  width={2}
                  height={2}
                  src={query.user?.avatarUrl || 'https://secure.gravatar.com/avatar'}
                  alt=""
                />
              </Box>
            }
            value={query.user?.displayName}
          />
        </Field>
        <Field label={t('query-library.query-details.date-added', 'Date added')}>
          <Input readOnly id={DATE_ADDED_ID} value={formattedTime} />
        </Field>
        <Field>
          <Checkbox
            label={t('query-library.query-details.make-query-visible', 'Share query with all users')}
            id={IS_VISIBLE_ID}
            disabled={!editingQuery}
            {...register('isVisible')}
          />
        </Field>
      </Box>
    </form>
  );
}

const QueryLibraryDetailsSkeleton: SkeletonComponent = ({ rootProps }) => {
  const skeletonStyles = useStyles2(getSkeletonStyles);
  return (
    <Box minWidth={0} {...rootProps}>
      <Stack direction="column" gap={2}>
        <Stack gap={1} alignItems="center" minWidth={0}>
          <Skeleton circle width={24} height={24} containerClassName={skeletonStyles.icon} />
          <Skeleton width={120} />
        </Stack>

        <Skeleton height={32} />

        <Box>
          <Skeleton width={60} />
          <Skeleton height={32} />
        </Box>

        <Box>
          <Skeleton width={60} />
          <Skeleton height={32} />
        </Box>

        <Box>
          <Skeleton width={60} />
          <Skeleton height={32} />
        </Box>
      </Stack>
    </Box>
  );
};

export const QueryLibraryDetails = attachSkeleton(QueryLibraryDetailsComponent, QueryLibraryDetailsSkeleton);

const getSkeletonStyles = () => ({
  icon: css({
    display: 'block',
    lineHeight: 1,
  }),
});

const getStyles = (theme: GrafanaTheme2) => ({
  query: css({
    backgroundColor: theme.colors.action.disabledBackground,
    borderRadius: theme.shape.radius.default,
    display: 'block',
    margin: theme.spacing(0, 0, 2, 0),
    overflowWrap: 'break-word',
    padding: theme.spacing(1),
    whiteSpace: 'pre-wrap',
  }),
  logo: css({
    width: '24px',
  }),
});
