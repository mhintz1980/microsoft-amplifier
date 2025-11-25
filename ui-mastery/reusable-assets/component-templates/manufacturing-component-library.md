# Manufacturing Component Library Template

A comprehensive template for creating manufacturing-specific UI component libraries that ensure consistency, performance, and industrial appropriateness.

## Component Library Structure

### Directory Organization
```
manufacturing-ui-library/
├── src/
│   ├── components/           # React/Vue/Svelte components
│   │   ├── controls/        # Industrial control components
│   │   ├── data-display/    # Data visualization components
│   │   ├── forms/          # Form components for industrial use
│   │   ├── layout/         # Layout and structural components
│   │   ├── navigation/     # Navigation components
│   │   └── status/         # Status and alert components
│   ├── styles/            # CSS/styling system
│   │   ├── tokens/        # Design tokens
│   │   ├── components/    # Component-specific styles
│   │   └── utilities/     # Utility classes
│   ├── icons/            # Custom icon library
│   └── utils/            # JavaScript utilities
├── docs/                 # Documentation
├── stories/              # Storybook stories
├── tests/                # Component tests
└── build/                # Build configuration
```

## Core Components

### 1. Control Components

#### Industrial Button Component
```typescript
// components/controls/IndustrialButton.tsx
interface IndustrialButtonProps {
  variant: 'primary' | 'secondary' | 'danger' | 'emergency';
  size: 'small' | 'medium' | 'large' | 'emergency';
  disabled?: boolean;
  loading?: boolean;
  confirm?: boolean; // Two-stage action for critical operations
  icon?: ReactNode;
  children: ReactNode;
  onClick?: () => void;
}

const IndustrialButton: React.FC<IndustrialButtonProps> = ({
  variant,
  size,
  disabled = false,
  loading = false,
  confirm = false,
  icon,
  children,
  onClick
}) => {
  const [showConfirm, setShowConfirm] = useState(false);

  const handleClick = () => {
    if (confirm && !showConfirm) {
      setShowConfirm(true);
      setTimeout(() => setShowConfirm(false), 3000);
    } else {
      onClick?.();
    }
  };

  return (
    <button
      className={`
        industrial-button
        industrial-button--${variant}
        industrial-button--${size}
        ${loading ? 'industrial-button--loading' : ''}
        ${showConfirm ? 'industrial-button--confirming' : ''}
      `}
      disabled={disabled || loading}
      onClick={handleClick}
    >
      {loading && <LoadingSpinner size="small" />}
      {icon && <span className="industrial-button__icon">{icon}</span>}
      <span className="industrial-button__content">
        {showConfirm && confirm ? 'Confirm?' : children}
      </span>
    </button>
  );
};
```

```css
/* components/IndustrialButton.css */
.industrial-button {
  /* Base button styles optimized for industrial use */
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: var(--button-padding);
  border: 2px solid var(--button-border-color);
  border-radius: var(--button-border-radius);
  font-family: var(--font-primary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  cursor: pointer;
  transition: all 0.2s ease-out;
  position: relative;
  overflow: hidden;
  min-height: var(--control-min-touch-target);
}

/* Size variants */
.industrial-button--small {
  --button-padding: 8px 16px;
  font-size: 12px;
}

.industrial-button--medium {
  --button-padding: 12px 24px;
  font-size: 14px;
}

.industrial-button--large {
  --button-padding: 16px 32px;
  font-size: 16px;
}

.industrial-button--emergency {
  --button-padding: 24px;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  flex-direction: column;
  font-size: 14px;
}

/* Variant styles */
.industrial-button--primary {
  --button-border-color: var(--accent-operational);
  --button-bg-color: var(--accent-operational);
  --button-text-color: white;
}

.industrial-button--danger {
  --button-border-color: var(--warning-critical);
  --button-bg-color: var(--warning-critical);
  --button-text-color: white;
  animation: emergency-pulse 2s ease-in-out infinite;
}

.industrial-button--emergency {
  --button-border-color: var(--text-primary);
  --button-bg-color: var(--warning-critical);
  --button-text-color: white;
  box-shadow: 0 4px 20px rgba(220, 38, 38, 0.3);
}

/* States */
.industrial-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.industrial-button:active {
  transform: translateY(0);
}

.industrial-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.industrial-button--loading {
  pointer-events: none;
}

.industrial-button--confirming {
  animation: confirm-pulse 0.5s ease-in-out;
}
```

