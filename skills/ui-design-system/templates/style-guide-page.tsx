'use client'

import { useState } from 'react'
import { 
  Palette,
  Type,
  MousePointer,
  TextCursor,
  LayoutGrid,
  CircleUser,
  MessageSquare,
  Ruler,
  Loader2,
  Mail,
  Search,
  Plus,
  Settings,
  ArrowRight,
  Check,
  X
} from 'lucide-react'

// ============================================
// IMPORTS: Update these with your actual components
// ============================================
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { 
  Card, 
  CardHeader, 
  CardTitle, 
  CardDescription, 
  CardContent, 
  CardFooter 
} from '@/components/ui/card'
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar'
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import { cn } from '@/lib/utils'

// ============================================
// NAVIGATION: Customize sections for your project
// ============================================
const NAV_ITEMS = [
  { id: 'colors', label: 'Colors', icon: Palette, children: [
    { id: 'brand', label: 'Brand' },
    { id: 'system', label: 'System' },
  ]},
  { id: 'typography', label: 'Typography', icon: Type },
  { id: 'buttons', label: 'Buttons', icon: MousePointer },
  { id: 'inputs', label: 'Inputs', icon: TextCursor },
  { id: 'cards', label: 'Cards', icon: LayoutGrid },
  { id: 'avatars', label: 'Avatars', icon: CircleUser },
  { id: 'dialogs', label: 'Dialogs', icon: MessageSquare },
  { id: 'loading', label: 'Loading', icon: Loader2 },
  { id: 'tokens', label: 'Tokens', icon: Ruler, children: [
    { id: 'spacing', label: 'Spacing' },
    { id: 'radius', label: 'Radius' },
    { id: 'shadows', label: 'Shadows' },
  ]},
]

