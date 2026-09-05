import { ButtonHTMLAttributes, ReactNode } from "react";

type PageHeaderProps = {
  eyebrow: string;
  title: string;
  description?: string;
  action?: ReactNode;
};

export function PageHeader({ eyebrow, title, description, action }: PageHeaderProps) {
  return (
    <header className="lunar-page-header">
      <div>
        <p className="lunar-eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        {description && <p className="lunar-description">{description}</p>}
      </div>
      {action && <div className="lunar-header-action">{action}</div>}
    </header>
  );
}

export function Panel({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <section className={`lunar-panel ${className}`}>{children}</section>;
}

export function StatusBadge({ children, tone = "signal" }: { children: ReactNode; tone?: "signal" | "violet" | "warn" | "danger" }) {
  return <span className={`lunar-status lunar-status-${tone}`}>{children}</span>;
}

type ActionButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode;
  variant?: "primary" | "secondary";
};

export function ActionButton({ children, variant = "primary", className = "", ...props }: ActionButtonProps) {
  return (
    <button {...props} className={`lunar-button lunar-button-${variant} ${className}`}>
      {children}
    </button>
  );
}
