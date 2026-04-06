import Layout from '../components/Layout';
import { useEffect, useState } from 'react';
import { apiClient } from '../lib/api';

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const userId = 1; // Demo user

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const data = await apiClient.getDashboard(userId);
      setSummary(data);
    } catch (err) {
      console.error('Failed to fetch dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <Layout><div className="text-center py-10">Loading...</div></Layout>;

  const daily = summary?.daily_summary || {};
  const progress = summary?.progress_report || {};

  return (
    <Layout title="Dashboard">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Dashboard</h1>
        <p className="text-gray-600">Welcome back! Here's your nutrition overview.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Calories Today"
          value={daily?.daily_macros?.calories || 0}
          subtext={`Target: ${daily?.nutrition_status?.targets?.daily_calories || 0}`}
          color="blue"
        />
        <StatCard
          title="Protein"
          value={`${daily?.daily_macros?.protein || 0}g`}
          subtext={`Target: ${daily?.nutrition_status?.targets?.macro_breakdown?.protein_grams || 0}g`}
          color="green"
        />
        <StatCard
          title="Weekly Progress"
          value={`${(progress?.progress_analysis?.weight_change_weekly || 0).toFixed(1)} g`}
          subtext={progress?.progress_analysis?.weight_trend || 'stable'}
          color="purple"
        />
        <StatCard
          title="Adherence"
          value={`${Math.round((progress?.progress_analysis?.adherence_rate || 0) * 100)}%`}
          subtext="Meal logging"
          color="orange"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Nutrition Overview */}
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Nutrition Status</h2>
          {daily?.nutrition_status ? (
            <div>
              <div className="mb-4">
                <div className="flex justify-between mb-1">
                  <span>Calories remaining</span>
                  <span className="font-medium">
                    {daily.nutrition_status.remaining?.calories || 0} kcal
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-blue-600 h-3 rounded-full"
                    style={{
                      width: `${Math.min(100, ((daily?.daily_macros?.calories || 0) / (daily?.nutrition_status?.targets?.daily_calories || 1)) * 100)}%`
                    }}
                  ></div>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-lg font-bold text-green-600">{daily?.daily_macros?.protein || 0}g</div>
                  <div className="text-sm text-gray-500">Protein</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-yellow-600">{daily?.daily_macros?.carbs || 0}g</div>
                  <div className="text-sm text-gray-500">Carbs</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-red-600">{daily?.daily_macros?.fat || 0}g</div>
                  <div className="text-sm text-gray-500">Fat</div>
                </div>
              </div>
            </div>
          ) : (
            <p className="text-gray-500">No data available</p>
          )}
        </div>

        {/* Meal Suggestions */}
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Suggested Meals</h2>
          {daily?.meal_suggestions?.length > 0 ? (
            <ul className="space-y-3">
              {daily.meal_suggestions.slice(0, 3).map((meal, idx) => (
                <li key={idx} className="border-b pb-3 last:border-0">
                  <div className="font-medium">{meal.name}</div>
                  <div className="text-sm text-gray-600">
                    {meal.nutrition?.calories} cal • P: {meal.nutrition?.protein}g • C: {meal.nutrition?.carbs}g • F: {meal.nutrition?.fat}g
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500">No suggestions yet. Log your meals to get recommendations.</p>
          )}
        </div>
      </div>

      {/* Recommendations */}
      {progress?.recommendations?.overall_feedback && (
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-xl p-6">
          <h2 className="text-xl font-semibold mb-2 text-blue-900">AI Coach Feedback</h2>
          <p className="text-blue-800">{progress.recommendations.overall_feedback}</p>
        </div>
      )}
    </Layout>
  );
}

function StatCard({ title, value, subtext, color }) {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-800',
    green: 'bg-green-100 text-green-800',
    purple: 'bg-purple-100 text-purple-800',
    orange: 'bg-orange-100 text-orange-800',
  };
  return (
    <div className="bg-white rounded-xl shadow p-6">
      <div className="text-sm text-gray-500 mb-1">{title}</div>
      <div className={`text-3xl font-bold mb-2 ${colorClasses[color].split(' ')[1]}`}>
        {value}
      </div>
      <div className="text-xs text-gray-500">{subtext}</div>
    </div>
  );
}
