import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

const RiskGauge = ({ riskProbability, riskClassification }) => {
  const percentage = Math.round(riskProbability * 100);
  
  const data = [
    { name: 'Risk', value: percentage },
    { name: 'Safe', value: 100 - percentage }
  ];

  const getColor = (classification) => {
    switch (classification?.toLowerCase()) {
      case 'high': return '#ef4444';
      case 'medium': return '#f59e0b';
      case 'low': return '#10b981';
      default: return '#6b7280';
    }
  };

  const COLORS = [getColor(riskClassification), '#e5e7eb'];

  return (
    <div className="card text-center">
      <h3 className="text-lg font-semibold mb-4">Disease Risk Assessment</h3>
      <div className="relative">
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              startAngle={90}
              endAngle={-270}
              innerRadius={60}
              outerRadius={80}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex items-center justify-center">
          <div>
            <div className="text-3xl font-bold" style={{ color: getColor(riskClassification) }}>
              {percentage}%
            </div>
            <div className="text-sm text-gray-600 capitalize">
              {riskClassification} Risk
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskGauge;