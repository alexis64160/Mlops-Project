import { css } from '@emotion/css';
import { useEffect, useState } from 'react';
import { Controller } from 'react-hook-form';
import { connect, ConnectedProps } from 'react-redux';

import {
  DataQuery,
  DataSourceInstanceSettings,
  getDefaultRelativeTimeRange,
  GrafanaTheme2,
  isEmptyObject,
  ScopedVars,
  VariableHide,
  VariableModel,
} from '@grafana/data';
import { Trans, t } from '@grafana/i18n';
import { getDataSourceSrv, isFetchError, reportInteraction } from '@grafana/runtime';
import {
  Alert,
  AlertVariant,
  Button,
  Field,
  Form,
  Icon,
  InlineField,
  Input,
  Label,
  Modal,
  RelativeTimeRangePicker,
  Switch,
  useStyles2,
} from '@grafana/ui';
import { getModalStyles } from '@grafana/ui/internal';
import { QueryOperationAction } from 'app/core/components/QueryOperationRow/QueryOperationAction';
import { contextSrv } from 'app/core/core';
import { variableAdapters } from 'app/features/variables/adapters';
import { hasOptions } from 'app/features/variables/guard';
import { getVariables } from 'app/features/variables/state/selectors';

import { getLicenseToken } from '../licensing/state/api';
import { LicenseToken } from '../licensing/types';
import { IdDataQuery, RecordedQuery, AccessControlAction, EnterpriseStoreState } from '../types';

import { recordedQueriesDeprecationNotice } from './RecordedQueriesConfig';
import { timeIntervals, TimeSelect } from './TimeSelect';
import { saveRecordedQuery, testRecordedQuery } from './state/actions';

function mapStateToProps(state: EnterpriseStoreState) {
  return {
    variables: getVariables(state),
  };
}

interface OwnProps {
  query?: DataQuery;
  queries?: Array<Partial<DataQuery>>;
  onAddQuery?: (query: DataQuery) => void;
  onChangeDataSource?: (ds: DataSourceInstanceSettings) => void;
  dataSource?: DataSourceInstanceSettings;
}

const connector = connect(mapStateToProps);
export type Props = ConnectedProps<typeof connector> & OwnProps;

interface DocLinkProps {
  href: string;
  trackingSource?: string;
}
const DocLink = ({ href, trackingSource }: DocLinkProps) => {
  const styles = useStyles2(getStyles);
  return (
    <a
      href={href}
      className={styles.docsLink}
      target="_blank"
      rel="noreferrer"
      onClick={() =>
        reportInteraction('cloud_user_clicked_create_recorded_query_modal_documentation_icon', {
          source: trackingSource,
        })
      }
    >
      <Icon name="info-circle" />
    </a>
  );
};

interface SaveAddRecordedQuery {
  name: string;
  description: string;
  aggregationType: string;
  interval: number;
  range: number;
  isCount: boolean;
}

