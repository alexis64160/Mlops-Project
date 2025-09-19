import { Controller, useForm } from 'react-hook-form';
import { useAsync } from 'react-use';

import { AppEvents } from '@grafana/data';
import { Trans, t } from '@grafana/i18n';
import { DataSourcePicker, getAppEvents, getDataSourceSrv } from '@grafana/runtime';
import { Button, Field, Checkbox, Input, Modal, TagsInput, TextArea } from '@grafana/ui';
import { getQueryDisplayText } from 'app/core/utils/richHistory';

import { useCreateQueryTemplateMutation } from '../api/clients/querylibrary/v0alpha1';

import { selectors } from './e2e-selectors/selectors';
import { QueryTemplate } from './types';
import { convertAddQueryTemplateCommandToDataQuerySpec } from './utils/mappers';
import { AddQueryTemplateCommand } from './utils/types';
import { useDatasource } from './utils/useDatasource';

type Props = {
  onCancel: () => void;
  onSave: (isSuccess: boolean) => void;
  templateData?: QueryTemplate;
};

export type QueryDetails = {
  title: string;
  description: string;
  tags: string[];
  isVisible: boolean;
};

const getInstructions = (isAdd: boolean) => {
  return isAdd
    ? t(
        'explore.query-template-modal.add-info',
        `You're about to save this query. Once saved, you can easily access it from the query library for future use and reference.`
      )
    : t(
        'explore.query-template-modal.edit-info',
        `You're about to edit this query. Once saved, you can easily access it from the query library for future use and reference.`
      );
};

export const QueryTemplateForm = ({ onCancel, onSave, templateData }: Props) => {
  const { register, handleSubmit, control } = useForm<QueryDetails>({
    defaultValues: {
      title: templateData?.title || t('explore.query-library.default-title', 'New query'),
      description: templateData?.description,
      isVisible: templateData?.isVisible ?? false,
    },
  });

  const [addQueryTemplate] = useCreateQueryTemplateMutation();

  const datasource = useDatasource(templateData?.query.datasource);
  // this is an array to support multi query templates sometime in the future
  const queries = templateData?.query !== undefined ? [templateData?.query] : [];

  const TAGS_ID = 'tags';

  const handleAddQueryTemplate = async (addQueryTemplateCommand: AddQueryTemplateCommand) => {
    return addQueryTemplate({
      queryTemplate: convertAddQueryTemplateCommandToDataQuerySpec(addQueryTemplateCommand),
    })
      .unwrap()
      .then(() => {
        getAppEvents().publish({
          type: AppEvents.alertSuccess.name,
          payload: [t('explore.query-library.query-template-added', 'Query successfully saved to the library')],
        });
        return true;
      })
      .catch(() => {
        getAppEvents().publish({
          type: AppEvents.alertError.name,
          payload: [
            t('explore.query-library.query-template-add-error', 'Error attempting to save this query to the library'),
          ],
        });
        return false;
      });
  };

  const onSubmit = async (data: QueryDetails) => {
    const temporaryDefaultTitle = data.title || t('explore.query-library.default-title', 'New query');

    if (templateData?.query) {
      handleAddQueryTemplate({
        title: temporaryDefaultTitle,
        description: data.description,
        isVisible: data.isVisible,
        targets: [templateData?.query],
        tags: data.tags,
      }).then((isSuccess) => {
        onSave(isSuccess);
      });
    }
  };

  const { value: queryText } = useAsync(async () => {
    const promises = queries.map(async (query, i) => {
      const datasource = await getDataSourceSrv().get(query.datasource);
      return datasource?.getQueryDisplayText?.(query) || getQueryDisplayText(query);
    });
    return Promise.all(promises);
  });

  return (
    <form data-testid={selectors.components.saveQueryModal.modal} onSubmit={handleSubmit(onSubmit)}>
      <p>{getInstructions(templateData === undefined)}</p>
      {queryText &&
        queryText.map((queryString, i) => (
          <Field key={`query-${i}`} label={t('explore.query-template-modal.query', 'Query')}>
            <TextArea readOnly={true} value={queryString}></TextArea>
          </Field>
        ))}
      {templateData?.query && (
        <>
          <Field label={t('explore.query-template-modal.data-source-name', 'Data source name')}>
            <DataSourcePicker current={datasource?.uid} disabled={true} />
          </Field>
          <Field label={t('explore.query-template-modall.data-source-type', 'Data source type')}>
            <Input disabled={true} defaultValue={datasource?.meta.name}></Input>
          </Field>
        </>
      )}
      <Field label={t('explore.query-template-modal.title', 'Title')}>
        <Input
          data-testid={selectors.components.saveQueryModal.title}
          id="query-template-title"
          autoFocus={true}
          {...register('title')}
        ></Input>
      </Field>
      <Field label={t('explore.query-template-modal.description', 'Description')}>
        <Input
          data-testid={selectors.components.saveQueryModal.description}
          id="query-template-description"
          {...register('description')}
        ></Input>
      </Field>
      <Field label={t('explore.query-template-modal.tags', 'Tags')}>
        <Controller
          name={TAGS_ID}
          control={control}
          defaultValue={templateData?.tags ?? []}
          render={({ field: { ref, value, onChange, ...field } }) => {
            return (
              <TagsInput
                {...field}
                id={TAGS_ID}
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
      <Field>
        <Checkbox
          label={t('query-library.query-details.make-query-visible', 'Share query with all users')}
          id="query-template-is-visible"
          {...register('isVisible')}
        />
      </Field>
      <Modal.ButtonRow>
        <Button
          data-testid={selectors.components.saveQueryModal.cancel}
          variant="secondary"
          onClick={() => onCancel()}
          fill="outline"
        >
          <Trans i18nKey="explore.query-library.cancel">Cancel</Trans>
        </Button>
        <Button data-testid={selectors.components.saveQueryModal.confirm} variant="primary" type="submit">
          <Trans i18nKey="explore.query-library.save">Save</Trans>
        </Button>
      </Modal.ButtonRow>
    </form>
  );
};
