import Layout from '../components/Layout';
import { useEffect, useState } from 'react';
import { apiClient } from '../lib/api';

export default function MealSuggestions() {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [constraints, setConstraints] = useState({
    meal_type: 'lunch',
    remaining_calories: null,
    remaining_protein: null,
    remaining_carbs: null,
    remaining_fat: null,
  });
  const userId = 1;

  useEffect(() => {
    fetchSuggestions();
  }, []);

  const fetchSuggestions = async () => {
    setLoading(true);
    try {
      const data = await apiClient.getMealSuggestions(userId, constraints);
      setSuggestions(data?.suggestions || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleConstraintChange = (e) => {
    const { name, value } = e.target;
    setConstraints(prev => ({
      ...prev,
      [name]: value ? parseInt(value) : null
    }));
  };

  return (
    <Layout title="Meal Suggestions">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Meal Suggestions</h1>
        <p className="text-gray-600">Get personalized meal ideas based on your remaining macros and preferences.</p>
      </div>

      {/* Constraints Form */}
      <div className="bg-white rounded-xl shadow p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Filter by Macros</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Meal Type</label>
            <select
              name="meal_type"
              value={constraints.meal_type}
              onChange={handleConstraintChange}
              className="w-full border rounded px-3 py-2"
            >
              <option value="breakfast">Breakfast</option>
              <option value="lunch">Lunch</option>
              <option value="dinner">Dinner</option>
              <option value="snack">Snack</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Remaining Calories</label>
            <input
              type="number"
              name="remaining_calories"
              value={constraints.remaining_calories || ''}
              onChange={handleConstraintChange}
              placeholder="e.g. 500"
              className="w-full border rounded px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Remaining Protein (g)</label>
            <input
              type="number"
              name="remaining_protein"
              value={constraints.remaining_protein || ''}
              onChange={handleConstraintChange}
              placeholder="e.g. 30"
              className="w-full border rounded px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Remaining Carbs (g)</label>
            <input
              type="number"
              name="remaining_carbs"
              value={constraints.remaining_carbs || ''}
              onChange={handleConstraintChange}
              placeholder="e.g. 50"
              className="w-full border rounded px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Remaining Fat (g)</label>
            <input
              type="number"
              name="remaining_fat"
              value={constraints.remaining_fat || ''}
              onChange={handleConstraintChange}
              placeholder="e.g. 15"
              className="w-full border rounded px-3 py-2"
            />
          </div>
        </div>
        <button
          onClick={fetchSuggestions}
          className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
        >
          Get Suggestions
        </button>
      </div>

      {loading ? (
        <div className="text-center py-10">Loading suggestions...</div>
      ) : suggestions.length === 0 ? (
        <div className="bg-white rounded-xl shadow p-6 text-center text-gray-500">
          No suggestions found. Try adjusting your constraints.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {suggestions.map((meal, idx) => (
            <div key={idx} className="bg-white rounded-xl shadow overflow-hidden">
              <div className="p-6">
                <h3 className="text-xl font-bold mb-2">{meal.name}</h3>
                <p className="text-sm text-gray-600 mb-4">
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
            </div>
          ))}
        </div>
      )}
    </Layout>
  );
}