export const CreateRecordedQueryUnconnected = ({ query, queries, dataSource, variables: propVariables }: Props) => {
  const [isOpen, setIsOpen] = useState(false);
  const [token, setToken] = useState<LicenseToken | undefined>();
  const [alertSeverity, setAlertSeverity] = useState<AlertVariant>('info');
  const [alertMessage, setAlertMessage] = useState('');
  const modalStyles = useStyles2(getModalStyles);
  const styles = useStyles2(getStyles);

  useEffect(() => {
    const setTokenIfAccess = async () => {
      if (contextSrv.hasPermission(AccessControlAction.LicensingRead)) {
        setToken(await getLicenseToken().catch(() => undefined));
      }
    };
    setTokenIfAccess();
  }, []);

  const closeModal = () => {
    setAlertMessage('');
    setAlertSeverity('info');
    setIsOpen(false);
  };

  const getRecordedQuery = async (data: SaveAddRecordedQuery) => {
    try {
      return await toRecordedQuery(data, variables);
    } catch (error) {
      setAlertSeverity('error');
      if (isFetchError(error)) {
        setAlertMessage(error.data.message);
      }
      return;
    }
  };

  const submitForm = async (data: SaveAddRecordedQuery) => {
    const rq = await getRecordedQuery(data);
    if (!rq) {
      return;
    }

    saveRecordedQuery(rq)
      .then(() => {
        setAlertSeverity('success');
        setAlertMessage(
          t(
            'recorded-queries.create-recorded-query-unconnected.success-alert-message',
            'Your new recorded query is recording successfully!'
          )
        );
        reportInteraction('cloud_user_created_recorded_query');
      })
      .catch((error) => {
        setAlertSeverity('error');
        setAlertMessage(error.data.message);
      });
  };

  const submitTest = async (data: SaveAddRecordedQuery) => {
    const rq = await getRecordedQuery(data);
    if (!rq) {
      return;
    }

    testRecordedQuery(rq)
      .then((value) => {
        setAlertSeverity('info');
        setAlertMessage(value.data.message);
      })
      .catch((error) => {
        setAlertSeverity('error');
        setAlertMessage(error.data.message);
      });
  };

  const toRecordedQuery = async (data: SaveAddRecordedQuery, scopedVars: ScopedVars | {}): Promise<RecordedQuery> => {
    const rq = {
      target_ref_id: query ? query.refId : '',
      name: data.name,
      description: data.description,
      interval: data.interval,
      range: data.range,
      count: data.isCount,
      active: true,
    } as RecordedQuery;
    const queriesWithVars = queries?.map(async (q) => {
      const dataSourceName = q.datasource || dataSource?.name;
      const ds = await getDataSourceSrv().get(dataSourceName);
      const interpolatedTarget = ds.interpolateVariablesInQueries
        ? ds.interpolateVariablesInQueries([q as DataQuery], { ...scopedVars })[0]
        : q;

      const idQ = interpolatedTarget as IdDataQuery;
      idQ.datasourceId = ds ? ds.id : -1;
      if (idQ.datasource === undefined) {
        if (q.datasource !== undefined && q.datasource !== null) {
          idQ.datasource = q.datasource;
        } else if (ds) {
          idQ.datasource = { uid: ds.uid, type: ds.type };
        }
      }
      return idQ;
    });
    rq.queries = queriesWithVars ? await Promise.all(queriesWithVars) : [];
    return rq;
  };

  const variables = propVariables?.filter((variable) => variable.hide !== VariableHide.hideVariable);
  const title = (
    <h2 className={modalStyles.modalHeaderTitle}>
      <Trans i18nKey="recorded-queries.create-recorded-query-unconnected.title-create-recorded-query">
        Create recorded query
      </Trans>
      <DocLink
        href="https://grafana.com/docs/grafana/latest/enterprise/recorded-queries/#create-a-recorded-query"
        trackingSource="modal-title"
      />
    </h2>
  );

  const syncButton =
    alertSeverity !== 'success' ? (
      <div
        aria-label={t(
          'recorded-queries.create-recorded-query-unconnected.sync-button.aria-label-test-the-recorded-query',
          'Test the recorded query'
        )}
      >
        <Icon name="sync" />
      </div>
    ) : undefined;

  const doneButton =
    alertSeverity === 'success' ? (
      <Button
        type="button"
        variant="primary"
        onClick={closeModal}
        aria-label={t(
          'recorded-queries.create-recorded-query-unconnected.done-button.aria-label-close-recording-query-button',
          'Close recording query button'
        )}
      >
        <Trans i18nKey="recorded-queries.create-recorded-query-unconnected.done-button.close">Close</Trans>
      </Button>
    ) : (
      <Button
        type="button"
        variant="secondary"
        onClick={closeModal}
        fill="outline"
        aria-label={t(
          'recorded-queries.create-recorded-query-unconnected.done-button.aria-label-cancel-recording-query-button',
          'Cancel recording query button'
        )}
      >
        <Trans i18nKey="recorded-queries.create-recorded-query-unconnected.done-button.cancel">Cancel</Trans>
      </Button>
    );

  const renderAlertMessage = () => {
    switch (alertSeverity) {
      case 'info':
        if (alertMessage === '') {
          return <></>;
        }
        return (
          <>
            <Trans i18nKey="recorded-queries.create-recorded-query-unconnected.results-alert-message">Results: </Trans>
            <pre>{alertMessage}</pre>
          </>
        );
      default:
        return <>{alertMessage}</>;
    }
  };

  return (
    <>
      <QueryOperationAction
        title={t(
          'recorded-queries.create-recorded-query-unconnected.title-create-recorded-query',
          'Create recorded query'
        )}
        icon="record-audio"
        onClick={() => {
          setIsOpen(true);
          reportInteraction('cloud_user_clicked_create_recorded_query_icon');
        }}
      />
      <Modal isOpen={isOpen} title={title} onDismiss={closeModal} className={styles.modal}>
        {recordedQueriesDeprecationNotice()}
        <Form onSubmit={submitForm} validateOn="all">
          {({ register, errors, control, getValues }) => (
            <>
              <Field
                label={t('recorded-queries.create-recorded-query-unconnected.label-name', 'Name')}
                description={t(
                  'recorded-queries.create-recorded-query-unconnected.description-give-this-query-a-name',
                  'Give this query a name'
                )}
                invalid={!!errors.name}
                error={errors.name?.message}
                required={true}
              >
                <Input
                  {...register('name', {
                    required: {
                      value: true,
                      message: t(
                        'recorded-queries.create-recorded-query-unconnected.message.name-is-required',
                        'Name is required'
                      ),
                    },
                  })}
                  id="add-recorded-query-name"
                  autoFocus
                />
              </Field>
              <Field
                label={t('recorded-queries.create-recorded-query-unconnected.label-description', 'Description')}
                description={t(
                  'recorded-queries.create-recorded-query-unconnected.description-provide-a-description-for-this-query',
                  'Provide a description for this query'
                )}
              >
                <Input {...register('description')} id="add-recorded-query-desc" />
              </Field>
              <div className={styles.timeSelect}>
                <Controller
                  name="interval"
                  control={control}
                  defaultValue={timeIntervals[0].value}
                  render={({ field: { ref, value, onChange, ...field } }) => {
                    return (
                      <TimeSelect
                        label={t('recorded-queries.create-recorded-query-unconnected.label-interval', 'Interval')}
                        description={t(
                          'recorded-queries.create-recorded-query-unconnected.description-decide-often-record-query',
                          'Decide how often to record this query'
                        )}
                        value={value}
                        onChange={onChange}
                      />
                    );
                  }}
                />
              </div>
              <div className={styles.timeSelect}>
                <Controller
                  name="range"
                  control={control}
                  defaultValue={getDefaultRelativeTimeRange().from}
                  render={({ field: { ref, value, onChange, ...field } }) => {
                    const desc = (
                      <>
                        {t(
                          'recorded-queries.create-recorded-query-unconnected.query-relative-time-range',
                          "Select this query's relative time range"
                        )}
                        <DocLink
                          href="https://grafana.com/docs/grafana/latest/dashboards/time-range-controls/#time-units-and-relative-ranges"
                          trackingSource="time-range"
                        />
                      </>
                    );
                    const label = (
                      <Label description={desc}>
                        <Trans i18nKey="recorded-queries.create-recorded-query-unconnected.label.relative-time-range">
                          Relative Time Range
                        </Trans>{' '}
                        *
                      </Label>
                    );
                    return (
                      <Field label={label} invalid={!!errors.range} error={errors.name?.message} required={true}>
                        <RelativeTimeRangePicker
                          timeRange={{ from: value, to: 0 }}
                          onChange={(r) => onChange(r.from)}
                        />
                      </Field>
                    );
                  }}
                />
              </div>
              {variables?.length > 0 ? (
                <Field
                  label={t(
                    'recorded-queries.create-recorded-query-unconnected.label-template-variables',
                    'Template variables'
                  )}
                  description={t(
                    'recorded-queries.create-recorded-query-unconnected.description-select-value-template-variable',
                    'Select a value for each template variable'
                  )}
                >
                  <>
                    {variables.map((variable) => {
                      const { picker: Picker, setValue } = variableAdapters.get(variable.type);
                      return (
                        <InlineField label={variable.name} key={variable.name} labelWidth={16}>
                          <Picker
                            onVariableChange={(updated: VariableModel) => {
                              if (hasOptions(updated) && !isEmptyObject(updated.current)) {
                                setValue(updated, updated.current);
                              }
                            }}
                            variable={variable}
                            readOnly={false}
                          />
                        </InlineField>
                      );
                    })}
                  </>
                </Field>
              ) : null}
              <Field
                label={t(
                  'recorded-queries.create-recorded-query-unconnected.label-count-query-results',
                  'Count query results'
                )}
                description={
                  <>
                    {t(
                      'recorded-queries.create-recorded-query-unconnected.count-rows-returned',
                      'Count the rows returned from this query'
                    )}
                    <DocLink
                      href="https://grafana.com/docs/grafana/latest/enterprise/recorded-queries/#create-a-recorded-query"
                      trackingSource="count-field"
                    />
                  </>
                }
              >
                <Switch {...register('isCount')} id="add-recorded-query-count" />
              </Field>
              <Alert
                className={styles.testQuery}
                severity={alertSeverity}
                title={
                  alertSeverity === 'success'
                    ? t('recorded-queries.create-recorded-query-unconnected.alert-severity-succesful', 'Successful')
                    : t(
                        'recorded-queries.create-recorded-query-unconnected.alert-severity-test',
                        'Test this recorded query'
                      )
                }
                buttonContent={syncButton}
                onRemove={alertSeverity !== 'success' ? () => submitTest(getValues()) : undefined} // undefined ensures no 'x' button
              >
                {renderAlertMessage()}
                {alertMessage === 'An unknown issue is preventing the system from processing your query.' &&
                  contactSupportMessage(token)}
              </Alert>
              <Modal.ButtonRow>
                {doneButton}
                {alertSeverity !== 'success' && (
                  <Button
                    type="submit"
                    aria-label={t(
                      'recorded-queries.create-recorded-query-unconnected.aria-label-start-recording-query-button',
                      'Start recording query button'
                    )}
                  >
                    <Trans i18nKey="recorded-queries.create-recorded-query-unconnected.start-recording-query">
                      Start recording query
                    </Trans>
                  </Button>
                )}
              </Modal.ButtonRow>
            </>
          )}
        </Form>
      </Modal>
    </>
  );
};

const contactSupportMessage = (token?: LicenseToken) => {
  let href = 'https://grafana.com/contact';
  if (token && token.slug && token.lid) {
    href = `https://grafana.com/orgs/${token.slug}/tickets?support=licensing&licenseId=${token.lid}`;
  }

  return (
    <>
      <Trans i18nKey="recorded-queries.create-recorded-query-unconnected.contact-support">
        To submit a support ticket to Grafana Labs, complete the <a href={href}>Contact Grafana Labs</a>
      </Trans>
    </>
  );
};

const getStyles = (theme: GrafanaTheme2) => {
  return {
    modal: css({
      width: '550px',
    }),
    testQuery: css({
      marginTop: theme.spacing(3),
    }),
    timeSelect: css({
      width: '50%',
    }),
    docsLink: css({
      marginLeft: theme.spacing(0.5),
    }),
  };
};

export const CreateRecordedQuery = connector(CreateRecordedQueryUnconnected);
