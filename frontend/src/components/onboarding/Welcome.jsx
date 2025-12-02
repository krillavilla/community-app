import { useNavigate } from 'react-router-dom';

/**
 * Welcome Screen - First step of onboarding
 * Introduces the Garden Platform with warmth and inclusivity
 */
export default function Welcome() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-emerald-50 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full text-center space-y-8">
        {/* Logo/Icon */}
        <div className="text-6xl mb-4">🌱</div>
        
        {/* Title */}
        <h1 className="text-4xl md:text-5xl font-bold text-green-900">
          Welcome to Garden
        </h1>
        
        {/* Subtitle */}
        <p className="text-xl md:text-2xl text-green-700 font-light">
          A space for personal growth, community support, 
          and meaningful connections
        </p>
        
        {/* Main Description */}
        <div className="bg-white rounded-2xl shadow-lg p-8 space-y-4">
          <p className="text-lg text-gray-700 leading-relaxed">
            Whether you're seeking <span className="font-semibold text-green-700">emotional healing</span>, 
            {' '}<span className="font-semibold text-green-700">spiritual depth</span>, 
            or simply a place to <span className="font-semibold text-green-700">grow</span>
            {' '}— you're welcome here.
          </p>
          
          <p className="text-gray-600">
            Plant seeds of positive habits. Nurture your personal garden. 
            Share your harvest with a supportive community.
          </p>
        </div>
        
        {/* CTA Button */}
        <button
          onClick={() => navigate('/onboarding/path')}
          className="bg-green-600 hover:bg-green-700 text-white font-semibold 
                     text-lg px-12 py-4 rounded-full shadow-lg 
                     transform transition hover:scale-105 active:scale-95"
        >
          Begin Your Journey 🌱
        </button>
        
        {/* Already have account */}
        <p className="text-sm text-gray-500">
          Already growing with us?{' '}
          <button 
            onClick={() => navigate('/login')}
            className="text-green-600 hover:text-green-700 font-medium underline"
          >
            Sign in
          </button>
        </p>
      </div>
    </div>
  );
}
