import { css } from '@emotion/css';

import { GrafanaTheme2 } from '@grafana/data';
import { Trans, t } from '@grafana/i18n';
import { featureEnabled, reportInteraction } from '@grafana/runtime';
import { LinkButton, useStyles2 } from '@grafana/ui';
import { UpgradeBox, UpgradeContentVertical } from 'app/core/components/Upgrade/UpgradeBox';
import { highlightTrial } from 'app/features/admin/utils';
import { ShareModalTabProps } from 'app/features/dashboard/components/ShareModal/types';
import { DashboardModel } from 'app/features/dashboard/state/DashboardModel';
import { DashboardScene } from 'app/features/dashboard-scene/scene/DashboardScene';

import { getNewReportUrl } from './utils/url';

interface Props extends Omit<ShareModalTabProps, 'dashboard'> {
  dashboard: DashboardModel | DashboardScene;
}
export const CreateReportTab = ({ dashboard, onDismiss }: Props) => {
  const styles = useStyles2(getStyles);

  const isReportsCreationDisabled = !featureEnabled('reports.creation');

  function onClickCreateReport() {
    reportInteraction('dashboards_sharing_report_create_clicked');
    onDismiss && onDismiss();
  }

  if (isReportsCreationDisabled) {
    return (
      <div className={styles.container}>
        <UpgradeBox featureName={'reporting'} featureId={'reporting-tab'} />
        <UpgradeContentVertical
          image={'reporting-email.png'}
          featureName={'reporting'}
          featureUrl={'https://grafana.com/docs/grafana/latest/enterprise/reporting'}
          description={t(
            'reports.create-report-tab.description-reporting-allows-automatically-generate-dashboards-grafana',
            'Reporting allows you to automatically generate PDFs from any of your dashboards and have Grafana email them to interested parties on a schedule.'
          )}
        />
      </div>
    );
  }

  return (
    <>
      {highlightTrial() && (
        <div className={styles.highlight}>
          <UpgradeBox
            featureId={'reporting-tab'}
            eventVariant={'trial'}
            featureName={'reporting'}
            text={t(
              'reports.create-report-tab.text-create-unlimited-reports-during-trial-grafana',
              'Create unlimited reports during your trial of Grafana Pro.'
            )}
          />
          <h3>
            <Trans i18nKey="reports.create-report-tab.get-started-with-reporting">Get started with reporting</Trans>
          </h3>
          <h6>
            <Trans i18nKey="reports.create-report-tab.description-reporting-allows-automatically-generate-dashboards-grafana">
              Reporting allows you to automatically generate PDFs from any of your dashboards and have Grafana email
              them to interested parties on a schedule.
            </Trans>
          </h6>
        </div>
      )}
      <LinkButton href={getNewReportUrl(dashboard)} onClick={onClickCreateReport} className={styles.button}>
        <Trans i18nKey="reports.create-report-tab.create-report-using-this-dashboard">
          Create report using this dashboard
        </Trans>
      </LinkButton>
      {highlightTrial() && (
        <LinkButton fill="text" href={'https://grafana.com/docs/grafana/latest/enterprise/reporting'}>
          <Trans i18nKey="reports.create-report-tab.learn-more">Learn more</Trans>
        </LinkButton>
      )}
    </>
  );
};

const getStyles = (theme: GrafanaTheme2) => {
  return {
    container: css({
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'flex-start',
    }),
    button: css({
      marginRight: theme.spacing(2),
    }),
    highlight: css({
      marginBottom: theme.spacing(3),

      h6: {
        fontWeight: theme.typography.fontWeightLight,
      },
    }),
  };
};
