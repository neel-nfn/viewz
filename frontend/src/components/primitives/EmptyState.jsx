import { tokens } from '../../theme/tokens';
import Button from './Button';

/**
 * EmptyState - Standard empty state component
 * Use when lists/tables have no data
 */
export default function EmptyState({ 
  icon: Icon,
  title,
  description,
  action,
  className = '',
}) {
  return (
    <div className={`flex flex-col items-center justify-center py-12 px-6 text-center ${className}`}>
      {Icon && (
        <div className="mb-4 text-textSecondary" style={{ fontSize: '3rem' }}>
          <Icon size={48} />
        </div>
      )}
      <h3 className="text-xl font-semibold text-textPrimary mb-2">{title}</h3>
      {description && (
        <p className="text-base text-textSecondary max-w-md mb-6">{description}</p>
      )}
      {action && (
        <Button {...action}>{action.label}</Button>
      )}
    </div>
  );
}

