import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { analysisAPI } from '../services/api';
import toast from 'react-hot-toast';
import { Eye, Trash2, Calendar, FileText, AlertCircle } from 'lucide-react';

const History = () => {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchAnalyses();
  }, []);

  const fetchAnalyses = async () => {
    try {
      console.log('📤 History: Fetching analyses...');
      const response = await analysisAPI.getHistory();
      console.log('✅ History: Analyses received:', response.data);
      
      // Normalize the data - handle both _id and id fields
      const normalizedAnalyses = (response.data || []).map(analysis => ({
        ...analysis,
        id: analysis.id || analysis._id
      }));
      
      console.log('📊 History: Normalized analyses:', normalizedAnalyses);
      setAnalyses(normalizedAnalyses);
    } catch (error) {
      console.error('❌ History: Error fetching analyses:', error);
      console.error('❌ History: Error response:', error.response);
      toast.error('Failed to load analysis history');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this analysis?')) {
      return;
    }

    try {
      await analysisAPI.deleteAnalysis(id);
      setAnalyses(analyses.filter(a => a.id !== id));
      toast.success('Analysis deleted successfully');
    } catch (error) {
      toast.error('Failed to delete analysis');
    }
  };

  const filteredAnalyses = analyses.filter(analysis => {
    if (filter === 'all') return true;
    return analysis.status === filter;
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'processing': return 'bg-yellow-100 text-yellow-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRiskColor = (risk) => {
    switch (risk?.toLowerCase()) {
      case 'high': return 'text-red-600';
      case 'medium': return 'text-yellow-600';
      case 'low': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto py-12 px-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading analysis history...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto py-12 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Analysis History</h1>
        <p className="text-gray-600">View and manage your genetic analysis results</p>
      </div>

      {/* Filter Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {['all', 'completed', 'processing', 'failed'].map((status) => (
              <button
                key={status}
                onClick={() => setFilter(status)}
                className={`py-2 px-1 border-b-2 font-medium text-sm capitalize ${
                  filter === status
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {status} ({analyses.filter(a => status === 'all' || a.status === status).length})
              </button>
            ))}
          </nav>
        </div>
      </div>

      {filteredAnalyses.length > 0 ? (
        <div className="card">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    File Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Risk Level
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Variants
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredAnalyses.map((analysis) => (
                  <tr key={analysis.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <FileText className="h-5 w-5 text-gray-400 mr-3" />
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {analysis.vcf_file}
                          </div>
                          <div className="text-sm text-gray-500">
                            ID: {analysis.id.slice(0, 8)}...
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(analysis.status)}`}>
                        {analysis.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {analysis.status === 'completed' ? (
                        <div>
                          <div className={`font-medium capitalize ${getRiskColor(analysis.risk_classification)}`}>
                            {analysis.risk_classification}
                          </div>
                          <div className="text-gray-500">
                            {Math.round(analysis.risk_probability * 100)}%
                          </div>
                        </div>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {analysis.status === 'completed' ? (
                        <div>
                          <div className="font-medium">{analysis.total_variants}</div>
                          <div className="text-gray-500">
                            {analysis.high_risk_variants} high risk
                          </div>
                        </div>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex items-center">
                        <Calendar className="h-4 w-4 mr-1" />
                        {new Date(analysis.created_at).toLocaleDateString()}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        {analysis.status === 'completed' && (
                          <Link
                            to={`/results/${analysis.id}`}
                            className="text-primary-600 hover:text-primary-900"
                          >
                            <Eye className="h-4 w-4" />
                          </Link>
                        )}
                        <button
                          onClick={() => handleDelete(analysis.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="card text-center">
          <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">
            {filter === 'all' ? 'No Analyses Found' : `No ${filter} analyses`}
          </h3>
          <p className="text-gray-600 mb-4">
            {filter === 'all' 
              ? 'Start by uploading your first VCF file'
              : `No analyses with ${filter} status found`
            }
          </p>
          {filter === 'all' && (
            <Link to="/upload" className="btn-primary">
              Upload VCF File
            </Link>
          )}
        </div>
      )}
    </div>
  );
};

export default History;