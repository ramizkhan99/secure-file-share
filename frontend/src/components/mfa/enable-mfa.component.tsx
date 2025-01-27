import { Button } from "@/components/ui/button";
import { useAppDispatch, useAppSelector } from "@/store";
import { clearFlags, enableMFA } from "@/store/slices/user.slice";
import { useEffect } from "react";
import { Alert, AlertDescription, AlertTitle } from "../ui/alert";
import { useNavigate } from "react-router-dom";

export function EnableMFA() {
    const dispatch = useAppDispatch();
    const navigate = useNavigate();
    const { isSuccess, isMFAEnabled } = useAppSelector((state) => state.user);

    const mfaEnabled = isSuccess || isMFAEnabled;

    const handleEnableMFA = () => {
        dispatch(enableMFA());
    };

    useEffect(() => {
        dispatch(clearFlags());
    }, [dispatch]);

    return (
        <div className="flex flex-col items-center justify-center min-h-screen p-4">
            <h1 className="text-2xl font-bold mb-4">Enable Multi-Factor Authentication</h1>
            {
                !mfaEnabled &&
                <p className="mb-4">Would you like to enable Multi-Factor Authentication (MFA) for added security?</p>
            }
            <div className="flex justify-center">
                {
                    !mfaEnabled && (
                        <Button onClick={handleEnableMFA}>Enable MFA</Button>
                    )
                }
            </div>
            {
                mfaEnabled && (
                    <Alert className="mt-4 flex flex-col items-center">
                        <AlertTitle>Success</AlertTitle>
                        <AlertDescription>MFA has been enabled.</AlertDescription>
                        <Button className="mt-4" onClick={() => navigate("/mfa/verify")}>Verify MFA</Button>
                    </Alert>
                )
            }
            {
                !mfaEnabled && (
                    <Button variant="link" className="mt-4 bg-transparent outline-none hover:border-none focus:outline-none" onClick={() => navigate("/home")}>
                        Skip for now
                    </Button>
                )
            }
        </div>
    );
}