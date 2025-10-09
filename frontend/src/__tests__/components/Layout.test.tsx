import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

import Layout from '../../components/Layout';
import { PageVisibilityProvider } from '../../context/PageVisibilityContext';

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  useLocation: () => ({ pathname: '/dashboard' }),
}));

const renderLayout = () =>
  render(
    <MemoryRouter>
      <PageVisibilityProvider>
        <Layout />
      </PageVisibilityProvider>
    </MemoryRouter>
  );

describe('Layout component', () => {
  it('renders navigation items', () => {
    renderLayout();
    expect(screen.getByText('UNS-ClaudeJP 2.0')).toBeInTheDocument();
    expect(screen.getByText('ダッシュボード')).toBeInTheDocument();
  });
});
