import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { mockQueryTemplateRow } from '../utils/mocks';

import { QueryLibraryItem } from './QueryLibraryItem';

jest.mock('@grafana/runtime', () => ({
  ...jest.requireActual('@grafana/runtime'),
  getDataSourceSrv: () => ({
    get: () => ({
      meta: {
        info: {
          logos: {
            small: 'foo/icn-prometheus.svg',
          },
        },
      },
      type: 'prometheus',
    }),
  }),
  getTemplateSrv: () => ({
    replace: (value: string) => value,
  }),
}));

describe('QueryLibraryItem', () => {
  const mockOnSelectQueryRow = jest.fn();
  const defaultProps = {
    queryRow: mockQueryTemplateRow,
    onSelectQueryRow: mockOnSelectQueryRow,
    isSelected: false,
  };

  it('renders query title', async () => {
    render(<QueryLibraryItem {...defaultProps} />);
    expect(await screen.findByText(mockQueryTemplateRow.title!)).toBeInTheDocument();
  });

  it('renders datasource logo', async () => {
    render(<QueryLibraryItem {...defaultProps} />);
    const logo = await screen.findByRole('img');
    expect(logo).toHaveAttribute('src', 'foo/icn-prometheus.svg');
    expect(logo).toHaveAttribute('alt', 'prometheus');
  });

  it('calls onSelectQueryRow when clicking the item', async () => {
    render(<QueryLibraryItem {...defaultProps} />);
    await userEvent.click(screen.getByRole('radio'));
    expect(mockOnSelectQueryRow).toHaveBeenCalledWith(mockQueryTemplateRow);
  });

  it('renders checked radio when selected', async () => {
    render(<QueryLibraryItem {...defaultProps} isSelected={true} />);
    expect(await screen.findByRole('radio')).toBeChecked();
  });

  it('renders unchecked radio when not selected', async () => {
    render(<QueryLibraryItem {...defaultProps} isSelected={false} />);
    expect(await screen.findByRole('radio')).not.toBeChecked();
  });
});