// ============================================
// MAIN PAGE
// ============================================
export default function StyleGuidePage() {
  const [dialogOpen, setDialogOpen] = useState(false)
  const [activeSection, setActiveSection] = useState('colors')

  const scrollToSection = (id: string) => {
    setActiveSection(id)
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="px-6 py-4">
          {/* TODO: Update with your project name */}
          <h1 className="text-2xl font-bold text-foreground">STYLE GUIDE</h1>
        </div>
      </header>

      <div className="flex">
        {/* Left Navigation */}
        <nav className="sticky top-[57px] h-[calc(100vh-57px)] w-56 shrink-0 overflow-y-auto border-r border-border bg-muted/30 p-4">
          <ul className="space-y-1">
            {NAV_ITEMS.map((item) => (
              <li key={item.id}>
                <button
                  onClick={() => scrollToSection(item.id)}
                  className={cn(
                    "flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                    activeSection === item.id || item.children?.some(c => activeSection === c.id)
                      ? "bg-primary/10 text-primary"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  )}
                >
                  <item.icon className="h-4 w-4" />
                  {item.label}
                </button>
                {item.children && (
                  <ul className="ml-6 mt-1 space-y-1">
                    {item.children.map((child) => (
                      <li key={child.id}>
                        <button
                          onClick={() => scrollToSection(child.id)}
                          className={cn(
                            "w-full rounded-md px-3 py-1.5 text-left text-xs transition-colors",
                            activeSection === child.id
                              ? "text-primary font-medium"
                              : "text-muted-foreground hover:text-foreground"
                          )}
                        >
                          {child.label}
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </li>
            ))}
          </ul>
        </nav>

        {/* Main Content */}
        <main className="flex-1 p-8 space-y-16 max-w-5xl">
          
          {/* ==========================================
              COLORS
              Update with your brand colors
          ========================================== */}
          <section id="colors">
            <SectionHeader title="Colors" />
            
            {/* Brand Colors */}
            <div id="brand" className="mb-8">
              <h4 className="text-sm font-medium text-muted-foreground mb-3">Brand</h4>
              <div className="flex flex-wrap gap-2">
                {/* TODO: Replace with your brand colors */}
                <ColorChip color="bg-primary" label="Primary" hex="#3B82F6" />
                <ColorChip color="bg-secondary" label="Secondary" hex="#6B7280" />
                <ColorChip color="bg-accent" label="Accent" hex="#F59E0B" />
              </div>
            </div>

            {/* System Colors */}
            <div id="system">
              <h4 className="text-sm font-medium text-muted-foreground mb-3">System</h4>
              <div className="flex flex-wrap gap-2">
                <ColorChip color="bg-background" label="Background" hex="#FFF" border />
                <ColorChip color="bg-foreground" label="Foreground" hex="#1F2937" light />
                <ColorChip color="bg-muted" label="Muted" hex="#F3F4F6" />
                <ColorChip color="bg-destructive" label="Destructive" hex="#EF4444" light />
                <ColorChip color="bg-border" label="Border" hex="#E5E7EB" />
              </div>
            </div>
          </section>

          {/* ==========================================
              TYPOGRAPHY
              Update with your fonts
          ========================================== */}
          <section id="typography">
            <SectionHeader title="Typography" />
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                {/* TODO: Update with your display font */}
                <h4 className="text-sm font-medium text-muted-foreground mb-3">Headings</h4>
                <div className="space-y-2">
                  <p className="text-4xl font-bold">Heading 1</p>
                  <p className="text-3xl font-bold">Heading 2</p>
                  <p className="text-2xl font-semibold">Heading 3</p>
                  <p className="text-xl font-semibold">Heading 4</p>
                </div>
              </div>
              <div>
                <h4 className="text-sm font-medium text-muted-foreground mb-3">Body</h4>
                <div className="space-y-2">
                  <p className="text-lg">Large body text</p>
                  <p className="text-base">Base body text</p>
                  <p className="text-sm text-muted-foreground">Small muted text</p>
                  <p className="text-xs text-muted-foreground">Extra small label</p>
                </div>
              </div>
            </div>
          </section>

          {/* ==========================================
              BUTTONS
          ========================================== */}
          <section id="buttons">
            <SectionHeader title="Buttons" />
            <div className="space-y-6">
              <div>
                <h4 className="text-xs font-medium text-muted-foreground mb-3 uppercase tracking-wide">Variants</h4>
                <div className="flex flex-wrap gap-3">
                  <Button variant="default">Default</Button>
                  <Button variant="secondary">Secondary</Button>
                  <Button variant="outline">Outline</Button>
                  <Button variant="ghost">Ghost</Button>
                  <Button variant="link">Link</Button>
                  <Button variant="destructive">Destructive</Button>
                </div>
              </div>
              <div>
                <h4 className="text-xs font-medium text-muted-foreground mb-3 uppercase tracking-wide">Sizes</h4>
                <div className="flex flex-wrap items-center gap-3">
                  <Button size="sm">Small</Button>
                  <Button size="default">Default</Button>
                  <Button size="lg">Large</Button>
                  <Button size="icon"><Plus /></Button>
                </div>
              </div>
              <div>
                <h4 className="text-xs font-medium text-muted-foreground mb-3 uppercase tracking-wide">With Icons</h4>
                <div className="flex flex-wrap gap-3">
                  <Button><Mail className="mr-2 h-4 w-4" />Email</Button>
                  <Button variant="outline">Next <ArrowRight className="ml-2 h-4 w-4" /></Button>
                  <Button variant="secondary"><Settings className="mr-2 h-4 w-4" />Settings</Button>
                </div>
              </div>
              <div>
                <h4 className="text-xs font-medium text-muted-foreground mb-3 uppercase tracking-wide">States</h4>
                <div className="flex flex-wrap gap-3">
                  <Button>Normal</Button>
                  <Button disabled>Disabled</Button>
                  <Button disabled>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Loading
                  </Button>
                </div>
              </div>
            </div>
          </section>

          {/* ==========================================
              INPUTS
          ========================================== */}
          <section id="inputs">
            <SectionHeader title="Inputs" />
            <div className="max-w-sm space-y-4">
              <div>
                <label className="text-sm font-medium mb-1 block">Default</label>
                <Input placeholder="Placeholder text..." />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">With Value</label>
                <Input defaultValue="Entered value" />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Disabled</label>
                <Input placeholder="Disabled" disabled />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Error</label>
                <Input placeholder="Error state" aria-invalid="true" />
                <p className="text-xs text-destructive mt-1">Validation error message</p>
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">With Icon</label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input placeholder="Search..." className="pl-10" />
                </div>
              </div>
            </div>
          </section>

          {/* ==========================================
              CARDS
          ========================================== */}
          <section id="cards">
            <SectionHeader title="Cards" />
            <div className="grid md:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle>Basic Card</CardTitle>
                  <CardDescription>Card with header and content</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">Card body content goes here.</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>With Footer</CardTitle>
                  <CardDescription>Card with action buttons</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">Card with footer actions.</p>
                </CardContent>
                <CardFooter className="gap-2">
                  <Button variant="outline" size="sm">Cancel</Button>
                  <Button size="sm">Save</Button>
                </CardFooter>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Interactive Card</CardTitle>
                  <CardDescription>With form elements</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <Input placeholder="Enter name..." />
                  <Input placeholder="Enter email..." />
                </CardContent>
                <CardFooter>
                  <Button className="w-full">Submit</Button>
                </CardFooter>
              </Card>
              <Card className="flex items-center justify-center p-8">
                <div className="text-center text-muted-foreground">
                  <Plus className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">Empty state placeholder</p>
                </div>
              </Card>
            </div>
          </section>

          {/* ==========================================
              AVATARS
          ========================================== */}
          <section id="avatars">
            <SectionHeader title="Avatars" />
            <div className="flex items-end gap-6">
              <div className="text-center">
                <Avatar className="h-8 w-8">
                  <AvatarFallback>S</AvatarFallback>
                </Avatar>
                <p className="text-xs text-muted-foreground mt-2">sm</p>
              </div>
              <div className="text-center">
                <Avatar className="h-10 w-10">
                  <AvatarImage src="https://github.com/shadcn.png" />
                  <AvatarFallback>M</AvatarFallback>
                </Avatar>
                <p className="text-xs text-muted-foreground mt-2">md</p>
              </div>
              <div className="text-center">
                <Avatar className="h-14 w-14">
                  <AvatarFallback className="bg-primary text-primary-foreground text-lg">LG</AvatarFallback>
                </Avatar>
                <p className="text-xs text-muted-foreground mt-2">lg</p>
              </div>
              <div className="text-center">
                <Avatar className="h-14 w-14">
                  <AvatarFallback className="bg-accent text-white text-xl">🎨</AvatarFallback>
                </Avatar>
                <p className="text-xs text-muted-foreground mt-2">emoji</p>
              </div>
            </div>
          </section>

          {/* ==========================================
              DIALOGS
          ========================================== */}
          <section id="dialogs">
            <SectionHeader title="Dialogs" />
            <div className="flex flex-wrap gap-4">
              <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                <DialogTrigger asChild>
                  <Button variant="outline">Open Dialog</Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Dialog Title</DialogTitle>
                    <DialogDescription>
                      Dialog description text that explains what this dialog is for.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="py-4">
                    <p className="text-sm text-muted-foreground">Dialog content goes here.</p>
                  </div>
                  <DialogFooter>
                    <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
                    <Button onClick={() => setDialogOpen(false)}>Confirm</Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
              
              {/* TODO: Add your custom dialogs here */}
            </div>
          </section>

          {/* ==========================================
              LOADING STATES
              TODO: Add your loading/spinner components
          ========================================== */}
          <section id="loading">
            <SectionHeader title="Loading States" />
            <div className="space-y-6">
              {/* Spinner */}
              <div>
                <h4 className="text-xs font-medium text-muted-foreground mb-3 uppercase tracking-wide">Spinners</h4>
                <div className="flex items-center gap-6">
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                    <span className="text-xs text-muted-foreground">sm</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-6 w-6 animate-spin text-primary" />
                    <span className="text-xs text-muted-foreground">md</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                    <span className="text-xs text-muted-foreground">lg</span>
                  </div>
                </div>
              </div>

              {/* Skeleton */}
              <div>
                <h4 className="text-xs font-medium text-muted-foreground mb-3 uppercase tracking-wide">Skeleton Loading</h4>
                <div className="max-w-md space-y-3">
                  <div className="h-4 bg-muted rounded animate-pulse" />
                  <div className="h-4 bg-muted rounded animate-pulse w-3/4" />
                  <div className="h-4 bg-muted rounded animate-pulse w-1/2" />
                </div>
              </div>

              {/* Status indicators */}
              <div>
                <h4 className="text-xs font-medium text-muted-foreground mb-3 uppercase tracking-wide">Status</h4>
                <div className="flex flex-wrap gap-4">
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-green-500" />
                    <span className="text-sm">Connected</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-yellow-500 animate-pulse" />
                    <span className="text-sm">Syncing</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-muted-foreground/50" />
                    <span className="text-sm">Offline</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-destructive" />
                    <span className="text-sm">Error</span>
                  </div>
                </div>
              </div>

              {/* TODO: Add thinking/AI indicators here */}
            </div>
          </section>

          {/* ==========================================
              DESIGN TOKENS
          ========================================== */}
          <section id="tokens">
            <SectionHeader title="Design Tokens" />
            
            {/* Spacing */}
            <div id="spacing" className="mb-8">
              <h4 className="text-xs font-medium text-muted-foreground mb-3 uppercase tracking-wide">Spacing</h4>
              <div className="flex items-end gap-1">
                {[1, 2, 3, 4, 6, 8, 12, 16].map(s => (
                  <div key={s} className="text-center">
                    <div className="bg-primary rounded-sm" style={{ width: s * 4, height: 32 }} />
                    <span className="text-[10px] text-muted-foreground">{s}</span>
                  </div>
                ))}
              </div>
              <p className="text-xs text-muted-foreground mt-2">Values shown in 4px units (1 = 4px, 2 = 8px, etc.)</p>
            </div>

            {/* Radius */}
            <div id="radius" className="mb-8">
              <h4 className="text-xs font-medium text-muted-foreground mb-3 uppercase tracking-wide">Border Radius</h4>
              <div className="flex gap-4">
                {[
                  { name: 'sm', class: 'rounded-sm' },
                  { name: 'md', class: 'rounded-md' },
                  { name: 'lg', class: 'rounded-lg' },
                  { name: 'xl', class: 'rounded-xl' },
                  { name: 'full', class: 'rounded-full' },
                ].map(r => (
                  <div key={r.name} className="text-center">
                    <div className={`h-12 w-12 bg-primary ${r.class}`} />
                    <span className="text-[10px] text-muted-foreground">{r.name}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Shadows */}
            <div id="shadows">
              <h4 className="text-xs font-medium text-muted-foreground mb-3 uppercase tracking-wide">Shadows</h4>
              <div className="flex gap-6">
                {[
                  { name: 'sm', class: 'shadow-sm' },
                  { name: 'md', class: 'shadow-md' },
                  { name: 'lg', class: 'shadow-lg' },
                  { name: 'xl', class: 'shadow-xl' },
                ].map(s => (
                  <div key={s.name} className="text-center">
                    <div className={`h-12 w-16 bg-card rounded-lg ${s.class}`} />
                    <span className="text-[10px] text-muted-foreground mt-2 block">{s.name}</span>
                  </div>
                ))}
              </div>
            </div>
          </section>

        </main>
      </div>
    </div>
  )
}

// ============================================
// HELPER COMPONENTS
// ============================================

function SectionHeader({ title }: { title: string }) {
  return (
    <h2 className="text-xl font-semibold text-foreground mb-6 pb-2 border-b border-border">
      {title}
    </h2>
  )
}

interface ColorChipProps {
  color: string
  label: string
  hex: string
  border?: boolean
  light?: boolean
}

function ColorChip({ color, label, hex, border, light }: ColorChipProps) {
  return (
    <div 
      className={cn(
        "flex items-center gap-2 rounded-full pl-1 pr-3 py-1",
        border && "border border-border"
      )}
    >
      <div className={cn("h-6 w-6 rounded-full", color)} />
      <div className="flex items-baseline gap-1.5">
        <span className="text-xs font-medium">{label}</span>
        <span className="text-[10px] text-muted-foreground font-mono">{hex}</span>
      </div>
    </div>
  )
}
