import Layout from '../components/Layout';
import { useEffect, useState } from 'react';
import { apiClient } from '../lib/api';

export default function AICoach() {
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(true);
  const [quickMessage, setQuickMessage] = useState('');
  const [quickFeedback, setQuickFeedback] = useState(null);
  const userId = 1;

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      const data = await apiClient.getProgressAnalysis(userId, 7);
      setRecommendations(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getQuickFeedback = async () => {
    try {
      const data = await apiClient.getRecommendations(userId); // Using same endpoint for now
      setQuickFeedback(data);
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) return <Layout><div className="text-center py-10">Loading coach recommendations...</div></Layout>;

  const rec = recommendations?.recommendations || {};
  const analysis = recommendations?.progress_analysis || {};

  return (
    <Layout title="AI Coach">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">AI Coach</h1>
        <p className="text-gray-600">Personalized advice based on your progress.</p>
      </div>

      {/* Overall Feedback */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 mb-8">
        <h2 className="text-xl font-semibold mb-2 text-blue-900">Overall Feedback</h2>
        <p className="text-blue-800 leading-relaxed">
          {rec.overall_feedback || 'No feedback available. Start logging meals to get personalized coaching.'}
        </p>
        <div className="mt-3 flex items-center gap-4">
          <span className="text-sm text-gray-600">Confidence: {Math.round((rec.confidence_score || 0) * 100)}%</span>
          <span className="text-sm text-gray-600">•</span>
          <span className="text-sm text-gray-600">Based on last 7 days</span>
        </div>
      </div>

      {/* Calorie Recommendation */}
      {rec.calorie_adjustment && (
        <div className="bg-white rounded-xl shadow p-6 mb-6">
          <h3 className="text-lg font-semibold mb-3 flex items-center">
            <span className="mr-2">🔥</span> Calorie Adjustment
          </h3>
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <span className="font-medium">Recommendation:</span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                rec.calorie_adjustment.adjustment === 'increase' ? 'bg-green-100 text-green-800' :
                rec.calorie_adjustment.adjustment === 'decrease' ? 'bg-red-100 text-red-800' :
                'bg-blue-100 text-blue-800'
              }`}>
                {rec.calorie_adjustment.adjustment === 'increase' ? '⬆ Increase' :
                 rec.calorie_adjustment.adjustment === 'decrease' ? '⬇ Decrease' : '→ Maintain'}
                {rec.calorie_adjustment.amount > 0 && ` by ${rec.calorie_adjustment.amount} kcal`}
              </span>
            </div>
            <p className="text-gray-700">{rec.calorie_adjustment.reason}</p>
          </div>
        </div>
      )}

      {/* Macro Recommendation */}
      {rec.macro_adjustment && (
        <div className="bg-white rounded-xl shadow p-6 mb-6">
          <h3 className="text-lg font-semibold mb-3 flex items-center">
            <span className="mr-2">🥩</span> Protein Adjustment
          </h3>
          <div className="p-4 bg-gray-50 rounded-lg">
            {rec.macro_adjustment.adjust_protein ? (
              <>
                <div className="flex justify-between items-center mb-2">
                  <span className="font-medium">Adjustment:</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    rec.macro_adjustment.change_grams > 0 ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {rec.macro_adjustment.change_grams > 0 ? '+' : ''}{rec.macro_adjustment.change_grams}g per day
                  </span>
                </div>
                <p className="text-gray-700">{rec.macro_adjustment.reason}</p>
              </>
            ) : (
              <p className="text-green-700">{rec.macro_adjustment.reason}</p>
            )}
          </div>
        </div>
      )}

      {/* Meal Timing */}
      {rec.meal_timing && rec.meal_timing.suggestions?.length > 0 && (
        <div className="bg-white rounded-xl shadow p-6 mb-6">
          <h3 className="text-lg font-semibold mb-3 flex items-center">
            <span className="mr-2">⏰</span> Meal Timing Suggestions
          </h3>
          <ul className="space-y-2">
            {rec.meal_timing.suggestions.map((suggestion, idx) => (
              <li key={idx} className="flex items-start">
                <span className="text-blue-500 mr-2">•</span>
                <span className="text-gray-700">{suggestion}</span>
              </li>
            ))}
          </ul>
          <p className="mt-3 text-sm text-gray-600">{rec.meal_timing.rationale}</p>
        </div>
      )}

      {/* Food Suggestions */}
      {rec.food_suggestions?.length > 0 && (
        <div className="bg-white rounded-xl shadow p-6 mb-6">
          <h3 className="text-lg font-semibold mb-3 flex items-center">
            <span className="mr-2">🍎</span> Food Suggestions
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {rec.food_suggestions.map((food, idx) => (
              <div key={idx} className="border rounded-lg p-3">
                <div className="font-medium">{food.food}</div>
                <div className="text-sm text-gray-600">{food.reason}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Feedback Button */}
      <div className="bg-gray-50 rounded-xl p-6 text-center">
        <h3 className="text-lg font-semibold mb-3">Need a quick boost?</h3>
        <button
          onClick={getQuickFeedback}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
        >
          Get Quick Feedback
        </button>
        {quickFeedback && (
          <div className="mt-4 p-4 bg-white rounded-lg border">
            <p className="text-gray-800">{quickFeedback.message}</p>
            {quickFeedback.suggestions && (
              <ul className="mt-2 space-y-1">
                {quickFeedback.suggestions.map((s, i) => (
                  <li key={i} className="text-sm text-gray-600">• {s}</li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </Layout>
  );
}
