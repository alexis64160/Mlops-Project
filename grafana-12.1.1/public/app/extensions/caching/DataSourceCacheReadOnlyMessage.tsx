import { t } from '@grafana/i18n';
import { Alert } from '@grafana/ui';

export function DataSourceCacheReadOnlyMessage() {
  return (
    <Alert severity="info" title={t('caching.alert.readonly.title', 'Provisioned data source')}>
      {t(
        'caching.alert.readonly.message',
        'This data source was added by config and caching cannot be modified using the UI. Please contact your server admin to update this data source.'
      )}
    </Alert>
  );
}
