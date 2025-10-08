import React from 'react';
import { PageKey, usePageVisibility } from '../context/PageVisibilityContext';
import UnderConstruction from '../pages/UnderConstruction';

interface VisibilityGuardProps {
  pageKey: PageKey;
  children: React.ReactNode;
}

const VisibilityGuard: React.FC<VisibilityGuardProps> = ({ pageKey, children }) => {
  const { isPageVisible } = usePageVisibility();

  if (!isPageVisible(pageKey)) {
    return <UnderConstruction />;
  }

  return <>{children}</>;
};

export default VisibilityGuard;
