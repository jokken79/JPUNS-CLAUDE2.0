import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

import Login from '../../pages/Login';

jest.mock('react-hot-toast', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

const fetchSpy = jest
  .spyOn(global, 'fetch')
  .mockResolvedValue({ ok: false, json: async () => ({ detail: 'error' }) } as Response);

afterAll(() => {
  fetchSpy.mockRestore();
});

describe('Login page', () => {
  it('allows entering credentials', () => {
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    );

    const username = screen.getByLabelText('ユーザー名');
    const password = screen.getByLabelText('パスワード');

    fireEvent.change(username, { target: { value: 'admin' } });
    fireEvent.change(password, { target: { value: 'secret' } });

    expect(username).toHaveValue('admin');
    expect(password).toHaveValue('secret');
  });
});
