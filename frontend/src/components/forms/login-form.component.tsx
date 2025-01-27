import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Link, useNavigate } from "react-router-dom"
import { useAppDispatch, useAppSelector } from "@/store"
import { loginUser } from "@/store/slices/user.slice"
import { useEffect } from "react"

const formSchema = z.object({
  username: z.string().min(6, {
    message: "Username must be at least 6 characters.",
  }),
  password: z.string().min(8, {
    message: "Password must be at least 8 characters.",
  }),
})

export function LoginForm() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: "",
      password: "",
    },
  })

  const dispatch = useAppDispatch();
  const { isSuccess, code } = useAppSelector((state) => state.user);
  const navigate = useNavigate();

  function onSubmit(values: z.infer<typeof formSchema>) {
    dispatch(loginUser({
      username: values.username,
      password: values.password,
    }))
  }

  useEffect(() => {
    if (isSuccess) {
      if (code && code === "MFA_REQUIRED") {
        navigate("/mfa/verify");
      } else {
        navigate("/home");
      }
    }
  }, [isSuccess, navigate, code]);

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
        <FormField
          control={form.control}
          name="username"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Username</FormLabel>
              <FormControl>
                <Input placeholder="username" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <Input type="password" placeholder="password" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <div className="button-and-register flex justify-between">
          <Button type="submit">Submit</Button>
          <Link to="/register">Register</Link>
        </div>
      </form>
    </Form>
  )
}