#### Industrial Slider Component
```typescript
// components/controls/IndustrialSlider.tsx
interface IndustrialSliderProps {
  value: number;
  min: number;
  max: number;
  step?: number;
  label: string;
  unit?: string;
  critical?: {
    min?: number;
    max?: number;
  };
  disabled?: boolean;
  showValue?: boolean;
  onChange: (value: number) => void;
}

const IndustrialSlider: React.FC<IndustrialSliderProps> = ({
  value,
  min,
  max,
  step = 1,
  label,
  unit,
  critical,
  disabled = false,
  showValue = true,
  onChange
}) => {
  const percentage = ((value - min) / (max - min)) * 100;
  const isCritical = critical && (
    (critical.min !== undefined && value <= critical.min) ||
    (critical.max !== undefined && value >= critical.max)
  );

  return (
    <div className="industrial-slider">
      <div className="industrial-slider__header">
        <label className="industrial-slider__label">{label}</label>
        {showValue && (
          <span className="industrial-slider__value">
            {value} {unit}
          </span>
        )}
      </div>
      <div className="industrial-slider__track">
        <div
          className={`industrial-slider__progress ${
            isCritical ? 'industrial-slider__progress--critical' : ''
          }`}
          style={{ width: `${percentage}%` }}
        />
        <div
          className="industrial-slider__thumb"
          style={{ left: `${percentage}%` }}
        />
      </div>
    </div>
  );
};
```

### 2. Data Display Components

#### Industrial Gauge Component
```typescript
// components/data-display/IndustrialGauge.tsx
interface IndustrialGaugeProps {
  value: number;
  min: number;
  max: number;
  label: string;
  unit: string;
  thresholds?: {
    warning: number;
    critical: number;
  };
  size?: 'small' | 'medium' | 'large';
}

const IndustrialGauge: React.FC<IndustrialGaugeProps> = ({
  value,
  min,
  max,
  label,
  unit,
  thresholds,
  size = 'medium'
}) => {
  const percentage = ((value - min) / (max - min)) * 100;
  const rotation = (percentage * 180) / 100 - 90; // -90 to +90 degrees

  const getStatus = () => {
    if (thresholds) {
      if (value >= thresholds.critical) return 'critical';
      if (value >= thresholds.warning) return 'warning';
    }
    return 'normal';
  };

  const status = getStatus();

  return (
    <div className={`industrial-gauge industrial-gauge--${size} industrial-gauge--${status}`}>
      <div className="industrial-gauge__label">{label}</div>
      <div className="industrial-gauge__display">
        <svg viewBox="0 0 200 120" className="industrial-gauge__svg">
          {/* Background arc */}
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke="var(--surface-tertiary)"
            strokeWidth="8"
            strokeLinecap="round"
          />

          {/* Progress arc */}
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke={`var(--status-${status})`}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={`${percentage * 2.51} 251`}
            className="industrial-gauge__progress"
          />

          {/* Needle */}
          <g
            transform={`translate(100, 100) rotate(${rotation})`}
            className="industrial-gauge__needle"
          >
            <line
              x1="0"
              y1="0"
              x2="0"
              y2="-60"
              stroke="var(--text-primary)"
              strokeWidth="3"
              strokeLinecap="round"
            />
            <circle cx="0" cy="0" r="6" fill="var(--text-primary)" />
          </g>
        </svg>

        <div className="industrial-gauge__value">
          <span className="industrial-gauge__number">{value}</span>
          <span className="industrial-gauge__unit">{unit}</span>
        </div>
      </div>
    </div>
  );
};
```

#### Status Panel Component
```typescript
// components/status/StatusPanel.tsx
interface StatusItem {
  id: string;
  label: string;
  value: string | number;
  status: 'normal' | 'warning' | 'error' | 'unknown';
  timestamp?: string;
}

interface StatusPanelProps {
  title: string;
  items: StatusItem[];
  compact?: boolean;
}

const StatusPanel: React.FC<StatusPanelProps> = ({
  title,
  items,
  compact = false
}) => {
  return (
    <div className="status-panel">
      <div className="status-panel__header">
        <h3 className="status-panel__title">{title}</h3>
        <div className="status-panel__summary">
          {items.filter(item => item.status === 'error').length > 0 && (
            <span className="status-panel__count status-panel__count--error">
              {items.filter(item => item.status === 'error').length} errors
            </span>
          )}
          {items.filter(item => item.status === 'warning').length > 0 && (
            <span className="status-panel__count status-panel__count--warning">
              {items.filter(item => item.status === 'warning').length} warnings
            </span>
          )}
        </div>
      </div>

      <div className="status-panel__items">
        {items.map(item => (
          <div key={item.id} className="status-item">
            <div className="status-item__info">
              <div className={`status-item__indicator status-item__indicator--${item.status}`} />
              <div className="status-item__details">
                <div className="status-item__label">{item.label}</div>
                <div className="status-item__value">{item.value}</div>
              </div>
            </div>
            {item.timestamp && (
              <div className="status-item__timestamp">{item.timestamp}</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
```

## Design Token System

