import { screen } from '@testing-library/react';

import { render } from '../../../../test/test-utils';
import { mockQueryTemplateRow } from '../utils/mocks';

import { QueryLibraryActions, QueryLibraryActionsProps } from './QueryLibraryActions';

const mockOpenAddQueryModal = jest.fn();
jest.mock('app/features/explore/QueryLibrary/QueryLibraryContext', () => ({
  useQueryLibraryContext: () => ({
    openAddQueryModal: mockOpenAddQueryModal,
  }),
}));

describe('QueryLibraryActions', () => {
  const mockOnSelectQuery = jest.fn();
  const defaultProps: QueryLibraryActionsProps = {
    onSelectQuery: mockOnSelectQuery,
    selectedQueryRow: mockQueryTemplateRow,
    isEditingQuery: false,
  };

  const lockedQueryTemplateRow = {
    ...mockQueryTemplateRow,
    isLocked: true,
  };

  const lockedQueryProps: QueryLibraryActionsProps = {
    onSelectQuery: mockOnSelectQuery,
    selectedQueryRow: lockedQueryTemplateRow,
    isEditingQuery: false,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render all action buttons', () => {
    render(<QueryLibraryActions {...defaultProps} />);
    expect(screen.getByRole('button', { name: 'Duplicate query' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Lock query' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Delete query' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Select query' })).toBeInTheDocument();
  });

  it('should render unlock button when query is locked', () => {
    render(<QueryLibraryActions {...lockedQueryProps} />);
    expect(screen.getByRole('button', { name: 'Unlock query' })).toBeInTheDocument();
  });

  it('should disable lock button when query is being edited', () => {
    render(<QueryLibraryActions {...defaultProps} isEditingQuery={true} />);
    expect(screen.getByRole('button', { name: 'Lock query' })).toBeDisabled();
  });

  it('should call onSelectQuery when the select button is clicked', async () => {
    const { user } = render(<QueryLibraryActions {...defaultProps} />);
    await user.click(screen.getByRole('button', { name: 'Select query' }));
    expect(mockOnSelectQuery).toHaveBeenCalledWith(mockQueryTemplateRow.query);
  });

  it('should open modal when duplicating query', async () => {
    const { user } = render(<QueryLibraryActions {...defaultProps} />);
    await user.click(screen.getByRole('button', { name: 'Duplicate query' }));
    expect(mockOpenAddQueryModal).toHaveBeenCalledWith(mockQueryTemplateRow.query, {
      title: `${mockQueryTemplateRow.title} Copy`,
      isDuplicating: true,
    });
  });
});
