import './App.scss'
import { LoginForm } from './components/forms';

function App() {
  return (
    <div className='flex items-center justify-center min-h-screen w-full'>
      <div className="w-full max-w-md">
        <LoginForm />
      </div>
    </div>
  )
}

export default App
