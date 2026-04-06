import Layout from '../components/Layout';
import { useEffect, useState } from 'react';
import { apiClient } from '../lib/api';

export default function DailyNutrition() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const userId = 1;

  useEffect(() => {
    fetchData();
  }, [date]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const data = await apiClient.getDailySummary(userId, date);
      setSummary(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <Layout><div className="text-center py-10">Loading...</div></Layout>;

  const macros = summary?.daily_macros || {};
  const targets = summary?.nutrition_status?.targets || {};
  const remaining = summary?.nutrition_status?.remaining || {};

  return (
    <Layout title="Daily Nutrition">
      <div className="mb-6 flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-800">Daily Nutrition</h1>
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="border rounded px-3 py-2"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MacroCard label="Calories" consumed={macros.calories || 0} target={targets.daily_calories || 0} unit="kcal" color="blue" />
        <MacroCard label="Protein" consumed={macros.protein || 0} target={targets.macro_breakdown?.protein_grams || 0} unit="g" color="green" />
        <MacroCard label="Carbs" consumed={macros.carbs || 0} target={targets.macro_breakdown?.carbs_grams || 0} unit="g" color="yellow" />
        <MacroCard label="Fat" consumed={macros.fat || 0} target={targets.macro_breakdown?.fat_grams || 0} unit="g" color="red" />
      </div>

      <div className="bg-white rounded-xl shadow p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Remaining for Today</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <RemainingItem label="Calories" value={remaining.calories || 0} />
          <RemainingItem label="Protein" value={`${remaining.protein || 0}g`} />
          <RemainingItem label="Carbs" value={`${remaining.carbs || 0}g`} />
          <RemainingItem label="Fat" value={`${remaining.fat || 0}g`} />
        </div>
      </div>

      {summary?.meal_suggestions?.length > 0 && (
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Meal Suggestions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {summary.meal_suggestions.map((meal, i) => (
              <div key={i} className="border rounded-lg p-4">
                <h3 className="font-medium text-lg mb-2">{meal.name}</h3>
                <p className="text-sm text-gray-600 mb-3">
                  <strong>Ingredients:</strong> {meal.ingredients?.join(', ')}
                </p>
                {meal.instructions && meal.instructions.length > 0 && (
                  <div className="mb-4">
                    <h4 className="font-medium mb-1">Instructions:</h4>
                    <ol className="list-decimal list-inside text-sm text-gray-700 space-y-1">
                      {meal.instructions.slice(0, 3).map((step, i) => (
                        <li key={i}>{step}</li>
                      ))}
                    </ol>
                  </div>
                )}
                <div className="border-t pt-4 mt-4">
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-gray-500">Calories:</span>
                      <div className="font-bold text-blue-600">{meal.nutrition?.calories || 0} kcal</div>
                    </div>
                    <div>
                      <span className="text-gray-500">Protein:</span>
                      <div className="font-bold text-green-600">{meal.nutrition?.protein || 0}g</div>
                    </div>
                    <div>
                      <span className="text-gray-500">Carbs:</span>
                      <div className="font-bold text-yellow-600">{meal.nutrition?.carbs || 0}g</div>
                    </div>
                    <div>
                      <span className="text-gray-500">Fat:</span>
                      <div className="font-bold text-red-600">{meal.nutrition?.fat || 0}g</div>
                    </div>
                  </div>
                </div>
                {(meal.prep_time_minutes || meal.cook_time_minutes) && (
                  <div className="mt-4 text-sm text-gray-500">
                    Prep: {meal.prep_time_minutes || 0}min | Cook: {meal.cook_time_minutes || 0}min
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </Layout>
  );
}

function MacroCard({ label, consumed, target, unit, color }) {
  const percent = target > 0 ? Math.min(100, (consumed / target) * 100) : 0;
  const colorMap = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500',
  };
  return (
    <div className="bg-white rounded-xl shadow p-6">
      <div className="text-sm text-gray-500">{label}</div>
      <div className="text-3xl font-bold mt-1">
        {consumed} <span className="text-base text-gray-400">{unit}</span>
      </div>
      <div className="mt-2 text-sm text-gray-600">Target: {target} {unit}</div>
      <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
        <div className={`${colorMap[color]} h-2 rounded-full`} style={{ width: `${percent}%` }}></div>
      </div>
    </div>
  );
}

function RemainingItem({ label, value }) {
  return (
    <div className="bg-gray-50 rounded-lg p-4 text-center">
      <div className="text-sm text-gray-500">{label}</div>
      <div className="text-2xl font-bold text-blue-600">{value}</div>
    </div>
  );
}
