import { css } from '@emotion/css';
import { useForm } from 'react-hook-form';
import { useParams } from 'react-router-dom-v5-compat';

import { GrafanaTheme2 } from '@grafana/data';
import { selectors as e2eSelectors } from '@grafana/e2e-selectors/src';
import { t } from '@grafana/i18n';
import { Button, Field, Input, Spinner, useStyles2 } from '@grafana/ui';
import { InnerBox, LoginLayout } from 'app/core/components/Login/LoginLayout';
import { useQueryParams } from 'app/core/hooks/useQueryParams';
import { validEmailRegex } from 'app/features/dashboard/components/ShareModal/SharePublicDashboard/SharePublicDashboardUtils';

import { useRequestAccessMutation } from './api/emailSharingApi';
import { getRequestAccessText } from './utils';

const formStyles = css({
  justifyContent: 'center',
  width: '100%',
});

interface FormData {
  email: string;
}

const selectors = e2eSelectors.pages.RequestViewAccess;

const RequestViewAccessPage = () => {
  const styles = useStyles2(getStyles);
  const { accessToken = '' } = useParams<{ accessToken: string }>();
  const [{ error }] = useQueryParams();

  const [requestAccess, { isLoading, isSuccess }] = useRequestAccessMutation();
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<FormData>({
    mode: 'onSubmit',
  });

  const bodyText = getRequestAccessText(error ? String(error) : undefined);

  const onSubmit = async (data: FormData) => {
    await requestAccess({ accessToken, email: data.email }).unwrap();
    reset();
  };

  return (
    <LoginLayout
      branding={{
        loginTitle: bodyText.title,
        loginSubtitle: bodyText.description,
        hideFooter: true,
      }}
    >
      <InnerBox>
        <form className={formStyles} onSubmit={handleSubmit(onSubmit)}>
          <Field
            label={t('public-dashboards.request-view-access-page.label-email', 'Email')}
            error={errors?.email?.message}
            invalid={!!errors.email}
          >
            <Input
              data-testid={selectors.recipientInput}
              placeholder={t('public-dashboards.request-view-access-page.placeholder-email', 'email')}
              autoCapitalize="none"
              {...register('email', {
                required: t('public-dashboards.request-view-access-page.register-required-email', 'Email is required'),
                pattern: {
                  value: validEmailRegex,
                  message: t(
                    'public-dashboards.request-view-access-page.register-pattern-invalid-email',
                    'Invalid email'
                  ),
                },
              })}
            />
          </Field>
          <Button data-testid={selectors.submitButton} disabled={isSuccess} type="submit" className={formStyles}>
            {isSuccess
              ? t('public-dashboards.request-view-access-page.access-requested', 'Access requested')
              : t('public-dashboards.request-view-access-page.request-access', 'Request access')}{' '}
            {isLoading && <Spinner className={styles.loadingSpinner} />}
          </Button>
        </form>
      </InnerBox>
    </LoginLayout>
  );
};

const getStyles = (theme: GrafanaTheme2) => ({
  loadingSpinner: css({
    marginLeft: theme.spacing(1),
  }),
});

export default RequestViewAccessPage;
