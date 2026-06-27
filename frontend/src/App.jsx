import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import CheckEmailStep from './components/auth/CheckEmailStep'



function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <CheckEmailStep />
      
    </>
  )
}

export default App
