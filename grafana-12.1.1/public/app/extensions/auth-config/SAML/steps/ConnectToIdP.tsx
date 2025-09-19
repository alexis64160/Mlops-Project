import { css } from '@emotion/css';
import { useState, FormEvent } from 'react';
import { Controller, useForm } from 'react-hook-form';
import { connect, ConnectedProps } from 'react-redux';

import { GrafanaTheme2 } from '@grafana/data';
import { Trans, t } from '@grafana/i18n';
import { ClipboardButton, Field, FileUpload, Input, RadioButtonGroup, TextArea, useStyles2 } from '@grafana/ui';

import { EnterpriseStoreState, SAMLFormData, SAMLStepKey } from '../../../types';
import SAMLForm from '../SAMLForm';
import { SAML_ACS_URL, SAML_Metadata_URL, SAML_SLO_URL } from '../constants';
import { settingsUpdated, setMetadataValueType } from '../state/reducers';

type ConnectIdPData = Pick<SAMLFormData, 'idpMetadataUrl' | 'idpMetadataPath' | 'idpMetadata' | 'metadataValueType'>;

function mapStateToProps(state: EnterpriseStoreState) {
  return {
    samlSettings: state.samlConfig.samlSettings,
    metadataValueType: state.samlConfig.metadataValueType,
  };
}

const mapDispatchToProps = {
  settingsUpdated,
  setMetadataValueType,
};

const connector = connect(mapStateToProps, mapDispatchToProps);
export type Props = ConnectedProps<typeof connector>;

const metadataOptions = [
  { label: 'URL for metadata', value: 'url' },
  { label: 'Base64-encoded content', value: 'base64' },
  { label: 'Path to file', value: 'path' },
];

