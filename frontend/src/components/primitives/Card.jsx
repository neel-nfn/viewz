import { tokens } from '../../theme/tokens';

/**
 * Card - Standardized card component
 * All content should live in Cards, not raw divs
 */
export default function Card({ 
  title,
  subtitle,
  actions,
  children,
  className = '',
  ...props 
}) {
  return (
    <div
      className={`bg-surface border border-border rounded-xl shadow-card p-6 ${className}`}
      style={{ borderRadius: tokens.radius.xl }}
      {...props}
    >
      {(title || subtitle || actions) && (
        <div className="flex items-start justify-between mb-4">
          <div>
            {title && (
              <h3 className="text-xl font-semibold text-textPrimary">{title}</h3>
            )}
            {subtitle && (
              <p className="text-sm text-textSecondary mt-1">{subtitle}</p>
            )}
          </div>
          {actions && (
            <div className="flex gap-2">{actions}</div>
          )}
        </div>
      )}
      <div>{children}</div>
    </div>
  );
}

