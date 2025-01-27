import { Api } from "@/lib/api";
import { createAsyncThunk, createSlice, PayloadAction } from "@reduxjs/toolkit";
import { PURGE } from "redux-persist";

interface UserState {
  username: string;
  email: string;
  isPending: boolean;
  error?: string;
  isSuccess?: boolean;
  isLogoutSuccess?: boolean;
  isMFAEnabled?: boolean;
  code?: string;
  role: "admin" | "user" | "guest";
}

const initialState: UserState = {
  username: "",
  email: "",
  isPending: false,
  error: "",
  isMFAEnabled: false,
  role: "guest",
};

export const registerUser = createAsyncThunk(
  "user/registerUser",
  async (userData: {
    username: string;
    email: string;
    password: string;
    role: "admin" | "user" | "guest";
  }) => {
    const response = await Api.post("users", userData, {
      withCredentials: true,
    });
    return {
      username: userData.username,
      email: userData.email,
      ...response.data,
    };
  }
);

export const loginUser = createAsyncThunk(
  "user/loginUser",
  async (userData: { username: string; password: string }) => {
    const response = await Api.post("users/login", userData, {
      withCredentials: true,
    });
    return { username: userData.username, response: response.data };
  }
);

export const logoutUser = createAsyncThunk("user/logoutUser", async () => {
  const response = await Api.delete("users/logout", {
    withCredentials: true,
  });
  return response.data;
});

export const enableMFA = createAsyncThunk("user/enableMFA", async () => {
  const response = await Api.post(
    "users/mfa/enable",
    {},
    {
      withCredentials: true,
    }
  );
  return response.data;
});

const userSlice = createSlice({
  name: "user",
  initialState,
  reducers: {
    setUser: (state, action: PayloadAction<UserState>) => {
      state.username = action.payload.username;
      state.email = action.payload.email;
      state.role = action.payload.role;
      state.isMFAEnabled = action.payload.isMFAEnabled;
    },
    setUsername: (state, action: PayloadAction<string>) => {
      state.username = action.payload;
    },
    clearUser: (state) => {
      state.username = "";
      state.email = "";
      state.error = "";
      state.isPending = false;
      state.isSuccess = false;
      state.isMFAEnabled = false;
      state.isLogoutSuccess = false;
      state.role = "guest";
    },
    clearFlags: (state) => {
      state.error = "";
      state.isPending = false;
      state.isSuccess = false;
      state.isLogoutSuccess = false;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(registerUser.pending, (state) => {
        state.isPending = true;
      })
      .addCase(
        registerUser.fulfilled,
        (state, action: PayloadAction<{ username: string; email: string }>) => {
          state.username = action.payload.username;
          state.email = action.payload.email;
          state.isPending = false;
          state.isSuccess = true;
        }
      )
      .addCase(registerUser.rejected, (state, action) => {
        state.error = action.error.message || "User registration failed";
        state.isPending = false;
        state.isSuccess = false;
      })
      .addCase(loginUser.pending, (state) => {
        state.isPending = true;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.isPending = false;
        state.isSuccess = true;
        state.code = action.payload.response.code;
        if (!state.code || state.code !== "MFA_REQUIRED") {
          state.isMFAEnabled = action.payload.response.data.isMFAEnabled;
          state.email = action.payload.response.data.email;
          state.username = action.payload.username;
          state.role = action.payload.response.data.role;
        }
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.error = action.error.message || "User login failed";
        state.isPending = false;
        state.isSuccess = false;
      })
      .addCase(enableMFA.pending, (state) => {
        state.isPending = true;
      })
      .addCase(enableMFA.fulfilled, (state) => {
        state.isPending = false;
        state.isMFAEnabled = true;
        state.isSuccess = true;
      })
      .addCase(enableMFA.rejected, (state, action) => {
        state.error = action.error.message || "MFA enable failed";
        state.isPending = false;
        state.isMFAEnabled = false;
      })
      .addCase(logoutUser.pending, (state) => {
        state.isPending = true;
      })
      .addCase(logoutUser.fulfilled, (state) => {
        state.username = "";
        state.email = "";
        state.isPending = false;
        state.isMFAEnabled = false;
        state.isLogoutSuccess = true;
        state.isSuccess = true;
      })
      .addCase(logoutUser.rejected, (state, action) => {
        state.error = action.error.message || "User logout failed";
        state.isPending = false;
        state.isSuccess = false;
      })
      .addCase(PURGE, () => initialState);
  },
});

export const { setUser, clearUser, clearFlags } = userSlice.actions;
export default userSlice.reducer;

export const selectIsAdmin = (state: { user: UserState }) =>
  state.user.role === "admin";

export const selectIsUser = (state: { user: UserState }) =>
  state.user.role === "user";
