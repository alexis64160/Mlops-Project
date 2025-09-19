import { generatedAPI } from './endpoints.gen';

export const alertEnrichmentAPIv0alpha1 = generatedAPI.enhanceEndpoints({});

export const { useListAlertEnrichmentQuery, useCreateAlertEnrichmentMutation, useDeleteAlertEnrichmentMutation } =
  alertEnrichmentAPIv0alpha1;