export const ConnectToIdPUnconnected = ({
  samlSettings,
  metadataValueType,
  settingsUpdated,
  setMetadataValueType,
}: Props): JSX.Element => {
  const styles = useStyles2(getStyles);

  const { idpMetadataUrl, idpMetadataPath, idpMetadata, singleLogout } = samlSettings;
  const {
    handleSubmit,
    control,
    register,
    watch,
    getValues,
    setValue,
    formState: { errors, isDirty },
  } = useForm({
    mode: 'onBlur',
    defaultValues: {
      idpMetadataUrl,
      idpMetadataPath,
      idpMetadata,
      metadataValueType: metadataValueType || 'url',
    },
  });

  const [metadataTypeLock, setMetadataTypeLock] = useState(
    [idpMetadataUrl, idpMetadataPath, idpMetadata].filter(Boolean).length !== 0
  );

  const watchMetadataValueType = watch('metadataValueType');

  const validateMetadaTypes = (): boolean | string => {
    let countMetadataDefinedTypes = ['idpMetadataUrl', 'idpMetadataPath', 'idpMetadata']
      .map(watch)
      .filter(Boolean).length;
    return countMetadataDefinedTypes === 1
      ? true
      : t('saml-connect-to-idp.validate-idp-metadata.require-one', 'One metadata type should be defined');
  };

  const updateMetadataTypeLock = ({ currentTarget: { value } }: FormEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setMetadataTypeLock(!!value);
  };

  const onSubmit = ({ metadataValueType, ...settings }: ConnectIdPData) => {
    if (isDirty) {
      settingsUpdated({
        ...samlSettings,
        ...settings,
      });
      setMetadataValueType(metadataValueType);
    }
  };

  const onFileUpload = async (event: FormEvent<HTMLInputElement>) => {
    if (event?.currentTarget?.files?.length) {
      const fileContent = event.currentTarget.files[0];
      const text = await fileContent.text();
      const base64Content = btoa(text);
      setValue('idpMetadata', base64Content, { shouldDirty: true });
    }
  };

  return (
    <SAMLForm
      activeStep={SAMLStepKey.ConnectToIdP}
      onSubmit={handleSubmit(onSubmit)}
      confirmRedirect={isDirty}
      getFormData={getValues}
      className={styles.wrapper}
      label={t(
        'auth-config.connect-to-idp-unconnected.label-connect-grafana-with-identity-provider',
        'Connect Grafana with Identity Provider'
      )}
    >
      <div className={styles.externalBorder}>
        <div className={styles.doubleSideContainer}>
          <div className={styles.internalContainer}>
            <div className={styles.internalContainerHeader}>
              <div className={styles.stepNumber}>
                <Trans i18nKey="auth-config.connect-to-idp-unconnected.step-number-1">1</Trans>
              </div>
              <h4>
                <Trans i18nKey="auth-config.connect-to-idp-unconnected.configure-idp-using-grafana-metadata">
                  Configure IdP using Grafana metadata
                </Trans>
              </h4>
            </div>
            <div className={styles.internalContainerBody}>
              <div className={styles.description}>
                <Trans i18nKey="auth-config.connect-to-idp-unconnected.description-setup-idp">
                  To configure your identity provider (IdP) you will need the Grafana metadata URL. All below endpoints
                  must be reachable by your Identity Provider (IdP).
                </Trans>
              </div>
              <Field
                label={t('auth-config.connect-to-idp-unconnected.label-sp-metadata-url-entity-id', 'Metadata URL')}
                description={t(
                  'auth-config.connect-to-idp-unconnected.description-sp-metadata-url-entity-id',
                  'SP metadata URL / SP Entity ID'
                )}
              >
                <div className={styles.inputWithCopyToClipboard}>
                  <Input width={50} id="spMetadata" value={SAML_Metadata_URL} disabled />
                  <ClipboardButton
                    className={styles.copyToClipboardButton}
                    variant="primary"
                    size="md"
                    icon="copy"
                    getText={() => SAML_Metadata_URL}
                  >
                    <Trans i18nKey="auth-config.connect-to-idp-unconnected.copy">Copy</Trans>
                  </ClipboardButton>
                </div>
              </Field>
              <Field
                label={t(
                  'auth-config.connect-to-idp-unconnected.label-assertion-consumer-service-url',
                  'Assertion Consumer Service URL'
                )}
                description={t(
                  'auth-config.connect-to-idp-unconnected.description-assertion-consumer-service-url',
                  'Assertion consumer service POST binding URL'
                )}
              >
                <div className={styles.inputWithCopyToClipboard}>
                  <Input width={50} id="spACS" value={SAML_ACS_URL} disabled />
                  <ClipboardButton
                    className={styles.copyToClipboardButton}
                    variant="primary"
                    size="md"
                    icon="copy"
                    getText={() => SAML_ACS_URL}
                  >
                    <Trans i18nKey="auth-config.connect-to-idp-unconnected.copy">Copy</Trans>
                  </ClipboardButton>
                </div>
              </Field>
              {singleLogout && (
                <Field
                  label={t('auth-config.connect-to-idp-unconnected.label-slo-url', 'SLO URL')}
                  description={t(
                    'auth-config.connect-to-idp-unconnected.description-slo-url',
                    'Logout service redirect binding URL / Logout service POST binding URL'
                  )}
                >
                  <div className={styles.inputWithCopyToClipboard}>
                    <Input width={50} id="spSLO" value={SAML_SLO_URL} disabled />
                    <ClipboardButton
                      className={styles.copyToClipboardButton}
                      variant="primary"
                      size="md"
                      icon="copy"
                      getText={() => SAML_SLO_URL}
                    >
                      <Trans i18nKey="auth-config.connect-to-idp-unconnected.copy">Copy</Trans>
                    </ClipboardButton>
                  </div>
                </Field>
              )}
            </div>
          </div>
          <div className={styles.internalContainer}>
            <div className={styles.internalContainerHeader}>
              <div className={styles.stepNumber}>
                <Trans i18nKey="auth-config.connect-to-idp-unconnected.step-number-2">2</Trans>
              </div>
              <h4>
                <Trans i18nKey="auth-config.connect-to-idp-unconnected.finish-configuring-grafana-using-idp-data">
                  Finish configuring Grafana using IdP data
                </Trans>
              </h4>
            </div>
            <div className={styles.internalContainerBody}>
              <div className={styles.description}>
                <Trans i18nKey="auth-config.connect-to-idp-unconnected.description-setup-required">
                  Visit your IdP&apos;s configuration panel, add new app and use metadata from step one to connect with
                  Grafana. You will need to copy your IdP&apos;s metadata and provide it below. Test connection and copy
                  assertion labels/values.
                </Trans>
              </div>
              <Field
                label={t('auth-config.connect-to-idp-unconnected.label-idp-metadata', "IdP's metadata ")}
                description={t(
                  'auth-config.connect-to-idp-unconnected.description-idp-metadata',
                  'Must be the same as set-up or required by IdP.'
                )}
              >
                <Controller
                  name={'metadataValueType'}
                  control={control}
                  render={({ field: { ref, ...field } }) => {
                    return <RadioButtonGroup {...field} options={metadataOptions} disabled={metadataTypeLock} />;
                  }}
                />
              </Field>
              {watchMetadataValueType === 'url' && (
                <Field
                  label={t('auth-config.connect-to-idp-unconnected.label-metadata-url', 'Metadata URL')}
                  description={t(
                    'auth-config.connect-to-idp-unconnected.description-metadata-url',
                    'URL for IdP metadata'
                  )}
                  invalid={!!errors.idpMetadataUrl}
                  error={errors.idpMetadataUrl?.message}
                >
                  <Input
                    {...register('idpMetadataUrl', {
                      onChange: updateMetadataTypeLock,
                      validate: validateMetadaTypes,
                    })}
                    id="metadataUrl"
                    width={60}
                  />
                </Field>
              )}
              {watchMetadataValueType === 'base64' && (
                <>
                  <Field
                    label={t(
                      'auth-config.connect-to-idp-unconnected.label-baseencoded-idp-metadata',
                      'Base64-encoded IdP metadata'
                    )}
                    invalid={!!errors.idpMetadata}
                    error={errors.idpMetadata?.message}
                  >
                    <Controller
                      name={'idpMetadata'}
                      control={control}
                      rules={{
                        validate: validateMetadaTypes,
                      }}
                      render={({ field: { onChange, ...field } }) => (
                        <TextArea
                          {...field}
                          id="metadataBase64"
                          width={60}
                          onChange={(e) => {
                            onChange(e);
                            updateMetadataTypeLock(e);
                          }}
                        />
                      )}
                    />
                  </Field>
                  <FileUpload showFileName={false} onFileUpload={onFileUpload} className={styles.uploadButton} />
                </>
              )}
              {watchMetadataValueType === 'path' && (
                <Field
                  label={t(
                    'auth-config.connect-to-idp-unconnected.label-path-to-idp-metadata-file',
                    'Path to IdP metadata file'
                  )}
                  invalid={!!errors.idpMetadataPath}
                  error={errors.idpMetadataPath?.message}
                >
                  <Input
                    {...register('idpMetadataPath', {
                      onChange: updateMetadataTypeLock,
                      validate: validateMetadaTypes,
                    })}
                    id="metadataPath"
                    width={60}
                  />
                </Field>
              )}
              <div className={styles.description}>
                <Trans i18nKey="auth-config.connect-to-idp-unconnected.description-test-connection">
                  If you want to test the connection from your IdP&apos;s panel make sure to allow IdP initiated login
                  and provide the relay state information.
                </Trans>
              </div>
            </div>
          </div>
        </div>
        <div className={styles.internalContainerHeader}>
          <div className={styles.stepNumber}>
            <Trans i18nKey="auth-config.connect-to-idp-unconnected.step-number-3">3</Trans>
          </div>
          <h4>
            <Trans i18nKey="auth-config.connect-to-idp-unconnected.configure-assertions-group-mappings">
              Configure assertions, group, group and org mappings in the next step.
            </Trans>
          </h4>
        </div>
      </div>
    </SAMLForm>
  );
};

