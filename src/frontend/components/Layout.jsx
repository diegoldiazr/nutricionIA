import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';

const navItems = [
  { name: 'Dashboard', href: '/', icon: '📊' },
  { name: 'Daily Nutrition', href: '/daily-nutrition', icon: '🥗' },
  { name: 'Meal Suggestions', href: '/meal-suggestions', icon: '🍽️' },
  { name: 'Weight Tracking', href: '/weight-tracking', icon: '⚖️' },
  { name: 'AI Coach', href: '/ai-coach', icon: '🤖' },
  { name: 'Settings', href: '/settings', icon: '⚙️' },
];

export default function Layout({ children, title = 'NutricionAI' }) {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>{title} - AI Nutrition Assistant</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 bg-gray-800 text-white min-h-screen fixed left-0 top-0">
          <div className="p-6">
            <h1 className="text-2xl font-bold mb-8">NutricionAI</h1>
            <nav className="space-y-2">
              {navItems.map(item => (
                <Link key={item.href} href={item.href}>
                  <a className={`flex items-center px-4 py-3 rounded-lg transition-colors ${
                    router.pathname === item.href
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-300 hover:bg-gray-700'
                  }`}>
                    <span className="mr-3 text-xl">{item.icon}</span>
                    {item.name}
                  </a>
                </Link>
              ))}
            </nav>
          </div>
        </aside>

        {/* Main content */}
        <main className="ml-64 flex-1 p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
