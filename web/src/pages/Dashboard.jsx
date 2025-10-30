import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { analysisAPI } from '../services/api';
import RiskGauge from '../components/RiskGauge';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Upload, History, TrendingUp, FileText, AlertTriangle } from 'lucide-react';

const Dashboard = ({ user }) => {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    total: 0,
    completed: 0,
    highRisk: 0,
    avgRisk: 0
  });

  useEffect(() => {
    fetchAnalyses();
  }, []);

  const fetchAnalyses = async () => {
    try {
      const response = await analysisAPI.getHistory();
      const analysisData = response.data;
      setAnalyses(analysisData);
      
      // Calculate stats
      const completed = analysisData.filter(a => a.status === 'completed');
      const highRisk = completed.filter(a => a.risk_classification === 'high').length;
      const avgRisk = completed.length > 0 
        ? completed.reduce((sum, a) => sum + a.risk_probability, 0) / completed.length 
        : 0;
      
      setStats({
        total: analysisData.length,
        completed: completed.length,
        highRisk,
        avgRisk
      });
    } catch (error) {
      console.error('Failed to fetch analyses:', error);
    } finally {
      setLoading(false);
    }
  };

  const recentAnalyses = analyses.slice(0, 5);
  const completedAnalyses = analyses.filter(a => a.status === 'completed');

  const chartData = completedAnalyses.map((analysis, index) => ({
    name: `Analysis ${index + 1}`,
    risk: Math.round(analysis.risk_probability * 100),
    variants: analysis.total_variants
  }));

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto py-12 px-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto py-12 px-4">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Welcome back, {user?.full_name || user?.username}!
        </h1>
        <p className="text-gray-600">
          Monitor your genetic analysis results and health insights
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid md:grid-cols-4 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center">
            <FileText className="h-8 w-8 text-primary-600 mr-3" />
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              <p className="text-gray-600">Total Analyses</p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-success-600 mr-3" />
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.completed}</p>
              <p className="text-gray-600">Completed</p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center">
            <AlertTriangle className="h-8 w-8 text-danger-600 mr-3" />
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.highRisk}</p>
              <p className="text-gray-600">High Risk</p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center">
            <BarChart className="h-8 w-8 text-warning-600 mr-3" />
            <div>
              <p className="text-2xl font-bold text-gray-900">{Math.round(stats.avgRisk * 100)}%</p>
              <p className="text-gray-600">Avg Risk</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Risk Overview */}
        <div className="lg:col-span-1">
          {completedAnalyses.length > 0 ? (
            <RiskGauge 
              riskProbability={completedAnalyses[0].risk_probability}
              riskClassification={completedAnalyses[0].risk_classification}
            />
          ) : (
            <div className="card text-center">
              <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No Analysis Yet</h3>
              <p className="text-gray-600 mb-4">Upload your first VCF file to get started</p>
              <Link to="/upload" className="btn-primary">
                Upload VCF File
              </Link>
            </div>
          )}
        </div>

        {/* Risk Trend Chart */}
        <div className="lg:col-span-2">
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Risk Analysis Trend</h3>
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="risk" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center py-12">
                <BarChart className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">No completed analyses to display</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recent Analyses */}
      <div className="mt-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Recent Analyses</h2>
          <Link to="/history" className="text-primary-600 hover:text-primary-700 flex items-center">
            <History className="h-4 w-4 mr-1" />
            View All
          </Link>
        </div>

        {recentAnalyses.length > 0 ? (
          <div className="card">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      File
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Risk Level
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {recentAnalyses.map((analysis) => (
                    <tr key={analysis.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {analysis.vcf_file}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          analysis.status === 'completed' 
                            ? 'bg-green-100 text-green-800'
                            : analysis.status === 'processing'
                            ? 'bg-yellow-100 text-yellow-800'
                            : analysis.status === 'failed'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {analysis.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {analysis.status === 'completed' ? (
                          <span className={`capitalize ${
                            analysis.risk_classification === 'high' ? 'text-red-600' :
                            analysis.risk_classification === 'medium' ? 'text-yellow-600' :
                            'text-green-600'
                          }`}>
                            {analysis.risk_classification}
                          </span>
                        ) : '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(analysis.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="card text-center">
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Analyses Yet</h3>
            <p className="text-gray-600 mb-4">Start by uploading your genomic data</p>
            <Link to="/upload" className="btn-primary">
              Upload VCF File
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;