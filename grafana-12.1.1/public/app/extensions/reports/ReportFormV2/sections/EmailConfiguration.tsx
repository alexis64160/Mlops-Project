import { css } from '@emotion/css';
import { useFormContext } from 'react-hook-form';

import { GrafanaTheme2 } from '@grafana/data';
import { Trans, t } from '@grafana/i18n';
import { Checkbox, Field, Icon, Input, Stack, TextArea, TextLink, useStyles2 } from '@grafana/ui';
import { ReportFormV2 } from 'app/extensions/types/reports';

import { SETTINGS_URL } from '../../constants';
import { selectors } from '../../e2e-selectors/selectors';
import { formSchemaValidationRules } from '../../utils/validation';
import ReportSection from '../ReportSection';

import { SectionProps } from './types';

export default function EmailConfiguration({ open, onToggle }: SectionProps) {
  const styles = useStyles2(getStyles);

  const {
    register,
    formState: { errors },
  } = useFormContext<ReportFormV2>();

  return (
    <ReportSection
      label={t('share-report.email-configuration.section-title', 'Email settings')}
      dataTestId={selectors.components.ReportFormDrawer.EmailConfiguration.header}
      contentDataTestId={selectors.components.ReportFormDrawer.EmailConfiguration.content}
      isOpen={open}
      onToggle={onToggle}
    >
      <Field
        label={t('share-report.email-configuration.subject-label', 'Email subject')}
        description={t(
          'share-report.email-configuration.subject-description',
          'The report name will be used as the email subject if this field is left empty'
        )}
      >
        <Input
          id="subject-input"
          {...register('subject')}
          type="text"
          data-testid={selectors.components.ReportFormDrawer.EmailConfiguration.subjectInput}
        />
      </Field>
      <Field label={t('share-report.email-configuration.message-label', 'Message')}>
        <TextArea
          id="message-input"
          {...register('message')}
          rows={4}
          placeholder={t('share-report.email-configuration.message-placeholder', 'Enter a message')}
          data-testid={selectors.components.ReportFormDrawer.EmailConfiguration.messageInput}
        />
      </Field>
      <Field
        label={t('share-report.email-configuration.reply-to-label', 'Reply-to-email address')}
        invalid={!!errors.replyTo}
        error={errors.replyTo?.message}
      >
        <Input
          id="reply-to-input"
          {...register('replyTo', formSchemaValidationRules().replyTo)}
          // eslint-disable-next-line @grafana/i18n/no-untranslated-strings
          placeholder="your.address@company.com"
          type="text"
          data-testid={selectors.components.ReportFormDrawer.EmailConfiguration.replyToInput}
        />
      </Field>
      <Stack direction="column" gap={1} alignItems={'start'}>
        <Checkbox
          {...register('addDashboardUrl')}
          label={t('share-report.email-configuration.add-dashboard-url-label', 'Include dashboard link')}
          data-testid={selectors.components.ReportFormDrawer.EmailConfiguration.addDashboardUrlCheckbox}
        />
        <Checkbox
          {...register('addDashboardImage')}
          label={t('share-report.email-configuration.add-dashboard-image-label', 'Embed dashboard image')}
          data-testid={selectors.components.ReportFormDrawer.EmailConfiguration.addDashboardImageCheckbox}
        />
        <div className={styles.imageSettings}>
          <Stack gap={1} alignItems="center">
            <Icon name="info-circle" />
            <Trans i18nKey="share-report.email-configuration.dashboard-image-settings-description">
              The dashboard image settings can be adjusted in the general
              <TextLink variant="bodySmall" href={SETTINGS_URL} inline external>
                report settings
              </TextLink>
            </Trans>
          </Stack>
        </div>
      </Stack>
    </ReportSection>
  );
}

const getStyles = (theme: GrafanaTheme2) => ({
  imageSettings: css({
    fontSize: theme.typography.bodySmall.fontSize,
    color: theme.colors.text.secondary,
    marginTop: theme.spacing(1),
  }),
});
