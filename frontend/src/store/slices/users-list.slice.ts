import { Api } from "@/lib/api";
import { createAsyncThunk, createSlice, PayloadAction } from "@reduxjs/toolkit";

interface User {
  username: string;
  email: string;
  role: "admin" | "user";
  isMFAEnabled: boolean;
}

interface UsersListState {
  users: User[];
  isPending: boolean;
  error?: string;
  isSuccess?: boolean;
}

const initialState: UsersListState = {
  users: [],
  isPending: false,
  error: "",
};

export const fetchUsers = createAsyncThunk("users/fetchUsers", async () => {
  const response = await Api.get("users", {
    withCredentials: true,
  });
  return response.data;
});

const usersListSlice = createSlice({
  name: "usersList",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchUsers.pending, (state) => {
        state.isPending = true;
      })
      .addCase(fetchUsers.fulfilled, (state, action: PayloadAction<User[]>) => {
        state.users = action.payload;
        state.isPending = false;
        state.isSuccess = true;
      })
      .addCase(fetchUsers.rejected, (state, action) => {
        state.error = action.error.message || "Failed to fetch users";
        state.isPending = false;
        state.isSuccess = false;
      });
  },
});

export default usersListSlice.reducer; 