import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Buffer } from "buffer";
import {
  Form,
  FormField,
  FormItem,
  FormControl,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useEffect, useState } from "react";
import { useAppDispatch, useAppSelector } from "@/store";
import { useNavigate } from "react-router-dom";
import { Api } from "@/lib/api";
import { setUser } from "@/store/slices";

const mfaSchema = z.object({
  totp: z.string().length(6, {
    message: "TOTP must be exactly 6 digits.",
  }),
});

export function VerifyMFA() {
  const [qrCode, setQrCode] = useState<string | null>(null);
  const { email, username } = useAppSelector((state) => state.user);
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  const form = useForm<z.infer<typeof mfaSchema>>({
    resolver: zodResolver(mfaSchema),
    defaultValues: {
      totp: "",
    },
  });

  useEffect(() => {
    Api.get('users/mfa/qr-code', {
      withCredentials: true,
      responseType: 'arraybuffer'
    }).then((response) => {
      const base64 = Buffer.from(response.data, 'binary').toString('base64');
      setQrCode(`data:image/png;base64,${base64}`);
    });
  }, [email, username]);

  const onSubmit = async (values: z.infer<typeof mfaSchema>) => {
    const response = await Api.post('users/mfa/verify', {
      token: values.totp,
      username,
    }, {
      withCredentials: true,
    })

    if (response.data.success) {
      dispatch(setUser({
        username: response.data.data.username,
        email: response.data.data.email,
        isMFAEnabled: true,
        isPending: false,
        role: response.data.data.role
      }))
      navigate("/home");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4">
      <h1 className="text-2xl font-bold mb-4">Verify Multi-Factor Authentication</h1>
      {
        qrCode && (
          <>
            <img src={qrCode} alt="QR Code" className="mb-4" />
            <p className="mb-4">Scan the QR code with your authenticator app to get the TOTP.</p>
            <h2>OR</h2>
          </>
        )
      }
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8 mt-4">
          <FormField
            control={form.control}
            name="totp"
            render={({ field }) => (
              <FormItem>
                <FormControl>
                  <Input placeholder="Enter 6-digit TOTP" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <div className="flex justify-center">
            <Button type="submit">Verify TOTP</Button>
          </div>
        </form>
      </Form>
    </div>
  );
}