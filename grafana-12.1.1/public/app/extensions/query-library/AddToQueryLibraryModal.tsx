import { t } from '@grafana/i18n';
import { DataQuery } from '@grafana/schema';
import { Modal } from '@grafana/ui';

import { QueryLibraryInteractions } from './QueryLibraryAnalyticsEvents';
import { QueryTemplateForm } from './QueryTemplateForm';

type Props = {
  query?: DataQuery;
  title?: string;
  context?: string;
  isOpen: boolean;
  onSave?: () => void;
  close: () => void;
};

export function AddToQueryLibraryModal({ query, title, context, isOpen, onSave, close }: Props) {
  return (
    <Modal
      title={t('explore.query-template-modal.add-title', 'Add to query library')}
      isOpen={isOpen}
      onDismiss={() => close()}
    >
      <QueryTemplateForm
        onCancel={() => {
          close();
        }}
        onSave={(isSuccess) => {
          if (isSuccess) {
            close();
            QueryLibraryInteractions.saveQuerySuccess();
            onSave?.();
          }
        }}
        templateData={{ query: query!, title }}
      />
    </Modal>
  );
}
