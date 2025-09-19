import { css } from '@emotion/css';

import { GrafanaTheme2 } from '@grafana/data';
import { Trans, t } from '@grafana/i18n';
import { Stack, Text, useStyles2 } from '@grafana/ui';

import { Spec } from '../api/clients/banners/v0alpha1';

import { Banner } from './Banner';

export type BannerPreviewProps = Pick<Spec, 'message' | 'variant'>;

export function BannerPreview({ message, variant }: BannerPreviewProps) {
  const styles = useStyles2(getStyles);

  return (
    <Stack direction={'column'} width={'100%'} gap={2}>
      <Text variant="h3">
        <Trans i18nKey="banner.preview.title">Preview</Trans>
      </Text>
      <div className={styles.container}>
        <Banner
          message={
            message || t('banner.preview.message.default', 'Update this preview by modifying the message field.')
          }
          variant={variant}
        />
      </div>
    </Stack>
  );
}

const getStyles = (theme: GrafanaTheme2) => {
  return {
    container: css({
      backgroundColor: theme.colors.background.canvas,
    }),
  };
};
