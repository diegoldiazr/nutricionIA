import Layout from '../components/Layout';
import { useEffect, useState } from 'react';
import { apiClient } from '../lib/api';

export default function WeightTracking() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newWeight, setNewWeight] = useState('');
  const [newDate, setNewDate] = useState(new Date().toISOString().split('T')[0]);
  const userId = 1;

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const data = await apiClient.getWeightHistory(userId, 30);
      setHistory(data?.entries || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const logWeight = async (e) => {
    e.preventDefault();
    if (!newWeight) return;

    try {
      await apiClient.logWeight(userId, { weight: parseFloat(newWeight), date: newDate });
      setNewWeight('');
      fetchHistory();
    } catch (err) {
      console.error('Failed to log weight:', err);
      alert('Failed to log weight');
    }
  };

  const calculateTrend = () => {
    if (history.length < 2) return { trend: 'N/A', change: 0 };
    const start = history[history.length - 1]?.weight;
    const end = history[0]?.weight;
    const change = end - start;
    const trend = change < -0.5 ? 'down' : change > 0.5 ? 'up' : 'stable';
    return { trend, change };
  };

  const { trend, change } = calculateTrend();

  if (loading) return <Layout><div className="text-center py-10">Loading...</div></Layout>;

  return (
    <Layout title="Weight Tracking">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Weight Tracking</h1>
        <p className="text-gray-600">Monitor your weight progress over time.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow p-6">
          <div className="text-sm text-gray-500">Current Weight</div>
          <div className="text-3xl font-bold text-blue-600">
            {history[0]?.weight || '—'} kg
          </div>
        </div>
        <div className="bg-white rounded-xl shadow p-6">
          <div className="text-sm text-gray-500">Change (30d)</div>
          <div className={`text-3xl font-bold ${change < 0 ? 'text-green-600' : change > 0 ? 'text-red-600' : 'text-gray-600'}`}>
            {change > 0 ? '+' : ''}{change?.toFixed(1)} kg
          </div>
        </div>
        <div className="bg-white rounded-xl shadow p-6">
          <div className="text-sm text-gray-500">Trend</div>
          <div className="text-3xl font-bold capitalize text-purple-600">{trend}</div>
        </div>
      </div>

      {/* Log new weight */}
      <div className="bg-white rounded-xl shadow p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Log New Weight</h2>
        <form onSubmit={logWeight} className="flex items-end gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
            <input
              type="date"
              value={newDate}
              onChange={(e) => setNewDate(e.target.value)}
              className="w-full border rounded px-3 py-2"
            />
          </div>
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">Weight (kg)</label>
            <input
              type="number"
              step="0.1"
              value={newWeight}
              onChange={(e) => setNewWeight(e.target.value)}
              placeholder="Enter weight"
              className="w-full border rounded px-3 py-2"
            />
          </div>
          <button
            type="submit"
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
          >
            Log Weight
          </button>
        </form>
      </div>

      {/* Weight history table */}
      <div className="bg-white rounded-xl shadow overflow-hidden">
        <div className="px-6 py-4 border-b">
          <h2 className="text-xl font-semibold">Weight History</h2>
        </div>
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">Date</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">Weight (kg)</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">Change</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {history.map((entry, idx) => {
              const prev = history[idx - 1]?.weight;
              const change = prev ? entry.weight - prev : 0;
              return (
                <tr key={entry.date}>
                  <td className="px-6 py-4">{entry.date}</td>
                  <td className="px-6 py-4 font-medium">{entry.weight}</td>
                  <td className="px-6 py-4">
                    {prev && (
                      <span className={change < 0 ? 'text-green-600' : change > 0 ? 'text-red-600' : 'text-gray-600'}>
                        {change > 0 ? '+' : ''}{change?.toFixed(1)}
                      </span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {history.length === 0 && (
          <div className="p-6 text-center text-gray-500">No weight entries yet</div>
        )}
      </div>
    </Layout>
  );
}
