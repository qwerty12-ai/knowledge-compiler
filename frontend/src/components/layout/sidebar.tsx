"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  FileSearch,
  FolderSearch,
  GitBranch,
  LayoutDashboard,
} from "lucide-react";

type NavItem = {
  label: string;
  href: string;
  icon: typeof LayoutDashboard;
};

const workspaceItems: NavItem[] = [
  {
    label: "Overview",
    href: "/",
    icon: LayoutDashboard,
  },
  {
    label: "Analyses",
    href: "/analyses",
    icon: Activity,
  },
  {
    label: "Claims",
    href: "/claims",
    icon: GitBranch,
  },
  {
    label: "Evidence",
    href: "/evidence",
    icon: FileSearch,
  },
];

const systemItems: NavItem[] = [
  {
    label: "Inspector",
    href: "/inspector",
    icon: FolderSearch,
  },
];

function isItemActive(
  pathname: string,
  href: string,
): boolean {
  if (href === "/") {
    return pathname === "/";
  }

  return (
    pathname === href ||
    pathname.startsWith(`${href}/`)
  );
}

function NavigationItem({
  item,
  pathname,
}: {
  item: NavItem;
  pathname: string;
}) {
  const Icon = item.icon;
  const active = isItemActive(
    pathname,
    item.href,
  );

  return (
    <Link
      href={item.href}
      className={[
        "group flex h-9 items-center gap-3 border-l-2 px-4 text-sm transition-colors",
        active
          ? "border-accent bg-accent/5 text-foreground"
          : "border-transparent text-muted-foreground hover:bg-surface-elevated hover:text-foreground",
      ].join(" ")}
    >
      <Icon
        size={16}
        strokeWidth={1.7}
        className={
          active
            ? "text-accent"
            : "text-muted-foreground group-hover:text-foreground"
        }
      />

      <span>{item.label}</span>
    </Link>
  );
}

function NavigationSection({
  label,
  items,
  pathname,
}: {
  label: string;
  items: NavItem[];
  pathname: string;
}) {
  return (
    <div className="space-y-1">
      <div className="px-4 pb-2 pt-5 font-mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground/60">
        {label}
      </div>

      <nav className="space-y-0.5">
        {items.map((item) => (
          <NavigationItem
            key={item.href}
            item={item}
            pathname={pathname}
          />
        ))}
      </nav>
    </div>
  );
}

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-56 shrink-0 border-r border-border-subtle bg-background lg:flex lg:flex-col">

      <div className="flex h-14 shrink-0 items-center border-b border-border-subtle px-4">
        <Link
          href="/"
          className="group flex min-w-0 items-center gap-3"
          aria-label="Knowledge Compiler home"
        >
          <div className="flex h-8 w-8 shrink-0 items-center justify-center">
            <Image
              src="/knowledge-compiler-mark.svg"
              alt=""
              width={32}
              height={32}
              priority
              className="h-8 w-8"
            />
          </div>

          <div className="min-w-0 leading-none">
            <div className="truncate text-sm font-medium tracking-tight text-foreground">
              Knowledge Compiler
            </div>
          </div>
        </Link>
      </div>

      <div className="flex-1 overflow-y-auto py-1">
        <NavigationSection
          label="Workspace"
          items={workspaceItems}
          pathname={pathname}
        />

        <NavigationSection
          label="System"
          items={systemItems}
          pathname={pathname}
        />
      </div>
    </aside>
  );
}