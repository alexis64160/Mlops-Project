import { v4 as uuidv4 } from 'uuid';

import { AnnoKeyCreatedBy } from 'app/features/apiserver/types';

import { ListQueryTemplateApiResponse, QueryTemplate as QT } from '../../api/clients/querylibrary/v0alpha1';

import { AddQueryTemplateCommand, QueryTemplate } from './types';

export const convertDataQueryResponseToQueryTemplates = (result: ListQueryTemplateApiResponse): QueryTemplate[] => {
  if (!result.items) {
    return [];
  }
  return result.items.map((spec) => {
    return {
      uid: spec.metadata?.name ?? '',
      title: spec.spec?.title ?? '',
      description: spec.spec?.description ?? '',
      tags: spec.spec?.tags ?? [],
      isLocked: spec.spec?.isLocked ?? false,
      isVisible: spec.spec?.isVisible ?? false,
      targets:
        spec.spec?.targets.map((target) => ({
          ...target.properties,
          refId: target.properties.refId ?? '',
        })) ?? [],
      createdAtTimestamp: new Date(spec.metadata?.creationTimestamp ?? '').getTime(),
      user: {
        uid: spec.metadata?.annotations?.[AnnoKeyCreatedBy] ?? '',
      },
    };
  });
};

export const convertAddQueryTemplateCommandToDataQuerySpec = (addQueryTemplateCommand: AddQueryTemplateCommand): QT => {
  const { title, targets, description, isLocked, isVisible, tags } = addQueryTemplateCommand;
  return {
    metadata: {
      /**
       * Server will append to whatever is passed here, but just to be safe we generate a uuid
       * More info https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api-conventions.md#idempotency
       */
      generateName: uuidv4(),
    },
    spec: {
      title,
      description,
      isVisible,
      vars: [], // TODO: Detect variables in #86838
      tags,
      targets: targets.map((dataQuery) => ({
        variables: {},
        properties: {
          ...dataQuery,
          datasource: {
            ...dataQuery.datasource,
            type: dataQuery.datasource?.type ?? '',
          },
        },
      })),
      isLocked: isLocked ?? false,
    },
  };
};
