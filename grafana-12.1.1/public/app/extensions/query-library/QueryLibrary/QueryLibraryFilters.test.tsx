import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { QueryLibraryFilters, QueryLibraryFiltersProps } from './QueryLibraryFilters';

const SEARCH_PLACEHOLDER = 'Search by data source, query content, title, or description';

describe('QueryLibraryFilters', () => {
  const mockOnChangeDatasourceFilters = jest.fn();
  const mockOnChangeSearchQuery = jest.fn();
  const mockOnChangeUserFilters = jest.fn();

  const defaultProps: QueryLibraryFiltersProps = {
    datasourceFilterOptions: [{ label: 'Datasource 1', value: 'ds1' }],
    datasourceFilters: [],
    disabled: false,
    onChangeDatasourceFilters: mockOnChangeDatasourceFilters,
    onChangeSearchQuery: mockOnChangeSearchQuery,
    onChangeUserFilters: mockOnChangeUserFilters,
    searchQuery: '',
    userFilterOptions: [{ label: 'User 1', value: 'user1' }],
    userFilters: [],
  };

  it('renders without crashing', () => {
    render(<QueryLibraryFilters {...defaultProps} />);
    expect(screen.getByPlaceholderText(SEARCH_PLACEHOLDER)).toBeInTheDocument();
  });

  it('calls onChangeSearchQuery when search input changes', async () => {
    render(<QueryLibraryFilters {...defaultProps} />);
    const searchInput = screen.getByPlaceholderText(SEARCH_PLACEHOLDER);
    await userEvent.type(searchInput, 'f');
    expect(mockOnChangeSearchQuery).toHaveBeenCalledWith('f');
  });

  it('calls onChangeDatasourceFilters when datasource filter changes', async () => {
    render(<QueryLibraryFilters {...defaultProps} />);
    const datasourceSelect = screen.getByLabelText('Data source name(s)');
    await userEvent.click(datasourceSelect);
    await userEvent.click(screen.getByText('Datasource 1'));
    expect(mockOnChangeDatasourceFilters).toHaveBeenCalledWith([
      {
        label: 'Datasource 1',
        value: 'ds1',
      },
    ]);
  });

  it('calls onChangeUserFilters when user filter changes', async () => {
    render(<QueryLibraryFilters {...defaultProps} />);
    const userSelect = screen.getByLabelText('User name(s)');
    await userEvent.click(userSelect);
    await userEvent.click(screen.getByText('User 1'));
    expect(defaultProps.onChangeUserFilters).toHaveBeenCalledWith([
      {
        label: 'User 1',
        value: 'user1',
      },
    ]);
  });

  it('disables inputs when disabled prop is true', () => {
    render(<QueryLibraryFilters {...defaultProps} disabled={true} />);
    expect(screen.getByPlaceholderText(SEARCH_PLACEHOLDER)).toBeDisabled();
    expect(screen.getByLabelText('Data source name(s)')).toBeDisabled();
    expect(screen.getByLabelText('User name(s)')).toBeDisabled();
  });
});
