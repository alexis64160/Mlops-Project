import { screen } from '@testing-library/react';
import { useState } from 'react';

import { generatedAPI } from 'app/extensions/api/clients/querylibrary/v0alpha1/endpoints.gen';
import { addExtraMiddleware, addRootReducer } from 'app/store/configureStore';

import { render } from '../../../../test/test-utils';
import { canEditQuery } from '../utils/identity';
import { mockQueryTemplateRow } from '../utils/mocks';
import { useDatasource } from '../utils/useDatasource';

import { QueryLibraryDetails } from './QueryLibraryDetails';

// Mock the canEditQuery function
jest.mock('../utils/identity', () => ({
  canEditQuery: jest.fn(),
}));

// Mock the useDatasource hook to avoid async state updates
jest.mock('../utils/useDatasource', () => ({
  useDatasource: jest.fn(),
}));

const mockCanEditQuery = canEditQuery as jest.MockedFunction<typeof canEditQuery>;
const mockUseDatasource = useDatasource as jest.MockedFunction<typeof useDatasource>;
// Mock useDatasource to return a consistent datasource object
mockUseDatasource.mockReturnValue({
  meta: {
    info: {
      logos: {
        small: 'foo/icn-prometheus.svg',
      },
    },
  },
  type: 'prometheus',
} as any);

beforeAll(() => {
  addRootReducer({
    [generatedAPI.reducerPath]: generatedAPI.reducer,
  });
  addExtraMiddleware(generatedAPI.middleware);
});

const QueryLibraryDetailsWrapper = ({ query }: { query: any }) => {
  const [editingQuery, setEditingQuery] = useState(false);

  return <QueryLibraryDetails query={query} editingQuery={editingQuery} setEditingQuery={setEditingQuery} />;
};

describe('QueryLibraryDetails', () => {
  beforeEach(() => {
    mockCanEditQuery.mockReturnValue(true);
  });

  it('should render datasource logo and query title', async () => {
    render(<QueryLibraryDetails query={mockQueryTemplateRow} editingQuery={false} setEditingQuery={jest.fn()} />);

    const logo = await screen.findByRole('img', { name: 'prometheus' });
    expect(logo).toHaveAttribute('src', 'foo/icn-prometheus.svg');

    const title = await screen.findByText(mockQueryTemplateRow.title!);
    expect(title).toBeInTheDocument();
  });

  it('should render other query details', async () => {
    render(<QueryLibraryDetails query={mockQueryTemplateRow} editingQuery={false} setEditingQuery={jest.fn()} />);

    const query = await screen.findByText(mockQueryTemplateRow.queryText!);
    expect(query).toBeInTheDocument();
    expect(await screen.getByLabelText('Data source')).toHaveValue(mockQueryTemplateRow.datasourceName);
    expect(await screen.getByLabelText('Description')).toHaveValue(mockQueryTemplateRow.description);
    expect(await screen.getByLabelText('Author')).toHaveValue(mockQueryTemplateRow.user?.displayName);
    expect(await screen.getByLabelText('Share query with all users')).toBeChecked();
  });

  it('should make form editable when clicking edit button', async () => {
    const { user } = render(<QueryLibraryDetailsWrapper query={mockQueryTemplateRow} />);
    const editButton = screen.getByRole('button', { name: 'Edit query' });

    await user.click(editButton);
    expect(editButton).not.toBeInTheDocument();

    const saveButton = screen.getByRole('button', { name: 'Save' });
    const cancelButton = screen.getByRole('button', { name: 'Cancel' });

    // Save and cancel buttons should always be visible in a pristine form.
    expect(saveButton).toBeDisabled();
    expect(cancelButton).toBeEnabled();

    const input = await screen.getByTestId('query-title-input');
    expect(input).toBeInTheDocument();

    await user.type(input, 't');

    // Save and cancel buttons should always be visible in a dirty form.
    expect(saveButton).toBeEnabled();
    expect(cancelButton).toBeEnabled();

    await user.type(input, '{backspace}');

    // Save and cancel buttons should always be visible in a pristine form.
    expect(saveButton).toBeDisabled();
    expect(cancelButton).toBeEnabled();

    // Click cancel button show display the edit pen button again
    await user.click(cancelButton);

    const newEditButton = screen.getByRole('button', { name: 'Edit query' });
    expect(newEditButton).toBeInTheDocument();
  });

  it('should show save button when a new tag is added', async () => {
    const { user } = render(
      <QueryLibraryDetails query={mockQueryTemplateRow} editingQuery={true} setEditingQuery={jest.fn()} />
    );

    const tagsInput = screen.getByLabelText('Tags');
    await user.type(tagsInput, 'new-tag{enter}');

    const saveButton = screen.getByRole('button', { name: 'Save' });
    expect(saveButton).toBeInTheDocument();
  });

  it('edit button should be disabled when query is locked', async () => {
    render(
      <QueryLibraryDetails
        query={{ ...mockQueryTemplateRow, isLocked: true }}
        editingQuery={false}
        setEditingQuery={jest.fn()}
      />
    );

    const editButton = await screen.findByRole('button', { name: 'Edit query' });
    expect(editButton).toBeDisabled();
  });

  it('edit button should be disabled when user does not have privileges', async () => {
    mockCanEditQuery.mockReturnValue(false);
    render(<QueryLibraryDetails query={mockQueryTemplateRow} editingQuery={false} setEditingQuery={jest.fn()} />);

    const editButton = screen.getByRole('button', { name: 'Edit query' });
    expect(editButton).toBeDisabled();
  });
});
