import { contextSrv } from 'app/core/core';

import { QueryTemplateRow } from '../types';

export const searchQueryLibrary = (
  queryLibrary: QueryTemplateRow[],
  query: string,
  dsFilters: string[],
  userNameFilters: string[]
) => {
  const result = queryLibrary.filter((item) => {
    const lowerCaseQuery = query.toLowerCase();
    const lowerCaseDatasourceName = item.datasourceName?.toLowerCase() || '';

    // If the datasource filter is empty, or the item's datasource is in the filter, display the item
    const foundDsFilterMatch =
      dsFilters.length === 0 ||
      dsFilters.some((filter) => {
        const lowerCaseFilter = filter.toLowerCase();
        return lowerCaseDatasourceName.includes(lowerCaseFilter);
      });

    // If the user filter is empty, or the item's user is in the filter, display the item
    const userName = item.user?.displayName || '';
    const foundUserNameFilterMatch = userNameFilters.length === 0 || userNameFilters.includes(userName);

    // If the user is the author or it's a public query, display the item
    const isAuthor = item.user?.uid?.replace('user:', '') === contextSrv?.user?.uid;
    const isVisible = item.isVisible || isAuthor;

    // If the query matches any of the fields, display the item
    const queryMatchesDatasourceName = lowerCaseDatasourceName.includes(lowerCaseQuery);
    const queryMatchesDatasourceType = item.datasourceType?.toLowerCase().includes(lowerCaseQuery);
    const queryMatchesTitle = item.title?.toLowerCase().includes(lowerCaseQuery);
    const queryMatchesDescription = item.description?.toLowerCase().includes(lowerCaseQuery);
    const queryMatchesQueryText = item.queryText?.toLowerCase().includes(lowerCaseQuery);
    const queryMatchesTags = item.tags?.some((tag) => tag.toLowerCase().includes(lowerCaseQuery));

    const foundQueryMatch =
      queryMatchesDatasourceName ||
      queryMatchesDatasourceType ||
      queryMatchesTitle ||
      queryMatchesDescription ||
      queryMatchesQueryText ||
      queryMatchesTags;

    return foundQueryMatch && foundDsFilterMatch && foundUserNameFilterMatch && isVisible;
  });
  return result;
};
