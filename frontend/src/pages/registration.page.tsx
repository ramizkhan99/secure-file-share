import * as React from "react";
import { RegisterForm } from "@/components/forms";

const RegistrationPage: React.FC = () => {
  return (
    <div className="flex items-center justify-center min-h-screen w-full">
      <div className="w-full max-w-md">
        <RegisterForm />
      </div>
    </div>
  );
};

export { RegistrationPage };