import { t } from '@grafana/i18n';
import { handleError } from 'app/api/utils';
import { notifyApp } from 'app/core/actions';
import { createSuccessNotification } from 'app/core/copy/appNotification';

import { QUERY_LIBRARY_GET_LIMIT } from './baseAPI';
import { generatedAPI } from './endpoints.gen';

export const queryLibraryAPIv0alpha1 = generatedAPI.enhanceEndpoints({
  endpoints: {
    // Need to mutate the generated query to force query limit
    listQueryTemplate: (endpointDefinition) => {
      const originalQuery = endpointDefinition.query;
      if (originalQuery) {
        endpointDefinition.query = (requestOptions) =>
          originalQuery({
            ...requestOptions,
            limit: QUERY_LIBRARY_GET_LIMIT,
          });
      }
    },
    // Need to mutate the generated query to set the Content-Type header correctly
    updateQueryTemplate: (endpointDefinition) => {
      const originalQuery = endpointDefinition.query;
      if (originalQuery) {
        endpointDefinition.query = (requestOptions) => ({
          ...originalQuery(requestOptions),
          headers: {
            'Content-Type': 'application/merge-patch+json',
          },
        });
      }
      endpointDefinition.onQueryStarted = async (_, { queryFulfilled, dispatch }) => {
        try {
          await queryFulfilled;
          dispatch(
            notifyApp(
              createSuccessNotification(
                t('explore.query-library.query-template-edited', 'Query template successfully edited')
              )
            )
          );
        } catch (e) {
          handleError(
            e,
            dispatch,
            t('explore.query-library.query-template-edit-error', 'Error attempting to edit this query')
          );
        }
      };
    },
  },
});

export const {
  useCreateQueryTemplateMutation,
  useDeleteQueryTemplateMutation,
  useListQueryTemplateQuery,
  useUpdateQueryTemplateMutation,
} = queryLibraryAPIv0alpha1;

// eslint-disable-next-line no-barrel-files/no-barrel-files
export type { TemplateQueryTemplate, QueryTemplate, ListQueryTemplateApiResponse } from './endpoints.gen';
