import '@testing-library/jest-dom';

const originalError = console.error;

beforeAll(() => {
  console.error = (...args: unknown[]) => {
    if (typeof args[0] === 'string' && args[0].includes('Warning:')) {
      return;
    }
    originalError(...args as []);
  };
});

afterAll(() => {
  console.error = originalError;
});
