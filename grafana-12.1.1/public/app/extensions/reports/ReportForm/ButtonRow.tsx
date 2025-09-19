import { css } from '@emotion/css';
import { forwardRef, useImperativeHandle, useRef } from 'react';

import { GrafanaTheme2 } from '@grafana/data';
import { Trans } from '@grafana/i18n';
import { Button, useStyles2 } from '@grafana/ui';

import { StepKey } from '../../types';
import { selectors } from '../e2e-selectors/selectors';
import { getNextStep, getPreviousStep, goToPreviousStep } from '../utils/stepper';

interface ButtonRowProps {
  activeStep: StepKey;
  disabled?: boolean;
  reportId?: string;
}

export type ButtonHandle = {
  click: () => void;
};

export const ButtonRow = forwardRef<ButtonHandle, ButtonRowProps>(({ activeStep, disabled, reportId }, ref) => {
  const styles = useStyles2(getStyles);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const previousStep = getPreviousStep(activeStep);
  const nextStep = getNextStep(activeStep);
  const isLastStep = nextStep.id === activeStep;

  // Enable clicking Submit from a parent component
  useImperativeHandle(ref, () => ({
    click: () => {
      buttonRef.current?.click();
    },
  }));

  return (
    <div className={styles.buttonRow}>
      <div className={styles.buttonRowInner}>
        <div>
          {previousStep && (
            <Button
              variant={'secondary'}
              onClick={() => goToPreviousStep(activeStep, reportId)}
              data-testid={selectors.components.reportForm.previousStep(previousStep.name)}
            >
              <Trans i18nKey="reporting.button-row.previous-step">Previous: {{ prevName: previousStep.name }}</Trans>
            </Button>
          )}
          {!isLastStep && (
            <Button
              ref={buttonRef}
              disabled={disabled}
              type="submit"
              data-testid={selectors.components.reportForm.nextStep(nextStep.name)}
            >
              <Trans i18nKey="reporting.button-row.next-step">Next: {{ nextName: nextStep.name }}</Trans>
            </Button>
          )}
        </div>
      </div>
    </div>
  );
});

ButtonRow.displayName = 'ButtonRow';

const getStyles = (theme: GrafanaTheme2) => {
  return {
    buttonRow: css({
      display: 'flex',
      padding: theme.spacing(2, 0, 0.5, 0),
      borderTop: `1px solid ${theme.colors.border.weak}`,
      width: '100%',
      backgroundColor: theme.colors.background.primary,
      button: {
        '&:first-of-type': {
          marginRight: theme.spacing(2),
        },
        '&:last-of-type': {
          marginRight: 0,
        },
      },
    }),
    buttonRowInner: css({
      display: 'flex',
      justifyContent: 'space-between',
      width: '100%',
    }),
  };
};
