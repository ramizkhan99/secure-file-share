import * as React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import App from "./App";
import { EnableMFAPage, RegistrationPage } from "@/pages";
import { VerifyMFAPage } from "./pages/verify-mfa.page";
import { HomePage } from "./pages/home.page";
import { UsersPage } from "./pages/users.page";
import { Toaster } from "./components/ui/toaster";

const AppRouter: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/register" element={<RegistrationPage />} />
        <Route path="/mfa/enable" element={<EnableMFAPage />} />
        <Route path="/mfa/verify" element={<VerifyMFAPage />} />
        <Route path="/home" element={<HomePage />} />
        <Route path="/users" element={<UsersPage />} />
      </Routes>
      <Toaster />
    </Router>
  );
};

export default AppRouter;