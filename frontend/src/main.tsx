import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.scss'
import AppRouter from './Router.tsx'
import store, { persistor } from './store/index.ts'
import { Provider } from 'react-redux'
import { PersistGate } from 'redux-persist/integration/react'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}>
        <AppRouter />
      </PersistGate>
    </Provider>
  </StrictMode>,
)
