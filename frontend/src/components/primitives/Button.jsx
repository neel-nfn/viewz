import { tokens } from '../../theme/tokens';

/**
 * Button - Standardized button component
 * Use this instead of raw <button> or ad-hoc styling
 */
export default function Button({ 
  variant = 'primary', 
  size = 'md',
  children, 
  className = '',
  ...props 
}) {
  const baseStyles = 'font-semibold rounded-xl transition-all duration-200 inline-flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variants = {
    primary: 'bg-primary text-white hover:bg-accent hover:shadow-hover active:translate-y-0',
    secondary: 'bg-transparent border-2 border-primary text-primary hover:bg-primary hover:text-white',
    ghost: 'bg-transparent text-textPrimary hover:bg-surface hover:text-primary',
    danger: 'bg-error text-white hover:bg-red-600',
  };
  
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };
  
  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}

