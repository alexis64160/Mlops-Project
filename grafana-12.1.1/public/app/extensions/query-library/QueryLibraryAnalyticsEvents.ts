import { reportInteraction } from '@grafana/runtime';

const queryLibraryInteraction = (event: string, properties?: Record<string, unknown>) => {
  reportInteraction(`query_library-${event}`, properties);
};

export const QueryLibraryInteractions = {
  queryLibraryOpened: () => {
    queryLibraryInteraction('opened');
  },
  queryLibraryClosedWithoutSelection: () => {
    queryLibraryInteraction('closed_without_selection');
  },
  // Outside Interactions
  addQueryFromLibraryClicked: () => {
    queryLibraryInteraction('add_query_from_library_clicked');
  },
  replaceWithQueryFromLibraryClicked: () => {
    queryLibraryInteraction('replace_with_query_from_library_clicked');
  },
  saveQueryToLibraryClicked: () => {
    queryLibraryInteraction('save_query_to_library_clicked');
  },
  saveQuerySuccess: () => {
    queryLibraryInteraction('save_query_success');
  },
  // Inside Interactions
  // Filter
  searchBarFocused: () => {
    queryLibraryInteraction('search_bar_focused');
  },
  dataSourceFilterChanged: () => {
    queryLibraryInteraction('data_source_filter_changed');
  },
  userFilterChanged: () => {
    queryLibraryInteraction('user_filter_changed');
  },
  // Bottom Action Row
  selectQueryClicked: () => {
    queryLibraryInteraction('select_query_clicked');
  },
  deleteQueryClicked: () => {
    queryLibraryInteraction('delete_query_clicked');
  },
  duplicateQueryClicked: () => {
    queryLibraryInteraction('duplicate_query_clicked');
  },
  lockQueryClicked: (isLocked: boolean) => {
    queryLibraryInteraction('lock_query_clicked', {
      isLocked,
    });
  },
  // Editing
  editQueryClicked: () => {
    queryLibraryInteraction('edit_query_clicked');
  },
  cancelEditClicked: () => {
    queryLibraryInteraction('cancel_edit_clicked');
  },
  saveEditClicked: (savedFields: Record<string, boolean | undefined>) => {
    queryLibraryInteraction('save_edit_clicked', { ...savedFields });
  },
};

export const dirtyFieldsToAnalyticsObject = (
  dirtyFields: Partial<{
    title?: boolean;
    description?: boolean;
    isVisible?: boolean;
    tags?: boolean[];
  }>
) => {
  const result: Record<string, boolean> = {};
  for (const [key, value] of Object.entries(dirtyFields)) {
    if (typeof value === 'boolean') {
      result[key] = value;
    }
  }
  return result;
};
