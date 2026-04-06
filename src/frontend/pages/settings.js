import Layout from '../components/Layout';
import { useEffect, useState } from 'react';
import { apiClient } from '../lib/api';

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    dietary_restrictions: [],
    favorite_foods: [],
    disliked_foods: [],
    cooking_equipment: ['airfryer', 'stove', 'oven'],
    prep_time_max: 45,
    difficulty_max: 'medium'
  });
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const userId = 1;

  const dietaryOptions = ['gluten-free', 'dairy-free', 'vegetarian', 'vegan', 'keto', 'paleo', 'low-carb'];
  const equipmentOptions = ['airfryer', 'stove', 'oven', 'microwave', 'thermomix', 'blender', 'slow-cooker'];
  const difficultyOptions = ['easy', 'medium', 'hard'];

  const toggleArrayItem = (arrayName, item) => {
    setSettings(prev => ({
      ...prev,
      [arrayName]: prev[arrayName].includes(item)
        ? prev[arrayName].filter(i => i !== item)
        : [...prev[arrayName], item]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');
    try {
      await apiClient.updateSettings(userId, settings);
      setMessage('Settings saved successfully!');
      setTimeout(() => setMessage(''), 3000);
    } catch (err) {
      setMessage('Failed to save settings');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Layout title="Settings">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Settings</h1>
        <p className="text-gray-600">Customize your nutrition preferences.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Dietary Restrictions */}
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Dietary Restrictions</h2>
          <div className="flex flex-wrap gap-3">
            {dietaryOptions.map(option => (
              <label key={option} className="inline-flex items-center px-4 py-2 border rounded-lg cursor-pointer hover:bg-gray-50">
                <input
                  type="checkbox"
                  checked={settings.dietary_restrictions.includes(option)}
                  onChange={() => toggleArrayItem('dietary_restrictions', option)}
                  className="form-checkbox text-blue-600"
                />
                <span className="ml-2 capitalize">{option}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Favorite Foods */}
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Favorite Foods</h2>
          <p className="text-sm text-gray-600 mb-3">Comma-separated list of foods you enjoy</p>
          <textarea
            value={settings.favorite_foods?.join(', ')}
            onChange={(e) => setSettings(prev => ({ ...prev, favorite_foods: e.target.value.split(',').map(s => s.trim()).filter(Boolean) }))}
            className="w-full border rounded-lg px-4 py-3 h-24"
            placeholder="chicken breast, brown rice, broccoli..."
          />
        </div>

        {/* Disliked Foods */}
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Disliked Foods</h2>
          <p className="text-sm text-gray-600 mb-3">Foods to avoid in suggestions</p>
          <textarea
            value={settings.disliked_foods?.join(', ')}
            onChange={(e) => setSettings(prev => ({ ...prev, disliked_foods: e.target.value.split(',').map(s => s.trim()).filter(Boolean) }))}
            className="w-full border rounded-lg px-4 py-3 h-24"
            placeholder="shellfish, olives..."
          />
        </div>

        {/* Cooking Equipment */}
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Cooking Equipment</h2>
          <div className="flex flex-wrap gap-3">
            {equipmentOptions.map(option => (
              <label key={option} className="inline-flex items-center px-4 py-2 border rounded-lg cursor-pointer hover:bg-gray-50">
                <input
                  type="checkbox"
                  checked={settings.cooking_equipment.includes(option)}
                  onChange={() => toggleArrayItem('cooking_equipment', option)}
                  className="form-checkbox text-blue-600"
                />
                <span className="ml-2 capitalize">{option.replace('-', ' ')}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Time & Difficulty */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Max Prep Time</h2>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min="10"
                max="120"
                step="5"
                value={settings.prep_time_max}
                onChange={(e) => setSettings(prev => ({ ...prev, prep_time_max: parseInt(e.target.value) }))}
                className="flex-1"
              />
              <span className="text-lg font-bold text-blue-600 w-20 text-right">{settings.prep_time_max} min</span>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Max Difficulty</h2>
            <div className="flex gap-3">
              {difficultyOptions.map(level => (
                <button
                  key={level}
                  type="button"
                  onClick={() => setSettings(prev => ({ ...prev, difficulty_max: level }))}
                  className={`flex-1 py-2 rounded-lg font-medium capitalize ${
                    settings.difficulty_max === level
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {level}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
          >
            {saving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>

        {message && (
          <div className={`p-4 rounded-lg ${message.includes('success') ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
            {message}
          </div>
        )}
      </form>
    </Layout>
  );
}