### Manufacturing-Specific Tokens
```css
/* tokens/manufacturing.css */
:root {
  /* Manufacturing Color System */
  --manufacturing-primary: #1e3a8a;
  --manufacturing-secondary: #374151;
  --manufacturing-accent: #059669;

  /* Safety Colors (ISO 3864) */
  --safety-red: #dc2626;        /* Prohibition, danger, emergency */
  --safety-orange: #ea580c;     /* Warning, caution */
  --safety-yellow: #facc15;     /* Alert, attention */
  --safety-blue: #2563eb;       /* Mandatory action, information */
  --safety-green: #16a34a;      /* Safe condition, go */

  /* Control States */
  --control-active: #059669;
  --control-inactive: #6b7280;
  --control-error: #dc2626;
  --control-warning: #d97706;

  /* Industrial Typography */
  --font-display: 'Industrial Display', system-ui, sans-serif;
  --font-body: 'Industrial Text', system-ui, sans-serif;
  --font-mono: 'Industrial Mono', 'SF Mono', monospace;

  /* Control Sizing */
  --control-min-touch-target: 44px;
  --control-standard-height: 48px;
  --emergency-control-size: 120px;

  /* Industrial Spacing */
  --spacing-panel: 16px;
  --spacing-control: 12px;
  --spacing-section: 24px;

  /* Status Timing */
  --status-pulse-duration: 2s;
  --warning-flash-duration: 1s;
  --emergency-pulse-duration: 0.5s;
}
```

## Component Documentation Template

### Storybook Stories
```typescript
// stories/IndustrialButton.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { IndustrialButton } from '../components/controls/IndustrialButton';

const meta: Meta<typeof IndustrialButton> = {
  title: 'Manufacturing/Controls/IndustrialButton',
  component: IndustrialButton,
  parameters: {
    docs: {
      description: {
        component: `
Industrial button component designed specifically for manufacturing environments.
Features include:
- Glove-friendly touch targets (minimum 44px)
- High contrast for visibility in various lighting conditions
- Two-stage confirmation for critical operations
- Emergency stop styling and sizing
- Accessibility compliance (WCAG AA)
        `
      }
    }
  },
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'danger', 'emergency'],
      description: 'Button variant for different industrial contexts'
    },
    size: {
      control: 'select',
      options: ['small', 'medium', 'large', 'emergency'],
      description: 'Button size optimized for different use cases'
    },
    confirm: {
      control: 'boolean',
      description: 'Enable two-stage confirmation for critical operations'
    }
  }
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Primary: Story = {
  args: {
    variant: 'primary',
    size: 'medium',
    children: 'Start Process'
  }
};

export const EmergencyStop: Story = {
  args: {
    variant: 'emergency',
    size: 'emergency',
    children: 'Emergency Stop'
  }
};

export const WithConfirmation: Story = {
  args: {
    variant: 'danger',
    size: 'medium',
    confirm: true,
    children: 'Shutdown System'
  }
};
```

## Testing Templates

### Component Test Template
```typescript
// tests/IndustrialButton.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { IndustrialButton } from '../components/controls/IndustrialButton';

describe('IndustrialButton', () => {
  it('renders with correct styling for manufacturing use', () => {
    render(<IndustrialButton variant="primary">Test Button</IndustrialButton>);

    const button = screen.getByRole('button');
    expect(button).toHaveClass('industrial-button--primary');
    expect(button).toHaveAttribute('type', 'button');
  });

  it('meets minimum touch target size for gloves', () => {
    render(<IndustrialButton variant="primary">Test Button</IndustrialButton>);

    const button = screen.getByRole('button');
    const styles = window.getComputedStyle(button);
    const height = parseInt(styles.height);
    const width = parseInt(styles.width);

    expect(height).toBeGreaterThanOrEqual(44);
    expect(width).toBeGreaterThanOrEqual(44);
  });

  it('shows confirmation state for critical operations', () => {
    const handleClick = jest.fn();
    render(
      <IndustrialButton variant="danger" confirm onClick={handleClick}>
        Delete Data
      </IndustrialButton>
    );

    const button = screen.getByRole('button');
    fireEvent.click(button);

    expect(button).toHaveClass('industrial-button--confirming');
    expect(screen.getByText('Confirm?')).toBeInTheDocument();
  });

  it('has proper ARIA attributes for accessibility', () => {
    render(<IndustrialButton variant="primary" disabled>Disabled Button</IndustrialButton>);

    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('disabled');
  });
});
```

## Build Configuration

### Webpack Configuration for Component Library
```javascript
// build/webpack.config.js
module.exports = {
  mode: 'production',
  entry: './src/index.ts',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'manufacturing-ui.js',
    library: 'ManufacturingUI',
    libraryTarget: 'umd'
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: 'ts-loader',
        exclude: /node_modules/
      },
      {
        test: /\.css$/,
        use: [
          'style-loader',
          'css-loader',
          {
            loader: 'postcss-loader',
            options: {
              postcssOptions: {
                plugins: [
                  require('autoprefixer'),
                  require('cssnano')
                ]
              }
            }
          }
        ]
      }
    ]
  },
  resolve: {
    extensions: ['.tsx', '.ts', '.js']
  },
  externals: {
    react: 'React',
    'react-dom': 'ReactDOM'
  }
};
```

This comprehensive component library template provides the foundation for building consistent, professional manufacturing interfaces that meet industrial requirements while maintaining high quality and accessibility standards.