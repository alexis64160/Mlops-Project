import { css } from '@emotion/css';
import { useEffect, useState } from 'react';

import { GrafanaTheme2 } from '@grafana/data';
import { Trans } from '@grafana/i18n';
import { RawQuery } from '@grafana/plugin-ui';
import { Icon, Input, Tooltip, useStyles2, useTheme2 } from '@grafana/ui';
import lokiGrammar from 'app/plugins/datasource/loki/syntax';

import { trimLBACRule } from './utils';

interface Props {
  value: string;
  isEditing?: boolean;
  disabled?: boolean;
  onChange?: (value: string) => void;
  error?: string;
}

export const EditableCell = ({ isEditing, value, disabled, error, onChange }: Props) => {
  const [cellValue, setCellValue] = useState(trimLBACRule(value));
  const theme = useTheme2();
  const styles = useStyles2(getStyles);

  useEffect(() => {
    if (!isEditing) {
      setCellValue(trimLBACRule(value));
    }
  }, [isEditing, value]);

  return (
    <div className={styles.wrapper}>
      {isEditing ? (
        <>
          <Input
            className={styles.input}
            value={cellValue}
            onChange={(event) => {
              const value = event.currentTarget.value;
              setCellValue(value);
              if (onChange) {
                onChange(`{ ${value} }`);
              }
            }}
            invalid={!!error}
            suffix={
              error && (
                <Tooltip content={error}>
                  <Icon name="exclamation-triangle" />
                </Tooltip>
              )
            }
          />
        </>
      ) : (
        <span style={{ color: disabled ? theme.colors.text.disabled : 'unset' }}>
          {value && value.trim() ? (
            <RawQuery query={value} language={{ grammar: lokiGrammar, name: 'logql' }} />
          ) : (
            <span className={styles.emptyValue}>
              <Trans i18nKey="team-lbac.editable-cell.empty-rule">Empty rule</Trans>
            </span>
          )}
        </span>
      )}
    </div>
  );
};

const getStyles = (theme: GrafanaTheme2) => {
  return {
    wrapper: css({
      padding: theme.spacing(0, 1),
    }),
    input: css({
      '& input': {
        fontFamily: theme.typography.fontFamilyMonospace,
      },
    }),
    emptyValue: css({
      fontStyle: 'italic',
      color: theme.colors.text.secondary,
    }),
  };
};
