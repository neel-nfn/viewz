import { tokens } from '../../theme/tokens';
import { AlertCircle, CheckCircle, Info, AlertTriangle } from 'lucide-react';

/**
 * Banner - Standard banner component for success/error/info/warning
 */
export default function Banner({ 
  variant = 'info',
  title,
  message,
  actions,
  onClose,
  className = '',
}) {
  const variants = {
    success: {
      bg: 'bg-green-50',
      border: 'border-green-200',
      icon: CheckCircle,
      iconColor: 'text-green-600',
      titleColor: 'text-green-900',
      textColor: 'text-green-700',
    },
    error: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      icon: AlertCircle,
      iconColor: 'text-red-600',
      titleColor: 'text-red-900',
      textColor: 'text-red-700',
    },
    warning: {
      bg: 'bg-amber-50',
      border: 'border-amber-200',
      icon: AlertTriangle,
      iconColor: 'text-amber-600',
      titleColor: 'text-amber-900',
      textColor: 'text-amber-700',
    },
    info: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      icon: Info,
      iconColor: 'text-blue-600',
      titleColor: 'text-blue-900',
      textColor: 'text-blue-700',
    },
  };
  
  const config = variants[variant];
  const Icon = config.icon;
  
  return (
    <div 
      className={`${config.bg} ${config.border} border rounded-lg p-4 flex items-start gap-3 ${className}`}
      style={{ borderRadius: tokens.radius.lg }}
    >
      <Icon className={`${config.iconColor} shrink-0 mt-0.5`} size={20} />
      <div className="flex-1">
        {title && (
          <h4 className={`font-semibold ${config.titleColor} mb-1`}>{title}</h4>
        )}
        {message && (
          <p className={`text-sm ${config.textColor}`}>{message}</p>
        )}
        {actions && (
          <div className="flex gap-2 mt-3">
            {actions}
          </div>
        )}
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className={`${config.textColor} hover:opacity-70 transition`}
        >
          ×
        </button>
      )}
    </div>
  );
}

