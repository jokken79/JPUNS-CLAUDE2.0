import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';

import ProtectedRoute from '../../components/ProtectedRoute';

const renderWithRoute = () =>
  render(
    <MemoryRouter initialEntries={['/protected']}>
      <Routes>
        <Route
          path="/protected"
          element={(
            <ProtectedRoute>
              <div>Protected content</div>
            </ProtectedRoute>
          )}
        />
        <Route path="/login" element={<div>Login page</div>} />
      </Routes>
    </MemoryRouter>
  );

describe('ProtectedRoute', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('redirects when token is missing', () => {
    renderWithRoute();
    expect(screen.getByText('Login page')).toBeInTheDocument();
  });

  it('renders children when token exists', () => {
    localStorage.setItem('token', 'test');
    renderWithRoute();
    expect(screen.getByText('Protected content')).toBeInTheDocument();
  });
});