const getStyles = (theme: GrafanaTheme2) => {
  return {
    wrapper: css({
      width: '100%',
    }),
    description: css({
      color: theme.colors.text.secondary,
      marginBottom: theme.spacing(2),
      fontSize: theme.typography.bodySmall.fontSize,
    }),
    externalBorder: css({
      borderRadius: theme.shape.borderRadius(1),
      border: `1px solid ${theme.colors.border.medium}`,
    }),
    doubleSideContainer: css({
      display: 'flex',
      flexDirection: 'row',
      justifyContent: 'space-around',
    }),
    internalContainer: css({
      flex: '1 1 0',
      borderBottom: `1px solid ${theme.colors.border.medium}`,
      '&:first-child': {
        borderRight: `1px solid ${theme.colors.border.medium}`,
      },
    }),
    internalContainerHeader: css({
      display: 'flex',
      justifyContent: 'center',
      borderBottom: `1px solid ${theme.colors.border.medium}`,
      padding: theme.spacing(2),
      textAlign: 'center',
      h4: {
        marginBottom: 0,
      },
    }),
    internalContainerBody: css({
      padding: theme.spacing(2),
    }),
    stepNumber: css({
      border: `1px solid ${theme.colors.background.secondary}`,
      borderRadius: theme.shape.borderRadius(4),
      background: theme.colors.background.secondary,
      color: theme.colors.text.secondary,
      width: theme.spacing(3),
      height: theme.spacing(3),
      marginRight: theme.spacing(1),
      fontWeight: theme.typography.fontWeightBold,
    }),
    copyToClipboardButton: css({
      borderTopLeftRadius: 'unset',
      borderBottomLeftRadius: 'unset',
    }),
    inputWithCopyToClipboard: css({
      padding: 0,
      display: 'flex',
    }),
    uploadButton: css({
      marginBottom: theme.spacing(2),
    }),
  };
};

export default connector(ConnectToIdPUnconnected);
