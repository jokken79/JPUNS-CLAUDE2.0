import React from 'react';
import { ExclamationTriangleIcon } from '@heroicons/react/24/solid';

interface VisaAlertProps {
  expiryDate: string | null;
  size?: 'sm' | 'md' | 'lg';
}

export const VisaAlert: React.FC<VisaAlertProps> = ({ expiryDate, size = 'md' }) => {
  if (!expiryDate) {
    return <span className="text-gray-400 text-xs">-</span>;
  }

  const today = new Date();
  const expiry = new Date(expiryDate);
  const daysUntilExpiry = Math.floor((expiry.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));

  // Determinar el estado de la alerta
  let alertType: 'expired' | 'critical' | 'warning' | 'caution' | 'good';
  let bgColor: string;
  let textColor: string;
  let borderColor: string;
  let showIcon = false;

  if (daysUntilExpiry < 0) {
    // Ya venció - 3 bolas rojas
    alertType = 'expired';
    bgColor = 'bg-red-100';
    textColor = 'text-red-800';
    borderColor = 'border-red-500';
  } else if (daysUntilExpiry <= 10) {
    // 10 días o menos - Rojo con exclamación
    alertType = 'critical';
    bgColor = 'bg-red-100';
    textColor = 'text-red-800';
    borderColor = 'border-red-600';
    showIcon = true;
  } else if (daysUntilExpiry <= 30) {
    // 1 mes o menos - Rojo
    alertType = 'warning';
    bgColor = 'bg-red-50';
    textColor = 'text-red-700';
    borderColor = 'border-red-400';
  } else if (daysUntilExpiry <= 90) {
    // 3 meses o menos - Amarillo
    alertType = 'caution';
    bgColor = 'bg-yellow-50';
    textColor = 'text-yellow-800';
    borderColor = 'border-yellow-400';
  } else {
    // Más de 3 meses - Verde
    alertType = 'good';
    bgColor = 'bg-green-50';
    textColor = 'text-green-700';
    borderColor = 'border-green-400';
  }

  const sizeClasses = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5',
  };

  const dotSize = sizeClasses[size];

  return (
    <div className="flex items-center gap-2">
      {/* Indicador visual */}
      <div className="flex items-center gap-1">
        {alertType === 'expired' ? (
          // Triple círculo rojo para vencido
          <>
            <span className={`${dotSize} rounded-full bg-red-600`} />
            <span className={`${dotSize} rounded-full bg-red-600`} />
            <span className={`${dotSize} rounded-full bg-red-600`} />
          </>
        ) : (
          // Un círculo con el color correspondiente
          <span className={`${dotSize} rounded-full ${borderColor.replace('border-', 'bg-')}`} />
        )}

        {showIcon && (
          <ExclamationTriangleIcon className={`${dotSize} ${textColor}`} />
        )}
      </div>

      {/* Fecha formateada */}
      <span className={`text-xs font-medium ${textColor}`}>
        {new Date(expiryDate).toLocaleDateString('ja-JP')}
      </span>

      {/* Badge con días restantes */}
      {daysUntilExpiry >= 0 && (
        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold ${bgColor} ${textColor} border ${borderColor}`}>
          {daysUntilExpiry}日
        </span>
      )}

      {daysUntilExpiry < 0 && (
        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-red-600 text-white animate-pulse">
          期限切れ
        </span>
      )}
    </div>
  );
};

export default VisaAlert;
