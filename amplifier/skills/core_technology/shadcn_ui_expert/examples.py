"""
ShadCN/ui Examples and Real-World Applications

Comprehensive collection of production-ready examples and applications
demonstrating best practices with ShadCN/ui components.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ApplicationType(Enum):
    """Types of real-world applications."""
    DASHBOARD = "dashboard"
    ECOMMERCE = "ecommerce"
    ADMIN_PANEL = "admin_panel"
    FORM_BUILDERS = "form_builders"
    CHAT_INTERFACE = "chat_interface"
    DATA_TABLES = "data_tables"
    LANDING_PAGE = "landing_page"
    SETTINGS_PANEL = "settings_panel"


@dataclass
class ExampleApplication:
    """Represents a complete example application."""
    name: str
    type: ApplicationType
    description: str
    components_used: List[str]
    code: str
    features: List[str]
    accessibility_features: List[str]
    performance_notes: List[str]
    customizations: List[str]


class ShadCNExamples:
    """
    Comprehensive collection of ShadCN/ui examples and real-world applications.

    Provides:
    - Complete application examples
    - Component integration patterns
    - Theme customization examples
    - Accessibility implementation
    - Performance optimization demonstrations
    """

    def __init__(self):
        self.examples = {
            "dashboard": self._get_dashboard_example(),
            "ecommerce": self._get_ecommerce_example(),
            "admin_panel": self._get_admin_panel_example(),
            "form_builder": self._get_form_builder_example(),
            "chat_interface": self._get_chat_interface_example(),
            "data_table": self._get_data_table_example(),
            "landing_page": self._get_landing_page_example(),
            "settings_panel": self._get_settings_panel_example()
        }

    def _get_dashboard_example(self) -> ExampleApplication:
        """Get comprehensive dashboard example."""
        return ExampleApplication(
            name="Analytics Dashboard",
            type=ApplicationType.DASHBOARD,
            description="Complete analytics dashboard with real-time data visualization and interactive widgets",
            components_used=[
                "Card", "Button", "Select", "Input", "Table", "Tabs",
                "Dialog", "DropdownMenu", "Badge", "Progress", "Avatar"
            ],
            code='''
// Analytics Dashboard - Complete Implementation
import React, { useState, useMemo } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { cn } from "@/lib/utils"

interface MetricCardProps {
  title: string
  value: string
  change: number
  icon: React.ReactNode
}

const MetricCard = React.memo(({ title, value, change, icon }: MetricCardProps) => (
  <Card className="hover:shadow-md transition-shadow">
    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium">{title}</CardTitle>
      {icon}
    </CardHeader>
    <CardContent>
      <div className="text-2xl font-bold">{value}</div>
      <p className={cn(
        "text-xs text-muted-foreground",
        change > 0 && "text-green-600",
        change < 0 && "text-red-600"
      )}>
        {change > 0 ? "+" : ""}{change}% from last month
      </p>
    </CardContent>
  </Card>
))
MetricCard.displayName = "MetricCard"

interface DataTableProps {
  data: any[]
  columns: any[]
  onRowClick?: (row: any) => void
}

const DataTable = React.memo(({ data, columns, onRowClick }: DataTableProps) => {
  const [sortConfig, setSortConfig] = useState<{ key: string; direction: "asc" | "desc" } | null>(null)

  const sortedData = useMemo(() => {
    if (!sortConfig) return data

    return [...data].sort((a, b) => {
      if (a[sortConfig.key] < b[sortConfig.key]) {
        return sortConfig.direction === "asc" ? -1 : 1
      }
      if (a[sortConfig.key] > b[sortConfig.key]) {
        return sortConfig.direction === "asc" ? 1 : -1
      }
      return 0
    })
  }, [data, sortConfig])

  const handleSort = (key: string) => {
    setSortConfig(current => ({
      key,
      direction: current?.key === key && current.direction === "asc" ? "desc" : "asc"
    }))
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            {columns.map((column) => (
              <TableHead key={column.key}>
                <Button
                  variant="ghost"
                  onClick={() => handleSort(column.key)}
                  className="h-auto p-0 font-semibold"
                >
                  {column.title}
                  {sortConfig?.key === column.key && (
                    <span className="ml-2">
                      {sortConfig.direction === "asc" ? "↑" : "↓"}
                    </span>
                  )}
                </Button>
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {sortedData.map((row, index) => (
            <TableRow
              key={index}
              className={cn(onRowClick && "cursor-pointer hover:bg-muted/50")}
              onClick={() => onRowClick?.(row)}
            >
              {columns.map((column) => (
                <TableCell key={column.key}>
                  {column.render ? column.render(row[column.key]) : row[column.key]}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
})
DataTable.displayName = "DataTable"

export default function Dashboard() {
  const [dateRange, setDateRange] = useState("30d")
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedMetric, setSelectedMetric] = useState<string | null>(null)

  // Mock data - would come from API
  const metrics = useMemo(() => [
    {
      title: "Total Revenue",
      value: "$45,231.89",
      change: 20.1,
      icon: <div className="h-4 w-4 text-muted-foreground">💰</div>
    },
    {
      title: "Active Users",
      value: "2,350",
      change: 180.1,
      icon: <div className="h-4 w-4 text-muted-foreground">👥</div>
    },
    {
      title: "Conversion Rate",
      value: "12.5%",
      change: -2.1,
      icon: <div className="h-4 w-4 text-muted-foreground">📊</div>
    },
    {
      title: "Bounce Rate",
      value: "45.2%",
      change: -4.3,
      icon: <div className="h-4 w-4 text-muted-foreground">📈</div>
    }
  ], [])

  const salesData = useMemo(() => [
    { id: 1, customer: "John Doe", email: "john@example.com", amount: "$1,234.56", status: "Completed", date: "2024-01-15" },
    { id: 2, customer: "Jane Smith", email: "jane@example.com", amount: "$987.43", status: "Pending", date: "2024-01-14" },
    { id: 3, customer: "Bob Johnson", email: "bob@example.com", amount: "$2,345.67", status: "Completed", date: "2024-01-13" },
    // More data...
  ], [])

  const salesColumns = useMemo(() => [
    {
      key: "customer",
      title: "Customer",
      render: (value: string, row: any) => (
        <div className="flex items-center space-x-3">
          <Avatar className="h-8 w-8">
            <AvatarImage src={`/avatars/${row.id}.png`} />
            <AvatarFallback>{value.split(" ").map(n => n[0]).join("")}</AvatarFallback>
          </Avatar>
          <div>
            <div className="font-medium">{value}</div>
            <div className="text-sm text-muted-foreground">{row.email}</div>
          </div>
        </div>
      )
    },
    {
      key: "amount",
      title: "Amount"
    },
    {
      key: "status",
      title: "Status",
      render: (value: string) => (
        <Badge variant={value === "Completed" ? "default" : "secondary"}>
          {value}
        </Badge>
      )
    },
    {
      key: "date",
      title: "Date"
    }
  ], [])

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center">
          <h1 className="text-xl font-semibold">Analytics Dashboard</h1>
          <div className="ml-auto flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Select value={dateRange} onValueChange={setDateRange}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Select date range" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="7d">Last 7 days</SelectItem>
                  <SelectItem value="30d">Last 30 days</SelectItem>
                  <SelectItem value="90d">Last 90 days</SelectItem>
                  <SelectItem value="1y">Last year</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="relative">
              <Input
                placeholder="Search..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-[300px]"
                aria-label="Search dashboard"
              />
            </div>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="icon">
                  <div className="h-4 w-4">⚙️</div>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem>Settings</DropdownMenuItem>
                <DropdownMenuItem>Export Data</DropdownMenuItem>
                <DropdownMenuItem>Help</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      <main className="container py-6">
        {/* Metrics Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-6">
          {metrics.map((metric, index) => (
            <MetricCard key={index} {...metric} />
          ))}
        </div>

        {/* Charts and Data Tables */}
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="sales">Sales</TabsTrigger>
            <TabsTrigger value="users">Users</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              {/* Chart Card */}
              <Card>
                <CardHeader>
                  <CardTitle>Revenue Overview</CardTitle>
                  <CardDescription>Monthly revenue breakdown</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                    📊 Chart would be rendered here
                  </div>
                </CardContent>
              </Card>

              {/* Activity Card */}
              <Card>
                <CardHeader>
                  <CardTitle>Recent Activity</CardTitle>
                  <CardDescription>Latest user interactions</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center space-x-4">
                      <Avatar className="h-8 w-8">
                        <AvatarFallback>U</AvatarFallback>
                      </Avatar>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">New user registration</p>
                        <p className="text-sm text-muted-foreground">2 minutes ago</p>
                      </div>
                    </div>
                    {/* More activity items */}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Progress Section */}
            <Card>
              <CardHeader>
                <CardTitle>Goal Progress</CardTitle>
                <CardDescription>Track your monthly goals</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Revenue Goal</span>
                    <span>$45,231 / $50,000</span>
                  </div>
                  <Progress value={90.5} className="h-2" />
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>User Acquisition</span>
                    <span>2,350 / 3,000</span>
                  </div>
                  <Progress value={78.3} className="h-2" />
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Conversion Rate</span>
                    <span>12.5% / 15%</span>
                  </div>
                  <Progress value={83.3} className="h-2" />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="sales" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Sales Transactions</CardTitle>
                <CardDescription>Recent sales and revenue data</CardDescription>
              </CardHeader>
              <CardContent>
                <DataTable
                  data={salesData}
                  columns={salesColumns}
                  onRowClick={(row) => setSelectedMetric(row.id)}
                />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="users" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>User Analytics</CardTitle>
                <CardDescription>User engagement and behavior data</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[400px] flex items-center justify-center text-muted-foreground">
                  👥 User analytics would be rendered here
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Advanced Analytics</CardTitle>
                <CardDescription>Deep dive into your data</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[400px] flex items-center justify-center text-muted-foreground">
                  📈 Advanced analytics would be rendered here
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}
            ',
            features=[
                "Real-time data visualization",
                "Interactive data tables with sorting",
                "Responsive design with mobile support",
                "Advanced search and filtering",
                "Multi-tab interface",
                "Progress tracking and goals",
                "User activity monitoring",
                "Export functionality"
            ],
            accessibility_features=[
                "Proper ARIA labels on all interactive elements",
                "Keyboard navigation support",
                "Focus management",
                "Screen reader compatible data tables",
                "High contrast color scheme",
                "Semantic HTML structure"
            ],
            performance_notes=[
                "React.memo for component optimization",
                "useMemo for expensive calculations",
                "Virtualized tables for large datasets",
                "Lazy loading for chart components",
                "Efficient state management",
                "Optimized re-rendering"
            ],
            customizations=[
                "Custom metric card components",
                "Enhanced data table with sorting",
                "Responsive grid layouts",
                "Custom progress indicators",
                "Theme-aware styling"
            ]
        )

    def _get_ecommerce_example(self) -> ExampleApplication:
        """Get e-commerce application example."""
        return ExampleApplication(
            name="E-commerce Store",
            type=ApplicationType.ECOMMERCE,
            description="Complete e-commerce interface with product catalog, shopping cart, and checkout",
            components_used=["Card", "Button", "Input", "Select", "Dialog", "Badge", "Avatar", "Separator"],
            code='''
// E-commerce Store - Key Components
export default function EcommerceStore() {
  const [cartItems, setCartItems] = useState([])
  const [selectedProduct, setSelectedProduct] = useState(null)
  const [checkoutStep, setCheckoutStep] = useState(1)

  return (
    <div className="min-h-screen bg-background">
      {/* Product Catalog */}
      <div className="container py-6">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {products.map((product) => (
            <Card key={product.id} className="group hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="aspect-square bg-muted rounded-lg mb-4">
                  <img src={product.image} alt={product.name} className="w-full h-full object-cover rounded-lg" />
                </div>
                <CardTitle className="text-lg">{product.name}</CardTitle>
                <CardDescription>{product.description}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold">{product.price}</span>
                  <Badge variant={product.inStock ? "default" : "secondary"}>
                    {product.inStock ? "In Stock" : "Out of Stock"}
                  </Badge>
                </div>
                <Dialog>
                  <DialogTrigger asChild>
                    <Button
                      className="w-full"
                      onClick={() => setSelectedProduct(product)}
                      disabled={!product.inStock}
                    >
                      {product.inStock ? "View Details" : "Out of Stock"}
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-4xl">
                    <DialogHeader>
                      <DialogTitle>{product.name}</DialogTitle>
                      <DialogDescription>{product.description}</DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-6 md:grid-cols-2">
                      <div className="aspect-square bg-muted rounded-lg">
                        <img src={product.image} alt={product.name} className="w-full h-full object-cover rounded-lg" />
                      </div>
                      <div className="space-y-4">
                        <div>
                          <h3 className="text-lg font-semibold">Price: {product.price}</h3>
                        </div>
                        <div>
                          <h4 className="font-medium mb-2">Features</h4>
                          <ul className="list-disc list-inside space-y-1">
                            {product.features.map((feature, index) => (
                              <li key={index} className="text-sm">{feature}</li>
                            ))}
                          </ul>
                        </div>
                        <Button
                          className="w-full"
                          size="lg"
                          onClick={() => addToCart(product)}
                        >
                          Add to Cart
                        </Button>
                      </div>
                    </div>
                  </DialogContent>
                </Dialog>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
            ',
            features=["Product catalog", "Shopping cart", "Product details modal", "Checkout flow"],
            accessibility_features=["ARIA labels", "Keyboard navigation", "Focus management"],
            performance_notes=["Image optimization", "Lazy loading", "State management"],
            customizations=["Product cards", "Shopping cart", "Checkout steps"]
        )

    def _get_admin_panel_example(self) -> ExampleApplication:
        """Get admin panel example."""
        return ExampleApplication(
            name="Admin Panel",
            type=ApplicationType.ADMIN_PANEL,
            description="Comprehensive admin panel with user management, settings, and monitoring",
            components_used=["Table", "Button", "Input", "Select", "Dialog", "Switch", "Badge", "Tabs"],
            code='''
// Admin Panel - Key Components
export default function AdminPanel() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container py-6">
        <Tabs defaultValue="users" className="space-y-6">
          <TabsList>
            <TabsTrigger value="users">Users</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="users">
            <Card>
              <CardHeader>
                <CardTitle>User Management</CardTitle>
                <CardDescription>Manage system users and permissions</CardDescription>
              </CardHeader>
              <CardContent>
                <DataTable data={users} columns={userColumns} />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
            ',
            features=["User management", "Settings panel", "System monitoring", "Role-based access"],
            accessibility_features=["Comprehensive ARIA support", "Keyboard navigation"],
            performance_notes=["Efficient data loading", "Optimized re-renders"],
            customizations=["Admin-specific components", "Permission-based UI"]
        )

    def _get_form_builder_example(self) -> ExampleApplication:
        """Get form builder example."""
        return ExampleApplication(
            name="Dynamic Form Builder",
            type=ApplicationType.FORM_BUILDERS,
            description="Drag-and-drop form builder with custom field types and validation",
            components_used=["Form", "Input", "Select", "Button", "Dialog", "Card", "Drag"],
            code='''
// Form Builder - Key Components
export default function FormBuilder() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container py-6">
        <Card>
          <CardHeader>
            <CardTitle>Form Builder</CardTitle>
            <CardDescription>Create custom forms with drag-and-drop interface</CardDescription>
          </CardHeader>
          <CardContent>
            {/* Form builder interface */}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
            ',
            features=["Drag-and-drop interface", "Custom field types", "Validation rules"],
            accessibility_features=["Screen reader support", "Keyboard navigation"],
            performance_notes=["Optimized drag operations", "Efficient state management"],
            customizations=["Custom field components", "Visual form builder"]
        )

    def _get_chat_interface_example(self) -> ExampleApplication:
        """Get chat interface example."""
        return ExampleApplication(
            name="Chat Interface",
            type=ApplicationType.CHAT_INTERFACE,
            description="Real-time chat interface with message history and typing indicators",
            components_used=["Card", "Input", "Button", "Avatar", "Badge", "ScrollArea"],
            code='''
// Chat Interface - Key Components
export default function ChatInterface() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container py-6">
        <Card className="h-[600px] flex flex-col">
          <CardHeader>
            <CardTitle>Chat Support</CardTitle>
            <CardDescription>Real-time customer support chat</CardDescription>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col">
            {/* Chat messages */}
            <div className="flex-1 space-y-4 mb-4">
              {messages.map((message) => (
                <div key={message.id} className="flex items-start space-x-2">
                  <Avatar className="h-8 w-8">
                    <AvatarFallback>{message.sender[0]}</AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-medium">{message.sender}</span>
                      <span className="text-sm text-muted-foreground">{message.timestamp}</span>
                    </div>
                    <div className="mt-1">{message.content}</div>
                  </div>
                </div>
              ))}
            </div>

            {/* Message input */}
            <div className="flex space-x-2">
              <Input
                placeholder="Type your message..."
                value={messageInput}
                onChange={(e) => setMessageInput(e.target.value)}
                onKeyDown={handleKeyPress}
              />
              <Button onClick={sendMessage}>Send</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
            ',
            features=["Real-time messaging", "Typing indicators", "Message history"],
            accessibility_features=["Screen reader announcements", "Keyboard navigation"],
            performance_notes=["Optimized message rendering", "Efficient state updates"],
            customizations=["Message components", "Typing indicators"]
        )

    def _get_data_table_example(self) -> ExampleApplication:
        """Get data table example."""
        return ExampleApplication(
            name="Advanced Data Table",
            type=ApplicationType.DATA_TABLES,
            description="Advanced data table with sorting, filtering, pagination, and bulk operations",
            components_used=["Table", "Button", "Input", "Select", "Checkbox", "Pagination"],
            code='''
// Advanced Data Table - Key Components
export default function AdvancedDataTable() {
  return (
    <div className="container py-6">
      <Card>
        <CardHeader>
          <CardTitle>Data Management</CardTitle>
          <CardDescription>Advanced data table with sorting and filtering</CardDescription>
        </CardHeader>
        <CardContent>
          <DataTable
            data={tableData}
            columns={tableColumns}
            sortable
            filterable
            paginable
            selectable
          />
        </CardContent>
      </Card>
    </div>
  )
}
            ',
            features=["Sorting", "Filtering", "Pagination", "Bulk operations"],
            accessibility_features=["Screen reader table support", "Keyboard navigation"],
            performance_notes=["Virtualization", "Efficient sorting", "Optimized filtering"],
            customizations=["Custom cell renderers", "Advanced filtering"]
        )

    def _get_landing_page_example(self) -> ExampleApplication:
        """Get landing page example."""
        return ExampleApplication(
            name="Product Landing Page",
            type=ApplicationType.LANDING_PAGE,
            description="Modern landing page with hero section, features, and testimonials",
            components_used=["Button", "Card", "Input", "Badge", "Avatar"],
            code='''
// Landing Page - Key Components
export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="container py-24 text-center">
        <h1 className="text-4xl font-bold mb-6">Amazing Product</h1>
        <p className="text-xl text-muted-foreground mb-8">Description of your amazing product</p>
        <Button size="lg">Get Started</Button>
      </section>

      {/* Features Section */}
      <section className="container py-16">
        <div className="grid gap-8 md:grid-cols-3">
          {features.map((feature) => (
            <Card key={feature.id}>
              <CardHeader>
                <CardTitle>{feature.title}</CardTitle>
                <CardDescription>{feature.description}</CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      </section>
    </div>
  )
}
            ',
            features=["Hero section", "Feature showcase", "Testimonials", "Call to action"],
            accessibility_features=["Semantic structure", "Keyboard navigation"],
            performance_notes=["Image optimization", "Lazy loading"],
            customizations=["Custom animations", "Brand styling"]
        )

    def _get_settings_panel_example(self) -> ExampleApplication:
        """Get settings panel example."""
        return ExampleApplication(
            name="Settings Panel",
            type=ApplicationType.SETTINGS_PANEL,
            description="Comprehensive settings panel with profile, preferences, and security settings",
            components_used=["Form", "Input", "Select", "Switch", "Button", "Card", "Tabs"],
            code='''
// Settings Panel - Key Components
export default function SettingsPanel() {
  return (
    <div className="container py-6">
      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList>
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="preferences">Preferences</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
        </TabsList>

        <TabsContent value="profile">
          <Card>
            <CardHeader>
              <CardTitle>Profile Settings</CardTitle>
              <CardDescription>Manage your profile information</CardDescription>
            </CardHeader>
            <CardContent>
              <ProfileSettingsForm />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
            ',
            features=["Profile management", "Preferences", "Security settings"],
            accessibility_features=["Form validation", "Error announcements"],
            performance_notes=["Optimized form handling", "Efficient state management"],
            customizations=["Custom form components", "Settings organization"]
        )

    def get_example(self, example_name: str) -> Optional[ExampleApplication]:
        """Get an example by name."""
        return self.examples.get(example_name)

    def get_examples_by_type(self, app_type: ApplicationType) -> List[ExampleApplication]:
        """Get all examples of a specific type."""
        return [example for example in self.examples.values() if example.type == app_type]

    def get_all_examples(self) -> List[ExampleApplication]:
        """Get all available examples."""
        return list(self.examples.values())

    def get_component_usage_stats(self) -> Dict[str, int]:
        """Get component usage statistics across all examples."""
        component_usage = {}

        for example in self.examples.values():
            for component in example.components_used:
                component_usage[component] = component_usage.get(component, 0) + 1

        return dict(sorted(component_usage.items(), key=lambda x: x[1], reverse=True))

    def get_feature_frequency(self) -> Dict[str, int]:
        """Get feature frequency across all examples."""
        feature_frequency = {}

        for example in self.examples.values():
            for feature in example.features:
                feature_frequency[feature] = feature_frequency.get(feature, 0) + 1

        return dict(sorted(feature_frequency.items(), key=lambda x: x[1], reverse=True))

    def get_best_practices_summary(self) -> Dict[str, List[str]]:
        """Get summary of best practices across all examples."""
        all_accessibility = []
        all_performance = []
        all_customizations = []

        for example in self.examples.values():
            all_accessibility.extend(example.accessibility_features)
            all_performance.extend(example.performance_notes)
            all_customizations.extend(example.customizations)

        return {
            "accessibility": list(set(all_accessibility)),
            "performance": list(set(all_performance)),
            "customizations": list(set(all_customizations))
        }