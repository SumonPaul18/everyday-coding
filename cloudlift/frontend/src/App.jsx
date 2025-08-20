// frontend/src/App.jsx
function App() {
  return (
    <>
      {/* Navbar */}
      <nav className="bg-white shadow-md fixed w-full top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-blue-600">CloudLift</h1>
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-full font-medium transition">
            Sign In
          </button>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-28 pb-20 text-center bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 text-white">
        <div className="max-w-4xl mx-auto px-6">
          <h1 className="text-4xl md:text-6xl font-extrabold mb-6">
            Build Your Cloud
            <span className="text-blue-300"> Faster</span>
          </h1>
          <p className="text-xl mb-10 text-blue-100">
            Launch VMs, manage networks, and scale your infrastructure on our OpenStack-powered cloud platform — simple, fast, and secure.
          </p>
          <div className="space-x-4">
            <button className="bg-white text-blue-900 hover:bg-gray-200 px-8 py-3 rounded-full text-lg font-semibold transition">
              Get Started Free
            </button>
            <button className="border-2 border-white text-white hover:bg-white hover:text-blue-900 px-8 py-3 rounded-full text-lg font-semibold transition">
              Learn More
            </button>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-800">Why Choose CloudLift?</h2>
          <div className="grid md:grid-cols-3 gap-10">
            <div className="text-center p-6 bg-white rounded-lg shadow">
              <h3 className="text-2xl font-bold text-blue-600 mb-4">⚡ Fast VMs</h3>
              <p className="text-gray-600">Launch instances in seconds with SSD storage and high-performance CPUs.</p>
            </div>
            <div className="text-center p-6 bg-white rounded-lg shadow">
              <h3 className="text-2xl font-bold text-blue-600 mb-4">🔒 Secure</h3>
              <p className="text-gray-600">Isolated projects, firewalls, and role-based access control for your safety.</p>
            </div>
            <div className="text-center p-6 bg-white rounded-lg shadow">
              <h3 className="text-2xl font-bold text-blue-600 mb-4">🌍 Global</h3>
              <p className="text-gray-600">Deploy in multiple regions with low-latency connectivity.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8 text-center">
        <p>&copy; 2025 CloudLift. All rights reserved.</p>
      </footer>
    </>
  );
}

export default App;