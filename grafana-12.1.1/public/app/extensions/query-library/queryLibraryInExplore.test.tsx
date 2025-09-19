import { Props } from 'react-virtualized-auto-sizer';

import { EventBusSrv } from '@grafana/data';
import { config } from '@grafana/runtime';
import { DataQuery } from '@grafana/schema/dist/esm/veneer/common.types';
import {
  assertAddToQueryLibraryButtonExists,
  assertQueryHistory,
  assertQueryLibraryTemplateExists,
  assertQueryLibraryTemplateDoesNotExists,
} from 'app/features/explore/spec/helper/assert';
import {
  addQueryHistoryToQueryLibrary,
  openQueryHistory,
  openQueryLibrary,
  submitAddToQueryLibrary,
} from 'app/features/explore/spec/helper/interactions';
import { setupExplore, waitForExplore } from 'app/features/explore/spec/helper/setup';

import { silenceConsoleOutput } from '../../../test/core/utils/silenceConsoleOutput';
import { addExtraMiddleware, addRootReducer } from '../../store/configureStore';
import { queryLibraryAPIv0alpha1 as queryLibraryAPI } from '../api/clients/querylibrary/v0alpha1';

import { QueryLibraryContextProvider } from './QueryLibraryContextProvider';

const reportInteractionMock = jest.fn();
const testEventBus = new EventBusSrv();
testEventBus.publish = jest.fn();

interface MockQuery extends DataQuery {
  expr: string;
}

jest.mock('./utils/dataFetching', () => {
  return {
    __esModule: true,
    ...jest.requireActual('./utils/dataFetching'),
    useLoadUsers: () => {
      return {
        data: {
          display: [
            {
              avatarUrl: '',
              displayName: 'john doe',
              identity: {
                name: 'JohnDoe',
                type: 'viewer',
              },
            },
          ],
        },
        isLoading: false,
        error: null,
      };
    },
  };
});

jest.mock('@grafana/runtime', () => ({
  ...jest.requireActual('@grafana/runtime'),
  reportInteraction: (...args: object[]) => {
    reportInteractionMock(...args);
  },
  getAppEvents: () => testEventBus,
  usePluginLinks: jest.fn().mockReturnValue({ links: [] }),
}));

jest.mock('app/core/core', () => ({
  contextSrv: {
    hasPermission: () => true,
    hasRole: (role: string) => true,
    isSignedIn: true,
    getValidIntervals: (defaultIntervals: string[]) => defaultIntervals,
    user: {
      isSignedIn: true,
      uid: 'u000000001',
    },
  },
}));

jest.mock('app/core/services/PreferencesService', () => ({
  PreferencesService: function () {
    return {
      patch: jest.fn(),
      load: jest.fn().mockResolvedValue({
        queryHistory: {
          homeTab: 'query',
        },
      }),
    };
  },
}));

jest.mock('../../features/explore/hooks/useExplorePageTitle', () => ({
  useExplorePageTitle: jest.fn(),
}));

jest.mock('react-virtualized-auto-sizer', () => {
  return {
    __esModule: true,
    default(props: Props) {
      return <div>{props.children({ height: 1, scaledHeight: 1, scaledWidth: 1000, width: 1000 })}</div>;
    },
  };
});

function setupQueryLibrary() {
  const mockQuery: MockQuery = { refId: 'TEST', expr: 'TEST' };

  addRootReducer({
    [queryLibraryAPI.reducerPath]: queryLibraryAPI.reducer,
  });
  addExtraMiddleware(queryLibraryAPI.middleware);

  setupExplore({
    queryHistory: {
      queryHistory: [{ datasourceUid: 'loki', queries: [mockQuery] }],
      totalCount: 1,
    },
    withAppChrome: true,
    provider: QueryLibraryContextProvider,
  });
}
let previousQueryLibraryEnabled: boolean | undefined;
let previousQueryHistoryEnabled: boolean;

describe('QueryLibrary', () => {
  silenceConsoleOutput();

  beforeAll(() => {
    previousQueryLibraryEnabled = config.featureToggles.queryLibrary;
    previousQueryHistoryEnabled = config.queryHistoryEnabled;

    config.featureToggles.queryLibrary = true;
    config.queryHistoryEnabled = true;
  });

  afterAll(() => {
    config.featureToggles.queryLibrary = previousQueryLibraryEnabled;
    config.queryHistoryEnabled = previousQueryHistoryEnabled;
    jest.restoreAllMocks();
  });

  it('Load query templates', async () => {
    setupQueryLibrary();
    await waitForExplore();
    await openQueryLibrary();
    await assertQueryLibraryTemplateExists('loki', 'Loki Query Template');
    await assertQueryLibraryTemplateDoesNotExists('Loki Query Template Hidden');
  });

  it('Shows add to query library button only when the toggle is enabled', async () => {
    setupQueryLibrary();
    await waitForExplore();
    await openQueryHistory();
    await assertQueryHistory(['{"expr":"TEST"}']);
    await assertAddToQueryLibraryButtonExists(true);
  });

  it('Does not show the query library button when the toggle is disabled', async () => {
    config.featureToggles.queryLibrary = false;
    setupQueryLibrary();
    await waitForExplore();
    await openQueryHistory();
    await assertQueryHistory(['{"expr":"TEST"}']);
    await assertAddToQueryLibraryButtonExists(false);
    config.featureToggles.queryLibrary = true;
  });

  it('Shows a notification when a template is added and hides the add button', async () => {
    setupQueryLibrary();
    await waitForExplore();
    await openQueryHistory();
    await assertQueryHistory(['{"expr":"TEST"}']);
    await addQueryHistoryToQueryLibrary();
    await submitAddToQueryLibrary({ title: 'Test' });
    expect(testEventBus.publish).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'alert-success',
        payload: ['Query successfully saved to the library'],
      })
    );
    await assertAddToQueryLibraryButtonExists(false);
  });
});
